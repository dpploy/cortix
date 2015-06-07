#!/usr/bin/env python
"""
Valmor F. de Almeida dealmeidav@ornl.gov; vfda

Cortix native Nitrino module 

Tue Jun 24 01:03:45 EDT 2014
"""
#*********************************************************************************
import os, sys, io, time, datetime
import math, random
import numpy as np
from scipy.integrate import odeint
#*********************************************************************************

#---------------------------------------------------------------------------------
def LeachFuel( self, facilityTime, timeStep ):

  if self.fuelSegments is None: return 

  dissolverVolume = self.dissolverVolume
  roughnessF = self.roughnessF 

  molarityHNO3 = self.historyHNO3MolarLiquid[ facilityTime ]

  uMolarMass  = self.molarMassU
  puMolarMass = self.molarMassPu
  fpMolarMass = self.molarMassFP
 
  uo2MolarMass       = self.molarMassUO2
  puo2MolarMass      = self.molarMassPuO2
  fpo1dot18MolarMass = self.molarMassFPO1dot18

  rhoUO2       = self.rho_uo2
  rhoPuO2      = self.rho_puo2
  rhoFPO1dot18 = self.rho_fpo1dot18

  segmentsGeoData  = self.fuelSegments[0]
  segmentsCompData = self.fuelSegments[1]

  #----------------------------------------------------------
  # begin assembly of the ODE system; x is the unknown vector
  #----------------------------------------------------------

  x        = list()
  x0       = list()
  varNames = list()

  #...................................................
  # data for each fuel segment
  #...................................................

  segParams = list()

  segId = 0
  for (segGeoData,segCompData) in zip(segmentsGeoData,segmentsCompData):

    for (name,unit,value) in segGeoData:
      if name=='mass': 
        mass = value
      if name=='massDensity': 
        dens = value
      if name=='innerDiameter': 
        iD = value
      if name=='length': 
        length = value

    segDissolArea = 2.0 * math.pi * iD * iD / 4.0 + \
                    length * 0.2 * math.pi * iD  # add 20% cladding infiltration

    for (name,unit,value) in segCompData:
      if name=='U':
         uMass = value
      if name=='Pu':
         puMass = value
      if name=='FP':
         fpMass = value

    mUO2       = uMass  + uMass/uMolarMass*2.0*16.0
    mPuO2      = puMass + puMass/puMolarMass*2.0*16.0
    mFPO1dot18 = fpMass + fpMass/fpMolarMass*1.18*16.0

    addedMass  = uMass/uMolarMass*2.0*16.0
    addedMass += puMass/puMolarMass*2.0*16.0
    addedMass += fpMass/fpMolarMass*1.18*16.0

    originalMass = mass
    mass += addedMass

    wUO2       = 0.0
    wPuO2      = 0.0
    wFPO1dot18 = 0.0

    if mass > 0.0: wUO2       = mUO2 / mass
    if mass > 0.0: wPuO2      = mPuO2 / mass
    if mass > 0.0: wFPO1dot18 = mFPO1dot18 / mass

    molesUO2       = mUO2/uo2MolarMass
    molesPuO2      = mPuO2/puo2MolarMass
    molesFPO1dot18 = mFPO1dot18/fpo1dot18MolarMass

    molesTotal = molesUO2 + molesPuO2 + molesFPO1dot18
  
    xUO2       = 0.0
    xPuO2      = 0.0
    xFPO1dot18 = 0.0

    if molesTotal > 0.0: xUO2       = molesUO2/molesTotal
    if molesTotal > 0.0: xPuO2      = molesPuO2/molesTotal
    if molesTotal > 0.0: xFPO1dot18 = molesFPO1dot18/molesTotal

    mReactOrder = 2.0*(2.0-xUO2)

    rhoPrime = 0.0
    denom = xUO2 * rhoUO2 + xPuO2 * rhoPuO2 + xFPO1dot18 * rhoFPO1dot18 
    if denom > 0.0: rhoPrime = 100.0 * dens / denom

    rateCte = ( 0.48 * math.exp(-0.091*rhoPrime) )**(xUO2) * \
              ( 5.0 * math.exp(-0.27*rhoPrime) )**(1-xUO2)

    dissolMassRate = - rateCte * molarityHNO3**mReactOrder * roughnessF * segDissolArea
 
    """
    print('*********** segment ***********')
    print('timeStep min = ', timeStep)
    print('dissolMassRate g/s = ', dissolMassRate)
    print('dissolv mass g/min = ', dissolMassRate*60.0)
    print('rateCte = ', rateCte)
    print('molarityHNO3 M = ', molarityHNO3)
    print('mReactOrder = ', mReactOrder)
    print('rhoPrime % = ', rhoPrime)
    print('dens  g/cc= ', dens)
    print('xUO2 = ', xUO2)
    print('xPuO2 = ', xPuO2)
    print('xFPO1dot18 = ', xFPO1dot18)
    print('wUO2 = ', wUO2)
    print('wPuO2 = ', wPuO2)
    print('wFPO1dot18 = ', wFPO1dot18)
    print('segDissolArea mm^2 = ', segDissolArea)
    print('seg mass g = ', mass)
    """
    a = dict()
    a['rateCte']            = rateCte
    a['roughnessF']         = roughnessF
    a['segDissolArea']      = segDissolArea
    a['mReactOrder']        = mReactOrder
    a['uo2MolarMass']       = uo2MolarMass
    a['puo2MolarMass']      = puo2MolarMass
    a['fpo1dot18MolarMass'] = fpo1dot18MolarMass
    a['wUO2']               = wUO2
    a['wPuO2']              = wPuO2
    a['wFPO1dot18']         = wFPO1dot18

    segParams.append(a)

    x0.append(originalMass)

    varNames.append('seg'+'-'+str(segId))
    segId += 1

  # end of: for (segGeoData,segCompData) in zip(segmentsGeoData,segmentsCompData):

#  print('****** initial values ******')
#  print(x0)

  #...................................................
  # data for nitric acid 
  #...................................................

  hno3Params = dict()

  hno3Params['molarMassHNO3'] = self.molarMassHNO3

  massHNO3 = molarityHNO3 * self.molarMassHNO3 * dissolverVolume

  x0.append(massHNO3)

  varNames.append('hno3')

  #...................................................
  # data for UN 
  #...................................................

  unParams = dict()

  unParams['molarMassUO2NO3_2'] = self.molarMassUO2NO3_2

  massConc = self.historyUNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume
  
  x0.append(mass)

  varNames.append('un')

  #...................................................
  # data for PuN
  #...................................................

  punParams = dict()

  punParams['molarMassPuNO3_4'] = self.molarMassPuNO3_4

  massConc = self.historyPuNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume

  x0.append(mass)

  varNames.append('pun')

  #...................................................
  # data for FPN
  #...................................................

  fpnParams = dict()

  fpnParams['molarMassFPNO3_2dot36'] = self.molarMassFPNO3_2dot36

  massConc = self.historyFPNMassConcLiquid[ facilityTime ] 
  mass = massConc * dissolverVolume

  x0.append(mass)

  varNames.append('fpn')

  #...................................................
  # data for H2O
  #...................................................

  h2oParams = dict()

  h2oParams['molarMassH2O'] = self.molarMassH2O

  massH2O = self.historyH2OMassLiquid[ facilityTime ] 

  x0.append(massH2O)

  varNames.append('h2o')

  #...................................................
  # data for NO  
  #...................................................

  noParams = dict()

  noParams['molarMassNO'] = self.molarMassNO

  massNO = self.historyNOMassVapor[ facilityTime ] 

  x0.append(massNO)

  varNames.append('no')

  #...................................................
  # data for NO2
  #...................................................

  no2Params = dict()

  no2Params['molarMassNO2'] = self.molarMassNO2

  massNO2 = self.historyNO2MassVapor[ facilityTime ] 

  x0.append(massNO2)

  varNames.append('no2')

  #-----------------------------
  # Solve mass balance equations
  #-----------------------------

  t = np.arange(0.0,timeStep*60.0) # two output times

  x = odeint( fx, x0, t, 
              args=( varNames, 
                     dissolverVolume,
                     segParams, hno3Params, unParams, punParams, fpnParams, h2oParams,
                     noParams, no2Params ) )

#  print('******* solution vector *******')
#  print(x[0,:])
#  print(x[1,:])

  #----------------------------------------------------------
  # Update the solid mass in the system (history is not saved)
  #----------------------------------------------------------

  # Reduce the mass in the solids inventory

  newSegmentsGeoData  = list()
  newSegmentsCompData = list()

  for varName in varNames:

    if varName.split('-')[0] == 'seg':
      index = varNames.index(varName)
#      print('index = ',index)
      reducedMass = x[1,:][index]
      if reducedMass < 0.0: reducedMass = 0.0
#      print('reducedMass = ',reducedMass)
      segGeoData = segmentsGeoData[index]
      for (name,unit,value) in segGeoData:
        if name=='mass': 
          mass = value
          massUnit = unit
        if name=='massDensity': 
          dens = value
          densUnit = unit
        if name=='innerDiameter': 
          iD = value
          iDUnit = unit
        if name=='length': 
          lengthUnit = unit
      # end of: for (name,unit,value) in segGeoData:
#      print('mass = ',mass)
      reducedVol = reducedMass/dens
      area = math.pi * iD * iD / 4.0
      reducedLength = 0.0
      if area > 0.0: reducedLength = reducedVol*1000.0 / area
      if reducedVol == 0.0: iD = 0.0; reducedLength = 0.0
#      print('reducedLength = ',reducedLength)
#      print('length = ',length)
      newSegGeoData = list()
      newSegGeoData.append( ('mass',massUnit,reducedMass) )
      newSegGeoData.append( ('massDensity',densUnit,dens) )
      newSegGeoData.append( ('innerDiameter',iDUnit,iD) )
      newSegGeoData.append( ('length',lengthUnit,reducedLength) )
      newSegmentsGeoData.append( newSegGeoData )

      massReduction = 0.0
      if mass > 0.0:
        massReduction = reducedMass/mass
#      print('massReduction = ', massReduction)

      segCompData = segmentsCompData[index]
      newSegCompData = list()
      for (name,unit,value) in segCompData:
        newSegCompData.append( (name,unit,value*massReduction) )
      newSegmentsCompData.append( newSegCompData )

    # end of: if varName.split('-')[0] == 'seg':

  # end of: for (name,value) in zip(varNames,x[1,:]):

  self.fuelSegments = (newSegmentsGeoData,newSegmentsCompData)

  #----------------------------------------------------------
  # Update molarity of nitric acid in the liquid (save history)
  #----------------------------------------------------------

  index = varNames.index('hno3')
  massHNO3 = x[1,:][index]
  molarityHNO3 = massHNO3 / self.molarMassHNO3 / dissolverVolume

  self.historyHNO3MolarLiquid[ facilityTime + timeStep ] = molarityHNO3

  #----------------------------------------------------------
  # Update UN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('un')
  massUN = x[1,:][index]
  massConcUN = massUN / dissolverVolume

  self.historyUNMassConcLiquid[ facilityTime + timeStep ] = massConcUN

  #----------------------------------------------------------
  # Update PuN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('pun')
  massPuN = x[1,:][index]
  massConcPuN = massPuN / dissolverVolume

  self.historyPuNMassConcLiquid[ facilityTime + timeStep ] = massConcPuN

  #----------------------------------------------------------
  # Update PuN mass concentration 
  #----------------------------------------------------------

  index = varNames.index('fpn')
  massFPN = x[1,:][index]
  massConcFPN = massFPN / dissolverVolume

  self.historyFPNMassConcLiquid[ facilityTime + timeStep ] = massConcFPN

  #----------------------------------------------------------
  # Update mass of H2O in the liquid (save history)
  #----------------------------------------------------------

  index = varNames.index('h2o')
  massH2O = x[1,:][index]

  self.historyH2OMassLiquid[ facilityTime + timeStep ] = massH2O       

  #----------------------------------------------------------
  # Update mass of NO in the vapor (save history)
  #----------------------------------------------------------

  index = varNames.index('no')
  massNO = x[1,:][index]

#  if abs( massNO - self.historyNOMassVapor[ facilityTime ] ) < 1.0e-4:
#     self.historyNOMassVapor[ facilityTime + timeStep ] = 0.0
#  else:
#     self.historyNOMassVapor[ facilityTime + timeStep ] = massNO

  self.historyNOMassVapor[ facilityTime + timeStep ] = massNO

  #----------------------------------------------------------
  # Update mass of NO2 in the vapor (save history)
  #----------------------------------------------------------

  index = varNames.index('no2')
  massNO2 = x[1,:][index]

#  if abs( massNO2 - self.historyNO2MassVapor[ facilityTime ] ) < 1.0e-4:
#     self.historyNO2MassVapor[ facilityTime + timeStep ] = 0.0
#  else:
#     self.historyNO2MassVapor[ facilityTime + timeStep ] = massNO2

  self.historyNO2MassVapor[ facilityTime + timeStep ] = massNO2

  #----------------------------------------------------------
  # Apply gas-liquid phase equilibrium for NOx after the fact; FIX THIS LATER
  #----------------------------------------------------------

  if facilityTime > 0.0:

     """
     massNO   = self.historyNOMassVapor[ facilityTime + timeStep ] 
     molesNO  = massNO / self.molarMassNO

     massH2O  = self.historyH2OMassLiquid[ facilityTime + timeStep ] 
     molesH2O = massH2O / self.molarMassH2O

     massNO2  = self.historyNO2MassVapor[ facilityTime + timeStep ] 
     molesNO2 = massNO2 / self.molarMassNO2

     molesHNO3 = self.historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.dissolverVolume

     molesNOproduced = excess * 1.0/3.0
     molesHNO3produced = excess * 1.0/2.0
     massNOproduced = molesNOproduced * molesH20 * self.molarMassNO
     self.historyNOMassVapor[ facilityTime + timeStep ] += massNOproduced
     totalMolesHNO3 = molesHNO3produced + molesHNO3
     self.historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMolesHNO3 / self.dissolverVolume

     """

#     if massNO == 0.0 and massNO2 != 0.0: 

#     eqFactor = random.random() * 1.0/100.0
     eqFactor = 5.0/100.0
     massNO   = eqFactor * abs(massNO2-self.historyNO2MassVapor[facilityTime])
     massNO2  -= massNO
     self.historyNOMassVapor[ facilityTime + timeStep ]  += massNO
     self.historyNO2MassVapor[ facilityTime + timeStep ] = massNO2
     molesNO2 = massNO2 / self.molarMassNO2
     massH2O = 1.0/3.0 * molesNO2 * self.molarMassH2O
     # liquid water consumed to form NO in the vapor
     self.historyH2OMassLiquid[ facilityTime + timeStep ] -= massH2O
     molesNO = massNO / self.molarMassNO
     massHNO3 = 2.0 * molesNO * self.molarMassHNO3
     totalMassHNO3 = self.historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.dissolverVolume * self.molarMassHNO3 
     # nitric acid formed 
     totalMassHNO3 += massHNO3
     self.historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMassHNO3 / self.molarMassHNO3 / self.dissolverVolume

#     if massNO != 0.0 and massNO2 == 0.0: 

#     eqFactor = random.random() * 99.0/100.0
#     eqFactor = 1.0/100.0
#     massNO2  = eqFactor * massNO
#     massNO  *= (1.0-eqFactor)
#     self.historyNOMassVapor[ facilityTime + timeStep ]  = massNO
#     self.historyNO2MassVapor[ facilityTime + timeStep ] = massNO2
#     molesNO = massNO / self.molarMassNO
#     massH2O = molesNO * self.molarMassH2O
#     # liquid water produced when consuming NO
#     self.historyH2OMassLiquid[ facilityTime + timeStep ] += massH2O
#     massHNO3 = 2.0 * molesNO * self.molarMassHNO3
#     totalMassHNO3 = self.historyHNO3MolarLiquid[ facilityTime + timeStep ] * self.dissolverVolume * self.molarMassHNO3 
#     # nitric acid consumed
#     totalMassHNO3 -= massHNO3
#     self.historyHNO3MolarLiquid[ facilityTime + timeStep ] = totalMassHNO3 / self.molarMassHNO3 / self.dissolverVolume
#     """
 
#--------------------------------------------------------------------------------
def fx( x, t,     
        varNames, 
        dissolverVolume,  
        segParams, hno3Params, unParams, punParams, fpnParams, h2oParams,
        noParams, no2Params ):

  fvec = list()

  #...................................................
  # equations for fuel segments
  #...................................................

  index         = varNames.index('hno3')
  massHNO3      = x[index]
  molarMassHNO3 = hno3Params['molarMassHNO3']
  molarityHNO3  = massHNO3 / molarMassHNO3 / dissolverVolume

  molesRateUO2  = 0.0
  molesRatePuO2 = 0.0
  molesRateFPO1dot18 = 0.0
  
  for p in segParams:

    index = segParams.index(p)
    
    rateCte            =  p['rateCte']             
    roughnessF         =  p['roughnessF']          
    segDissolArea      =  p['segDissolArea']       
    mReactOrder        =  p['mReactOrder']         
    uo2MolarMass       =  p['uo2MolarMass']        
    puo2MolarMass      =  p['puo2MolarMass']       
    fpo1dot18MolarMass =  p['fpo1dot18MolarMass']  
    wUO2               =  p['wUO2']                
    wPuO2              =  p['wPuO2']               
    wFPO1dot18         =  p['wFPO1dot18']          

    f = - rateCte * roughnessF * segDissolArea * molarityHNO3 ** mReactOrder

    molesRateUO2       += abs(f) / uo2MolarMass       * wUO2
    molesRatePuO2      += abs(f) / puo2MolarMass      * wPuO2
    molesRateFPO1dot18 += abs(f) / fpo1dot18MolarMass * wFPO1dot18
 
    fvec.append(f)

  # end of: for p in segParams:

  #...................................................
  # equation for nitric acid
  #...................................................

  if molarityHNO3 <= 8.0:
     f = - ( 2.7*molesRateUO2 + 4.0*molesRatePuO2 + 2.36*molesRateFPO1dot18 ) * molarMassHNO3
  else:
     f = - ( 4.0*molesRateUO2 + 4.0*molesRatePuO2 + 2.36*molesRateFPO1dot18 ) * molarMassHNO3

  fvec.append(f)

  #...................................................
  # equation for UN 
  #...................................................

  molarMassUO2NO3_2 = unParams['molarMassUO2NO3_2']

  f = molesRateUO2 * molarMassUO2NO3_2 

  fvec.append(f)

  #...................................................
  # equation for PuN 
  #...................................................

  molarMassPuNO3_4 = punParams['molarMassPuNO3_4'] 

  f = molesRatePuO2 * molarMassPuNO3_4 

  fvec.append(f)

  #...................................................
  # equation for FPN 
  #...................................................

  molarMassFPNO3_2dot36 = fpnParams['molarMassFPNO3_2dot36'] 

  f = molesRateFPO1dot18 * molarMassFPNO3_2dot36 

  fvec.append(f)

  #...................................................
  # equation for H2O 
  #...................................................

  molarMassH2O = h2oParams['molarMassH2O']

  if molarityHNO3 <= 8.0:
     f = ( 1.3*molesRateUO2 + 2.0*molesRatePuO2 + 1.18*molesRateFPO1dot18 ) * molarMassH2O
  else:
     f = ( 2.0*molesRateUO2 + 2.0*molesRatePuO2 + 1.18*molesRateFPO1dot18 ) * molarMassH2O

  fvec.append(f)

  #...................................................
  # equation for NO  
  #...................................................

  index = varNames.index('no2')

  molarMassNO = noParams['molarMassNO']

  if molarityHNO3 <= 8.0:
     f = 0.7*molesRateUO2 * molarMassNO
  else:
     f = 0.0

  fvec.append(f)

  #...................................................
  # equation for NO2
  #...................................................

#  index = varNames.index('hno3')

  molarMassNO2 = no2Params['molarMassNO2']

  if molarityHNO3 <= 8.0:
     f = 0.0
  else:
     f = 2.0*molesRateUO2 * molarMassNO2

  fvec.append(f)

  #...................................................

  return fvec

#*********************************************************************************
