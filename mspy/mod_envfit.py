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
from numpy.linalg import solve as solveLinEq

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_compound
import obj_peaklist

# load modules
import mod_pattern
import mod_signal
import mod_peakpicking
import mod_calibration


# ENVELOPE FIT
# ------------

class envfit():
    """Fit modeled profiles with exchanged atoms to acquired data."""
    
    def __init__(self, formula, charge, scales, loss='H', gain='H{2}', peakShape='gaussian'):
        
        loss = obj_compound.compound(loss)
        loss.negate()
        self._lossFormula = loss.formula()
        self._gainFormula = gain
        
        self.formula = formula
        self.charge = charge
        self.fwhm = 0.1
        self.peakShape = peakShape
        self.mzrange = [0.0, float('inf')]
        
        self.spectrum = []
        self.data = []
        self.model = []
        self.models = {}
        
        self.composition = None
        self.ncomposition = None
        self.average = None
        
        self._initModels(scales)
        self._initRange()
    # ----
    
    
    def tospectrum(self, signal, fwhm=0.1, forceFwhm=True, autoAlign=True, iterLimit=None, relThreshold=0., pickingHeight=0.90, baseline=None):
        """Fit modeled profiles to spectrum using tmp peaklist.
            signal (numpy array) - m/z / intensity pairs
            fwhm (float) - defaut fwhm
            forceFwhm (bool) - use default fwhm
            autoAlign (bool) - automatic m/z shift
            iterLimit (int) - maximum number of iterations
            pickingHeight (float) - peak picking height for centroiding
            relThreshold (float) - relative intensity threshold
            baseline (numpy array) - signal baseline
        """
        
        # crop signal to relevant m/z range
        i1 = mod_signal.locate(signal, self.mzrange[0])
        i2 = mod_signal.locate(signal, self.mzrange[1])
        signal = signal[i1:i2]
        
        # get peaklist from signal
        peaklist = mod_peakpicking.labelscan(
            signal = signal,
            pickingHeight = pickingHeight,
            relThreshold = relThreshold,
            baseline = baseline
        )
        
        # remove shoulder peaks
        peaklist.remshoulders(fwhm=fwhm)
        
        # correct signal baseline
        if baseline != None:
            self.spectrum = mod_signal.subbase(signal, baseline)
        
        # fit to peaklist
        return self.topeaklist(
            peaklist = peaklist,
            fwhm = fwhm,
            forceFwhm = forceFwhm,
            autoAlign = autoAlign,
            iterLimit = iterLimit,
            relThreshold = relThreshold,
        )
    # ----
    
    
    def topeaklist(self, peaklist, fwhm=0.1, forceFwhm=True, autoAlign=True, iterLimit=None, relThreshold=0.):
        """Fit modeled profiles to peaklist.
            peaklist (mspy.peaklist) - peak list
            fwhm (float) - defaut fwhm
            forceFwhm (bool) - use default fwhm
            autoAlign (bool) - automatic m/z shift
            iterLimit (int) - maximum number of iterations
        """
        
        # check peaklist object
        if not isinstance(peaklist, obj_peaklist.peaklist):
            peaklist = obj_peaklist.peaklist(peaklist)
        
        # crop peaklist to relevant m/z range
        peaklist = peaklist.duplicate()
        peaklist.crop(self.mzrange[0], self.mzrange[1])
        
        # remove peaks below threshold
        peaklist.remthreshold(relThreshold=relThreshold)
        
        # get fwhm from basepeak
        if not forceFwhm and peaklist.basepeak and peaklist.basepeak.fwhm:
            fwhm = peaklist.basepeak.fwhm
        
        # make data to fit
        points = numpy.array([(p.mz, p.intensity) for p in peaklist])
        
        # fit
        return self.topoints(
            points = points,
            fwhm = fwhm,
            autoAlign = autoAlign,
            iterLimit = iterLimit,
        )
    # ----
    
    
    def topoints(self, points, fwhm=0.1, autoAlign=True, iterLimit=None):
        """Fit modeled profiles to given points.
            points (numpy array or list) - m/z / intensity pairs
            fwhm (float) - defaut fwhm
            autoAlign (bool) - automatic m/z shift
            iterLimit (int) - maximum number of iterations
        """
        
        self.fwhm = fwhm
        
        # reset previous results
        self.composition = {}
        self.ncomposition = {}
        self.average = 0.
        self.model = numpy.array([])
        for x in self.models:
            self.models[x][2] = 0.0 # abs comp
            self.models[x][3] = 0.0 # rel comp
        
        # check points type
        if not isinstance(points, numpy.ndarray):
            points = numpy.array(points)
        
        # crop points to relevant m/z range
        i1 = mod_signal.locate(points, self.mzrange[0])
        i2 = mod_signal.locate(points, self.mzrange[1])
        self.data = numpy.array(points[i1:i2])
        
        # check data
        if len(self.data) == 0:
            return False
        
        # auto align data and theoretical pattern
        if autoAlign:
            self._alignData()
        
        # split data to raster and intensities
        xAxis, yAxis = numpy.hsplit(self.data, 2)
        raster = xAxis.flatten()
        intensities = yAxis.flatten()
        
        # model profiles
        models, exchanged = self._makeModels(raster, reset=False)
        
        # fit data to models
        fit = self._leastSquare(intensities, models, iterLimit=iterLimit)
        if not sum(fit):
            return False
        
        f = 1./sum(fit)
        for i, abundance in enumerate(fit):
            self.models[exchanged[i]][2] = abundance
            self.models[exchanged[i]][3] = f*abundance
        
        # calc average exchange
        for x in self.models:
            self.average += x * self.models[x][3]
        
        # get compositions
        for x in sorted(self.models.keys()):
            self.composition[x] = self.models[x][2]
            self.ncomposition[x] = self.models[x][3]
        
        # get calculated points
        raster.shape = (-1,1)
        intensities = numpy.sum(models * [[x] for x in fit], axis=0)
        intensities.shape = (-1,1)
        self.model = numpy.concatenate((raster, intensities), axis=1).copy()
        
        return True
    # ----
    
    
    def envelope(self, points=10):
        """Make envelope for current composition."""
        
        # get isotopes
        isotopes = []
        for x in self.models:
            abundance = self.models[x][2]
            isotopes += [(p[0], p[1]*abundance) for p in self.models[x][1]]
        
        # make profile from isotopes
        profile = mod_pattern.profile(isotopes, fwhm=self.fwhm, points=points, model=self.peakShape)
        
        return profile
    # ----
    
    
    # HELPERS
    
    def _initModels(self, scales):
        """Init theoretical envelope models."""
        
        self.models = {}
        
        # generate possible models to fit
        for x in scales:
            
            CHECK_FORCE_QUIT()
            
            # make compound
            item = "%s(%s)%d(%s)%d" % (self.formula, self._lossFormula, x, self._gainFormula, x)
            compound = obj_compound.compound(item)
            
            # check compound
            if not compound.isvalid(charge=self.charge):
                continue
            
            # append model [0-compound, 1-pattern, 2-abs abundance, 3-rel abundance]
            self.models[x] = [compound, [], 0.0, 0.0]
    # ----
    
    
    def _initRange(self):
        """Get relevant mz range from models."""
        
        scales = self.models.keys()
        
        compound = self.models[min(scales)][0]
        pattern = compound.pattern(fwhm=0.5, charge=self.charge)
        x1, x2 = pattern[0][0], pattern[-1][0]
        
        compound = self.models[max(scales)][0]
        pattern = compound.pattern(fwhm=0.5, charge=self.charge)
        x3, x4 = pattern[0][0], pattern[-1][0]
        
        self.mzrange[0] = min(x1, x2, x3, x4)
        self.mzrange[1] = max(x1, x2, x3, x4)
        
        self.mzrange[0] -= self.mzrange[0] * .001
        self.mzrange[1] += self.mzrange[1] * .001
    # ----
    
    
    def _makeModels(self, raster, reset=True):
        """Calculate pattern for every model."""
        
        models = []
        exchanged = []
        
        # get raster
        rasterMin = raster[0] - self.fwhm
        rasterMax = raster[-1] + self.fwhm
        
        for x in sorted(self.models.keys()):
            
            CHECK_FORCE_QUIT()
            
            # get compound
            compound = self.models[x][0]
            
            # check if mz is within raster
            mz = compound.mz(self.charge)
            if mz[0] > rasterMax or mz[1] < rasterMin:
                continue
            
            # calculate isotopic pattern
            pattern = self.models[x][1]
            if reset or pattern == []:
                pattern = compound.pattern(fwhm=self.fwhm, charge=self.charge, real=False)
                self.models[x][1] = pattern
            
            # calculate model profile
            profile = mod_pattern.profile(pattern, fwhm=self.fwhm, raster=raster, model=self.peakShape)
            model = profile[:,1].flatten()
            
            # check model profile
            if model.any():
                models.append(model)
                exchanged.append(x)
        
        # make models matrix
        models = numpy.array(models)
        
        return models, exchanged
    # ----
    
    
    def _alignData(self):
        """Re-calibrate data using theoretical envelope."""
        
        # split data to raster and intensities
        xAxis, yAxis = numpy.hsplit(self.data, 2)
        raster = xAxis.flatten()
        intensities = yAxis.flatten()
        
        # model profiles
        models, exchanged = self._makeModels(raster)
        
        # fit current data
        fit = self._leastSquare(intensities, models, iterLimit=len(self.models))
        
        # get all isotopes for all used models
        isotopes = []
        for i, abundance in enumerate(fit):
            pattern = self.models[exchanged[i]][1]
            isotopes += [(p[0], p[1]*abundance) for p in pattern]
        
        # check isotopes
        if not isotopes:
            return
        
        # make total envelope
        profile = mod_pattern.profile(isotopes, fwhm=self.fwhm, points=10, model=self.peakShape)
        
        # label peaks in profile
        peaklist = mod_peakpicking.labelscan(profile, pickingHeight=0.95, relThreshold=0.01)
        
        # find useful calibrants
        calibrants = []
        tolerance = self.fwhm/1.5
        for peak in peaklist:
            for point in self.data:
                error = point[0] - peak.mz
                if abs(error) <= tolerance:
                    if calibrants and calibrants[-1][0] == peak.mz and calibrants[-1][1] < point[1]:
                        calibrants[-1] = (point[0], peak.mz)
                    else:
                        calibrants.append((point[0], peak.mz))
                elif error > tolerance:
                    break
        
        # calc calibration
        if len(calibrants) > 3:
            model, params, chi = mod_calibration.calibration(calibrants, model='quadratic')
        elif len(calibrants) > 1:
            model, params, chi = mod_calibration.calibration(calibrants, model='linear')
        else:
            return
        
        # apply calibration to data
        for x in range(len(self.data)):
            self.data[x][0] = model(params, self.data[x][0])
        for x in range(len(self.spectrum)):
            self.spectrum[x][0] = model(params, self.spectrum[x][0])
    # ----
    
    
    def _leastSquare(self, data, models, iterLimit=None, chiLimit=1e-3):
        """Least-square fitting. Adapted from the original code by Konrad Hinsen."""
        
        normf = 100./numpy.max(data)
        data *= normf
        
        params = [50.] * len(models)
        id = numpy.identity(len(params))
        chisq, alpha = self._chiSquare(data, models, params)
        l = 0.001
        
        niter = 0
        while True:
            
            CHECK_FORCE_QUIT()
            
            niter += 1
            delta = solveLinEq(alpha+l*numpy.diagonal(alpha)*id,-0.5*numpy.array(chisq[1]))
            next_params = map(lambda a,b: a+b, params, delta)
            
            for x in range(len(next_params)):
                if next_params[x] < 0.:
                    next_params[x] = 0.
            
            next_chisq, next_alpha = self._chiSquare(data, models, next_params)
            if next_chisq[0] > chisq[0]:
                l = 5.*l
            elif chisq[0] - next_chisq[0] < chiLimit:
                break
            else:
                l = 0.5*l
                params = next_params
                chisq = next_chisq
                alpha = next_alpha
            
            if iterLimit and niter == iterLimit:
                break
        
        next_params /= normf
        
        return next_params
    # ----
    
    
    def _chiSquare(self, data, models, params):
        """Calculate fitting chi-square for current parameter set."""
        
        # calculate differences and chi-square value between calculated and real data
        differences = numpy.sum(models * [[x] for x in params], axis=0) - data
        chisq_value = numpy.sum(differences**2)
        
        # calculate chi-square deriv and alpha
        cycles = len(models)
        chisq_deriv = cycles*[0]
        alpha = numpy.zeros((len(params), len(params)))
        for x in range(len(data)):
            
            deriv = cycles*[0]
            for i in range(cycles):
                p_deriv = cycles*[0]
                p_deriv[i] = models[i][x]
                deriv = map(lambda a,b: a+b, deriv, p_deriv)
            chisq_deriv = map(lambda a,b: a+b, chisq_deriv, map(lambda x,f=differences[x]*2:f*x, deriv))
            
            d = numpy.array(deriv)
            alpha = alpha + d[:,numpy.newaxis]*d
        
        return [chisq_value, chisq_deriv], alpha
    # ----
    
    
 