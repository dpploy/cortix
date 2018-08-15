#!/usr/bin/env bash

# This file is used to build the sphinx documentation

# Clean up
rm -rf *_rst

# Update the readme.md convert
 pandoc -s -o readme_converted.rst ../README.md  

# Build docs for src project
sphinx-apidoc -o src_rst ../src
# Build docs for src/utils subdirectory
sphinx-apidoc -o src_rst/utils_rst ../src/utils

# Build docs for support directory
sphinx-apidoc -o support_rst ../support

# Make documentation
make clean
make html
