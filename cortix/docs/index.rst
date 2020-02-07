.. Cortix documentation master file, created by
   sphinx-quickstart on Fri Aug  3 14:46:32 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
=========================================
Network dynamics simulation
=========================================

What is Cortix?
---------------
* Cortix is an open-source Python library for enabling development and simulation of
  `network` models on `massively` parallel computers.
* Cortix takes a collection of computational `modules` and provides an 
  environment for the coupling of these modules into a `network` simulation.
* Cortix provides a layer for data communication between `modules` in the `network`
  using parallel libraries (MPI for heterogeneous computing, and the Python 
  multiprocessing library for multi-core computing).
* Virtually any computational model that can be mapped onto a network is a 
  candidate for Cortix development.

.. image:: https://cortix.org/cortix-cover.png

Features
--------
* Module parent class for module development and coupling.
* Massively parallel execution with `mpi4py <https://mpi4py.readthedocs.io/en/stable/>`_.
* Support classes for building applications and modules.
* Examples of applications using Cortix.

Bugs/Requests
-------------
Please use the `GitHub issue tracker <https://github.com/dpploy/cortix/issues>`_ to submit bugs or request features.

..
   Table of Contents
   -----------------
   .. toctree::
      src_rst/modules
      examples_rst/modules
      support_rst/modules
      :maxdepth: 2

..
   Indices and tables
   ==================
   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
