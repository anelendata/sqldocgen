# sqldocgen

SQL Documentation Generator

(Proof-of-concept state)

## What is sqldocgen?

It is a common practice to manage SQL views in data warehouses with the tools
like [dbt](https://docs.getdbt.com). The queries to generate views often involve
complex operations. The definition of the output columns are not easy to
understand. The documentation is poor and stale if it exists at all.

We treat SQL as a mission critical program code that computes the numbers
that affects the business decisions. As in the software development pratice,
the best place to document is the source code. The code author is more likely
to leave documents in the source code as the code is authored and modified.

sqldocgen automatically generates clickable SQL View dependency digrams.
It also lists the columns of the output view. The author of the SQL can also
leave a description by inserting the SQL comment like `/* Here is the doc. */`
before the query body in the query file (.sql).

All it requires is a set of SQL files stored in a directory to run sqldocgen.
It works nicely with dbt as you can point sqldocgen to the model directory
of dbt.

## How to Install

From the root of the repository,

1. Create virtual environment (Optional but recommended.)

```
python3 -m venv ./venv
source venv/bin/activate
```

2. Install

```
python setup.py install
```

### Install gitbook

Install [Gitbook](https://github.com/GitbookIO/gitbook/blob/master/docs/setup.md)

```
npm install gitbook-cli -g
```

## How to run

### Database access

sqldocgen extracts the list of columns from the target tables by accessing the
database (data warehouse).

#### BigQuery specific prerequisites

Make sure you have the dataset read access to BigQuery.

Install [Google Cloud SDK](https://cloud.google.com/sdk/docs).

Then run this before running sqldocgen:

```
gcloud auth application-default login
```

To revoke the access, run:

```
gcloud auth application-default revoke
```

Or go to [Security Checkup](https://myaccount.google.com/security-checkup) page and
expand "Third-party access". Then click on "Remove access" under Google Auth Library.

### sqldocgen command

Example:
```
sqldocgen -o ./doc -s analytics -c bigquery --gcp_project_id sandbox-000000 ./models
```

Here is the full usage description (`sqldocgen -h` to show this help)

```
usage: sqldocgen [-h] [-o OUT_DIR] [-s SCHEMA] [-i IMAGE_FORMAT]
                 [-g [HAS_GRAPHVIZ]] [-c COLUMN_DATA_SOURCE]
                 [--gcp_project_id GCP_PROJECT_ID]
                 [--gcp_secrets_file GCP_SECRETS_FILE]
                 model_dir

Generate SQL View document.

positional arguments:
  model_dir             SQL model directory.

optional arguments:
  -h, --help            show this help message and exit
  -o OUT_DIR, --out_dir OUT_DIR
                        Document output location. Default is the current
                        directory.
  -s SCHEMA, --schema SCHEMA
                        The schema to generate the documentation. Currently,
                        the document is generated per schema.
  -i IMAGE_FORMAT, --image_format IMAGE_FORMAT
                        Image format (default=d3, svg, png, jpg). You need to
                        install Graphviz and Python Graphviz to sepecify non
                        d3 formats.
  -g [HAS_GRAPHVIZ], --has_graphviz [HAS_GRAPHVIZ]
                        graphviz is installed default=False
  -c COLUMN_DATA_SOURCE, --column_data_source COLUMN_DATA_SOURCE
                        Column data source. bigquery or csv are currently
                        supported. For csv, you need to have a CSV file under
                        the model directory with the schema name.
  --gcp_project_id GCP_PROJECT_ID
                        Google Cloud Project ID
  --gcp_secrets_file GCP_SECRETS_FILE
                        Google Cloud secrets file (.json)
```

### Alternative authentication method for BiqQuery

Alternatively, you can use OAuth 2.0 client to let sqldocgen access BigQuery.

Please follow
[Create authorization credentials section](https://developers.google.com/identity/protocols/OAuth2WebServer#creatingcred)
of Google's OAuth documentation to generate the client and download secrets json file.

In this method, you will need to specify `--gcp_secrets_file` option to specify the secrets json file
when you first authenticate to access BigQuery from sqldocgen.

## Viewing the documentation

Go to the output directory and run:

```
gitbook serve
```

Then point your web browser to http://localhost:4000


## Optional: Graphviz library

If you install Graphviz, you can generate the image in svg or png instead of
d3. Using png also allows you to generate PDF version of the docuemnt.

Note: The diagrams are clickable only with the image formats d3 or svg.

### Install

1. Install [graphviz](https://www.graphviz.org/download/)

For mac,
```
brew install Graphviz
```

2. Install Python Graphviz

```
pip install graphviz
```

### Generate PDF

First, install [Calibre](https://calibre-ebook.com/).

For Mac:

```
brew cask install calibre
```

To generate PDF version of gitbook, you need to use `-i png -g true` option when
you run sqldocgen.pdf

Once sqldocgen completes, run the gitbook pdf command to convert the gitbook to PDF.

Example:

```
gitbook pdf ./doc ./my_doc.pdf
```


## Reporting bugs and contribution

Please report any bug by creating a [issue](https://github.com/anelendata/sqldocgen/issues).
Please be specific on your environment (e.g. OS and Python version, Graphviz version, and etc).

This software is a proof-of-concept phase and there is no guarantee of bug fixes and enhancements.

For contribution, please pull-request. Please be clearly document the intention of the enhancements and bug-fixes.

## Dev environment and notes

Create Python virtual env

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install node

Installing via [nvm](https://github.com/creationix/nvm) is recommended.

```
nvm install v10.15.3
```

### setup.py

https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
