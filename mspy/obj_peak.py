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
import blocks

# load modules
import mod_basics


# PEAK OBJECT DEFINITION
# ----------------------

class peak:
    """Peak object definition."""
    
    def __init__(self, mz, ai=0., base=0., sn=None, charge=None, isotope=None, fwhm=None, group='', **attr):
        
        self.mz = float(mz)
        self.ai = float(ai)
        self.base = float(base)
        self.sn = sn
        self.charge = charge
        self.isotope = isotope
        self.fwhm = fwhm
        self.group = group
        
        self.childScanNumber = None
        
        # set intensity
        self.ri = 1.
        self.intensity = self.ai - self.base
        
        # set resolution
        self.resolution = None
        if self.fwhm:
            self.resolution = self.mz/self.fwhm
        
        # set buffers
        self._mass = None
        
        # get additional attributes
        self.attributes = {}
        for name, value in attr.items():
            self.attributes[name] = value
    # ----
    
    
    def reset(self):
        """Clear peak buffers and set intensity and resolution."""
        
        # clear mass buffer
        self._mass = None
        
        # update intensity
        self.intensity = self.ai - self.base
        
        # update resolution
        self.resolution = None
        if self.fwhm:
            self.resolution = self.mz/self.fwhm
    # ----
    
    
    
    # GETTERS
    
    def mass(self):
        """Get neutral peak mass."""
        
        # check charge
        if self.charge == None:
            return None
        
        # check mass buffer
        if self._mass != None:
            return self._mass
        
        # calculate neutral mass
        self._mass = mod_basics.mz(self.mz, 0, self.charge, agentFormula='H', agentCharge=1)
        
        return self._mass
    # ----
    
    
    
    # SETTERS
    
    def setmz(self, mz):
        """Set new m/z value."""
        
        # update value
        self.mz = mz
        
        # update resolution
        self.resolution = None
        if self.fwhm:
            self.resolution = self.mz/self.fwhm
        
        # clear mass buffer
        self._mass = None
    # ----
    
    
    def setai(self, ai):
        """Set new a.i. value."""
        
        # update value
        self.ai = ai
        
        # update intensity
        self.intensity = self.ai - self.base
    # ----
    
    
    def setbase(self, base):
        """Set new baseline value."""
        
        # update value
        self.base = base
        
        # update intensity
        self.intensity = self.ai - self.base
    # ----
    
    
    def setsn(self, sn):
        """Set new s/n value."""
        self.sn = sn
    # ----
    
    
    def setcharge(self, charge):
        """Set new charge value."""
        
        # update value
        self.charge = charge
        
        # clear mass buffer
        self._mass = None
    # ----
    
    
    def setisotope(self, isotope):
        """Set new isotope value."""
        self.isotope = isotope
    # ----
    
    
    def setfwhm(self, fwhm):
        """Set new fwhm value."""
        
        # update value
        self.fwhm = fwhm
        
        # update resolution
        self.resolution = None
        if self.fwhm:
            self.resolution = self.mz/self.fwhm
    # ----
    
    
    def setgroup(self, group):
        """Set new group name value."""
        self.group = group
    # ----
    
    

