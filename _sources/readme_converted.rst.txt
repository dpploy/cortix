A Python library for network dynamics modeling and HPC simulation.

| |Website|
| |Build Status|
| |PyPI version|
| |Repo Size|
| |PyPI - Python Version|

|image5|

What is Cortix?
---------------

-  Cortix is a massively parallel Python library for system-level module
   coupling, execution, and
   analysis of dynamical system models that exchange time-dependent
   data.
-  Cortix takes as input a collection of computational modules and
   provides an
   environment for the coupling of these modules into a single
   simulation.
-  Cortix supports:

   -  Module decoupling
   -  Communication between modules
   -  Data visualization

-  Cortix runs on top of `MPI <https://www.open-mpi.org/>`__ and scales
   across many cores.

Installation: start by installing `MPI <https://www.open-mpi.org/>`__
---------------------------------------------------------------------

Installing via PyPI
-------------------

::

    pip install --user cortix

Installing from source
----------------------

#. Clone this repository to install the latest version of Cortix

   ::

       git clone https://github.com/dpploy/cortix.git

#. Install the required dependencies listed in ``requirements.txt``

   ::

       pip install --user -r cortix/requirements.txt

#. Add ``cortix``'s parent path to your ``$PYTHONPATH`` variable

   ::

       export PYTHONPATH=$PYTHONPATH:$(pwd)

   Note: you may want to add this line to your ``.bashrc`` in order for
   it to be persistent

Verify your Cortix install by running the Droplet example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    mpirun -np 12 examples/droplet_run.py

Testing
-------

Testing is facilitated by `PyTest <http://pytest.org>`__. Tests can be
run locally from within the ``tests`` directory

::

    cd tests && py.test

Using Cortix
------------

Please refer to the `documentation <https://cortix.org/contents.html>`__
for more on getting started!

Team
----

-  Valmor F. de Almeida: valmor\_\ dealmeida@uml.edu
-  Taha M. Azzaoui: tazzaoui@cs.uml.edu
-  Seamus D. Gallagher: seamus\_\ gallagher@student.uml.edu
-  Austin Rotker: austin_rotker@student.uml.edu
-  Gilberto E. Alas: gilberto\_\ alas@student.uml.edu

Contributing
------------

Pull requests are welcome. For major changes, please open an
`issue <https://github.com/dpploy/cortix/issues>`__ first to discuss
what you would like to change.

Please make sure to update tests as appropriate.

Location
--------

Cortix Group

c/o `UMass Innovation Hub <https://www.uml.edu/Innovation-Hub/>`__

110 Canal St., 3rd Floor

Lowell, MA 01852

.. |Website| image:: https://img.shields.io/website/https/github.com/dpploy/cortix.svg
.. |Build Status| image:: https://travis-ci.org/dpploy/cortix.svg?branch=master
   :target: https://travis-ci.org/dpploy/cortix
.. |PyPI version| image:: https://badge.fury.io/py/cortix.svg
   :target: https://badge.fury.io/py/cortix
.. |Repo Size| image:: https://img.shields.io/github/repo-size/dpploy/cortix.svg?style=flat
   :target: https://cortix.org
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/Django.svg
   :target: https://badge.fury.io/py/cortix
.. |image5| image:: cortix-cover.png

