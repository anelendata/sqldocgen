#!/usr/bin/env python

from datetime import datetime
from graphviz import  Digraph
import csv

def field_label(tok):
    return """
      <tr><td bgcolor='grey96' align='left' port='{0}'>{0}</td></tr>\n""".format(tok[0])


def table_label(name, table):
    fields = "".join([field_label([x]) for x in list(table)])
    tok = {"tableName": name, "fields": fields}
    return """<
    <table border='0' cellspacing='0' cellborder='1'>
      <tr><td bgcolor='lightblue2'>
        <font face='Times-bold' point-size='20'>{tableName}</font></td></tr>
        {fields}
    </table> >""".format(**tok)


def walk_dep(node, depth, deps, depth_limit=None, active_tables=set(), active_deps=set()):
    active_tables.add(node)
    if depth_limit is not None and depth >= depth_limit:
        return(active_tables, active_deps)
    for dep in deps:
        if dep[0] == node:
            active_deps.add(dep)
            t, d = walk_dep(dep[1], depth + 1, deps, depth_limit, active_tables, active_deps)
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
def build_dot(tables, deps, root=None, depth_limit=None):
    dot = Digraph(comment=filename + ' %s' % datetime.now())
    dot.attr(rankdir='LR') #, size='8,5')
    dot.attr('node', shape='none')
    if root is None:
        active_tables = tables.keys()
        active_deps = deps
    else:
        active_tables, active_deps = walk_dep(root, 0, deps, depth_limit)

    for table_name in active_tables:
        table = tables[table_name]
        label = table_label(table_name, table)
        dot.node(table_name, label)

    for dep in active_deps:
        dot.edge(dep[0], dep[1])

    return dot

def render_dot(tables, deps, root=None, depth_limit=None, use_print=False):
    if use_print:
        return print_dot(tables, deps, root, depth_limit)
    return build_dot(tables, deps, root, depth_limit)


def build_dependency_from_csv(filename, source_table_col=0, source_column_col=1, depend_view_col=2):
    tables = dict()
    deps = set()
    with open(filename, "r") as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in rows:
            if tables.get(row[source_table_col], None) is None:
                tables[row[source_table_col]] = set()
            tables[row[source_table_col]].add(row[source_column_col])
            if tables.get(row[depend_view_col], None) is None:
                tables[row[depend_view_col]] = set()
            deps.add((row[depend_view_col], row[source_table_col]))
    return tables, deps

if __name__ == '__main__':
    import sys
    filename = sys.stdin if len(sys.argv) == 1 else sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else None
    depth_limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    tables, deps = build_dependency_from_csv(filename)
    dot = render_dot(tables, deps, root, depth_limit, True)
    if dot:
        print(dot.source)
