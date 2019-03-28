from setuptools import setup
from setuptools import find_packages


setup(
    name="sqldocgen",
    version="0.1dev",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data = {
        "sqldocgen.bigquery": ['*.sql'],
    },
    license="Creative Commons Attribution-Noncommercial-Share Alike license",
    description="sqldocgen is a command line tool to generate the doxgen-like documentation from SQL scripts.",
    long_description=open("README.md").read(),
    author="Anelen Co., LLC",
    entry_points = {
        "console_scripts": ["sqldocgen=sqldocgen.command_line:main"],
    }
)
