#!/usr/local/python
"""
OAuth
https://cloud.google.com/bigquery/docs/authentication/end-user-installed
"""
import os
from google import auth
from google.cloud import exceptions, bigquery


LIST_SCHEMA_TABLE_COL_SQL_FILE = os.path.join(os.path.split(__file__)[0], "schema_table_column.sql")


def authenticate_oauth():
    scopes = ("https://www.googleapis.com/auth/bigquery",
              "https://www.googleapis.com/auth/cloud-platform",
              "https://www.googleapis.com/auth/drive")
    credentials, project_id = auth.default(scopes=scopes)
    return credentials


def authenticate():
    return authenticate_oauth()


def get_client(project_id, credentials, location="US"):
    client = bigquery.Client(project=project_id, credentials=credentials, location=location)
    return client


def get_schema_table_column(
        client,
        schema,
        schema_col=0, table_col=1, column_col=2,
        location="US"):
    with open(LIST_SCHEMA_TABLE_COL_SQL_FILE, "r") as f:
        query = f.read().replace("\n", " ") % schema
    query_job = client.query(
        query,
        # Location must match that of the dataset(s) referenced in the query.
        location=location
    )  # API request - starts the query

    all_columns = {}
    for row in query_job:
        cur_schema = row[schema_col]
        cur_table = row[table_col]
        cur_schema_table = cur_schema + "." + cur_table
        cur_column = row[column_col]
        if all_columns.get(cur_schema_table, None) is None:
            all_columns[cur_schema_table] = []
        all_columns[cur_schema_table] = list(set().union(all_columns[cur_schema_table], [cur_column]))
    return all_columns


if __name__ == "__main__":
    project_id = "my_project_id"
    # client_secrets_file = ".secret/xxxx.apps.googleusercontent.com.json"
    credentials = authenticate()
    client = get_client(project_id, credentials)
    all_columns = get_schema_table_column(client, "my_schema")
    print(all_columns)
