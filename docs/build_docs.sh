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
sphinx-apidoc -o support_rst/nuclear_rst ../support/nuclear

# Build docs for examples directory
sphinx-apidoc -o examples_rst ../examples
sphinx-apidoc -o examples_rst/city_justice_rst ../examples/city_justice
sphinx-apidoc -o examples_rst/droplet_swirl_rst ../examples/droplet_swirl
sphinx-apidoc -o examples_rst/nbody_rst ../examples/nbody

# Make documentation
make clean
make html
