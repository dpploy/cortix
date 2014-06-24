#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix module for shearing 

Tue Jun 24 12:36:17 EDT 2014
"""
#*********************************************************************************
import os, sys, io
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

def main(argv):

 assert len(argv) == 4, 'missing command line input.'

# first command line argument is an input file
 inputFullPathFileName = argv[1]

 tree = ElementTree()

# second command line argument is the Cortix parameter file
 cortexParamFullPathFileName = argv[2]
 tree.parse(cortexParamFullPathFileName)
 cortexParamXMLRootNode = tree.getroot()
 paramNode = cortexParamXMLRootNode 

# third command line argument is the Cortix communication file
 cortexCommFullPathFileName  = argv[3]
 tree.parse(cortexCommFullPathFileName)
 cortexCommXMLRootNode = tree.getroot()

#*********************************************************************************
# Usage: -> python pymain.py or ./pyplot.py
if __name__ == "__main__":
   main(sys.argv)
