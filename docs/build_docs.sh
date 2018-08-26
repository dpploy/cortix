#!/usr/bin/env bash

# This file is used to build the sphinx documentation

# Clean up
rm -rf *_rst

# Update the readme.md convert
 pandoc -f markdown_github -t rst -o readme_converted.rst ../README.md

# Correct the path to cortix-cover.png in readme_converted.rst
sed -i 's+docs/cortix-cover.png+cortix-cover.png+g' readme_converted.rst

# Build docs for src project
sphinx-apidoc -o src_rst ../src
# Build docs for src/utils subdirectory
sphinx-apidoc -o src_rst/utils_rst ../src/utils

# Build docs for support directory
sphinx-apidoc -o support_rst ../support

# Make documentation
make clean
make html
