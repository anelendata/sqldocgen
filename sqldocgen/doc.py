from collections import defaultdict
import csv, os, re, sys


def rec_dd():
    return defaultdict(rec_dd)


def build_dep(dep_list, dep_schema, dep_view, refs):
    for ref in refs:
        s = ref.strip("`").split(".")
        table = s[-1]
        schema = s[-2]
        dep_list.append([schema, table, dep_schema, dep_view])
    return dep_list


def get_markdown(doc, sql, schema, table, columns, refs, image_format="png"):
    if image_format == "svg":
        image_embed = '<embed src="./svg/%s.%s.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></embed>' % (schema, table)
    else:
        image_embed = '<img src="./%s/%s.%s.%s" width="80%%"/>' % (image_format, schema, table, image_format)

    output = (["## %s.%s" % (schema, table),
               doc] +
              ['\n' + image_embed] +
              ["\n### Columns"] +
              ["- %s" % col for col in columns] +
              ["\n### Depencencies"] +
              ["- [%s](%s.%s.md)" % (ref, schema, ref) for ref in refs] +
              ["\n### SQL source\n", "```mysql", sql,  "```"])
    return "\n".join(output)


def parse_sql_file(path, fname, schema="", all_columns={}):
    table = fname[0:-4]
    refs = set()
    cols = []
    with open(os.path.join(path, fname)) as f:
        dbt = f.read()
        doc_start = dbt.find("/*")
        doc_end = dbt.find("*/")
        doc = dbt[doc_start + 2:doc_end] if doc_start > -1 else ""
        sql = dbt[doc_end + 2:] if doc_end > -1 else dbt
        pattern = re.compile(r"`.*`")
        # pattern = re.compile(r"{{(ref)\('([a-z0-9_]*)'\)}}")
        for ref in pattern.findall(dbt):
            refs.add(ref)

    schema_table = schema + "." + table
    columns = all_columns.get(schema_table, [])
    columns.sort()

    return (doc, sql, schema, table, columns, refs)


def write_doc(dirname, outdir, schema, all_columns, image_format="svg"):
    model_dir = os.walk(dirname)
    toc = []
    dep_list = []
    for cdir, dirs, files in model_dir:
        for fname in files:
            tname = fname[0:-4]
            with open(os.path.join(outdir, schema + "." + tname + ".md"), "w") as f:
                d, sql, s, t, c, r = parse_sql_file(cdir, fname, schema, all_columns)
                output = get_markdown(d, sql, s, t, c, r, image_format)
                f.write(output)
                toc = toc + ["* [%s.%s](%s.%s.md)" % (schema, tname, schema, tname)]
                dep_list = build_dep(dep_list, s, t, r)

    # dep_list format: [source_schema, source_table, dep_schema, dep_view]
    with open(os.path.join(outdir, "_dependency.csv"), "w") as f:
        w = csv.writer(f)
        for row in dep_list:
            w.writerow(row)

    toc.sort()
    with open(os.path.join(outdir, "SUMMARY.md"), "w") as f:
        f.write("# Summary\n")
        f.write("\n".join(toc))


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
