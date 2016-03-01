#!/usr/bin/env python3

from __future__ import print_function
from setuptools import setup, find_packages
import os.path
import sys

if sys.version_info[0] != 3:
    print("Only Python 3 is supported!")
    sys.exit(1)

setup(
    name='russell',
    packages=['russell'],
    version='0.4.4',
    license='MIT',
    description='A static HTML blog generator.',
    author='Andreas Lutro',
    author_email='anlutro@gmail.com',
    url='https://github.com/anlutro/russell',
    keywords=['blog', 'static', 'html', 'generator'],
    classifiers=[],
    install_requires=[
        'Jinja2>=2.7',
        'Markdown>=2.4',
        'PyRSS2Gen>=1.1',
        'python-dateutil>=2.2',
        'python-slugify>=1.1',
        'PyYAML>=3.11',
    ],
    entry_points={
        "console_scripts": ["russell=russell.cli:main"]
    },
)
