#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################
# File Name: setup.py
# Author: mafei
# Mail: logan62334@gmail.com
# Created Time:  2017-06-26 01:25:34 AM
#############################################

from setuptools import setup, find_packages

import apptoolkit

setup(
    name="apptoolkit",
    version=apptoolkit.__version__,
    description="apptoolkit",
    long_description=open("README.md").read(),
    license="MIT Licence",

    author="mafei",
    author_email="logan62334@gmail.com",
    url="https://github.com/logan62334/python-apptoolkit.git",

    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    platforms="any",
    install_requires=[]
)
