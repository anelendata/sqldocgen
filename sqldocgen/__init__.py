import argparse, os, sys

if __name__ == "__main__":
    import doc, graph, bigquery
else:
    from . import doc, graph, bigquery

print(__file__)

def main():
    parser = argparse.ArgumentParser(description='Generate SQL View document.')
    parser.add_argument("model_dir", type=str, help="SQL model directory.")
    parser.add_argument("-o", "--out_dir", type=str, default=".", help="Document output location")
    parser.add_argument("-t", "--table_schemas", type=str, default="table_schema.csv", help="CSV file for table schema: <schema>, <table>, <column>")
    parser.add_argument("-s", "--schema", type=str, default=None, help="Limit the doc to this schema")
    parser.add_argument("-i", "--image_format", type=str, default="svg", help="Image format (svg, png, jpg)")
    parser.add_argument("-l", "--depth_limit", type=int, default=1, help="Graph depth (default = 1)")
    parser.add_argument("-r", "--root_table", type=str, default="*", help="Generate doc only derived from this root table.")
    parser.add_argument("-d", "--database", type=str, default=None, help="Database type.")
    parser.add_argument("-g", "--gcp_project_id", type=str, default=None, help="Google Cloud Project ID")
    parser.add_argument("-a", "--gcp_secret_file", type=str, default=None, help="Google Cloud OAuth secrets file (json)")
    args = parser.parse_args()

    # Generate markdown doc
    model_dir = args.model_dir
    out_dir = args.out_dir
    table_schemas = args.table_schemas
    schema = args.schema
    db = args.database
    gcp_project_id = args.gcp_project_id
    gcp_secret_file = args.gcp_secret_file

    if not os.path.isdir(model_dir):
        raise "The directory %s does not exist" % model_dir

    if db == "bigquery":
        if not all([gcp_project_id, gcp_secret_file]):
            raise(Exception("To use BigQuery, set gcp_project_id and gcp_secret_file"))
        client = bigquery.authenticate(gcp_project_id, gcp_secret_file)
        tables = bigquery.get_schema_table_column(client, schema)
    else:
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
            graph.output_source(os.path.join(out_dir, "dot"), table, dot)
    elif root_table != "":
        dot = graph.render_dot(schema, tables, deps, root, depth_limit, add_child=False)
        dot.format = image_format
        graph.output_graph(os.path.join(out_dir, image_format), root, dot)
    else:
        dot = graph.render_dot(schema, tables, deps, None, None, add_child=False)
        dot.format = image_format
        graph.output_graph(os.path.join(out_dir, image_format), "all_tables", dot)


if __name__ == '__main__':
    main()
