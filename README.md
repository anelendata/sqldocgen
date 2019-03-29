# sqldocgen

SQL Documentation Generator

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
