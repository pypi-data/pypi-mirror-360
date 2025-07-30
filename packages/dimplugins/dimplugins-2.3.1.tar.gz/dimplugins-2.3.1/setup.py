#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Decentralized Instant Messaging (Python Plugins)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Plugins for MingKeMing module
"""

import io

from setuptools import setup, find_packages

__version__ = '2.3.1'
__author__ = 'Albert Moky'
__contact__ = 'albert.moky@gmail.com'

with io.open('README.md', 'r', encoding='utf-8') as fh:
    readme = fh.read()

setup(
    name='dimplugins',
    version=__version__,
    url='https://github.com/dimchat/sdk-py',
    license='MIT',
    author=__author__,
    author_email=__contact__,
    description='Decentralized Instant Messaging (Python Plugins)',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        '': ['res/*.js']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'dimp>=2.3.1',

        'pycryptodome',  # 3.14.1
        'base58',  # 1.0.3
        'ecdsa',   # 0.16.1
    ]
)
