#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
'''
Crimninal justice network dynamics modeling.

This example uses 7 modules:
    - Community
    - Arrested
    - Adjudication
    - Jail
    - Prison
    - Probation
    - Parole
and a population balance model is used to follow the offenders population
groups between modules.

To run this case using MPI you should compute the number of
processes as follows:

    `nprocs = 7 + 1 cortix`

then issue the MPI run command as follows (replace `nprocs` with a number):

     `mpiexec -n nprocs run_justice.py`

To run this case with the Python multiprocessing library, just run this file at the
command line as

    `run_justice.py`

'''

import scipy.constants as const

import matplotlib.pyplot as plt

from cortix.src.cortix_main import Cortix
from cortix.src.network import Network

from cortix.examples.prison import Prison
from cortix.examples.parole import Parole
from cortix.examples.adjudication import Adjudication
from cortix.examples.jail import Jail
from cortix.examples.arrested import Arrested
from cortix.examples.probation import Probation
from cortix.examples.community import Community

def main():
    '''Cortix run file for a criminal justice network.

    Attributes
    ----------
    n_groups : int
        Number of population groups being followed. This must be the same for all
        modules.
    end_time: float
        End of the flow time in SI unit.
    time_step: float
        Size of the time step between port communications in SI unit.
    use_mpi: bool
        If set to `True` use MPI otherwise use Python multiprocessing.

    '''

    # Configuration Parameters
    n_groups  = 150 # number of population groups
    end_time  = 50 * const.day
    time_step = 0.5 * const.day

    use_mpi = True  # True for MPI; False for Python multiprocessing

    lowell = Cortix(use_mpi=use_mpi, splash=True)

    lowell.network = Network()

    prison = Prison(n_groups=n_groups)
    lowell.network.module(prison)
    prison.end_time = end_time
    prison.time_step = time_step

    parole = Parole(n_groups=n_groups)
    lowell.network.module(parole)
    parole.end_time = end_time
    parole.time_step = time_step

    adjudication = Adjudication(n_groups=n_groups)
    lowell.network.module(adjudication)
    adjudication.end_time = end_time
    adjudication.time_step = time_step

    jail = Jail(n_groups=n_groups)
    lowell.network.module(jail)
    jail.end_time = end_time
    jail.time_step = time_step

    arrested = Arrested(n_groups=n_groups)
    lowell.network.module(arrested)
    arrested.end_time = end_time
    arrested.time_step = time_step

    probation = Probation(n_groups=n_groups)
    lowell.network.module(probation)
    probation.end_time = end_time
    probation.time_step = time_step

    community = Community(n_groups=n_groups, maturity_rate=100/const.day,
            offender_pool_size=10)
    lowell.network.module(community)
    community.end_time = end_time
    community.time_step = time_step
    community.show_time = (True,10*const.day)

    lowell.network.connect( prison, parole, 'bidirectional' )
    lowell.network.connect( adjudication, prison )
    lowell.network.connect( jail, prison )
    lowell.network.connect( adjudication, jail )
    lowell.network.connect( arrested, jail )
    lowell.network.connect( arrested, adjudication )
    lowell.network.connect( arrested, probation )
    lowell.network.connect( probation, jail )
    lowell.network.connect( adjudication, probation )

    lowell.network.connect( arrested, community )
    lowell.network.connect( jail, community )
    lowell.network.connect( probation, community )
    lowell.network.connect( adjudication, community )
    lowell.network.connect( prison, community )
    lowell.network.connect( parole, community )

    lowell.network.draw()

    lowell.run()

    if lowell.use_multiprocessing or lowell.rank == 0:

        # Attach to data
        prison       = lowell.network.modules[0]
        parole       = lowell.network.modules[1]
        adjudication = lowell.network.modules[2]
        jail         = lowell.network.modules[3]
        arrested     = lowell.network.modules[4]
        probation    = lowell.network.modules[5]
        community    = lowell.network.modules[6]

        total_num_unknowns = n_groups * len(lowell.network.modules)
        total_num_params = 0

        # Inspect Data Function
        def inspect_module_data(module,quant_name):
            population_phase = module.state
            (fxg_quant, time_unit) = population_phase.get_quantity_history(quant_name)

            fxg_quant.plot( x_scaling=1/const.day, x_label='Time [day]',
                    y_label=fxg_quant.name+' ['+fxg_quant.unit+']')

            # Number of parameters in the prison model
            n_params = (len(population_phase.GetActors())-1)*n_groups
            return n_params

        quant_names = ['fpg','feg','fag','fjg','frg','fbg','f0g']
        for (m,quant_name) in zip(lowell.network.modules,quant_names):
            total_num_params += inspect_module_data(m,quant_name)
            plt.grid()
            plt.savefig(m.name+'.png', dpi=300)

        # Total number of unknowns and parameters

        lowell.log.info('total number of unknowns   ='+str(total_num_unknowns))
        lowell.log.info('total number of parameters ='+str(total_num_params))

    # Properly shutdow lowell
    lowell.close()

if __name__ == '__main__':
    main()
