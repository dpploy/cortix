.. raw:: html

   <h1>

Cortix

.. raw:: html

   </h1>

.. raw:: html

   <p align="center">

.. raw:: html

   </p>

.. raw:: html

   <h2>

What is Cortix?

.. raw:: html

   </h2>

.. raw:: html

   <ul>

.. raw:: html

   <li>

Cortix is a Python library for system-level module coupling, execution,
and analysis.

.. raw:: html

   </li>

.. raw:: html

   <li>

Cortix takes as input a collection of computational modules and provides
an environment for the coupling of those modules into a single
simulation.

.. raw:: html

   </li>

.. raw:: html

   <li>

Cortix handles

.. raw:: html

   <ul>

::

    <li>Communication between the modules</li>
    <li>Numerical integration</li>
    <li>Data visualization</li>

.. raw:: html

   </ul>

.. raw:: html

   </li>

.. raw:: html

   </ul>

The primary concepts in Cortix are the creation of an Application and a
Simulation involving Tasks.

.. raw:: html

   <h2>

Dependencies

.. raw:: html

   </h2>

.. raw:: html

   <ul>

.. raw:: html

   <li>

Python >= 3.6.5

.. raw:: html

   </li>

.. raw:: html

   <li>

mpi4py >= 3.0.0 (use openmpi >= 3.1.1)

.. raw:: html

   </li>

.. raw:: html

   <li>

networkx >= 1.11

.. raw:: html

   </li>

.. raw:: html

   <li>

matplotlib >= 2.2.2

.. raw:: html

   </li>

.. raw:: html

   <li>

numpy >= 1.10.4

.. raw:: html

   </li>

.. raw:: html

   </ul>

.. raw:: html

   <h2>

Usage

.. raw:: html

   </h2>

Cortix is a library and it is best used when copied to its own
directory, say inside a project directory of your choice, e.g.

/somepath/myproject/cortix/

or anywhere else in your system, e.g.

/somepath/cortix

Then add either /somepath/myproject to $PYTHONPATH or /somepath to
$PYTHONPATH, respectively.

Cortix has a directory (examples/) that contains examples for input
files and a driver file. At the moment these input files are past files
used in the development of Cortix.

A driver file is needed to run Cortix. There is an example
(examples/driver-cortix.py) that can be copied to say:

/somepath/driver-test.py

or

/somepath/myproject/driver-test.py

An input configuration (xml) file is also needed. An example is provided
in the in the examples/input/ directory (cortix-config.xml).

Then to run Cortix, enter the directory of the driver and run the driver

./driver-test.py

which will run an MPI process for Cortix and an additional MPI process
for each launched module in its own MPI process (or pool of processes;
to be implemented in the future).

To capture the Cortix screen output of log messages and other messages,
do

/driver-cortix.py >& screen.out

under Linux (inspect the output file screen.out when the run is
finished). Extensive logging of runtime information is stored in the
directory specified in the cortix-config.xml input file.

.. raw:: html

   <h2>

Maintainers

.. raw:: html

   </h2>

.. raw:: html

   <ul>

.. raw:: html

   <li>

Valmor F. de Almeida: Valmor\_deAlmeida@uml.edu

.. raw:: html

   </li>

.. raw:: html

   <li>

Taha M. Azzaoui: tazzaoui@cs.uml.edu

.. raw:: html

   </li>

.. raw:: html

   </ul>

.. raw:: html

   <h2>

Documentation

.. raw:: html

   </h2>

.. raw:: html

   <ul>

.. raw:: html

   <li>

Gilberto E. Alas: gilbert\_alas@student.uml.edu

.. raw:: html

   </li>

.. raw:: html

   </ul>
