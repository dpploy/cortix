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

# Usage: ./format-all.sh

./format-code.sh ../src/*.py
./format-code.sh ../examples/*.py
./format-code.sh ../modulib/pyplot/*.py
./format-code.sh ../support/*.py
./format-code.sh ../tests/*.py
./format-code.sh ../*.py
