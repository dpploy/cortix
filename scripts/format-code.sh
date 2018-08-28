#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/cortix
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/cortix/blob/master/COPYRIGHT.txt
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt

# Usage: ./format-code.sh example.py

for FILE in "$@"
do
    echo "Formatting $FILE..."

    # Backup the file
    cp $FILE "$FILE~"

    # Format the file according to pep-8
    autopep8 --in-place --aggressive $FILE
done
