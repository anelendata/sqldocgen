import os, re
from setuptools import setup
from setuptools import find_packages


requirement_file = os.path.join(os.path.split(__file__)[0], "requirements.txt")
with open(requirement_file) as f:
    # Ignore comments
    requirements = [re.sub(r"#.*", "", line).replace("\n","") for line in f]


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
    install_requires=requirements,
    entry_points = {
        "console_scripts": ["sqldocgen=sqldocgen.command_line:main"],
    }
)
