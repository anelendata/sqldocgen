import csv, os
from datetime import datetime
from graphviz import  Digraph


def field_label(tok):
    return """
      <tr><td bgcolor='grey96' align='left' port='{0}'>{0}</td></tr>\n""".format(tok[0])


def table_label(name, table):
    fields = "".join([field_label([x]) for x in list(table)])
    tok = {"tableName": name, "fields": fields}
    return """<
    <table border='0' cellspacing='0' cellborder='1'>
      <tr><td bgcolor='lightblue2'>
        <font face='Times-bold' point-size='20'>{tableName}</font>
      </td></tr>
        {fields}
    </table> >""".format(**tok)


def walk_dep(node, depth, deps, depth_limit=None, active_tables=None, active_deps=None, reverse=False):
    if active_tables is None:
        active_tables = set()
    if active_deps is None:
        active_deps = set()

    cur = 0
    ref = 1
    if reverse:
        cur = 1
        ref = 0
    active_tables.add(node)
    if depth_limit is not None and depth >= depth_limit:
        return(active_tables, active_deps)
    for dep in deps:
        if dep[cur] == node:
            active_deps.add(dep)
            t, d = walk_dep(dep[ref], depth + 1, deps, depth_limit, active_tables, active_deps, reverse)
            active_tables.union(t)
            active_deps.union(d)
    return (active_tables, active_deps)


####
# Using print
def create_table_act(name, label):
    return '''
"%s" [
shape=none
  label=%s ];''' % (name, label)


def add_dependency(tok):
    return '  "{refTableName}" -> "{srcTableName}"'.format(**tok)


def print_table(name, table):
    label = table_label(name, table)
    print(create_table_act(name, label))


def print_dep(dep):
    print(add_dependency({"refTableName": dep[0], "srcTableName":dep[1]}))


def print_dot(tables, deps, root=None, depth_limit=None):
    # dot file header
    print("/*")
    print(" * Graphviz of '%s', created %s" % (filename, datetime.now()))
    print(" */")
    print("digraph g { graph [ rankdir = \"LR\" ];")

    if root is None:
        active_tables = tables.keys()
        active_deps = deps
    else:
        active_tables, active_deps = walk_dep(root, 0, deps, depth_limit)

    for table_name in active_tables:
        table = tables[table_name]
        print_table(table_name, table)

    for dep in active_deps:
        print_dep(dep)

    print("}")


####
# Use graphviz library
def build_dot(schema, tables, deps, root=None, depth_limit=None, link_ext="html", add_child=True):
    dot = Digraph(comment=schema + ' %s' % datetime.now())
    dot.attr(rankdir='LR') #, size='8,5')
    dot.attr('node', shape='none')

    if root is None:
        active_tables = tables.keys()
        active_deps = deps
    else:
        active_tables, active_deps = walk_dep(root, 0, deps, depth_limit)
        if add_child:
            t, d = walk_dep(root, 0, deps, depth_limit, reverse=True)
            active_tables = list(set().union(active_tables, t))
            active_deps = list(set().union(active_deps, d))

    for schema_table_name in active_tables:
        print(schema_table_name)
        table = tables[schema_table_name]
        label = table_label(schema_table_name, table)
        cur_schema, cur_table = schema_table_name.split(".")
        if cur_schema == schema:
            dot.node(schema_table_name, label, href="../" + schema_table_name + "." + link_ext, target="_parent")
        else:
            dot.node(schema_table_name, label)

    for dep in active_deps:
        dot.edge(dep[0], dep[1])

    return dot

def render_dot(schema, tables, deps, root=None, depth_limit=None, use_print=False, add_child=True):
    if use_print:
        return print_dot(tables, deps, root, depth_limit)
    return build_dot(schema, tables, deps, root, depth_limit, add_child=add_child)


def output_graph(outdir, filename, dot):
    dot.render(filename, directory=outdir, cleanup=True)


def build_dependency_from_csv(path, schema, filename="_dependency.csv"):
    source_schema_col = 0
    source_table_col = 1
    depend_schema_col = 2
    depend_view_col = 3
    deps = set()
    with open(os.path.join(path, filename), "r") as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in rows:
            source_schema_table = row[source_schema_col] + "." + row[source_table_col]
            depend_schema_view = row[depend_schema_col] + "." + row[depend_view_col]

            if schema != row[depend_schema_col]:
                continue

            deps.add((depend_schema_view, source_schema_table))
    return deps


if __name__ == '__main__':
    import sys
    import doc
    if len(sys.argv) < 2:
        print("graph <dbt_dir> <work_dir> <all_column_file.csv> <root_schema_table> <depth_limit>")
    dbt_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    work_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    all_column_file = sys.argv[3] if len(sys.argv) > 3 else None
    root = sys.argv[4] if len(sys.argv) > 4 else None
    schema, root_table = root.split(".")
    depth_limit = int(sys.argv[5]) if len(sys.argv) > 5 else None

    deps = build_dependency_from_csv(work_dir, schema)
    tables = doc.read_columns_from_csv(os.path.join(dbt_dir, "models"), all_column_file)
    if root_table == "*":
        for table in tables.keys():
            dot = render_dot(schema, tables, deps, table, 1)
            # print(dot.source)
            dot.format = "svg"
            output_graph("output/svg", table, dot)
    elif root_table != "":
        dot = render_dot(schema, tables, deps, root, depth_limit, add_child=False)
        dot.format = "svg"
        output_graph("output/svg", root, dot)
    else:
        dot = render_dot(schema, tables, deps, None, None, add_child=False)
        dot.format = "svg"
        output_graph("output/svg", "all_tables", dot)
