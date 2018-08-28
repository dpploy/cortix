#/usr/bin/env bash

# This file is part of the Cortix toolkit evironment
# https://github.com/dpploy/...
#
# All rights reserved, see COPYRIGHT for full restrictions.
# https://github.com/dpploy/COPYRIGHT
#
# Licensed under the GNU General Public License v. 3, please see LICENSE file.
# https://www.gnu.org/licenses/gpl-3.0.txt

# Run pylint on the code base using cortix's custom options using the pylintc
# Usage: ./pylint-src.sh

pylint --rcfile=../.pylintrc ../src/*.py
