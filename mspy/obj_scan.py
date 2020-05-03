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
import copy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak
import obj_peaklist

# load modules
import mod_signal
import mod_peakpicking


# SCAN OBJECT DEFINITION
# ----------------------

class scan:
    """Scan object definition."""
    
    def __init__(self, profile=[], peaklist=[], **attr):
        
        self.title = ''
        self.scanNumber = None
        self.parentScanNumber = None
        self.polarity = None
        self.msLevel = None
        self.retentionTime = None
        self.totIonCurrent = None
        self.basePeakMZ = None
        self.basePeakIntensity = None
        self.precursorMZ = None
        self.precursorIntensity = None
        self.precursorCharge = None
        
        # buffers
        self._baseline = None
        self._baselineParams = {'window': None, 'offset': None}
        
        # convert profile to numPy array
        if not isinstance(profile, numpy.ndarray):
            profile = numpy.array(profile)
        self.profile = profile
        
        # convert peaks to peaklist
        if not isinstance(peaklist, obj_peaklist.peaklist):
            peaklist = obj_peaklist.peaklist(peaklist)
        self.peaklist = peaklist
        
        # get additional attributes
        self.attributes = {}
        for name, value in attr.items():
            self.attributes[name] = value
    # ----
    
    
    def __len__(self):
        return len(self.profile)
    # ----
    
    
    def __add__(self, other):
        """Return A+B."""
        
        new = self.duplicate()
        new.combine(other)
        return new
    # ----
    
    
    def __sub__(self, other):
        """Return A-B."""
        
        new = self.duplicate()
        new.subtract(other)
        return new
    # ----
    
    
    def __mul__(self, y):
        """Return A*y."""
        
        new = self.duplicate()
        new.multiply(y)
        return new
    # ----
    
    
    def reset(self):
        """Clear scan buffers."""
        
        self._baseline = None
        self._baselineParams = {'window': None, 'offset': None}
    # ----
    
    
    
    # GETTERS
    
    def duplicate(self):
        """Return copy of current scan."""
        return copy.deepcopy(self)
    # ----
    
    
    def noise(self, minX=None, maxX=None, mz=None, window=0.1):
        """Return noise level and width for specified m/z range or m/z value.
            minX (float) - lower m/z limit
            maxX (float) - upper m/z limit
            mz (float) - m/z value
            window (float) - percentage around specified m/z value to use for noise calculation
        """
        
        # calculate noise
        return mod_signal.noise(
            signal = self.profile,
            minX = minX,
            maxX = maxX,
            x = mz,
            window = window
        )
    # ----
    
    
    def baseline(self, window=0.1, offset=0.):
        """Return spectrum baseline data.
            window (float or None) - noise calculation window (%/100)
            offset (float) - baseline offset, relative to noise width (in %/100)
        """
        
        # calculate baseline
        if self._baseline == None \
            or self._baselineParams['window'] != window \
            or self._baselineParams['offset'] != offset:
            
            self._baseline = mod_signal.baseline(
                signal = self.profile,
                window = window,
                offset = offset
            )
            
            self._baselineParams['window'] = window
            self._baselineParams['offset'] = offset
        
        return self._baseline
    # ----
    
    
    def normalization(self):
        """Return normalization params."""
        
        # calculate range for spectrum and peaklist
        if len(self.profile) > 0 and len(self.peaklist) > 0:
            spectrumMax = numpy.maximum.reduce(self.profile)[1]
            spectrumMin = numpy.minimum.reduce(self.profile)[1]
            peaklistMax = max([peak.ai for peak in self.peaklist])
            peaklistMin = min([peak.base for peak in self.peaklist])
            
            return max(spectrumMax, peaklistMax)/100.
        
        # calculate range for spectrum only
        elif len(self.profile) > 0:
            spectrumMax = numpy.maximum.reduce(self.profile)[1]
            shift = numpy.minimum.reduce(self.profile)[1]
            
            return spectrumMax/100.
        
        # calculate range for peaklist only
        elif len(self.peaklist) > 0:
            peaklistMax = max([peak.ai for peak in self.peaklist])
            shift = min([peak.base for peak in self.peaklist])
            
            return peaklistMax/100.
        
        # no data
        else:
            return 1.
    # ----
    
    
    def intensity(self, mz):
        """Return interpolated intensity for given m/z.
            mz (float) - m/z value
        """
        
        # calculate peak intensity
        return mod_signal.intensity(self.profile, mz)
    # ----
    
    
    def width(self, mz, intensity):
        """Return peak width for given m/z and height.
            mz (float) - peak m/z value
            intensity (float) - intensity of width measurement
        """
        
        # calculate peak width
        return mod_signal.width(self.profile, mz, intensity)
    # ----
    
    
    def area(self, minX=None, maxX=None, baselineWindow=0.1, baselineOffset=0.):
        """Return labeled peak in given m/z range.
            minX (float) - starting m/z value
            maxX (float) - ending m/z value
            baselineWindow (float or None) - noise calculation window (%/100)
            baselineOffset (float) - baseline offset, relative to noise width (in %/100)
        """
        
        # check data
        if len(self.profile) == 0:
            return 0.0
        
        # get baseline
        baseline = self.baseline(
            window = baselineWindow,
            offset = baselineOffset
        )
        
        # get peak area
        area = mod_signal.area(
            signal = self.profile,
            minX = minX,
            maxX = maxX,
            baseline = baseline
        )
        
        return area
    # ----
    
    
    def hasprofile(self):
        """Return true if scan has profile data."""
        return bool(len(self.profile))
    # ----
    
    
    def haspeaks(self):
        """Return true if scan has peaks in peaklist."""
        return bool(len(self.peaklist))
    # ----
    
    
    
    # SETTERS
    
    def setprofile(self, profile):
        """Set new profile data."""
        
        self.profile = profile
        self.reset()
    # ----
    
    
    def setpeaklist(self, peaks):
        """Set new peaklist."""
        
        # convert peaks to peaklist
        if isinstance(peaks, obj_peaklist.peaklist):
            self.peaklist = peaks
        else:
            self.peaklist = obj_peaklist.peaklist(peaks)
    # ----
    
    
    
    # MODIFIERS
    
    def swap(self):
        """Swap data between profile and peaklist."""
        
        # make new profile
        profile = [[i.mz, i.ai] for i in self.peaklist]
        profile = numpy.array(profile)
        
        # make new peaklist
        peaks = [obj_peak.peak(i[0],i[1]) for i in self.profile]
        peaks = obj_peaklist.peaklist(peaks)
        
        # update scan
        self.profile = profile
        self.peaklist = peaks
        
        # clear buffers
        self.reset()
    # ----
    
    
    def crop(self, minX, maxX):
        """Crop profile and peaklist.
            minX (float) - lower m/z limit
            maxX (float) - upper m/z limit
        """
        
        # crop spectrum data
        self.profile = mod_signal.crop(self.profile, minX, maxX)
        
        # crop peaklist data
        self.peaklist.crop(minX, maxX)
        
        # clear buffers
        self.reset()
    # ----
    
    
    def multiply(self, y):
        """Multiply profile and peaklist by Y.
            y (int or float) - multiplier factor
        """
        
        # multiply spectrum
        if len(self.profile):
            self.profile = mod_signal.multiply(self.profile, y=y)
        
        # multiply peakslist
        self.peaklist.multiply(y)
        
        # clear buffers
        self.reset()
    # ----
    
    
    def normalize(self):
        """Normalize profile and peaklist."""
        
        # get normalization params
        f = self.normalization()
        
        # normalize profile
        if len(self.profile) > 0:
            self.profile /= numpy.array((1, f))
        
        # normalize peaklist
        if len(self.peaklist) > 0:
            for peak in self.peaklist:
                peak.setai(peak.ai / f)
                peak.setbase(peak.base / f)
            self.peaklist.reset()
        
        # clear buffers
        self.reset()
    # ----
    
    
    def combine(self, other):
        """Add data from given scan.
            other (mspy.scan) - scan to combine with
        """
        
        # check scan
        if not isinstance(other, scan):
            raise TypeError, "Cannot combine with non-scan object!"
        
        # use profiles only
        if len(self.profile) or len(other.profile):
            
            # combine profiles
            self.profile = mod_signal.combine(self.profile, other.profile)
            
            # empty peaklist
            self.peaklist.empty()
        
        # use peaklists only
        elif len(self.peaklist) or len(other.peaklist):
            self.peaklist.combine(other.peaklist)
        
        # clear buffers
        self.reset()
    # ----
    
    
    def overlay(self, other):
        """Overlay with data from given scan.
            other (mspy.scan) - scan to overlay with
        """
        
        # check scan
        if not isinstance(other, scan):
            raise TypeError, "Cannot overlay with non-scan object!"
        
        # use profiles only
        if len(self.profile) or len(other.profile):
            
            # overlay profiles
            self.profile = mod_signal.overlay(self.profile, other.profile)
            
            # empty peaklist
            self.peaklist.empty()
            
            # clear buffers
            self.reset()
    # ----
    
    
    def subtract(self, other):
        """Subtract given data from current scan.
            other (mspy.scan) - scan to subtract
        """
        
        # check scan
        if not isinstance(other, scan):
            raise TypeError, "Cannot subtract non-scan object!"
        
        # use profiles only
        if len(self.profile) and len(other.profile):
            
            # subtract profile
            self.profile = mod_signal.subtract(self.profile, other.profile)
            
            # empty peaklist
            self.peaklist.empty()
            
            # clear buffers
            self.reset()
    # ----
    
    
    def smooth(self, method, window, cycles=1):
        """Smooth profile.
            method (MA GA SG) - smoothing method
            window (float) - m/z window size for smoothing
            cycles (int) - number of repeating cycles
        """
        
        # smooth data
        profile = mod_signal.smooth(
            signal = self.profile,
            method = method,
            window = window,
            cycles = cycles
        )
        
        # store data
        self.profile = profile
        self.peaklist.empty()
        
        # clear buffers
        self.reset()
    # ----
    
    
    def recalibrate(self, fn, params):
        """Apply calibration to profile and peaklist.
            fn (function) - calibration model
            params (list or tuple) - params for calibration model
        """
        
        # calibrate profile
        for x, point in enumerate(self.profile):
            self.profile[x][0] = fn(params, point[0])
        
        # calibrate peaklist
        self.peaklist.recalibrate(fn, params)
        
        # clear buffers
        self.reset()
    # ----
    
    
    def subbase(self, window=0.1, offset=0.):
        """Subtract baseline from profile.
            window (float or None) - noise calculation window (%/100)
            offset (float) - baseline offset, relative to noise width (in %/100)
        """
        
        # get baseline
        baseline = self.baseline(
            window = window,
            offset = offset
        )
        
        # subtract baseline
        profile = mod_signal.subbase(
            signal = self.profile,
            baseline = baseline
        )
        
        # store data
        self.profile = profile
        self.peaklist.empty()
        
        # clear buffers
        self.reset()
    # ----
    
    
    
    # PEAKLIST FUNCTIONS
    
    def labelscan(self, pickingHeight=0.75, absThreshold=0., relThreshold=0., snThreshold=0., baselineWindow=0.1, baselineOffset=0., smoothMethod=None, smoothWindow=0.2, smoothCycles=1):
        """Label centroides in current scan.
            pickingHeight (float) - peak picking height for centroiding
            absThreshold (float) - absolute intensity threshold
            relThreshold (float) - relative intensity threshold
            snThreshold (float) - signal to noise threshold
            baselineWindow (float) - noise calculation window (in %/100)
            baselineOffset (float) - baseline offset, relative to noise width (in %/100)
            smoothMethod (None, MA, GA or SG) - smoothing method
            smoothWindow (float) - m/z window size for smoothing
            smoothCycles (int) - number of smoothing cycles
        """
        
        # get baseline
        baseline = self.baseline(
            window = baselineWindow,
            offset = baselineOffset
        )
        
        # pre-smooth profile
        profile = self.profile
        if smoothMethod:
            profile = mod_signal.smooth(
                signal = profile,
                method = smoothMethod,
                window = smoothWindow,
                cycles = smoothCycles
            )
        
        # label peaks
        peaklist = mod_peakpicking.labelscan(
            signal = profile,
            pickingHeight = pickingHeight,
            absThreshold = absThreshold,
            relThreshold = relThreshold,
            snThreshold = snThreshold,
            baseline = baseline
        )
        
        # check peaklist
        if peaklist == None:
            return False
        
        # update peaklist
        self.peaklist = peaklist
        
        return True
    # ----
    
    
    def labelpeak(self, mz=None, minX=None, maxX=None, pickingHeight=0.75, baselineWindow=0.1, baselineOffset=0.):
        """Return labeled peak in given m/z range.
            mz (float) - m/z value to label
            minX (float) - m/z range start
            maxX (float) - m/z range end
            pickingHeight (float) - centroiding height
            baselineWindow (float) - noise calculation window (in %/100)
            baselineOffset (float) - baseline offset, relative to noise width (in %/100)
        """
        
        # get baseline
        baseline = self.baseline(
            window = baselineWindow,
            offset = baselineOffset
        )
        
        # label peak
        peak = mod_peakpicking.labelpeak(
            signal = self.profile,
            mz = mz,
            minX = minX,
            maxX = maxX,
            pickingHeight = pickingHeight,
            baseline = baseline
        )
        
        # check peak
        if not peak:
            return False
        
        # append peak
        self.peaklist.append(peak)
        
        return True
    # ----
    
    
    def labelpoint(self, mz, baselineWindow=0.1, baselineOffset=0.):
        """Label peak at given m/z value.
            mz (float) - m/z value to label
            baselineWindow (float) - noise calculation window (in %/100)
            baselineOffset (float) - baseline offset, relative to noise width (in %/100)
        """
        
        # get baseline
        baseline = self.baseline(
            window = baselineWindow,
            offset = baselineOffset
        )
        
        # label point
        peak = mod_peakpicking.labelpoint(
            signal = self.profile,
            mz = mz,
            baseline = baseline
        )
        
        # check peak
        if not peak:
            return False
        
        # append peak
        self.peaklist.append(peak)
        
        return True
    # ----
    
    
    def deisotope(self, maxCharge=1, mzTolerance=0.15, intTolerance=0.5, isotopeShift=0.0):
        """Calculate peak charges and find isotopes.
            maxCharge (float) - max charge to be searched
            zTolerance (float) - absolute m/z tolerance for isotopes distance
            intTolerance (float) - relative intensity tolerance for isotopes and model (in %/100)
            isotopeShift (float) - isotope distance correction (neutral mass) (for HDX etc.)
        """
        
        # find istopes
        self.peaklist.deisotope(
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
        
        # delete profile data
        self.profile = numpy.array([])
        
        # deconvolute peaklist
        self.peaklist.deconvolute(massType=massType)
        
        # clear buffers
        self.reset()
    # ----
    
    
    def consolidate(self, window, forceWindow=False):
        """Group peaks within specified window.
            window (float) - default grouping window if no peak fwhm
            forceWindow (bool) - use default window for all peaks instead of fwhm
        """
        
        self.peaklist.consolidate(
            window = window,
            forceWindow = forceWindow
        )
    # ----
    
    
    def remthreshold(self, absThreshold=0., relThreshold=0., snThreshold=0.):
        """Remove peaks below threshold.
            absThreshold (float) - absolute intensity threshold
            relThreshold (float) - relative intensity threshold
            snThreshold (float) - signal to noise threshold
        """
        
        self.peaklist.remthreshold(
            absThreshold = absThreshold,
            relThreshold = relThreshold,
            snThreshold = snThreshold
        )
    # ----
    
    
    def remshoulders(self, window=2.5, relThreshold=0.05, fwhm=0.01):
        """Remove shoulder peaks from current peaklist.
            window (float) - peak width multiplier to make search window
            relThreshold (float) - max relative intensity of shoulder/parent peak (in %/100)
            fwhm (float) - default peak width if not set in peak
        """
        
        self.peaklist.remshoulders(
            window = window,
            relThreshold = relThreshold,
            fwhm = fwhm
        )
    # ----
    
    
    def remisotopes(self):
        """Remove isotopes from current peaklist."""
        self.peaklist.remisotopes()
    # ----
    
    
    def remuncharged(self):
        """Remove uncharged peaks from current peaklist."""
        self.peaklist.remuncharged()
    # ----
    
    

