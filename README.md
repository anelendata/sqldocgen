# sqldocgen

SQL Documentation Generator

## How to use

### Install

```
python setup.py install
```

### Install gitbook

Install [Gitbook](https://github.com/GitbookIO/gitbook/blob/master/docs/setup.md)

```
npm install gitbook-cli -g
```

### Input files

## View dependency CSV files

| Column 0 | Column 1 | Column 2 | Column 3 | Column 4 |
| :---- | :---- | :---- | :---- | :---- |
| source_schema | source_table | source_column | depend_schema | depend_view |

## View CSV file

| Column 0 | Column 1 | Column 2 |
| :---- | :---- | :---- | :---- | :---- |
| source_schema | source_view | source_column |


## Generate PDF

Follow [here](https://toolchain.gitbook.com/ebook.html)


## Install Dev environment

### Install Graphviz

```
brew install Graphviz
```

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
