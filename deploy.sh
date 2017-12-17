#!/usr/bin/env bash

# 指定脚本版本,然后进行部署.
source venv/bin/activate
rm -rf dist/*
python setup.py bdist_wheel --universal
twine upload dist/apptoolkit*
