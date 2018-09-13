# Cortix

[![Build Status](https://travis-ci.org/dpploy/cortix.svg?branch=master)](https://travis-ci.org/dpploy/cortix)
[![PyPI version](https://badge.fury.io/py/cortix.svg)](https://badge.fury.io/py/cortix)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)
![AUR](https://img.shields.io/aur/license/yaourt.svg)
![](cortix/docs/cortix-cover.png)

## What is Cortix?

* Cortix is a Python library for system-level module coupling, execution, and
  analysis.
* Cortix takes as input a collection of computational modules and provides an 
  environment for the coupling of those modules into a single simulation.
* Cortix handles:
    - Communication between the modules
    - Numerical integration
    - Data visualization

The basic concepts in Cortix are the creation of an `Application` and a `Simulation` involving `Tasks`.

## Installing

Cortix can be installed on any Unix-based machine via pip. Simply run 
```
pip install cortix
```
to install the latest version of cortix.

## Usage

Cortix is a library and it is best used when copied to its own directory, say inside a project directory of your choice, *e.g.*, `/somepath/myproject/cortix/`, or anywhere else in your system, *e.g.*, `/somepath/cortix`. Then add either `/somepath/myproject to $PYTHONPATH` or `/somepath to $PYTHONPATH`, respectively.

Cortix has a directory (`examples/`) that contains examples for input files, and a driver file. At the moment these input files are past files used in the development of Cortix. A driver file is needed to run Cortix. There is an example (`examples/driver-cortix.py`) that can be copied to say: `/somepath/driver-test.py or /somepath/myproject/driver-test.py`. An input configuration (xml) file is also needed. An example is provided in the `examples/input/` directory (cortix-config.xml). Then to run Cortix, enter the directory of the driver and run the driver `./driver-test.py` which will run an MPI process for Cortix and an additional MPI process for each launched module as a single MPI process or as a pool of processes. To capture the Cortix screen output of log messages (and other standard output messages), issue the bash command `/driver-cortix.py >& screen.out` under Linux (inspect the output file `screen.out` when the run is finished). Extensive logging of runtime information is stored in the `<work_dir>` directory specified in the `cortix-config.xml` input file.

## Testing

Testing is facilitated through <a href="http://pytest.org">PyTest</a>. To execute the tests, run the ```py.test``` command from the tests directory.

## Developers 

- Valmor F. de Almeida: Valmor\_deAlmeida@uml.edu
- Taha M. Azzaoui: tazzaoui@cs.uml.edu

## Documentation

- Gilberto E. Alas: gilberto\_alas@student.uml.edu
