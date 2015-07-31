#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix: a program for system-level modules
        coupling, execution, and analysis.

Sat Jun  6 22:43:33 EDT 2015
"""
#*********************************************************************************
import os, sys, io, time, datetime
#*********************************************************************************

#---------------------------------------------------------------------------------
def _SetRuntimeStatus(self, status):

  status = status.strip()
  assert status == 'running' or status == 'finished', 'status invalid.'

  fout = open( self.runtimeStatusFullPathFileName,'w' )
  s = '<?xml version="1.0" encoding="UTF-8"?>\n'; fout.write(s)
  s = '<!-- Written by Launcher.py -->\n'; fout.write(s)
  today = datetime.datetime.today()
  s = '<!-- '+str(today)+' -->\n'; fout.write(s)
  s = '<runtime>\n'; fout.write(s)
  s = '<status>'+status+'</status>\n'; fout.write(s)
  s = '</runtime>\n'; fout.write(s)
  fout.close()

#*********************************************************************************
