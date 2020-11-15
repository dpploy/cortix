#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment
# https://cortix.org
"""Crimninal justice network dynamics modeling.

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

    `run_city_justice.py`

To profile this run do:

     python -m cProfile -s time run_city_justice.py > lixo

"""

import scipy.constants as unit
import matplotlib.pyplot as plt

from cortix import Cortix
from cortix import Network

from cortix.examples.city_justice.prison import Prison
from cortix.examples.city_justice.parole import Parole
from cortix.examples.city_justice.adjudication import Adjudication
from cortix.examples.city_justice.jail import Jail
from cortix.examples.city_justice.arrested import Arrested
from cortix.examples.city_justice.probation import Probation
from cortix.examples.city_justice.community import Community

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
    n_groups  =  10 # number of population groups
    end_time  =  30* unit.year
    time_step = 1.0 * unit.day

    use_mpi = False  # True for MPI; False for Python multiprocessing

    city = Cortix(use_mpi=use_mpi, splash=True)

    city.network = Network()

    community = Community(n_groups=n_groups, non_offender_adult_population=100000,
                          offender_pool_size=0)
    city.network.module(community)
    community.end_time = end_time
    community.time_step = time_step
    community.show_time = (True, 30*unit.day)
    community.save = True

    prison = Prison(n_groups=n_groups, pool_size=0.0)
    city.network.module(prison)
    prison.end_time = end_time
    prison.time_step = time_step
    prison.save = True

    parole = Parole(n_groups=n_groups)
    city.network.module(parole)
    parole.end_time = end_time
    parole.time_step = time_step
    parole.save = True

    adjudication = Adjudication(n_groups=n_groups)
    city.network.module(adjudication)
    adjudication.end_time = end_time
    adjudication.time_step = time_step
    adjudication.save = True

    jail = Jail(n_groups=n_groups)
    city.network.module(jail)
    jail.end_time = end_time
    jail.time_step = time_step
    jail.save = True

    arrested = Arrested(n_groups=n_groups)
    city.network.module(arrested)
    arrested.end_time = end_time
    arrested.time_step = time_step
    arrested.save = True

    probation = Probation(n_groups=n_groups)
    city.network.module(probation)
    probation.end_time = end_time
    probation.time_step = time_step
    probation.save = True

    city.network.connect( prison, parole, 'bidirectional' )
    city.network.connect( adjudication, prison )
    city.network.connect( jail, prison )
    city.network.connect( adjudication, jail )
    city.network.connect( arrested, jail )
    city.network.connect( arrested, adjudication )
    city.network.connect( arrested, probation )
    city.network.connect( probation, jail )
    city.network.connect( adjudication, probation )

    city.network.connect( arrested, community, 'bidirectional' )
    city.network.connect( jail, community )
    city.network.connect( probation, community )
    city.network.connect( adjudication, community )
    city.network.connect( prison, community )
    city.network.connect( parole, community )

    city.network.draw()

    city.run()

    if city.use_multiprocessing or city.rank == 0:

        total_num_unknowns = n_groups * len(city.network.modules)
        total_num_params = 0

        # Inspect Data Function
        def inspect_module_data(module, quant_name):
            population_phase = module.population_phase
            (fxg_quant, time_unit) = population_phase.get_quantity_history(quant_name)

            fxg_quant.plot( x_scaling=1/unit.year, x_label='Time [y]',
                    y_label=fxg_quant.latex_name+' ['+fxg_quant.unit+']')

            # Number of parameters in the prison model
            n_params = (len(population_phase.GetActors())-1)*n_groups
            return n_params

        quant_names = {'Prison':'npg','Parole':'feg','Adjudication':'fag',
                'Jail':'fjg','Arrested':'frg','Probation':'fbg','Community':'f0g'}

        for m in city.network.modules:
            quant_name = quant_names[m.name]
            total_num_params += inspect_module_data(m,quant_name)
            plt.grid()
            plt.savefig(m.name+'.png', dpi=300)
            if m.name=='Community':
                inspect_module_data(m,'n0')
                plt.grid()
                plt.savefig(m.name+'-n0.png', dpi=300)

        # Total number of unknowns and parameters

        city.log.info('total number of unknowns   ='+str(total_num_unknowns))
        city.log.info('total number of parameters ='+str(total_num_params))

    # Properly shutdow city
    city.close()

if __name__ == '__main__':
    main()
