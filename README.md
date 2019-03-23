# Cortix
> A Python library for system-level module coupling, execution, and analysis.

![Website](https://img.shields.io/website/https/github.com/dpploy/cortix.svg)
[![Repo Size](https://img.shields.io/github/repo-size/dpploy/cortix.svg?style=flat)](https://cortix.org)
[![Build Status](https://travis-ci.org/dpploy/cortix.svg?branch=master)](https://travis-ci.org/dpploy/cortix)
[![PyPI version](https://badge.fury.io/py/cortix.svg)](https://badge.fury.io/py/cortix)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)](https://badge.fury.io/py/cortix)

![](cortix/docs/cortix-cover.png)

## What is Cortix?

* Cortix is a Python library for system-level module coupling, execution, and
  analysis of dynamical system models that exchange time-dependent data.
* Cortix takes as input a collection of computational modules and provides an 
  environment for the coupling of these modules into a single simulation.
* Cortix supports:
    - Communication between modules
    - Time synchronization
    - Data visualization

The basic concepts in Cortix are the creation of an `Application` and a `Simulation` involving `Tasks`.

## Installation: Cortix can be installed on any Unix-based environment

## Installing via PyPI
```
pip install --user cortix
```

## Installing from source
1. Clone this repository to install the current version of Cortix in PyPI. 
```
git clone https://github.com/dpploy/cortix.git
```
2. Install the required dependencies listed in requirements.txt
```
pip install --user -r cortix/requirements.txt
```
3. Add ```cortix```'s parent path to your ```$PYTHONPATH``` variable
```
export PYTHONPATH=$PYTHONPATH:$(pwd)
```
Note: you may want to add this line to your ```.bashrc``` in order for it to be persistent

## Testing

Testing is facilitated through <a href="http://pytest.org">PyTest</a>. To test your Cortix install, run the droplet example from the python shell
```
   >> from cortix.examples.console_run import droplet_run as droplet 
   >> droplet.run()
```

## Using Cortix

Cortix requires a set of input files, a driver, and a configuration file. See `examples/console_run` for working examples of Cortix simulations. Cortix will output logging information to `stdout` by default, extensive logging of runtime information is also stored in the `<work_dir>` directory specified in the `cortix-config.xml` input file.

## Developers 

- Valmor F. de Almeida: valmor\_dealmeida@uml.edu
- Taha M. Azzaoui: tazzaoui@cs.uml.edu
- Seamus D. Gallagher: seamus\_gallagher@student.uml.edu

## Documentation

- Austin Rotker: austin_rotker@student.uml.edu
- Gilberto E. Alas: gilberto\_alas@student.uml.edu

## Physical Address

Cortix Group <br>
c/o [UMass Innovation Hub](https://www.uml.edu/Innovation-Hub/) <br>
110 Canal St., 3rd Floor <br>
Lowell, MA  01852
