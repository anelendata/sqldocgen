import csv, os
from datetime import datetime


graphviz = None


def field_label(tok, style=False):
    label = "<tr><td "
    if style:
        label = label + "bgcolor='#FFFFFF' align='left' border='0' "
    label = label + "port='{0}'>{0}</td></tr>\n".format(tok[0])
    return label


def table_label(schema_table_name, table, style=False, current=None):
    # Current page's table
    if current == schema_table_name:
        td_header_color = "#AACCFF"
        class_name = "current"
    else:
        td_header_color = "#CCCCCC"
        class_name = "normal"

    schema_name, table_name = schema_table_name.split(".")

    col_list = list(table)
    if len(col_list) > 20:
        col_list = col_list[0:19] + ["..."]
    fields = "".join([field_label([x], style=style) for x in col_list])
    tok = {"schemaName": schema_name, "tableName": table_name, "fields": fields,
            "table_style": "", "td_style":  "", "font": "", "font_close": ""}
    if style:
        tok["table_style"] = "border='1' cellspacing='0' cellborder='1'"
        tok["td_style"] = "bgcolor='" + td_header_color + "' border='0' "
        tok["font"] = "<font face='Times-bold' point-size='20'>"
        tok["font_close"] = "</font>"
        tok["class"] = ""
    else:
        tok["class"] = "class='" + class_name + "'"
    label = """<
    <table {class} {table_style}>
      <tr><td {td_style}>{font}{schemaName}{font_close}</td></tr>
      <tr><td {td_style}>{font}{tableName}{font_close}</td></tr>
        {fields}
    </table> >""".format(**tok)
    return label

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


def create_table_act(name, label, href=None, target=None):
    keys = {"tableName": name, "label": label, "href":"", "target": ""}
    if href:
        keys["href"] = 'href="%s"' % href
    if target:
        keys["target"] = 'target="%s"' % target

    return '"{tableName}" [shape=none label={label} {href} {target}];'.format(**keys)


def add_dependency(keys):
    return '  "{refTableName}" -> "{srcTableName}"'.format(**keys)


def get_active(schema, tables, deps, root, depth_limit=None, add_child=True, limit_to_schema=True):
    root_table_name = None
    if root is None:
        active_deps = deps
        if limit_to_schema:
            active_tables = set()
            for key in tables.keys():
                names = key.split(".")
                if names[0] == schema:
                    active_tables.add(key)
            # also include the tables appear in the dep tree
            active_tables = list(active_tables.union([e for t in deps for e in t]))
        else:
            active_tables = tables.keys()
    else:
        root_table_name = root.split(".")[-1]
        active_tables, active_deps = walk_dep(root, 0, deps, depth_limit)
        if add_child:
            t, d = walk_dep(root, 0, deps, depth_limit, reverse=True)
            active_tables = list(set().union(active_tables, t))
            active_deps = list(set().union(active_deps, d))

    return active_tables, active_deps


def build_without_graphviz(schema, tables, deps, root=None, depth_limit=None, link_ext="html", add_child=True):
    dot = """// %s %s
digraph {
rankdir =LR
node [shape=none]
""" % (schema, datetime.now())

    active_tables, active_deps = get_active(schema, tables, deps, root, depth_limit, add_child)

    for schema_table_name in active_tables:
        table_name = schema_table_name.split(".")[-1]
        table = tables[schema_table_name] if schema_table_name in tables.keys() else {}

        cur_schema, cur_table = schema_table_name.split(".")
        label = table_label(schema_table_name, table, style=True, current=root)


        if True or cur_schema == schema:
            href = "../" + schema_table_name + "." + link_ext
            target = "_parent"
            dot = dot + create_table_act(schema_table_name, label, href=href, target=target)
        else:
            dot = dot + create_table_act(schema_table_name, label)

    for dep in active_deps:
        dot = dot + add_dependency({"refTableName": dep[0], "srcTableName":dep[1]})

    dot = dot + "}"

    return dot

def build_with_graphviz(schema, tables, deps, root=None, depth_limit=None, link_ext="html", add_child=True):
    """Build with graphviz library"""
    dot = graphviz.Digraph(comment=schema + ' %s' % datetime.now())
    dot.attr(rankdir='LR') #, size='8,5')
    dot.attr('node', shape='none')

    active_tables, active_deps = get_active(schema, tables, deps, root, depth_limit, add_child)

    for schema_table_name in active_tables:
        table_name = schema_table_name.split(".")[-1]
        table = tables[schema_table_name] if schema_table_name in tables.keys() else {}

        cur_schema, cur_table = schema_table_name.split(".")
        label = table_label(schema_table_name, table, style=True, current=root)

        href = "../" + schema_table_name + "." + link_ext
        target = "_parent"

        if cur_schema == schema:
            dot.node(schema_table_name, label, href="../" + schema_table_name + "." + link_ext, target="_parent")
        else:
            dot.node(schema_table_name, label)

    for dep in active_deps:
        dot.edge(dep[0], dep[1])

    return dot


def render_dot(schema, tables, deps, root=None, depth_limit=None, has_graphviz=True, add_child=True):
    if not has_graphviz:
        return build_without_graphviz(schema, tables, deps, root, depth_limit, add_child=add_child)

    global graphviz
    if graphviz is None:
        import graphviz

    return build_with_graphviz(schema, tables, deps, root, depth_limit, add_child=add_child)


def output_graph(outdir, filename, dot):
    dot.render(filename, directory=outdir, cleanup=True)


def output_source(outdir, filename, dot_source):
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    with open(os.path.join(outdir, filename), "w") as f:
        f.write(dot_source)


def build_dependency(path, schema, tables, dep_table=None, csv_file="_dependency.csv"):
    source_schema_col = 0
    source_table_col = 1
    depend_schema_col = 2
    depend_view_col = 3
    deps = set()

    if dep_table is not None:
        for row in dep_table:
            source_schema_table = row[source_schema_col] + "." + row[source_table_col]
            depend_schema_view = row[depend_schema_col] + "." + row[depend_view_col]

            # At least dependant table must be listed in the list of tables from the database
            if schema != row[depend_schema_col] or not depend_schema_view in tables.keys():
                continue

            deps.add((depend_schema_view, source_schema_table))
    else:
        with open(os.path.join(path, csv_file), "r") as csv_file:
            rows = csv.reader(csv_file, delimiter=',', quotechar='"')
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
    from graphviz import  Digraph
    if len(sys.argv) < 2:
        print("graph <dbt_dir> <work_dir> <all_column_file.csv> <root_schema_table> <depth_limit>")
    dbt_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    work_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    all_column_file = sys.argv[3] if len(sys.argv) > 3 else None
    root = sys.argv[4] if len(sys.argv) > 4 else None
    schema, root_table = root.split(".")
    depth_limit = int(sys.argv[5]) if len(sys.argv) > 5 else None

    image_format = "png"
    # image_format = "svg"

    deps = build_dependency(work_dir, schema)
    tables = doc.read_columns_from_csv(os.path.join(dbt_dir, "models"), all_column_file)
    if root_table == "*":
        for table in tables.keys():
            dot = render_dot(schema, tables, deps, table, 1)
            # print(dot.source)
            dot.format = image_format
            output_graph("output/" + image_format, table, dot)
    elif root_table != "":
        dot = render_dot(schema, tables, deps, root, depth_limit, add_child=False)
        dot.format = image_format
        output_graph("output/" + image_format, root, dot)
    else:
        dot = render_dot(schema, tables, deps, None, None, add_child=False)
        dot.format = image_format
        output_graph("output/" + image_format, "all_tables", dot)
