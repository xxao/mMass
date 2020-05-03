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
import copy
import math
import numpy
import time

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load blocks
import blocks

# load objects
import obj_compound
import obj_peak
import obj_peaklist

# load modules
import mod_basics
import mod_signal


# BASIC CONSTANTS
# ---------------

ISOTOPE_DISTANCE = 1.00287
AVERAGE_AMINO = {'C':4.9384, 'H':7.7583, 'N':1.3577, 'O':1.4773, 'S':0.0417}
AVERAGE_BASE = {'C':9.75, 'H':12.25, 'N':3.75, 'O':6, 'P':1}


# PEAK PICKING FUNCTIONS
# ----------------------

def labelpoint(signal, mz, baseline=None):
    """Return labeled peak at given x-value.
        signal (numpy array) - signal data points
        mz (float) - x-value to label
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
    
    # check m/z value
    if mz <= 0:
        return None
    
    # get peak intensity
    ai = mod_signal.intensity(signal, mz)
    if not ai:
        return None
    
    # get peak baseline and s/n
    base = 0.0
    sn = None
    if baseline == None:
        base, noise = mod_signal.noise(signal, x=mz)
        if noise:
            sn = (ai - base) / noise
    else:
        idx = mod_signal.locate(baseline, mz)
        if (idx > 0) and (idx < len(baseline)):
            base = mod_signal.interpolate( (baseline[idx-1][0], baseline[idx-1][1]), (baseline[idx][0], baseline[idx][1]), x=mz)
            noise = mod_signal.interpolate( (baseline[idx-1][0], baseline[idx-1][2]), (baseline[idx][0], baseline[idx][2]), x=mz)
            if noise:
                sn = (ai - base) / noise
    
    # check peak intensity
    if ai <= base:
        return None
    
    # get peak fwhm
    height = base + (ai - base) * 0.5
    fwhm = mod_signal.width(signal, mz, height)
    
    # make peak object
    peak = obj_peak.peak(mz=mz, ai=ai, base=base, sn=sn, fwhm=fwhm)
    
    return peak
# ----


def labelpeak(signal, mz=None, minX=None, maxX=None, pickingHeight=0.75, baseline=None):
    """Return labeled peak in given m/z range.
        signal (numpy array) - signal data points
        mz (float) - x-value to label
        minX (float) - x-range start
        maxX (float) - x-range end
        pickingHeight (float) - centroiding height
        baseline (numpy array) - signal baseline
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError, "Signal must be NumPy array!"
    
   # check baseline type
    if baseline != None and not isinstance(baseline, numpy.ndarray):
        raise TypeError, "Baseline must be NumPy array!"
    
    # check m/z value or range
    if mz == None and minX == None and maxX == None:
        raise TypeError, "m/z value or range must be specified!"
    
    # check signal data
    if len(signal) == 0:
        return None
    
    # check m/z value
    if mz != None:
        minX = mz
    if minX <= 0:
        return False
    
    # get index of given m/z or range maximum
    if mz != None:
        imax = mod_signal.locate(signal, mz)
    else:
        i1 = mod_signal.locate(signal, minX)
        i2 = mod_signal.locate(signal, maxX)
        imax = i1
        if i1 != i2:
            imax += mod_signal.basepeak(signal[i1:i2])
    if (imax == 0) or (imax == len(signal)):
        return None
    
    # get centroid height
    h = signal[imax][1] * pickingHeight
    if baseline != None:
        idx = mod_signal.locate(baseline, signal[imax][0])
        if (idx > 0) and (idx < len(baseline)):
            base = mod_signal.interpolate( (baseline[idx-1][0], baseline[idx-1][1]), (baseline[idx][0], baseline[idx][1]), x=signal[imax][0])
            h = ((signal[imax][1] - base) * pickingHeight) + base
    
    # get centroid
    ileft = imax-1
    while (ileft > 0) and (signal[ileft][1] > h):
        ileft -= 1
    
    iright = imax
    while (iright < len(signal)-1) and (signal[iright][1] > h):
        iright += 1
    
    leftMZ = mod_signal.interpolate(signal[ileft], signal[ileft+1], y=h)
    rightMZ = mod_signal.interpolate(signal[iright-1], signal[iright], y=h)
    
    # check range
    if mz == None and (leftMZ < minX or rightMZ > maxX) and (leftMZ != rightMZ):
        return None
    
    # label peak in the newly found selection
    if mz != None and leftMZ != rightMZ:
        peak = labelpeak(
            signal = signal,
            minX = leftMZ,
            maxX = rightMZ,
            pickingHeight = pickingHeight,
            baseline = baseline
        )
    
    # label current point
    else:
        peak = labelpoint(
            signal = signal,
            mz = ((leftMZ + rightMZ)/2.),
            baseline = baseline
        )
    
    return peak
# ----


def labelscan(signal, minX=None, maxX=None, pickingHeight=0.75, absThreshold=0., relThreshold=0., snThreshold=0., baseline=None):
    """Return centroided peaklist for given data points.
        signal (numpy array) - signal data points
        minX (float) - x-range start
        maxX (float) - x-range end
        pickingHeight (float) - centroiding height
        absThreshold (float) - absolute intensity threshold
        relThreshold (float) - relative intensity threshold
        snThreshold (float) - signal to noise threshold
        baseline (numpy array) - signal baseline
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError, "Signal must be NumPy array!"
    
   # check baseline type
    if baseline != None and not isinstance(baseline, numpy.ndarray):
        raise TypeError, "Baseline must be NumPy array!"
    
    # crop data
    if minX != None and maxX != None:
        i1 = mod_signal.locate(signal, minX)
        i2 = mod_signal.locate(signal, maxX)
        signal = signal[i1:i2]
    
    # check data points
    if len(signal) == 0:
        return obj_peaklist.peaklist([])
    
    # get local maxima
    buff = []
    basepeak = mod_signal.basepeak(signal)
    threshold = max(signal[basepeak][1] * relThreshold, absThreshold)
    for peak in mod_signal.maxima(signal):
        if peak[1] >= threshold:
            buff.append( [peak[0], peak[1], 0., None, None] ) # mz, ai, base, sn, fwhm
    
    CHECK_FORCE_QUIT()
    
    # get peaks baseline and s/n
    basepeak = 0.0
    if baseline != None:
        for peak in buff:
            idx = mod_signal.locate(baseline, peak[0])
            if (idx > 0) and (idx < len(baseline)):
                p1 = baseline[idx-1]
                p2 = baseline[idx]
                peak[2] = mod_signal.interpolate( (p1[0], p1[1]), (p2[0], p2[1]), x=peak[0])
                noise = mod_signal.interpolate( (p1[0], p1[2]), (p2[0], p2[2]), x=peak[0])
                intens = peak[1] - peak[2]
                if noise:
                    peak[3] = intens / noise
                if intens > basepeak:
                    basepeak = intens
    
    CHECK_FORCE_QUIT()
    
    # remove peaks bellow threshold
    threshold = max(basepeak * relThreshold, absThreshold)
    candidates = []
    for peak in buff:
        if peak[0] > 0 and (peak[1] - peak[2]) >= threshold and (not peak[3] or peak[3] >= snThreshold):
            candidates.append(peak)
    
    # make centroides
    if pickingHeight < 1.:
        buff = []
        previous = None
        for peak in candidates:
            
            CHECK_FORCE_QUIT()
            
            # calc peak height
            h = ((peak[1]-peak[2]) * pickingHeight) + peak[2]
            
            # get centroid indexes
            idx = mod_signal.locate(signal, peak[0])
            if (idx == 0) or (idx == len(signal)):
                continue
            
            ileft = idx-1
            while (ileft > 0) and (signal[ileft][1] > h):
                ileft -= 1
            
            iright = idx
            while (iright < len(signal)-1) and (signal[iright][1] > h):
                iright += 1
            
            # calculate peak mz
            leftMZ = mod_signal.interpolate(signal[ileft], signal[ileft+1], y=h)
            rightMZ = mod_signal.interpolate(signal[iright-1], signal[iright], y=h)
            peak[0] = (leftMZ + rightMZ)/2.
            
            # get peak intensity
            intens = mod_signal.intensity(signal, peak[0])
            if intens and intens <= peak[1]:
                peak[1] = intens
            else:
                continue
            
            # try to group with previous peak
            if previous != None and leftMZ < previous:
                if peak[1] > buff[-1][1]:
                    buff[-1] = peak
                    previous = rightMZ
            else:
                buff.append(peak)
                previous = rightMZ
        
        # store as candidates
        candidates = buff
    
    CHECK_FORCE_QUIT()
    
    # get peaks baseline and s/n
    basepeak = 0.0
    if baseline != None:
        for peak in candidates:
            idx = mod_signal.locate(baseline, peak[0])
            if (idx > 0) and (idx < len(baseline)):
                p1 = baseline[idx-1]
                p2 = baseline[idx]
                peak[2] = mod_signal.interpolate( (p1[0], p1[1]), (p2[0], p2[1]), x=peak[0])
                noise = mod_signal.interpolate( (p1[0], p1[2]), (p2[0], p2[2]), x=peak[0])
                intens = peak[1] - peak[2]
                if noise:
                    peak[3] = intens / noise
                if intens > basepeak:
                    basepeak = intens
    
    CHECK_FORCE_QUIT()
    
    # remove peaks bellow threshold and calculate fwhm
    threshold = max(basepeak * relThreshold, absThreshold)
    centroides = []
    for peak in candidates:
        if peak[0] > 0 and (peak[1] - peak[2]) >= threshold and (not peak[3] or peak[3] >= snThreshold):
            peak[4] = mod_signal.width(signal, peak[0], (peak[2] + ((peak[1] - peak[2]) * 0.5)))
            centroides.append(obj_peak.peak(mz=peak[0], ai=peak[1], base=peak[2], sn=peak[3], fwhm=peak[4]))
    
    # return peaklist object
    return obj_peaklist.peaklist(centroides)
# ----


def envcentroid(isotopes, pickingHeight=0.5, intensity='maximum'):
    """Calculate envelope centroid for given isotopes.
        isotopes (mspy.peaklist or list of mspy.peak) envelope isotopes
        pickingHeight (float) - centroiding height
        intensity (maximum | sum | average) envelope intensity type
    """
    
    # check isotopes
    if len(isotopes) == 0:
        return None
    elif len(isotopes) == 1:
        return isotopes[0]
    
    # check peaklist object
    if not isinstance(isotopes, obj_peaklist.peaklist):
        isotopes = obj_peaklist.peaklist(isotopes)
    
    # get sums
    sumMZ = 0.
    sumIntensity = 0.
    for isotope in isotopes:
        sumMZ += isotope.mz * isotope.intensity
        sumIntensity += isotope.intensity
    
    # get average m/z
    mz = sumMZ / sumIntensity
    
    # get ai, base and sn
    base = isotopes.basepeak.base
    sn = isotopes.basepeak.sn
    fwhm = isotopes.basepeak.fwhm
    if intensity == 'sum':
        ai = base + sumIntensity
    elif intensity == 'average':
        ai = base + sumIntensity / len(isotopes)
    else:
        ai = isotopes.basepeak.ai
    if isotopes.basepeak.sn:
        sn = (ai - base) * isotopes.basepeak.sn / (isotopes.basepeak.ai - base)
    
    # get envelope width
    minInt = isotopes.basepeak.intensity * pickingHeight
    i1 = None
    i2 = None
    for x, isotope in enumerate(isotopes):
        if isotope.intensity >= minInt:
            i2 = x
            if i1 == None:
                i1 = x
    
    mz1 = isotopes[i1].mz
    mz2 = isotopes[i2].mz
    if i1 != 0:
        mz1 = mod_signal.interpolate((isotopes[i1-1].mz, isotopes[i1-1].ai), (isotopes[i1].mz, isotopes[i1].ai), y=minInt)
    if i2 < len(isotopes)-1:
        mz2 = mod_signal.interpolate((isotopes[i2].mz, isotopes[i2].ai), (isotopes[i2+1].mz, isotopes[i2+1].ai), y=minInt)
    if mz1 != mz2:
        fwhm = abs(mz2 - mz1)
    
    # make peak
    peak = obj_peak.peak(mz=mz, ai=ai, base=base, sn=sn, fwhm=fwhm)
    
    return peak
# ----


def envmono(isotopes, charge, intensity='maximum'):
    """Calculate envelope centroid for given isotopes.
        isotopes (mspy.peaklist or list of mspy.peak) - envelope isotopes
        charge (int) - peak charge
        intensity (maximum | sum | average) - envelope intensity type
    """
    
    # check isotopes
    if len(isotopes) == 0:
        return None
    
    # check peaklist object
    if not isinstance(isotopes, obj_peaklist.peaklist):
        isotopes = obj_peaklist.peaklist(isotopes)
    
    # calc averagine
    avFormula = averagine(isotopes.basepeak.mz, charge=charge, composition=AVERAGE_AMINO)
    avPattern = avFormula.pattern(fwhm=0.1, threshold=0.001, charge=charge)
    avPattern = obj_peaklist.peaklist(avPattern)
    
    # get envelope centroid
    points = numpy.array([(p.mz, p.intensity) for p in isotopes])
    centroid = labelpeak(points, mz=isotopes.basepeak.mz, pickingHeight=0.8)
    if not centroid:
        centroid = isotopes.basepeak
    
    # get averagine centroid
    points = numpy.array([(p.mz, p.intensity) for p in avPattern])
    avCentroid = labelpeak(points, mz=avPattern.basepeak.mz, pickingHeight=0.8)
    if not avCentroid:
        avCentroid = avPattern.basepeak
    
    # align profiles and get monoisotopic mass
    shift = centroid.mz - avCentroid.mz
    errors = [(abs(p.mz - avPattern.basepeak.mz - shift), p.mz) for p in isotopes]
    mz = min(errors)[1] - (avPattern.basepeak.mz - avFormula.mz(charge)[0])
    
    # sum intensities
    sumIntensity = 0
    for isotope in isotopes:
        sumIntensity += isotope.intensity
    
    # get ai, base and sn
    base = isotopes.basepeak.base
    sn = isotopes.basepeak.sn
    fwhm = isotopes.basepeak.fwhm
    if intensity == 'sum':
        ai = base + sumIntensity
    elif intensity == 'average':
        ai = base + sumIntensity / len(isotopes)
    else:
        ai = isotopes.basepeak.ai
    if isotopes.basepeak.sn:
        sn = (ai - base) * isotopes.basepeak.sn / (isotopes.basepeak.ai - base)
    
    # make peak
    peak = obj_peak.peak(mz=mz, ai=ai, base=base, sn=sn, fwhm=fwhm, isotope=0)
    
    return peak
# ----


def deisotope(peaklist, maxCharge=1, mzTolerance=0.15, intTolerance=0.5, isotopeShift=0.0):
    """Isotopes determination and calculation of peaks charge.
        peaklist (mspy.peaklist) - peaklist to process
        maxCharge (float) - max charge to be searched
        mzTolerance (float) - absolute m/z tolerance for isotopes distance
        intTolerance (float) - relative intensity tolerance for isotopes and model (in %/100)
        isotopeShift (float) - isotope distance correction (neutral mass) (for HDX etc.)
    """
    
    # check peaklist
    if not isinstance(peaklist, obj_peaklist.peaklist):
        raise TypeError, "Peak list must be mspy.peaklist object!"
    
    # clear previous results
    for peak in peaklist:
        peak.setcharge(None)
        peak.setisotope(None)
    
    # get charges
    if maxCharge < 0:
        charges = [-x for x in range(1, abs(maxCharge)+1)]
    else:
        charges = [x for x in range(1, maxCharge+1)]
    charges.reverse()
    
    # walk in a peaklist
    maxIndex = len(peaklist)
    for x, parent in enumerate(peaklist):
        
        CHECK_FORCE_QUIT()
        
        # skip assigned peaks
        if parent.isotope != None:
            continue
        
        # try all charge states
        for z in charges:
            cluster = [parent]
            
            # search for next isotope within m/z tolerance
            difference = (ISOTOPE_DISTANCE + isotopeShift)/abs(z)
            y = 1
            while x+y < maxIndex:
                mzError = (peaklist[x+y].mz - cluster[-1].mz - difference)
                if abs(mzError) <= mzTolerance:
                    cluster.append(peaklist[x+y])
                elif mzError > mzTolerance:
                    break
                y += 1
            
            # no isotope found
            if len(cluster) == 1:
                continue
            
            # get theoretical isotopic pattern
            mass = min(15000, int( mod_basics.mz( parent.mz, 0, z))) / 200
            pattern = patternLookupTable[mass]
            
            # check minimal number of isotopes in the cluster
            limit = 0
            for p in pattern:
                if p >= 0.33:
                    limit += 1
            if len(cluster) < limit and abs(z) > 1:
                continue
            
            # check peak intensities in cluster
            valid = True
            isotope = 1
            limit = min(len(pattern), len(cluster))
            while (isotope < limit):
                
                # calc theoretical intensity from previous peak and current error
                intTheoretical = (cluster[isotope-1].intensity / pattern[isotope-1]) * pattern[isotope]
                intError = cluster[isotope].intensity - intTheoretical
                
                # intensity in tolerance
                if abs(intError) <= (intTheoretical * intTolerance):
                    cluster[isotope].setisotope(isotope)
                    cluster[isotope].setcharge(z)
                
                # intensity is higher (overlap)
                elif intError > 0:
                    pass
                
                # intensity is lower and first isotope is checked (nonsense)
                elif (intError < 0 and isotope == 1):
                    valid = False
                    break
                
                # try next peak
                isotope += 1
            
            # cluster is OK, set parent peak and skip other charges
            if valid:
                parent.setisotope(0)
                parent.setcharge(z)
                break
# ----


def deconvolute(peaklist, massType=0):
    """Recalculate peaklist to singly charged.
        peaklist (mspy.peaklist) - peak list to deconvolute
        massType (0 or 1) - mass type used for m/z re-calculation, 0 = monoisotopic, 1 = average
    """
    
    # recalculate peaks
    buff = []
    for peak in copy.deepcopy(peaklist):
        
        CHECK_FORCE_QUIT()
        
        # uncharged peak
        if not peak.charge:
            continue
        
        # charge is correct
        elif abs(peak.charge) == 1:
            buff.append(peak)
        
        # recalculate peak
        else:
            
            # set fwhm
            if peak.fwhm:
                newFwhm = abs(peak.fwhm*peak.charge)
                peak.setfwhm(newFwhm)
            
            # set m/z and charge
            if peak.charge < 0:
                newMz = mod_basics.mz(mass=peak.mz, charge=-1, currentCharge=peak.charge, massType=massType)
                peak.setmz(newMz)
                peak.setcharge(-1)
            else:
                newMz = mod_basics.mz(mass=peak.mz, charge=1, currentCharge=peak.charge, massType=massType)
                peak.setmz(newMz)
                peak.setcharge(1)
            
            # store peak
            buff.append(peak)
    
    # remove baseline
    if buff:
        for peak in buff:
            peak.setsn(None)
            peak.setai(peak.intensity)
            peak.setbase(0.)
    
    # update peaklist
    peaklist = obj_peaklist.peaklist(buff)
    
    return peaklist
# ----



# PATTERN LOOKUP TABLE
# --------------------

def averagine(mz, charge=0, composition=AVERAGE_AMINO):
    """Calculate average formula for given mass and building block composition.
        mz (float) - peak m/z
        charge (int) - peak charge
        composition (dict) - building block composition
    """
    
    # get average mass of block
    blockMass = 0.
    for element in composition:
        blockMass += blocks.elements[element].mass[1] * composition[element]
    
    # get block count
    neutralMass = mod_basics.mz(mz, charge=0, currentCharge=charge, massType=1)
    count = max(1, neutralMass / blockMass)
    
    # make formula
    formula = ''
    for element in composition:
        formula += '%s%d' % (element, int(composition[element]*count))
    formula = obj_compound.compound(formula)
    
    # add some hydrogens to reach the mass
    hydrogens = int(round((neutralMass - formula.mass(1)) / blocks.elements['H'].mass[1]))
    hydrogens = max(hydrogens, -1*formula.count('H'))
    formula += 'H%d' % hydrogens
    
    return formula
# ----


def _gentable(highmass, step=200, composition=AVERAGE_AMINO, table='tuple'):
    """Print pattern lookup table."""
    
    for mass in range(0, highmass, step):
        formula = averagine(mass, charge=0, composition=composition)
        
        pattern = ''
        for mz, abundance in formula.pattern(fwhm=0.1, threshold=0.001):
            pattern += '%.3f, ' % abundance
        
        if table == 'tuple':
            print '(%s), #%d' % (pattern[:-2], mass)
        elif table == 'dict':
            print '%d: (%s),' % (mass, pattern[:-2])
# ----


# pattern lookup table for amino building block
patternLookupTable = (
    (1.000, 0.059, 0.003), #0
    (1.000, 0.122, 0.013), #200
    (1.000, 0.241, 0.040, 0.005), #400
    (1.000, 0.303, 0.059, 0.008), #600
    (1.000, 0.426, 0.109, 0.020, 0.003), #800
    (1.000, 0.533, 0.166, 0.038, 0.006), #1000
    (1.000, 0.655, 0.244, 0.066, 0.014, 0.002), #1200
    (1.000, 0.786, 0.388, 0.143, 0.042, 0.009, 0.001), #1400
    (1.000, 0.845, 0.441, 0.171, 0.053, 0.013, 0.002), #1600
    (1.000, 0.967, 0.557, 0.236, 0.080, 0.021, 0.005), #1800
    (0.921, 1.000, 0.630, 0.291, 0.107, 0.032, 0.007, 0.001), #2000
    (0.828, 1.000, 0.687, 0.343, 0.136, 0.044, 0.011, 0.002), #2200
    (0.752, 1.000, 0.744, 0.400, 0.171, 0.060, 0.017, 0.004), #2400
    (0.720, 1.000, 0.772, 0.428, 0.188, 0.068, 0.020, 0.005), #2600
    (0.667, 1.000, 0.825, 0.487, 0.228, 0.088, 0.028, 0.007), #2800
    (0.616, 1.000, 0.884, 0.556, 0.276, 0.113, 0.039, 0.010, 0.002), #3000
    (0.574, 1.000, 0.941, 0.628, 0.330, 0.143, 0.052, 0.015, 0.003), #3200
    (0.536, 0.999, 1.000, 0.706, 0.392, 0.179, 0.069, 0.022, 0.005), #3400
    (0.506, 0.972, 1.000, 0.725, 0.412, 0.193, 0.077, 0.025, 0.006), #3600
    (0.449, 0.919, 1.000, 0.764, 0.457, 0.226, 0.094, 0.033, 0.009, 0.001), #3800
    (0.392, 0.853, 1.000, 0.831, 0.543, 0.295, 0.136, 0.053, 0.017, 0.004), #4000
    (0.353, 0.812, 1.000, 0.869, 0.593, 0.336, 0.162, 0.067, 0.023, 0.006), #4200
    (0.321, 0.776, 1.000, 0.907, 0.644, 0.379, 0.190, 0.082, 0.030, 0.009), #4400
    (0.308, 0.760, 1.000, 0.924, 0.669, 0.401, 0.205, 0.090, 0.033, 0.011, 0.001), #4600
    (0.282, 0.729, 1.000, 0.962, 0.723, 0.451, 0.239, 0.110, 0.042, 0.014, 0.003), #4800
    (0.258, 0.699, 1.000, 1.000, 0.780, 0.504, 0.277, 0.132, 0.053, 0.018, 0.004), #5000
    (0.228, 0.645, 0.962, 1.000, 0.809, 0.542, 0.308, 0.153, 0.065, 0.023, 0.007), #5200
    (0.203, 0.598, 0.927, 1.000, 0.839, 0.581, 0.343, 0.176, 0.078, 0.029, 0.010), #5400
    (0.192, 0.577, 0.911, 1.000, 0.854, 0.602, 0.361, 0.189, 0.086, 0.033, 0.011), #5600
    (0.171, 0.536, 0.880, 1.000, 0.884, 0.644, 0.399, 0.216, 0.102, 0.040, 0.014, 0.003), #5800
    (0.154, 0.501, 0.851, 1.000, 0.912, 0.686, 0.439, 0.244, 0.120, 0.050, 0.018, 0.004), #6000
    (0.139, 0.468, 0.823, 1.000, 0.942, 0.730, 0.482, 0.278, 0.141, 0.062, 0.023, 0.007), #6200
    (0.126, 0.441, 0.799, 1.000, 0.969, 0.772, 0.524, 0.310, 0.162, 0.073, 0.028, 0.009), #6400
    (0.121, 0.427, 0.787, 1.000, 0.983, 0.794, 0.547, 0.328, 0.174, 0.080, 0.031, 0.011), #6600
    (0.104, 0.381, 0.732, 0.971, 1.000, 0.848, 0.614, 0.390, 0.219, 0.109, 0.045, 0.016, 0.004), #6800
    (0.092, 0.349, 0.691, 0.944, 1.000, 0.872, 0.648, 0.422, 0.244, 0.125, 0.054, 0.020, 0.006), #7000
    (0.082, 0.321, 0.654, 0.919, 1.000, 0.894, 0.682, 0.456, 0.270, 0.143, 0.063, 0.024, 0.008), #7200
    (0.073, 0.296, 0.620, 0.895, 1.000, 0.917, 0.718, 0.492, 0.299, 0.162, 0.077, 0.030, 0.011), #7400
    (0.069, 0.284, 0.604, 0.884, 1.000, 0.929, 0.735, 0.509, 0.313, 0.172, 0.084, 0.033, 0.012), #7600
    (0.062, 0.262, 0.573, 0.861, 1.000, 0.952, 0.772, 0.548, 0.345, 0.195, 0.098, 0.040, 0.015, 0.003), #7800
    (0.056, 0.243, 0.544, 0.839, 1.000, 0.976, 0.811, 0.589, 0.380, 0.220, 0.114, 0.049, 0.019, 0.005), #8000
    (0.051, 0.227, 0.521, 0.821, 1.000, 0.997, 0.846, 0.628, 0.413, 0.244, 0.130, 0.058, 0.022, 0.007), #8200
    (0.045, 0.206, 0.486, 0.786, 0.980, 1.000, 0.869, 0.660, 0.444, 0.268, 0.147, 0.070, 0.027, 0.010), #8400
    (0.042, 0.196, 0.468, 0.767, 0.968, 1.000, 0.879, 0.676, 0.460, 0.281, 0.156, 0.075, 0.030, 0.011), #8600
    (0.038, 0.179, 0.437, 0.733, 0.947, 1.000, 0.899, 0.705, 0.491, 0.307, 0.173, 0.086, 0.036, 0.013, 0.002), #8800
    (0.033, 0.163, 0.408, 0.701, 0.926, 1.000, 0.919, 0.736, 0.524, 0.335, 0.193, 0.099, 0.043, 0.016, 0.004), #9000
    (0.030, 0.149, 0.382, 0.670, 0.906, 1.000, 0.938, 0.768, 0.558, 0.364, 0.215, 0.113, 0.051, 0.020, 0.006), #9200
    (0.026, 0.132, 0.348, 0.629, 0.877, 1.000, 0.971, 0.823, 0.620, 0.420, 0.258, 0.143, 0.069, 0.028, 0.010), #9400
    (0.024, 0.126, 0.337, 0.616, 0.868, 1.000, 0.981, 0.839, 0.638, 0.437, 0.271, 0.153, 0.074, 0.031, 0.011), #9600
    (0.022, 0.116, 0.317, 0.592, 0.851, 1.000, 1.000, 0.872, 0.676, 0.472, 0.298, 0.172, 0.087, 0.037, 0.014, 0.002), #9800
    (0.020, 0.106, 0.294, 0.561, 0.822, 0.983, 1.000, 0.888, 0.700, 0.498, 0.320, 0.188, 0.099, 0.043, 0.017, 0.004), #10000
    (0.017, 0.096, 0.272, 0.529, 0.790, 0.965, 1.000, 0.905, 0.727, 0.526, 0.346, 0.207, 0.113, 0.050, 0.020, 0.006), #10200
    (0.015, 0.087, 0.251, 0.499, 0.761, 0.946, 1.000, 0.922, 0.755, 0.556, 0.373, 0.227, 0.126, 0.061, 0.024, 0.008), #10400
    (0.014, 0.083, 0.242, 0.486, 0.747, 0.937, 1.000, 0.930, 0.768, 0.570, 0.385, 0.237, 0.134, 0.065, 0.026, 0.009), #10600
    (0.013, 0.075, 0.225, 0.459, 0.720, 0.920, 1.000, 0.947, 0.796, 0.602, 0.415, 0.260, 0.149, 0.075, 0.032, 0.012, 0.001), #10800
    (0.012, 0.069, 0.208, 0.435, 0.695, 0.904, 1.000, 0.963, 0.824, 0.633, 0.443, 0.284, 0.165, 0.085, 0.037, 0.015, 0.002), #11000
    (0.010, 0.063, 0.194, 0.412, 0.669, 0.888, 1.000, 0.980, 0.852, 0.667, 0.475, 0.309, 0.184, 0.098, 0.044, 0.018, 0.005), #11200
    (0.009, 0.057, 0.180, 0.391, 0.646, 0.872, 1.000, 0.997, 0.882, 0.702, 0.509, 0.336, 0.204, 0.113, 0.052, 0.021, 0.006), #11400
    (0.009, 0.054, 0.173, 0.379, 0.631, 0.861, 0.995, 1.000, 0.892, 0.717, 0.523, 0.350, 0.214, 0.119, 0.057, 0.023, 0.008), #11600
    (0.008, 0.049, 0.160, 0.355, 0.602, 0.834, 0.980, 1.000, 0.906, 0.739, 0.548, 0.373, 0.231, 0.132, 0.066, 0.026, 0.010), #11800
    (0.007, 0.042, 0.141, 0.321, 0.557, 0.791, 0.953, 1.000, 0.931, 0.781, 0.596, 0.417, 0.268, 0.158, 0.082, 0.037, 0.014, 0.002), #12000
    (0.006, 0.038, 0.130, 0.301, 0.531, 0.767, 0.939, 1.000, 0.945, 0.805, 0.624, 0.443, 0.289, 0.174, 0.093, 0.043, 0.017, 0.004), #12200
    (0.005, 0.035, 0.120, 0.283, 0.507, 0.744, 0.925, 1.000, 0.960, 0.830, 0.653, 0.470, 0.312, 0.191, 0.106, 0.051, 0.020, 0.006), #12400
    (0.005, 0.033, 0.115, 0.274, 0.495, 0.732, 0.918, 1.000, 0.967, 0.842, 0.668, 0.485, 0.324, 0.200, 0.112, 0.054, 0.023, 0.007), #12600
    (0.004, 0.030, 0.107, 0.257, 0.472, 0.710, 0.904, 1.000, 0.982, 0.868, 0.699, 0.515, 0.351, 0.219, 0.126, 0.063, 0.027, 0.010), #12800
    (0.004, 0.027, 0.098, 0.242, 0.450, 0.689, 0.890, 1.000, 0.997, 0.894, 0.731, 0.547, 0.378, 0.241, 0.141, 0.072, 0.032, 0.012, 0.002), #13000
    (0.003, 0.025, 0.090, 0.224, 0.426, 0.661, 0.867, 0.989, 1.000, 0.911, 0.756, 0.574, 0.402, 0.260, 0.155, 0.082, 0.037, 0.014, 0.003), #13200
    (0.003, 0.022, 0.082, 0.208, 0.402, 0.633, 0.843, 0.975, 1.000, 0.925, 0.777, 0.598, 0.425, 0.279, 0.169, 0.092, 0.043, 0.017, 0.005), #13400
    (0.003, 0.021, 0.079, 0.202, 0.392, 0.621, 0.833, 0.969, 1.000, 0.930, 0.786, 0.609, 0.435, 0.288, 0.176, 0.097, 0.046, 0.018, 0.006), #13600
    (0.003, 0.019, 0.073, 0.188, 0.370, 0.595, 0.810, 0.955, 1.000, 0.943, 0.808, 0.634, 0.460, 0.309, 0.191, 0.108, 0.053, 0.022, 0.007), #13800
    (0.002, 0.017, 0.067, 0.175, 0.350, 0.570, 0.787, 0.942, 1.000, 0.956, 0.831, 0.662, 0.487, 0.331, 0.209, 0.121, 0.062, 0.026, 0.010), #14000
    (0.002, 0.016, 0.061, 0.163, 0.330, 0.547, 0.765, 0.929, 1.000, 0.968, 0.855, 0.690, 0.515, 0.356, 0.227, 0.135, 0.070, 0.031, 0.012, 0.002), #14200
    (0.002, 0.014, 0.056, 0.151, 0.312, 0.524, 0.743, 0.916, 1.000, 0.982, 0.878, 0.718, 0.544, 0.382, 0.247, 0.149, 0.079, 0.037, 0.014, 0.003), #14400
    (0.002, 0.013, 0.054, 0.146, 0.304, 0.514, 0.733, 0.909, 1.000, 0.989, 0.890, 0.733, 0.559, 0.395, 0.257, 0.156, 0.084, 0.039, 0.016, 0.004), #14600
    (0.001, 0.012, 0.047, 0.131, 0.276, 0.478, 0.697, 0.881, 0.989, 1.000, 0.920, 0.777, 0.605, 0.437, 0.292, 0.182, 0.102, 0.051, 0.022, 0.007), #14800
    (0.001, 0.010, 0.043, 0.121, 0.259, 0.454, 0.671, 0.859, 0.977, 1.000, 0.932, 0.797, 0.629, 0.460, 0.312, 0.197, 0.114, 0.058, 0.025, 0.008, 0.001), #15000
)
