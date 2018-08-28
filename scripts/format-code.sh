#/usr/bin/env bash

# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt

# This script uses the autopep8 python module
# to format python code according to pep8 standards. 

# Usage: ./format-code.sh example.py

for FILE in "$@"
do
    echo "Formatting $FILE..."

    # Backup the file
    cp $FILE "$FILE~"

    # Format the file according to pep-8
    autopep8 --in-place --aggressive $FILE
done
