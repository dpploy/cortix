#!/usr/bin/env bash

# This file is used to build the sphinx documentation

# Editing of the generated .rst files may be necessary when adding new files

# Clean up
# rm -rf *_rst

# Update the readme.md convert
pandoc -f markdown_github -t rst -o readme_converted.rst ../../README.md

# Correct the path to cortix-cover.png in readme_converted.rst
sed -i 's+cortix/docs/cortix-cover.png+cortix-cover.png+g' readme_converted.rst

# Remove Cortix double heading
sed -i -e 1,3d readme_converted.rst

# Build docs for src directory
sphinx-apidoc -o src_rst ../src

# Build docs for support directory
sphinx-apidoc -o support_rst ../support

# Build docs for examples directory
sphinx-apidoc -o examples_rst ../examples

# Build docs for vortex subdirectory
#sphinx-apidoc -o examples_rst/modulib_rst/vortex_rst ../examples/modulib/vortex

# Make documentation
make clean
make html
