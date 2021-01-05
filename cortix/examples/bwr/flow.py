#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Cortix toolkit environment.
# https://cortix.org

import logging
from copy import deepcopy

import scipy.constants as unit
import numpy as math

import iapws.iapws97 as steam_table

from cortix import Module
from cortix.support.phase_new import PhaseNew as Phase
from cortix import Quantity

class Flow():
    """A flow is a container representing a discretized unit of fluid flow that
    is passed between two Cortix modules (think: x kg of liquid  water at          temperature a, pressure b, with thermophysical properties c, d and e. It 
    has three purposes:
    1. Provide a standard set of variable names and data types for passing data
    between Cortix modules.
    2. Ensure that any Cortix plant simulation module will "work" with any 
    other plant simulation module.
    3. Make it easy to understand the operation of models used to generate data    determine the range of their validity and what assumptions have been made 
    in regard to their operation.

    Flows work in the following way:
    1. A developer specifies what quantities a module needs to receive from 
    other modules in the network to perform calculations. These are listed in 
    the "inflow_attributes" attribute of the module class, which is inherited 
    from the PlantSim module superclass.
    2. The developer also specifies which quantities the module calculates that    can be made availible for other modules in the "outflow_attributes" 
    attribute.
    3. The developer records information in the docstrings of each of the 
    module's methods that specifies:
        -What inflow_attributes it requires
        -What outflow_attributes it requies
        -How the outflow_attributes are calculated
        -What assumptions are made in the calculation of the outflow_attributes
        -The range of each inflow_attribute over which the method is designed 
        to be used
        -Major references
    4. A user implements the module into a Cortix network. When ports are 
    connected, the receiving module's inflow_attributes list is checked against    the sending module's outflow_attributes list; Any attributes in the 
    former's list which are not present in the latter's list must be findable 
    using Flow's built-in methods, or an error will be thrown.
    5. If debug mode is on, A method of flow parses the docstrings of all the 
    methods in the sending module's class and ties inflow_attributes, 
    outflow_attributes and internal intermediate_attributes to the method that     utilizes them.
    6. Using graphviz, a network diagram is constructed which links 
    inflow_attributes, outflow_attributes, intermediate_attributes and methods     together both within and between modules in the order in which information 
    is actually processed.
    7. A text document is generated with module names and all relevant 
    docstrings using Latex, along with any network diagrams that have been 
    generated.
    8. When module A sends information through a port to module B, the 
    calculated values for outflow_attributes at that time step are 
    automatically added to a flow object.
    9. The flow object then uses the methods it inherits from its class to 
    generate values for any remaining inflow_attributes required by the 
    receiving module.
    10. The flow object is passed between the ports.
    11. The receiving module extracts any information it needs from flow, and 
    its methods proceed as normal.

    """


