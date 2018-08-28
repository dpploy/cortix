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

# Usage: ./format-all.sh

./format-code.sh ../src/*.py
./format-code.sh ../examples/*.py
./format-code.sh ../modulib/pyplot/*.py
./format-code.sh ../support/*.py
./format-code.sh ../tests/*.py
./format-code.sh ../*.py
