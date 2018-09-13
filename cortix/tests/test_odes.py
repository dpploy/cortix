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


import numpy as np
from scikits.odes import ode
import pickle


def van_der_pol(t, y, ydot):
    """ we create rhs equations for the problem"""
    ydot[0] = y[1]
    ydot[1] = 1000 * (1.0 - y[0]**2) * y[1] - y[0]


def test_odes():
    """
    Solve a test ODE and make sure the results are accurate
    """
    sols = []
    with open("input/test_odes_sols.pickle", "rb") as test_vals:
        real_sols = pickle.load(test_vals)
    t0, y0 = 1, np.array([0.5, 0.5])  # initial condition
    solution = ode(
        'cvode',
        van_der_pol,
        old_api=False).solve(
        np.linspace(
            t0,
            500,
            200),
        y0)
    for sol in solution.values.y:
        sols.append(sol)
    assert np.array_equal(sols, real_sols)


if __name__ == "__main__":
    test_odes()
