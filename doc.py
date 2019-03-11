import csv, os, re, sys


def parse_sql_file(path, fname, schema="", all_columns={}):
    table = fname[0:-4]
    refs = set()
    cols = []
    with open(os.path.join(path, fname)) as f:
        dbt = f.read()
        exit
        pos = dbt.find("/*")
        doc = dbt[pos + 2:dbt.find("*/")] if pos > -1 else ""
        pattern = re.compile(r"{{(ref)\('([a-z0-9_]*)'\)}}")
        for ref in pattern.findall(dbt):
            refs.add(ref[1])

    schema_table = schema + "." + table
    columns = all_columns.get(schema_table, [])
    columns.sort()
    output = (["## %s.%s" % (schema, table),
               doc] +
              ["\n", '<embed src="./svg/%s.%s.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></embed>' % (schema, table)] +
              ["### Columns"] +
              ["- %s" % col for col in columns] +
              ["### Depencencies"] +
              ["- [%s](%s.%s.md)" % (ref, schema, ref) for ref in refs] +
              ["### SQL source\n", "```mysql", dbt,  "```"])
    return "\n".join(output)


def run(dirname, outdir, schema, all_column_file,
        schema_col=0, table_col=1, column_col=2):

    model_dir = os.walk(dirname)
    cdir, dirs, files = model_dir.next()

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

    toc = []
    while cdir:
        for fname in files:
            tname = fname[0:-4]
            with open(os.path.join(outdir, schema + "." + tname + ".md"), "w") as f:
                output = parse_sql_file(cdir, fname, schema, all_columns)
                f.write(output)
                toc = toc + ["* [%s.%s](%s.%s.md)" % (schema, tname, schema, tname)]

        try:
            cdir, dirs, files = model_dir.next()

        except StopIteration:
            cdir = None
            pass

    toc.sort()
    with open(os.path.join(outdir, "SUMMARY.md"), "w") as f:
        f.write("# Summary")
        f.write("\n".join(toc))


if __name__ == '__main__':
    dirname = "." if len(sys.argv) == 1 else sys.argv[1]
    outdir = os.path.join(dirname, "doc") if len(sys.argv) < 3 else sys.argv[2]
    all_column_file = None if len(sys.argv) < 4 else sys.argv[3]

    if not os.path.isdir(dirname):
        raise "The directory %s does not exist" % dirname
    run(os.path.join(dirname, "models"), outdir, "analytics", all_column_file)
