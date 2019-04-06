import argparse, os, sys

if __name__ == "__main__":
    import doc, graph, bigquery
else:
    from . import doc, graph, bigquery

print(__file__)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args():
    parser = argparse.ArgumentParser(description='Generate SQL View document.')
    parser.add_argument("model_dir", type=str, help="SQL model directory.")
    parser.add_argument("-o", "--out_dir", type=str, default=".", help="Document output location. Default is the current directory.")
    parser.add_argument("-s", "--schema", type=str, default=None, help="The schema to generate the documentation. Currently, the document is generated per schema.")
    parser.add_argument("-i", "--image_format", type=str, default="d3", help="Image format (default=d3, svg, png, jpg). You need to install Graphviz and Python Graphviz to sepecify non d3 formats.")
    parser.add_argument("-g", "--has_graphviz", type=str2bool, nargs="?", const=True, default=False, help="graphviz is installed default=False")
    parser.add_argument("-c", "--column_data_source", type=str, default=None, help="Column data source. bigquery or csv are currently supported. For csv, you need to have a CSV file under the model directory with the schema name.")
    parser.add_argument("-e", "--extra_schemas", type=str, default=None, help="The schemas that cannot be inferred from the SQL but should be searched for populating columns. A comma separated list.")
    parser.add_argument("--gcp_project_id", type=str, default=None, help="Google Cloud Project ID")
    parser.add_argument("--gcp_secrets_file", type=str, default=None, help="Google Cloud secrets file (.json)")
    return parser.parse_args()

def main():
    args = parse_args()
    model_dir = args.model_dir
    out_dir = args.out_dir
    column_data_source = args.column_data_source
    gcp_project_id = args.gcp_project_id
    gcp_secrets_file = args.gcp_secrets_file
    has_graphviz = args.has_graphviz
    image_format = args.image_format
    main_schema = args.schema

    schemas = set([main_schema])
    extra_schemas = args.extra_schemas
    if extra_schemas:
        schemas = schemas.union(extra_schemas.split(","))

    # Check input
    if not has_graphviz and image_format != "d3":
        raise ValueError("Must have graphviz when image format is not d3")

    if not os.path.isdir(model_dir):
        alt_dir = os.path.join(os.getcwd(), model_dir)
        if os.path.isdir(alt_dir):
            model_dir = alt_dir
        else:
            raise ValueError("The model directory %s does not exist" % model_dir)

    print("Model directory: " + model_dir)

    if out_dir is "." or not os.path.isdir(out_dir):
        alt_dir = os.path.join(os.getcwd(), out_dir)
        if os.path.isdir(alt_dir):
            out_dir = alt_dir
        else:
            raise ValueError("The output directory %s does not exist" % out_dir)

    print("Ouput directory: " + out_dir)

    if gcp_secrets_file is not None and not os.path.isfile(gcp_secrets_file):
        alt_loc = os.path.join(os.getcwd(), gcp_secrets_file)
        if os.path.isdir(alt_loc):
            gcp_secrets_file = alt_loc
        else:
            raise ValueError("GCP secrets file %s does not exist" % gcp_secrets_file)

    # Build dependency tree
    dep_table = doc.make_tree(model_dir, out_dir, main_schema, write_file=False)

    # dep_table is [[dependent_schema, dependent_table, source_schema, source_table], ...]
    dep_schemas = schemas
    for d in dep_table:
        dep_schemas = dep_schemas.union([d[0], d[2]])

    # Extract table-columns from the listed schemas
    if column_data_source == "bigquery":
        if not gcp_project_id:
            raise(Exception("To use BigQuery, set gcp_project_id"))

        if gcp_secrets_file is not None:
            credentials = bigquery.appflow_auth(gcp_project_id, gcp_secrets_file)
        else:
            credentials = bigquery.gcp_sdk_auth()

        client = bigquery.get_client(gcp_project_id, credentials)
        tables = bigquery.get_schema_table_column(client, dep_schemas)
    elif column_data_source == "csv":
        tables = doc.read_columns_from_csv(model_dir, schema + ".csv")
    else:
        raise ValueError("Unsupported column data source type: " + column_data_source)

    append = False
    for schema in schemas:
        print("Building for " + schema + " schema...")
        deps = graph.build_dependency(out_dir, schema, tables, dep_table=dep_table)
        # Generate graph
        for table in tables.keys():
            dot = graph.render_dot(schema, tables, deps, table, 1, has_graphviz=has_graphviz)
            if has_graphviz:
                dot.format = image_format
                graph.output_graph(os.path.join(out_dir, image_format), table, dot)
                graph.output_source(os.path.join(out_dir, "dot"), table + ".dot", dot.source)
            else:
                graph.output_source(os.path.join(out_dir, "dot"), table + ".dot", dot)

        # Generate markdown doc
        topics = doc.write_pages(model_dir, out_dir, schema, tables, image_format=image_format,)
        doc.write_toc(schema, out_dir, topics, append=append)
        append = True


    print("Generating all_tables tree")
    deps = graph.build_dependency(out_dir, main_schema, tables, dep_table=dep_table)
    dot = graph.render_dot(main_schema, tables, deps, None, None, add_child=False, has_graphviz=has_graphviz)
    if has_graphviz:
        dot.format = image_format
        graph.output_graph(os.path.join(out_dir, image_format), "all_tables", dot)
        graph.output_source(os.path.join(out_dir, "dot"), "all_tables.dot", dot.source)
    else:
        graph.output_source(os.path.join(out_dir, "dot"), "all_tables.dot", dot)

    doc.write_overview(main_schema, out_dir, topics, image_format)

if __name__ == '__main__':
    main()
