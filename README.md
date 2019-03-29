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

sqldocgen automatically generates SQL View dependency digrams. It also lists
the columns of the output view. The author of the SQL can also leave a
description by inserting the SQL comment like `/* Here is the doc. */` before
the query body in the query file (.sql).

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
pip install -r requirements.txt
python setup.py install
```

### Install gitbook

Install [Gitbook](https://github.com/GitbookIO/gitbook/blob/master/docs/setup.md)

```
npm install gitbook-cli -g
```

## How to run

Example:
```
sqldocgen -o ./doc -s analytics -c bigquery --gcp_project_id sandbox-000000 ./models
```

Here is the full usage description (`sqldocgen -h` to show this help)

```
usage: sqldocgen [-h] [-o OUT_DIR] [-s SCHEMA] [-i IMAGE_FORMAT]
                 [-g [HAS_GRAPHVIZ]] [-c COLUMN_DATA_SOURCE]
                 [--gcp_project_id GCP_PROJECT_ID]
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
```

## Viewing the documentation

Go to the output directory and run:

```
gitbook serve
```

Then point your web browser to http://localhost:4000


## Optional: Graphviz library

If you install Graphviz, you can generate the image in svg or png instead of
d3. Using png also allows you to generate PDF version of the docuemnt.

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

To generate PDF version of gitbook, you need to use `-i png` option when
you run sqldocgen.

Once sqldocgen completes, follow [here](https://toolchain.gitbook.com/ebook.html)
to convert the gitbook to PDF.


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
