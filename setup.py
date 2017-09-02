#!/usr/bin/env python3

from __future__ import print_function
from setuptools import setup, find_packages
import os.path
import sys

if sys.version_info[0] != 3:
    print("Only Python 3 is supported!")
    sys.exit(1)

def read_requirements(path='requirements.txt'):
    fullpath = os.path.join(os.path.dirname(__file__), path)
    with open(fullpath, 'r') as f:
        lines = f.readlines()
    lines = [l.strip() for l in lines if l]
    return [l for l in lines if l]

setup(
    name='russell',
    packages=['russell'],
    version='0.5.3',
    license='MIT',
    description='A static HTML blog generator.',
    author='Andreas Lutro',
    author_email='anlutro@gmail.com',
    url='https://github.com/anlutro/russell',
    keywords=['blog', 'static', 'html', 'generator'],
    classifiers=[],
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'russell=russell.cli:main'
        ],
    },
)
