#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from signate import info
import codecs
import sys

if sys.version_info[:2] < (3, 8):
    raise RuntimeError("Python version >= 3.8 required.")

CLI_REQUIRES = ['click', 'requests', 'tabulate']

setup(
    name='signate',
    version=info.VERSION,
    description=info.NAME,
    url='https://user.competition.signate.jp',
    long_description=codecs.open('README.md', 'r', 'utf-8').read(),
    long_description_content_type='text/markdown',
    author='SIGNATE Inc.',
    keywords=['signate', 'signate-cli'],
    entry_points={'console_scripts': ['signate = signate.cli:main']},
    install_requires=CLI_REQUIRES,
    python_requires='>=3.8',
    packages=find_packages(exclude=['tests']),
    license='Apache 2.0')
