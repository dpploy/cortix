**********************************************************************************
Valmor F. de Almeida; dealmeidav@ornl.gov; vfda
**********************************************************************************

Cortix is a program (in the form of a library) for system-level modules coupling,
execution, and analysis.

The primary concepts in Cortix are the creation of an Application and a Simulation
involving Tasks.

**********************************************************************************
Fri Jul 31 18:02:36 EDT 2015 vfda

Cortix is a library and it is best used when copied to its own directory, say

  /somepath/cortix/

Then add /somepath/cortix to $PYTHONPATH

A driver is needed to run Cortix. 
There is an example in the repository (driver-test-1.py).
This driver can be copied to say:

   /somesimulationpath/driver-test.py

An input configuration (xml) file is also needed. An example is provided in 
the repository (cortix-config.xml).

Then to run Cortix, enter the directory of the driver and run the driver.

Alternatively, Cortix can run from its own directory. Enter the /somepath/cortix/
and run the driver.


**********************************************************************************
Thu Jul 30 16:00:19 EDT 2015; vfda

This repository was created as follows:

 cd cortix
 git remote add origin git@code.ornl.gov:fvu/cortix.git
 git push -u origin master

The git remote repository is at the ORNL external gitlab:

git remote add origin git@code.ornl.gov:fvu/cortix.git


