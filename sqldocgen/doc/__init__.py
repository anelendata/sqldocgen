from collections import defaultdict
import csv, os, re, sys


def rec_dd():
    return defaultdict(rec_dd)


def build_dep(dep_list, dep_schema, dep_view, refs):
    for ref in refs:
        s = ref.strip("`").split(".")
        table = s[-1]
        if len(s) >= 2:
            schema = s[-2]
        else:
            schema = dep_schema
        dep_list.append([schema, table, dep_schema, dep_view])
    return dep_list


def get_markdown(doc, sql, schema, table, columns, refs, image_format="png", dot_dir="."):
    if image_format == "d3":
        with open(os.path.join(dot_dir, "%s.%s.dot" % (schema, table)), "r") as f:
            dot = f.read()
        image_embed = """
<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="https://unpkg.com/viz.js@1.8.0/viz.js" type="application/javascript"></script>
<script src="https://unpkg.com/d3-graphviz@1.4.0/build/d3-graphviz.min.js"></script>
<div id="graph" style="text-align: center;"></div>
<script>
d3.select("#graph").graphviz()
  .fade(false)
  .renderDot(`%s`);
</script>""" % dot

    elif image_format == "svg":
        image_embed = '<embed src="./svg/%s.%s.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></embed>' % (schema, table)
    else:
        image_embed = '<img src="./%s/%s.%s.%s" width="80%%"/>' % (image_format, schema, table, image_format)

    output = (["## %s.%s" % (schema, table)] +
              ["\n" + image_embed] +
              ["\n" + doc] +
              ["\n### Columns"] +
              ["- %s" % col for col in columns] +
              ["\n### Depencencies"] +
              ["- [%s](%s.%s.md)" % (ref, schema, ref) for ref in refs] +
              ["\n### SQL source\n", "```mysql", sql,  "```"])
    return "\n".join(output)


def parse_sql_file(path, fname, schema="", all_columns={}):
    fullpath = os.path.join(path, fname)
    if fname[-3:] != "sql":
        raise ValueError("Non-sql file: " + fullpath)

    print("Parsing " + fullpath)
    table = fname[0:-4]
    refs = set()
    cols = []
    with open(fullpath) as f:
        dbt = f.read()
        doc_start = dbt.find("/*")
        doc_end = dbt.find("*/")
        doc = dbt[doc_start + 2:doc_end] if doc_start > -1 else ""
        sql = (dbt[doc_end + 2:] if doc_end > -1 else dbt)
        pattern = re.compile(r"\bfrom[ ][ ]*[^\s({][^\s]*\b|\bjoin\b[ ][ ]*[^\s({][^\s]*", flags=re.I)
        for m in pattern.findall(sql):
            ref = m[5:].strip().strip("`").strip("[").strip("]")
            refs.add(ref)

        # dbt pattern
        pattern = re.compile(r"{{[ ]*ref[ ]*\([ ]*'([a-zA-Z_]*)'[ ]*\)[ ]*}}")
        for m in pattern.findall(sql):
            ref = schema + "." + m.strip().strip("`")
            refs.add(ref)

    schema_table = schema + "." + table
    columns = all_columns.get(schema_table, [])
    columns.sort()

    return (doc, sql, schema, table, columns, refs)


def write_doc(model_dir, out_dir, schema, all_columns, image_format="svg"):
    model_dirs = os.walk(model_dir)
    toc = []
    dot_dir = os.path.join(out_dir, "dot")
    for cdir, dirs, files in model_dirs:
        for fname in files:
            if fname[-3:] != "sql":
                print("Skipping non-sql file: " + fname)
                continue

            tname = fname[0:-4]
            try:
                d, sql, s, t, c, r = parse_sql_file(cdir, fname, schema, all_columns)
            except ValueError as e:
                print(e)
                continue
            if not r:
                print("Not found dependency")
                continue
            output = get_markdown(d, sql, s, t, c, r, image_format, dot_dir=dot_dir)
            with open(os.path.join(out_dir, schema + "." + tname + ".md"), "w") as f:
                f.write(output)
            toc = toc + ["* [%s](%s.%s.md)" % (tname, schema, tname)]

    toc.sort()
    with open(os.path.join(out_dir, "README.md"), "w") as f:
        f.write("# %s\n" % schema)
        if image_format == "svg":
            f.write('<embed src="./svg/all_tables.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></embed>\n')
        else:
            f.write('<img src="./' + image_format + '/all_tables.' + image_format + '" width="80%%"/>\n')
        f.write("\n".join(toc))


    with open(os.path.join(out_dir, "SUMMARY.md"), "w") as f:
        f.write("# Summary\n")
        f.write("\n".join(toc))


def make_tree(model_dir, out_dir, schema, all_columns, write_file=True):
    model_dirs = os.walk(model_dir)
    toc = []
    dep_list = []
    print("Building TOC")
    for cdir, dirs, files in model_dirs:
        for fname in files:
            if fname[-3:] != "sql":
                print("Skipping non-sql file: " + fname)
                continue
            try:
                d, sql, s, t, c, r = parse_sql_file(cdir, fname, schema, all_columns)
            except ValueError as e:
                print(e)
                continue
            if not r:
                print("Not found dependency")
                continue
            dep_list = build_dep(dep_list, s, t, r)

    if write_file:
        # dep_list format: [source_schema, source_table, dep_schema, dep_view]
        with open(os.path.join(out_dir, "_dependency.csv"), "w") as f:
            w = csv.writer(f)
            for row in dep_list:
                w.writerow(row)

    return dep_list


def read_columns_from_csv(dirname, all_column_file,
                          schema_col=0, table_col=1, column_col=2):
    all_columns = {}
    if all_column_file:
        with open(all_column_file) as csvfile:
            rows = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in rows:
                cur_schema = row[schema_col]
                cur_table = row[table_col]
                cur_schema_table = cur_schema + "." + cur_table
                cur_column = row[column_col]
                if all_columns.get(cur_schema_table, None) is None:
                    all_columns[cur_schema_table] = []
                all_columns[cur_schema_table] = list(set().union(all_columns[cur_schema_table], [cur_column]))
    return all_columns


if __name__ == '__main__':
    """
    Usage: python doc.py dbt_root_dir output_dir schema_name column_list.csv
    """
    dirname = "." if len(sys.argv) == 1 else sys.argv[1]
    outdir = os.path.join(dirname, "doc") if len(sys.argv) < 3 else sys.argv[2]
    schema = None if len(sys.argv) < 4 else sys.argv[3]
    all_column_file = None if len(sys.argv) < 5 else sys.argv[4]

    if not os.path.isdir(dirname):
        raise "The directory %s does not exist" % dirname
    run(os.path.join(dirname, "models"), outdir, schema, all_column_file)
