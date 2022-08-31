#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Model of a target rod (assembly).
'''
from copy import deepcopy
from cortix.support.phase_new import PhaseNew as Phase

class TargetRod:
    '''Target rod for irradiation and dissolution.

    Two solid phases: cladding and compact
    '''

    def __init__(self, specs=None, cladding_phase=None, compact_phase=None):
        '''Constructor.

        Parameters
        ----------
        specs: dict
        Dictionary of all geometric specifications of the target rod.

        cladding_phase: Phase
        Solid phase for the cladding domain.

        compact_phase: Phase
        Solid phase for the compact domain.

        Attributes
        ----------
        '''

        if specs is not None:
            assert isinstance(specs, dict)
        else:
            self.specs = deepcopy(specs)

        if cladding_phase is not None:
            assert isinstance(cladding_phase, Phase)
        else:
            self.cladding_phase = deepcopy(cladding_phase)

        if compact_phase is not None:
            assert isinstance(compact_phase, Phase)
        else:
            self.compact_phase = deepcopy(compact_phase)

if __name__ == '__main__':
    # Create an empty target rod
    trod = TargetRod()
    print(trod)
