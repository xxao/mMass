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

#load libs
import numpy
import re
import copy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak

# load modules
import mod_peakpicking


# PEAKLIST OBJECT DEFINITION
# --------------------------

class peaklist:
    """Peaklist object definition."""
    
    def __init__(self, peaks=[]):
        
        # check data
        self.peaks = []
        for item in peaks:
            item = self._checkPeak(item)
            self.peaks.append(item)
        
        # sort peaklist by m/z
        self.sort()
        
        # set basepeak
        self.basepeak = None
        self._setbasepeak()
        
        # set relative intensities
        self._setRelativeIntensities()
    # ----
    
    
    def __len__(self):
        return len(self.peaks)
    # ----
    
    
    def __setitem__(self, i, item):
        
        # check item
        item = self._checkPeak(item)
        
        # basepeak is edited - set new
        if self.peaks[i] is self.basepeak:
            self.peaks[i] = item
            self._setbasepeak()
            self._setRelativeIntensities()
        
        # new basepeak set
        elif self.basepeak and item.intensity > self.basepeak.intensity:
            self.peaks[i] = item
            self.basepeak = item
            self._setRelativeIntensities()
        
        # lower than basepeak
        elif self.basepeak:
            item.ri = item.intensity / self.basepeak.intensity
            self.peaks[i] = item
        
        # no basepeak set
        else:
            self.peaks[i] = item
            self._setbasepeak()
            self._setRelativeIntensities()
        
        # sort peaklist
        self.sort()
    # ----
    
    
    def __getitem__(self, i):
        return self.peaks[i]
    # ----
    
    
    def __delitem__(self, i):
        
        # delete basepeak
        if self.peaks[i] is self.basepeak:
            del self.peaks[i]
            self._setbasepeak()
            self._setRelativeIntensities()
        
        # delete others
        else:
            del self.peaks[i]
    # ----
    
    
    def __iter__(self):
        self._index = 0
        return self
    # ----
    
    
    def __add__(self, other):
        """Return A+B."""
        
        new = self.duplicate()
        new.combine(other)
        return new
    # ----
    
    
    def __mul__(self, y):
        """Return A*y."""
        
        new = self.duplicate()
        new.multiply(y)
        return new
    # ----
    
    
    def next(self):
        
        if self._index < len(self.peaks):
            self._index += 1
            return self.peaks[self._index-1]
        else:
            raise StopIteration
    # ----
    
    
    def append(self, item):
        """Append new peak.
            item (peak or [#, #] or (#,#)) - peak to be added
        """
        
        # check peak
        item = self._checkPeak(item)
        
        # add peak and sort peaklist
        if self.peaks and self.peaks[-1].mz > item.mz:
            self.peaks.append(item)
            self.sort()
        else:
            self.peaks.append(item)
        
        # new basepeak set
        if self.basepeak and item.intensity > self.basepeak.intensity:
            self.basepeak = item
            self._setRelativeIntensities()
        
        # lower than basepeak
        elif self.basepeak and self.basepeak.intensity != 0:
            item.ri = item.intensity / self.basepeak.intensity
        
        # no basepeak set
        else:
            item.ri = 1.
            self._setbasepeak()
    # ----
    
    
    def reset(self):
        """Sort peaklist and recalculate basepeak and relative intensities."""
        
        self.sort()
        self._setbasepeak()
        self._setRelativeIntensities()
    # ----
    
    
    
    # GETTERS
    
    def duplicate(self):
        """Return copy of current peaklist."""
        return copy.deepcopy(self)
    # ----
    
    
    def groupname(self):
        """Get available group name."""
        
        # get used names
        used = []
        for peak in self.peaks:
            if peak.group != None and not peak.group in used:
                used.append(peak.group)
        
        # generate new name
        size = 1
        while True:
            for name in self._generateGroupNames(size):
                if not name in used:
                    return name
            size += 1
    # ----
    
    
    
    # MODIFIERS
    
    def sort(self):
        """Sort peaks according to m/z."""
        
        buff = []
        for item in self.peaks:
            buff.append((item.mz, item))
        buff.sort()
        
        self.peaks = []
        for item in buff:
            self.peaks.append(item[1])
    # ----
    
    
    def delete(self, indexes=[]):
        """Delete selected peaks.
            indexes (list or tuple) - indexes of peaks to be deleted
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # delete peaks
        relint = False
        for i in sorted(indexes, reverse=True):
            if self.peaks[i] is self.basepeak:
                relint = True
            del self.peaks[i]
        
        # recalculate basepeak and relative intensities
        if relint:
            self._setbasepeak()
            self._setRelativeIntensities()
    # ----
    
    
    def empty(self):
        """Remove all peaks."""
        
        del self.peaks[:]
        self.basepeak = None
    # ----
    
    
    def crop(self, minX, maxX):
        """Delete peaks outside given range.
            minX (float) - lower m/z limit
            maxX (float) - upper m/z limit
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # get indexes to delete
        indexes = []
        for x, peak in enumerate(self.peaks):
            if peak.mz < minX or peak.mz > maxX:
                indexes.append(x)
        
        # delete peaks
        self.delete(indexes)
    # ----
    
    
    def multiply(self, y):
        """Multiply each peak intensity by Y.
            y (int or float) - multiplier factor
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # multiply all peaks
        for peak in self.peaks:
            peak.setai(peak.ai * y)
            peak.setbase(peak.base * y)
        
        # update peaklist
        self._setbasepeak()
        self._setRelativeIntensities()
    # ----
    
    
    def combine(self, other):
        """Add data from given peaklist."""
        
        # check peaks
        buff = []
        for peak in copy.deepcopy(other):
            peak = self._checkPeak(peak)
            buff.append(peak)
        
        # store peaks
        self.peaks += buff
        
        # update peaklist
        self.sort()
        self._setbasepeak()
        self._setRelativeIntensities()
    # ----
    
    
    def recalibrate(self, fn, params):
        """Apply calibration to peaks.
            fn (function) - calibration model
            params (list or tuple) - params for calibration model
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # apply calibration
        for peak in self.peaks:
            peak.setmz( fn(params, peak.mz) )
    # ----
    
    
    def deisotope(self, maxCharge=1, mzTolerance=0.15, intTolerance=0.5, isotopeShift=0.0):
        """Calculate peak charges and find isotopes.
            maxCharge (float) - max charge to be searched
            mzTolerance (float) - absolute m/z tolerance for isotopes distance
            intTolerance (float) - relative intensity tolerance for isotopes and model (in %/100)
            isotopeShift (float) - isotope distance correction (neutral mass) (for HDX etc.)
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # find isotopes
        mod_peakpicking.deisotope(
            peaklist = self,
            maxCharge = maxCharge,
            mzTolerance = mzTolerance,
            intTolerance = intTolerance,
            isotopeShift = isotopeShift
        )
    # ----
    
    
    def deconvolute(self, massType=0):
        """Recalculate peaklist to singly charged.
            massType (0 or 1) - mass type used for m/z re-calculation, 0 = monoisotopic, 1 = average
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # deconvolute peaklist
        peaks = mod_peakpicking.deconvolute(
            peaklist = self,
            massType = massType
        )
        
        # store data
        self.peaks[:] = peaks.peaks[:]
        
        # update peaklist
        self.sort()
        self._setbasepeak()
        self._setRelativeIntensities()
    # ----
    
    
    def consolidate(self, window, forceWindow=False):
        """Group peaks within specified window.
            window (float) - default grouping window if peak fwhm not set
            forceWindow (bool) - use default window for all peaks instead of fwhm
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # group peaks
        buff = []
        buff.append(self.peaks[0])
        for current in self.peaks[1:]:
            previous = buff[-1]
            
            # set window
            win = window
            if not forceWindow and previous.fwhm and current.fwhm:
                win = (previous.fwhm + current.fwhm) / 8.
            
            # group with previous peak
            if (previous.mz + win) > current.mz:
                
                # get intensity
                intensity = previous.intensity + current.intensity
                ai = intensity + previous.base
                
                # get m/z
                mz = (previous.mz*previous.intensity + current.mz*current.intensity) / intensity
                
                # get fwhm
                fwhm = previous.fwhm
                if previous.fwhm and current.fwhm:
                    fwhm = (previous.fwhm*previous.intensity + current.fwhm*current.intensity) / intensity
                
                # update previous peak
                buff[-1].setmz(mz)
                buff[-1].setai(ai)
                buff[-1].setfwhm(fwhm)
            
            # add new peak
            else:
                buff.append(current)
        
        # remove group names
        for peak in buff:
            peak.setgroup('')
        
        # store data
        self.peaks[:] = buff[:]
        
        # update peaklist
        self.sort()
        self._setbasepeak()
        self._setRelativeIntensities()
    # ----
    
    
    def remthreshold(self, absThreshold=0., relThreshold=0., snThreshold=0.):
        """Remove peaks below threshold.
            absThreshold (float) - absolute intensity threshold
            relThreshold (float) - relative intensity threshold
            snThreshold (float) - signal to noise threshold
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # get absolute threshold
        threshold = self.basepeak.intensity * relThreshold
        threshold = max(threshold, absThreshold)
        
        # get indexes to delete
        indexes = []
        for x, peak in enumerate(self.peaks):
            if peak.intensity < threshold or (peak.sn != None and peak.sn < snThreshold):
                indexes.append(x)
        
        # delete peaks
        self.delete(indexes)
    # ----
    
    
    def remshoulders(self, window=2.5, relThreshold=0.05, fwhm=0.01):
        """Remove FT shoulder peaks.
            window (float) - peak width multiplier to make search window
            relThreshold (float) - max relative intensity of shoulder/parent peak (in %/100)
            fwhm (float) - default peak width if not set in peak
        """
        
        # check peaklist
        if not self.peaks:
            return
        
        # get possible parent peaks
        candidates = []
        for peak in self.peaks:
            if not peak.sn or peak.sn*relThreshold > 3:
                candidates.append(peak)
            
        # filter shoulder peaks
        indexes = []
        for parent in candidates:
            
            # get shoulder window
            if parent.fwhm:
                lowMZ = parent.mz - parent.fwhm * window
                highMZ = parent.mz + parent.fwhm * window
            elif fwhm:
                lowMZ = parent.mz - fwhm * window
                highMZ = parent.mz + fwhm * window
            else:
                continue
            
            # get intensity threshold
            intThreshold = parent.intensity * relThreshold
            
            # get indexes to delete
            for x, peak in enumerate(self.peaks):
                if (lowMZ < peak.mz < highMZ) and (peak.intensity < intThreshold) and (not x in indexes):
                    indexes.append(x)
                if peak.mz > highMZ:
                    break
        
        # delete peaks
        self.delete(indexes)
    # ----
    
    
    def remisotopes(self):
        """Remove isotopes."""
        
        # check peaklist
        if not self.peaks:
            return
        
        # get indexes to delete
        indexes = []
        for x, peak in enumerate(self.peaks):
            if peak.isotope != 0 and peak.charge != None:
                indexes.append(x)
        
        # delete peaks
        self.delete(indexes)
    # ----
    
    
    def remuncharged(self):
        """Remove uncharged peaks."""
        
        # check peaklist
        if not self.peaks:
            return
        
        # get indexes to delete
        indexes = []
        for x, peak in enumerate(self.peaks):
            if peak.charge == None:
                indexes.append(x)
        
        # delete peaks
        self.delete(indexes)
    # ----
    
    
    
    # HELPERS
    
    def _checkPeak(self, item):
        """Check item to be a valid peak."""
        
        # peak instance
        if isinstance(item, obj_peak.peak):
            return item
        
        # make peak from list or tuple
        elif type(item) in (list, tuple) and len(item)==2:
            return obj_peak.peak(item[0], item[1])
        
        # not valid peak data
        raise TypeError, 'Item must be a peak object or list/tuple of two floats!'
    # ----
    
    
    def _setbasepeak(self):
        """Get most intens peak."""
        
        # check peaklist
        if not self.peaks:
            self.basepeak = None
            return
        
        # set new basepeak
        self.basepeak = self.peaks[0]
        maxInt = self.basepeak.intensity
        for item in self.peaks[1:]:
            if item.intensity > maxInt:
                self.basepeak = item
                maxInt = item.intensity
    # ----
    
    
    def _setRelativeIntensities(self):
        """Set relative intensities for all peaks."""
        
        # check peaklist
        if not self.peaks:
            return
        
        # set relative intensities
        maxInt = self.basepeak.intensity
        if maxInt:
            for item in self.peaks:
                item.ri = item.intensity / maxInt
        else:
            for item in self.peaks:
                item.ri = 1.
    # ----
    
    
    def _generateGroupNames(self, size):
        """Generates serie of group names like A B.. AA AB... AAA AAB.."""
        
        pools = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ'] * size
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield ''.join(prod)
    # ----
    
    

