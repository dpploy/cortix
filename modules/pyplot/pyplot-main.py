#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix module for plotting

Tue Jun 24 12:13:50 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time
import datetime
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
#*********************************************************************************

def main(argv):

 assert len(argv) == 5, 'missing command line input.'

# First command line argument is the module input file name with full path.
# This input file is used by both the wrapper and the inner-code for 
# communication.
 inputFullPathFileName = argv[1]

 tree = ElementTree()

# Second command line argument is the Cortix parameter file
 cortexParamFullPathFileName = argv[2]
 tree.parse(cortexParamFullPathFileName)
 cortexParamTreeRoot = tree.getroot()

# Third command line argument is the Cortix communication file
 cortexCommFullPathFileName  = argv[3]
 tree.parse(cortexCommFullPathFileName)
 cortexCommTreeRoot = tree.getroot()

# Fourth command line argument is the module runtime-status.xml file
 runtimeStatusFullPathFileName = argv[4]

# Run PyPlot

 fout = open( runtimeStatusFullPathFileName,'w' )
 s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
 s = '<!-- Written by PyPlot.py -->\n'; fout.write(s)
 s = '<runtime>\n'; fout.write(s)
 s = '<status>running</status>\n'; fout.write(s)
 s = '</runtime>\n'; fout.write(s)
 fout.close()

 time.sleep(10)

# Communicate with Nitron to check running status


# Shutdown 

 tree.parse(runtimeStatusFullPathFileName)
 runtimeStatusXMLRootNode = tree.getroot()
 root = runtimeStatusXMLRootNode
 node = root.find('status')
 node.text = 'finished'
 a = Element('comment')
 a.text = 'Written by PyPlot.py'
 root.append(a)
 tree.write(runtimeStatusFullPathFileName,xml_declaration=True,encoding="UTF-8",method="xml")

#*********************************************************************************
# Usage: -> python pyplot.py or ./pyplot.py
if __name__ == "__main__":
   main(sys.argv)
