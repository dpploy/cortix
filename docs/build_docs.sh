#!/usr/bin/env bash

# This file is used to build the sphinx documentation

# Clean up
rm -rf src_rst

# Update the readme.md convert
 pandoc -s -o readme_converted.rst ../README.md  

# Build docs for main project
sphinx-apidoc -o src_rst ../src

# Build docs for utils subdirectory
sphinx-apidoc -o src_rst/utils_rst ../src/utils

# Make documentation
make clean
make html
