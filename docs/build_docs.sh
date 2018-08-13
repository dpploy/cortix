#!/usr/bin/env bash

# This file is used to build documentation

rm -rf src_rst

# Build docs for main project
sphinx-apidoc -o src_rst ../src

# Build docs for utils subdirectory
sphinx-apidoc -o src_rst/utils_rst ../src/utils

# Make documentation
make clean
make html
