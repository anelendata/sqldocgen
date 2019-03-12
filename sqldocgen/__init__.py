import os, sys
import doc

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
    all_columns = doc.read_columns_from_csv(os.path.join(dirname, "models"), all_column_file)
    doc.write_doc(os.path.join(dirname, "models"), outdir, schema, all_columns)
