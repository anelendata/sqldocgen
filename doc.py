import os, re, sys


def parse_sql_file(path, fname, schema=""):
    table = fname[0:-4]
    refs = set()
    cols = []
    with open(os.path.join(path, fname)) as f:
        dbt = f.read()
        exit
        pos = dbt.find("/*")
        doc = dbt[pos + 2:dbt.find("*/")] if pos > -1 else ""
        pattern = re.compile(r"{{ref\('([a-z0-9_]*)'\)}}")
        refs = refs.union(set(pattern.findall(dbt)))

    output = (["## %s.%s" % (schema, table),
               doc,
               "### Depencencies"] +
              ["- [%s](%s.%s.md)" % (ref, schema, ref) for ref in refs] +
              # ["\n", '<img src="./svg/%s.%s.svg" width="80%%"></img>' % (schema, table)])
              ["\n", '<embed src="./svg/%s.%s.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></embed>' % (schema, table),
              # ["\n", '<object data="./svg/%s.%s.svg" width="80%%" type="image/svg+xml" codebase="http://www.savarese.com/software/svgplugin/"></object>' % (schema, table)])
               "### SQL source", "```mysql", dbt,  "```"])
    return "\n".join(output)


def run(dirname, outdir, schema):
    model_dir = os.walk(dirname)
    cdir, dirs, files = model_dir.next()

    toc = []
    while cdir:
        for fname in files:
            tname = fname[0:-4]
            with open(os.path.join(outdir, schema + "." + tname + ".md"), "w") as f:
                output = parse_sql_file(cdir, fname, schema)
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
    dirname = "./models" if len(sys.argv) == 1 else sys.argv[1]
    if not os.path.isdir(dirname):
        raise "The directory %s does not exist" % dirname
    outdir = os.path.join(dirname, "../doc")
    run(dirname, outdir, "analytics")
