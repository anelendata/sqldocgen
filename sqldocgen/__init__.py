import argparse, os, sys
import doc, graph

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate SQL View document.')
    parser.add_argument("model_dir", type=str, help="SQL model directory.")
    parser.add_argument("-o", "--out_dir", type=str, default=".", help="Document output location")
    parser.add_argument("-t", "--table_schemas", type=str, default="table_schema.csv", help="CSV file for table schema: <schema>, <table>, <column>")
    parser.add_argument("-s", "--schema", type=str, default=None, help="Limit the doc to this schema")
    parser.add_argument("-i", "--image_format", type=str, default="svg", help="Image format (svg, png, jpg)")
    parser.add_argument("-d", "--depth_limit", type=int, default=1, help="Graph depth (default = 1)")
    parser.add_argument("-r", "--root_table", type=str, default="*", help="Generate doc only derived from this root table.")
    args = parser.parse_args()

    # Generate markdown doc
    model_dir = args.model_dir
    out_dir = args.out_dir
    table_schemas = args.table_schemas
    schema = args.schema

    if not os.path.isdir(model_dir):
        raise "The directory %s does not exist" % model_dir

    tables = doc.read_columns_from_csv(model_dir, table_schemas)
    doc.write_doc(model_dir, out_dir, schema, tables)

    # Generate graph
    depth_limit = args.depth_limit
    image_format = args.image_format
    root_table = args.root_table

    deps = graph.build_dependency_from_csv(out_dir, schema)
    if root_table == "*":
        for table in tables.keys():
            dot = graph.render_dot(schema, tables, deps, table, 1)
            # print(dot.source)
            dot.format = image_format
            graph.output_graph(os.path.join(out_dir, image_format), table, dot)
    elif root_table != "":
        dot = graph.render_dot(schema, tables, deps, root, depth_limit, add_child=False)
        dot.format = image_format
        graph.output_graph(os.path.join(out_dir, image_format), root, dot)
    else:
        dot = graph.render_dot(schema, tables, deps, None, None, add_child=False)
        dot.format = image_format
        graph.output_graph(os.path.join(out_dir, image_format), "all_tables", dot)
