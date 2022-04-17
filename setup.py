#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################
# File Name: setup.py
# Author: mafei
# Mail: logan62334@gmail.com
# Created Time:  2017-06-26 01:25:34 AM
#############################################

from setuptools import setup, find_packages

import jmdevice

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="jmdevice",
    version=jmdevice.__version__,
    description="jmdevice",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="MIT Licence",

    author="mafei",
    author_email="logan62334@gmail.com",
    url="https://github.com/logan62334/jmdevice.git",

    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    platforms="any",
    install_requires=[
        'tidevice'
    ]
)
