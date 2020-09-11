#!/usr/bin/env python3

from __future__ import print_function
import ast
import os
import setuptools
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if sys.version_info[0] != 3:
    print("Only Python 3 is supported!")
    sys.exit(1)


def read_requirements(path="requirements.txt"):
    fullpath = os.path.join(os.path.dirname(__file__), path)
    with open(fullpath, "r") as f:
        lines = f.readlines()
    lines = [l.strip() for l in lines if l]
    return [l for l in lines if l]


def get_version(path="russell/__version__.py"):
    with open(path) as fh:
        for line in fh:
            if line.startswith("__version__ ="):
                return ast.literal_eval(line[14:])


setuptools.setup(
    name="russell",
    packages=["russell"],
    version=get_version(),
    license="GPL-3.0",
    description="A static HTML blog generator.",
    author="Andreas Lutro",
    author_email="anlutro@gmail.com",
    url="https://github.com/anlutro/russell",
    keywords=["blog", "static", "html", "generator"],
    classifiers=[],
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": ["russell=russell.cli:main"],
    },
)
