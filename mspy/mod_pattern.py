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
import numpy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load blocks
import blocks

# load objects
import obj_compound
import obj_peaklist

# load modules
import calculations
import mod_basics
import mod_signal
import mod_peakpicking


# ISOTOPIC PATTERN FUNCTIONS
# --------------------------

def pattern(compound, fwhm=0.1, threshold=0.01, charge=0, agentFormula='H', agentCharge=1, real=True, model='gaussian'):
    """Calculate isotopic pattern for given compound.
        compound (str or mspy.compound) - compound
        fwhm (float) - gaussian peak width
        threshold (float) - relative intensity threshold for isotopes (in %/100)
        charge (int) - charge to be calculated
        agentFormula (str or mspy.compound) - charging agent formula
        agentCharge (int) - charging agent unit charge
        real (bool) - get real peaks from calculated profile
        model (gaussian, lorentzian, gausslorentzian) - peak shape function
    """
    
    # check compound
    if not isinstance(compound, obj_compound.compound):
        compound = obj_compound.compound(compound)
    
    # check agent formula
    if agentFormula != 'e' and not isinstance(agentFormula, obj_compound.compound):
        agentFormula = obj_compound.compound(agentFormula)
    
    # add charging agent to compound
    if charge and agentFormula != 'e':
        formula = compound.formula()
        for atom, count in agentFormula.composition().items():
            formula += '%s%d' % (atom, count*(charge/agentCharge))
        compound = obj_compound.compound(formula)
    
    # get composition and check for negative atom counts
    composition = compound.composition()
    for atom in composition:
        if composition[atom] < 0:
            raise ValueError, 'Pattern cannot be calculated for this formula! --> ' + compound.formula()
    
    # set internal thresholds
    internalThreshold = threshold/100.
    groupingWindow = fwhm/4.
    
    # calculate pattern
    finalPattern = []
    for atom in composition:
        
        # get isotopic profile for current atom or specified isotope only
        atomCount = composition[atom]
        atomPattern = []
        match = mod_basics.ELEMENT_PATTERN.match(atom)
        symbol, massNumber, tmp = match.groups()
        if massNumber:
            isotope = blocks.elements[symbol].isotopes[int(massNumber)]
            atomPattern.append([isotope[0], 1.]) # [mass, abundance]
        else:
            for massNumber, isotope in blocks.elements[atom].isotopes.items():
                if isotope[1] > 0.:
                    atomPattern.append(list(isotope)) # [mass, abundance]
        
        # add atoms
        for i in range(atomCount):
            
            CHECK_FORCE_QUIT()
            
            # if pattern is empty (first atom) add current atom pattern
            if len(finalPattern) == 0:
                finalPattern = _normalize(atomPattern)
                continue
            
            # add atom to each peak of final pattern
            currentPattern = []
            for patternIsotope in finalPattern:
                
                # skip peak under relevant abundance threshold
                if patternIsotope[1] < internalThreshold:
                    continue
                
                # add each isotope of current atom to peak
                for atomIsotope in atomPattern:
                    mass = patternIsotope[0] + atomIsotope[0]
                    abundance = patternIsotope[1] * atomIsotope[1]
                    currentPattern.append([mass, abundance])
            
            # group isotopes and normalize pattern
            finalPattern = _consolidate(currentPattern, groupingWindow)
            finalPattern = _normalize(finalPattern)
    
    # correct charge
    if charge:
        for i in range(len(finalPattern)):
            finalPattern[i][0] = (finalPattern[i][0] - mod_basics.ELECTRON_MASS*charge) / abs(charge)
    
    # group isotopes
    finalPattern = _consolidate(finalPattern, groupingWindow)
    
    # get real peaks from profile
    if real:
        prof = profile(finalPattern, fwhm=fwhm, points=100, model=model)
        finalPattern = []
        for isotope in mod_signal.maxima(prof):
            finalPattern.append(isotope)
            centroid = mod_signal.centroid(prof, isotope[0], isotope[1]*0.99)
            if abs(centroid-isotope[0]) < fwhm/100.:
                finalPattern[-1][0] = centroid
    
    # normalize pattern
    finalPattern = _normalize(finalPattern)
    
    # discard peaks below threshold
    filteredPeaks = []
    for peak in finalPattern:
        if peak[1] >= threshold:
            filteredPeaks.append(list(peak))
    finalPattern = filteredPeaks
    
    return finalPattern
# ----


def gaussian(x, minY, maxY, fwhm=0.1, points=500):
    """Make Gaussian peak.
        mz (float) - peak m/z value
        minY (float) - min y-value
        maxY (float) - max y-value
        fwhm (float) - peak fwhm value
        points (int) - number of points
    """
    
    # make gaussian
    return calculations.signal_gaussian(float(x), float(minY), float(maxY), float(fwhm), int(points))
# ----


def lorentzian(x, minY, maxY, fwhm=0.1, points=500):
    """Make Lorentzian peak.
        mz (float) - peak m/z value
        minY (float) - min y-value
        maxY (float) - max y-value
        fwhm (float) - peak fwhm value
        points (int) - number of points
    """
    
    # make gaussian
    return calculations.signal_lorentzian(float(x), float(minY), float(maxY), float(fwhm), int(points))
# ----


def gausslorentzian(x, minY, maxY, fwhm=0.1, points=500):
    """Make half-Gaussian half-Lorentzian peak.
        mz (float) - peak m/z value
        minY (float) - min y-value
        maxY (float) - max y-value
        fwhm (float) - peak fwhm value
        points (int) - number of points
    """
    
    # make gaussian
    return calculations.signal_gausslorentzian(float(x), float(minY), float(maxY), float(fwhm), int(points))
# ----


def profile(peaklist, fwhm=0.1, points=10, noise=0, raster=None, forceFwhm=False, model='gaussian'):
    """Make profile spectrum for given peaklist.
        peaklist (mspy.peaklist) - peaklist
        fwhm (float) - default peak fwhm
        points (int) - default number of points per peak width (not used if raster is given)
        noise (float) - random noise width
        raster (1D numpy.array) - m/z raster
        forceFwhm (bool) - use default fwhm for all peaks
        model (gaussian, lorentzian, gausslorentzian) - peak shape function
    """
    
    # check peaklist type
    if not isinstance(peaklist, obj_peaklist.peaklist):
        peaklist = obj_peaklist.peaklist(peaklist)
    
    # check raster type
    if raster != None and not isinstance(raster, numpy.ndarray):
        raster = numpy.array(raster)
    
    # get peaks
    peaks = []
    for peak in peaklist:
        peaks.append([peak.mz, peak.intensity, peak.fwhm])
        if forceFwhm or not peak.fwhm:
            peaks[-1][2] = fwhm
    
    # get model
    shape = 0
    if model == 'gaussian':
        shape = 0
    elif model == 'lorentzian':
        shape = 1
    elif model == 'gausslorentzian':
        shape = 2
    
    # make profile
    if raster != None:
        data = calculations.signal_profile_to_raster(numpy.array(peaks), raster, float(noise), shape)
    else:
        data = calculations.signal_profile(numpy.array(peaks), int(points), float(noise), shape)
    
    # make baseline
    baseline = []
    for peak in peaklist:
        if not baseline or baseline[-1][0] != peak.mz:
            baseline.append([peak.mz, -peak.base])
    
    # apply baseline
    data = mod_signal.subbase(data, numpy.array(baseline))
    
    return data
# ----


def matchpattern(signal, pattern, pickingHeight=0.75, baseline=None):
    """Compare signal with given isotopic pattern.
        signal (numpy array) - signal data points
        pattern (list of [mz,intens]) - theoretical pattern to compare
        pickingHeight (float) - centroiding height
        baseline (numpy array) - signal baseline
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError, "Signal must be NumPy array!"
    
   # check baseline type
    if baseline != None and not isinstance(baseline, numpy.ndarray):
        raise TypeError, "Baseline must be NumPy array!"
    
    # check signal data
    if len(signal) == 0:
        return None
    
    # get signal intensites for isotopes
    peaklist = []
    for isotope in pattern:
        peak = mod_peakpicking.labelpeak(
            signal = signal,
            mz = isotope[0],
            pickingHeight = pickingHeight,
            baseline = baseline
        )
        if peak:
            peaklist.append(peak.intensity)
        else:
            peaklist.append(0.0)
        
    # normalize peaklist
    basepeak = max(peaklist)
    if basepeak:
        peaklist = [p/basepeak for p in peaklist]
    else:
        return None
    
    # get rms
    rms = 0
    for x, isotope in enumerate(pattern):
        rms += (isotope[1] - peaklist[x])**2
    if len(pattern) > 1:
        rms = math.sqrt(rms/(len(pattern)-1))
    
    return rms
# ----


def _consolidate(isotopes, window):
    """Group peaks within specified window.
        isotopes: (list of [mass, abundance]) isotopes list
        window: (float) grouping window
    """
    
    if isinstance(isotopes, numpy.ndarray):
        isotopes = isotopes.tolist()
    
    isotopes.sort()
    
    f = (window/1.66)*(window/1.66)
    
    buff = []
    buff.append(isotopes[0])
    
    for current in isotopes[1:]:
        previous = buff[-1]
        if (previous[0] + window) >= current[0]:
            mass = (previous[0]*previous[1] + current[0]*current[1]) / (previous[1] + current[1])
            #ab1 = previous[1] * math.exp( - ((previous[0]-mass)*(previous[0]-mass)) / f )
            #ab2 = current[1] * math.exp( - ((current[0]-mass)*(current[0]-mass)) / f )
            #buff[-1] = [mass, ab1+ab2]
            buff[-1] = [mass, previous[1] + current[1]]
        else:
            buff.append(current)
    
    return buff
# ----


def _normalize(data):
    """Normalize data."""
    
    # get maximum Y
    maximum = data[0][1]
    for item in data:
        if item[1] > maximum:
            maximum = item[1]
    
    # normalize data data
    for x in range(len(data)):
        data[x][1] /= maximum
    
    return data
# ----


