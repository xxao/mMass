# -------------------------------------------------------------------------
#     Copyright (C) 2005-2013 Martin Strohalm <www.mmass.org>

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.

#     Complete text of GNU GPL can be found in the file LICENSE.TXT in the
#     main directory of the program.
# -------------------------------------------------------------------------

# load libs
import math
import re

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load blocks
import blocks

# load objects
import obj_compound


# BASIC CONSTANTS
# ---------------

ELECTRON_MASS = 0.00054857990924

FORMULA_PATTERN = re.compile(r'''
    ^(
        ([\(])* # start parenthesis
        (
            ([A-Z][a-z]{0,2}) # atom symbol
            (\{[\d]+\})? # isotope
            (([\-][\d]+)|[\d]*) # atom count
        )+
        ([\)][\d]*)* # end parenthesis
    )*$
''', re.X)

ELEMENT_PATTERN = re.compile(r'''
            ([A-Z][a-z]{0,2}) # atom symbol
            (?:\{([\d]+)\})? # isotope
            ([\-]?[\d]*) # atom count
''', re.X)


# BASIC FUNCTIONS
# ---------------

def delta(measuredMass, countedMass, units='ppm'):
    """Calculate error between measured Mass and counted Mass in specified units.
        measuredMass (float) - measured mass
        countedMass (float) - counted mass
        units (Da, ppm or %) - error units
    """
    
    if units == 'ppm':
        return (measuredMass - countedMass) / countedMass*1000000
    elif units == 'Da':
        return (measuredMass - countedMass)
    elif units == '%':
        return (measuredMass - countedMass) / countedMass*100
    else:
        raise ValueError, 'Unknown units for delta! -->' + units
# ----


def mz(mass, charge, currentCharge=0, agentFormula='H', agentCharge=1, massType=0):
    """Calculate m/z value for given mass and charge.
        mass (tuple of (Mo, Av) or float) - current mass
        charge (int) - final charge of ion
        currentCharge (int) - current mass charge
        agentFormula (str or mspy.compound) - charging agent formula
        agentCharge (int) - charging agent unit charge
        massType (0 or 1) - used mass type if mass value is float, 0 = monoisotopic, 1 = average
    """
    
    # check agent formula
    if agentFormula != 'e' and not isinstance(agentFormula, obj_compound.compound):
        agentFormula = obj_compound.compound(agentFormula)
    
    # get agent mass
    if agentFormula == 'e':
        agentMass = [ELECTRON_MASS, ELECTRON_MASS]
    else:
        agentMass = agentFormula.mass()
        agentMass = (agentMass[0]-agentCharge*ELECTRON_MASS, agentMass[1]-agentCharge*ELECTRON_MASS)
    
    # recalculate zero charge
    agentCount = currentCharge/agentCharge
    if currentCharge != 0:
        if type(mass) in (tuple, list):
            massMo = mass[0]*abs(currentCharge) - agentMass[0]*agentCount
            massAv = mass[1]*abs(currentCharge) - agentMass[1]*agentCount
            mass = (massMo, massAv)
        else:
            mass = mass*abs(currentCharge) - agentMass[massType]*agentCount
    if charge == 0:
        return mass
    
    # calculate final charge
    agentCount = charge/agentCharge
    if type(mass) in (tuple, list):
        massMo = (mass[0] + agentMass[0]*agentCount)/abs(charge)
        massAv = (mass[1] + agentMass[1]*agentCount)/abs(charge)
        return (massMo, massAv)
    else:
        return (mass + agentMass[massType]*agentCount)/abs(charge)
# ----


def md(mass, mdType='standard', kendrickFormula='CH2', rounding='floor'):
    """Calculate mass defect for given monoisotopic mass.
        mass (float) - monoisotopic mass
        mdType (fraction | standard | relative | kendrick) - mass defect type
        kendrickFormula (str) - kendrick group formula
        rounding (floor | ceil | round) - nominal mass rounding function
    """
    
    # return fractional part
    if mdType == 'fraction':
        return mass - math.floor(mass)
    
    # return standard mass defect
    elif mdType == 'standard':
        return mass - nominalmass(mass, rounding)
    
    # return relative mass defect
    elif mdType == 'relative':
        return 1e6 * (mass - nominalmass(mass, rounding)) / mass
    
    # return Kendrick mass defect
    elif mdType == 'kendrick':
        
        if not isinstance(kendrickFormula, obj_compound.compound):
            kendrickFormula = obj_compound.compound(kendrickFormula)
        
        kendrickF = kendrickFormula.nominalmass()/kendrickFormula.mass(0)
        
        return  nominalmass(mass * kendrickF, rounding) - (mass * kendrickF)
    
    # unknown mass defect type
    else: raise ValueError, 'Unknown mass defect type! --> ' + mdType
# ----


def nominalmass(mass, rounding='floor'):
    """Calculate for given monoisotopic mass and rounding function.
        mass (float) - monoisotopic mass
        rounding (floor | ceil | round) - nominal mass rounding function
    """
    
    if rounding == 'floor':
        return math.floor(mass)
    
    elif rounding == 'ceil':
        return math.ceil(mass)
    
    elif rounding == 'round':
        return round(mass)
    
    # unknown rounding function
    else: raise ValueError, 'Unknown nominal mass rounding! --> ' + rounding
# ----



# FORMULA FUNCTIONS
# -----------------

def rdbe(compound):
    """Get RDBE (Range or Double Bonds Equivalents) of a given compound.
        compound (str or mspy.compound) - compound
    """
    
    # check compound
    if not isinstance(compound, obj_compound.compound):
        compound = obj_compound.compound(compound)
    
    # get composition
    comp = compound.composition()
    
    # get atoms from composition
    atoms = []
    for item in comp:
        match = ELEMENT_PATTERN.match(item)
        if match and not match.group(1) in atoms:
            atoms.append(match.group(1))
    
    # get rdbe
    rdbeValue = 0.
    for a in atoms:
        valence = blocks.elements[a].valence
        if valence:
            rdbeValue += (valence - 2) * compound.count(a, groupIsotopes=True)
    rdbeValue /= 2.
    rdbeValue += 1.
    
    return rdbeValue
# ----


def frules(compound, rules=['HC','NOPSC','NOPS','RDBE','RDBEInt'], HC=(0.1, 3.0), NOPSC=(4,3,2,3), RDBE=(-1,40)):
    """Check formula rules for a given compound.
        compound (str or mspy.compound) - compound
        rules (list of str) - rules to be checked
        HC (tuple) - H/C limits
        NOPSC (tuple) - NOPS/C max values
        RDBE (tuple) - RDBE limits
    """
    
    # check compound
    if not isinstance(compound, obj_compound.compound):
        compound = obj_compound.compound(compound)
    
    # get element counts
    countC = float(compound.count('C', groupIsotopes=True))
    countH = float(compound.count('H', groupIsotopes=True))
    countN = float(compound.count('N', groupIsotopes=True))
    countO = float(compound.count('O', groupIsotopes=True))
    countP = float(compound.count('P', groupIsotopes=True))
    countS = float(compound.count('S', groupIsotopes=True))
    
    # get carbon ratios
    if countC:
        ratioHC = countH / countC
        ratioNC = countN / countC
        ratioOC = countO / countC
        ratioPC = countP / countC
        ratioSC = countS / countC
    
    # get RDBE
    rdbeValue = rdbe(compound)
    
    # check HC rule
    if 'HC' in rules and countC:
        if (ratioHC < HC[0] or ratioHC > HC[1]):
            return False
    
    # check NOPS rule
    if 'NOPSC' in rules and countC:
        if (ratioNC > NOPSC[0] or ratioOC > NOPSC[1] or ratioPC > NOPSC[2] or ratioSC > NOPSC[3]):
            return False
    
    # check NOPS all > 1 rule
    if 'NOPS' in rules and (countN > 1 and countO > 1 and countP > 1 and countS > 1):
        if (countN >= 10 or countO >= 20 or countP >= 4 or countS >= 3):
            return False
    
    # check NOP all > 3 rule
    if 'NOPS' in rules and (countN > 3 and countO > 3 and countP > 3):
        if (countN >= 11 or countO >= 22 or countP >= 6):
            return False
    
    # check NOS all > 1 rule
    if 'NOPS' in rules and (countN > 1 and countO > 1 and countS > 1):
        if (countN >= 19 or countO >= 14 or countS >= 8):
            return False
    
    # check NPS all > 1 rule
    if 'NOPS' in rules and (countN > 1 and countP > 1 and countS > 1):
        if (countN >= 3 or countP >= 3 or countS >= 3):
            return False
    
    # check OPS all > 1 rule
    if 'NOPS' in rules and (countO > 1 and countP > 1 and countS > 1):
        if (countO >= 14 or countP >= 3 or countS >= 3):
            return False
    
    # check RDBE range
    if 'RDBE' in rules:
        if rdbeValue < RDBE[0] or rdbeValue > RDBE[1]:
            return False
    
    # check integer RDBE
    if 'RDBEInt' in rules:
        if rdbeValue % 1:
            return False
    
    # all ok
    return True
# ----


