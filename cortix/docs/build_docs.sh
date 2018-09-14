#!/usr/bin/env bash

# This file is used to build the sphinx documentation

# Editing of the generated .rst files may be necessary when adding new files

# Clean up
# rm -rf *_rst

# Update the readme.md convert
pandoc -f markdown_github -t rst -o readme_converted.rst ../../README.md

# Correct the path to cortix-cover.png in readme_converted.rst
sed -i 's+docs/cortix-cover.png+cortix-cover.png+g' readme_converted.rst

# Remove Cortix double heading
sed -i -e 1,3d readme_converted.rst

# Build docs for src directory
sphinx-apidoc -o src_rst ../src

# Build docs for src/utils subdirectory
sphinx-apidoc -o src_rst/utils_rst ../src/utils

# Build docs for support directory
sphinx-apidoc -o support_rst ../support

# Build docs for modulib directory
sphinx-apidoc -o modulib_rst

# Build docs for pyplot subdirectory
sphinx-apidoc -o modulib_rst/pyplot_rst ../modulib/pyplot

# Build docs for examples directory
sphinx-apidoc -o examples_rst ../examples

# Make documentation
make clean
make html
