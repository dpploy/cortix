.. Cortix documentation master file, created by
   sphinx-quickstart on Fri Aug  3 14:46:32 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
=========================================

Cortix: system dynamics simulation
=========================================

What is Cortix?
---------------
* Cortix is a Python library for system-level module coupling, execution, and
  analysis of dynamical system models that exchange time-dependent data.
* Cortix allows you to assemble a coupled system by connecting discrete
  `modules` into a `network` 
* Cortix takes as input a collection of computational modules and provides an 
  environment for the coupling of these modules into a single simulation.

.. image:: https://cortix.org/cortix-cover.png

Features
--------
* Massively parallel execution with `mpi4py <https://mpi4py.readthedocs.io/en/stable/>`_
* Efficient ODE and DAE solver
* Built-in time synchronization
* Data visualization
* Extensive logging

Documentation
-------------
Please see :ref:`Contents <toc>` for full documentation, including installation, examples, and PDF documents.

Bugs/Requests
-------------
Please use the `GitHub issue tracker <https://github.com/dpploy/cortix/issues>`_ to submit bugs or request features.

..
   Table of Contents
   -----------------
   .. toctree::
      src_rst/modules
      modulib_rst/modules
      examples_rst/modules
      support_rst/modules
      :maxdepth: 2

..
   Indices and tables
   ==================
   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
