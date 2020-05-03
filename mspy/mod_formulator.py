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

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_compound

# load modules
import mod_basics
import calculations


# MASS TO FORMULA FUNCTIONS
# -------------------------

def formulator(mz, charge=0, tolerance=1., units='ppm', composition={}, agentFormula='H', agentCharge=1, limit=1000):
    """Generate formulae for given mass, tolerance and composition limits.
        mz (float) - searched m/z value
        charge (int) - current charge
        tolerance (float) - mass tolerance
        units (ppm or Da) - mass tolerance units
        composition (dict of 'element':[min count, max count]) - composition limits
        agentFormula (str) - charging agent formula
        agentCharge (int) - charging agent unit charge
        limit (int) - maximum formulae allowed to be calculated
    """
    
    # get neutral mass
    if charge != 0 and agentFormula:
        mass = mod_basics.mz(mz, 0, currentCharge=charge, agentFormula=agentFormula, agentCharge=agentCharge)
    else:
        mass = mz
    
    # check neutral mass
    if mass <= 0:
        return []
    
    # get mass limits
    if units == 'ppm':
        loMass = mass - (mass/1e6) * tolerance
        hiMass = mass + (mass/1e6) * tolerance
    elif charge != 0:
        loMass = mass - abs(charge)*tolerance
        hiMass = mass + abs(charge)*tolerance
    else:
        loMass = mass - tolerance
        hiMass = mass + tolerance
    
    # sort elements by masses to speed up processing
    buff = []
    for el in composition:
        elMass = obj_compound.compound(el).mass(0)
        buff.append([elMass, el])
    buff.sort(reverse=True)
    
    # compile elements and counts
    elementMasses = []
    elements = []
    minComposition = []
    maxComposition = []
    for el in buff:
        elementMasses.append(el[0])
        elements.append(el[1])
        minComposition.append(composition[el[1]][0])
        maxComposition.append(composition[el[1]][1])
    
    # check max composition
    for i in range(len(maxComposition)):
        maxComposition[i] = min(maxComposition[i], int(hiMass/elementMasses[i]))
    
    # generate compositions
    formulae = []
    comps = _compositions(minComposition, maxComposition, elementMasses, loMass, hiMass, limit)
    for comp in comps:
        
        CHECK_FORCE_QUIT()
        
        formula = ''
        for i in range(len(comp)):
            formula += '%s%d' % (elements[i], comp[i])
        
        formulae.append(formula)
    
    return formulae
# ----


def _compositions(minimum, maximum, masses, loMass, hiMass, limit):
    """Generates composition variants within given atom count limits and mass range.
        minimum (list or tuple of int) - miminum atom counts
        maximum (list or tuple of int) - maximum atom counts
        masses (list or tuple of float) - element masses reverse ordered
        loMass (float) - low mass limit
        hiMass (float) - high mass limit
        limit (int) - max number of items to be counted
    """
    
    # check data
    if (len(minimum) != len(maximum) or len(minimum) != len(masses)):
        raise ValueError, "Sizes of minimum, maximum and masses are not equal!"
    
    # generate compositions
    return calculations.formula_composition(tuple(minimum), tuple(maximum), tuple(masses), float(loMass), float(hiMass), int(limit))
# ----

