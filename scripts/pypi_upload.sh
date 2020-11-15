#!/usr/bin/env bash

# This script is used to uplaod a new release of cortix to PyPI
# https://pypi.org/project/cortix/

cd ..
python3 setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build cortix.egg-info dist
