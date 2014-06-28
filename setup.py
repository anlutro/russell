#!/usr/bin/env python3

import os.path
from setuptools import setup, find_packages

setup(
    name='russell',
    packages=['russell'],
    version='0.3.0',
    license='MIT',
    description='A static HTML blog generator.',
    author='Andreas Lutro',
    author_email='anlutro@gmail.com',
    url='https://github.com/anlutro/russell',
    keywords=['blog', 'static', 'html', 'generator'],
    classifiers=[],
    install_requires=[
        'Jinja2>=2.7.0',
        'Markdown>=2.4',
        'MarkupSafe>=0.19',
        'Unidecode>=0.04.14',
        'docopt>=0.6.1',
        'python-slugify>=0.0.7',
        'python-dateutil>=2.2',
        'PyRSS2Gen>=1.1',
    ],
    package_dir={'': 'src'},
    entry_points={
        "console_scripts": ["russell=russell.cli:main"]
    },
)
