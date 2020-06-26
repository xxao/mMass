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
import numpy

# load stopper
from .mod_stopper import CHECK_FORCE_QUIT

# load modules
import calculations


# SIGNAL PROCESSING FUNCTIONS
# ---------------------------

def locate(signal, x):
    """Find nearest higher index of searched x-value.
        signal (numpy array) - signal data points
        x (float) - x value
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return 0
    
    # locate x
    return calculations.signal_locate_x(signal, float(x))
# ----


def basepeak(signal):
    """Locate highest y-value in signal. Point index is returned.
        signal (numpy array) - signal data points
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # locate x
    return calculations.signal_locate_max_y(signal)
# ----


def interpolate(p1, p2, x=None, y=None):
    """Calculates inner point between two points by linear interpolation.
        p1 (tuple of floats) - point 1
        p2 (tuple of floats) - point 2
        x (float) - x value (to interpolate y)
        y (float) - y value (to interpolate x)
    """
    
    # interpolate y point
    if x != None:
        return calculations.signal_interpolate_y(float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1]), float(x))
    
    # interpolate x point
    elif y != None:
        return calculations.signal_interpolate_x(float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1]), float(y))
    
    # no value
    else:
        raise ValueError("No x/y value provided for interpolation!")
# ----


def boundaries(signal):
    """Calculates signal minima and maxima as (minX, minY, maxX, maxY).
        signal (numpy array) - signal data points
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # calculate boundaries
    return calculations.signal_box(signal)
# ----


def maxima(signal):
    """Find local maxima in signal.
        signal (numpy array) - signal data points
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # determine intensity
    return calculations.signal_local_maxima(signal)
# ----


def intensity(signal, x):
    """Find corresponding y-value for searched x-value.
        signal (numpy array) - signal data points
        x (float) - x-value
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # determine intensity
    return calculations.signal_intensity(signal, float(x))
# ----


def centroid(signal, x, height):
    """Find peak centroid for searched x-value measured at y-value.
        signal (numpy array) - signal data points
        x (float) - x-value
        height (float) - y-value for width determination
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # determine centroid
    return calculations.signal_centroid(signal, float(x), float(height))
# ----


def width(signal, x, height):
    """Find peak width for searched x-value measured at y-value.
        signal (numpy array) - signal data points
        x (float) - x-value
        height (float) - y-value for width determination
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # determine width
    return calculations.signal_width(signal, float(x), float(height))
# ----


def area(signal, minX=None, maxX=None, baseline=None):
    """Return area under signal curve.
        signal (numpy array) - signal data points
        minX (float) - starting m/z value
        maxX (float) - ending m/z value
        baseline (numpy array) - signal baseline
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check baseline type
    if baseline != None:
        if not isinstance(baseline, numpy.ndarray):
            raise TypeError("Baseline must be NumPy array!")
        if baseline.dtype.name != 'float64':
            raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return 0.0
    
    # check range
    if minX != None and maxX != None and minX == maxX:
        return 0.0
    
    # crop data
    if minX != None and maxX != None:
        signal = crop(signal, minX, maxX)
    
    # subtract baseline
    if baseline != None:
        signal = subbase(signal, baseline)
    
    # calculate area
    return calculations.signal_area(signal)
# ----


def noise(signal, minX=None, maxX=None, x=None, window=0.1):
    """Calculates signal noise level and width.
        signal (numpy array) - signal data points
        minX, maxX (float) - x-axis range to use for calculation
        x (float) - x-value for which to calculate the noise +- window
        window (float) - x-axis range used for calculation, relative to given x (in %/100)
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return (0.0, 0.0)
    
    # use specified signal range
    if minX != None and maxX != None:
        i1 = locate(signal, minX)
        i2 = locate(signal, maxX)
    
    # use specified x +- window
    elif x != None and window != None:
        window = x*window
        i1 = locate(signal, x-window)
        i2 = locate(signal, x+window)
    
    # use whole signal range
    else:
        i1 = 0
        i2 = len(signal)
    
    # get data from signal
    signal = signal[i1:i2]
    
    # check signal data
    if len(signal) == 0:
        return (0.0, 0.0)
    
    # calculate noise
    return calculations.signal_noise(signal)
# ----


def baseline(signal, window=0.1, offset=0.):
    """Return baseline data.
        signal (numpy array) - signal data points
        window (float or None) - noise calculation window (%/100)
        offset (float) - baseline offset, relative to noise width (in %/100)
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        raise ValueError("Signal contains no data!")
    
    # single segment baseline
    if window is None:
        noiseLevel, noiseWidth = noise(signal)
        noiseLevel -= noiseWidth*offset
        return numpy.array([ [signal[0][0], noiseLevel, noiseWidth], [signal[-1][0], noiseLevel, noiseWidth] ])
    
    # make raster
    raster = []
    minimum = max(0, signal[0][0])
    x = signal[-1][0]
    while x > minimum:
        raster.append(x)
        x -= max(50, x*window)
    raster.append(minimum)
    raster.sort()
    
    # calc baseline data
    levels = []
    widths = []
    for i, x in enumerate(raster):
        i1 = locate(signal, x-x*window)
        i2 = locate(signal, x+x*window)
        if i1 == i2:
            noiseLevel = signal[i1][1]
            noiseWidth = 0.0
        else:
            noiseLevel, noiseWidth = noise(signal[i1:i2])
        levels.append([x, noiseLevel])
        widths.append([x, noiseWidth])
    
    # smooth baseline data
    swindow = 5 * window * (signal[-1][0] - signal[0][0])
    levels = smooth(numpy.array(levels), 'GA', swindow, 2)
    widths = smooth(numpy.array(widths), 'GA', swindow, 2)
    
    # make baseline and apply offset
    buff = []
    for i, x in enumerate(raster):
        width = abs(widths[i][1])
        level = max(0, levels[i][1] - width*offset)
        buff.append([x, level, width])
    
    return numpy.array(buff)
# ----


def crop(signal, minX, maxX):
    """Crop signal to given x-range. New array is returned.
        signal (numpy array) - signal data points
        minX (float) - minimum x-value
        maxX (float) - maximum x-value
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    
    # check limits
    if minX > maxX:
        minX, maxX = maxX, minX
    
    # check signal data
    if len(signal) == 0 or signal[-1][0] < minX or signal[0][0] > maxX:
        return numpy.array([])
    
    # crop data
    return calculations.signal_crop(signal, float(minX), float(maxX))
# ----


def offset(signal, x=0.0, y=0.0):
    """Shift signal by offset. New array is returned.
        signal (numpy array) - signal data points
        x (float) - x-axis offset
        y (float) - y-axis offset
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # offset signal
    return calculations.signal_offset(signal, float(x), float(y))
# ----


def multiply(signal, x=1.0, y=1.0):
    """Multiply signal values by factor. New array is returned.
        signal (numpy array) - signal data points
        x (float) - x-axis multiplicator
        y (float) - y-axis multiplicator
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # multiply signal
    return calculations.signal_multiply(signal, float(x), float(y))
# ----


def normalize(signal):
    """Normalize y-values of the signal to max 1. New array is returned.
        signal (numpy array) - signal data points
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # offset signal
    return calculations.signal_normalize(signal)
# ----


def smooth(signal, method, window, cycles=1):
    """Smooth signal by moving average filter. New array is returned.
        signal (numpy array) - signal data points
        method (MA GA SG) - smoothing method: MA - moving average, GA - Gaussian, SG - Savitzky-Golay
        window (float) - m/z window size for smoothing
        cycles (int) - number of repeating cycles
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray):
        raise TypeError("Signal must be NumPy array!")
    if signal.dtype.name != 'float64':
        raise TypeError("Signal data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # apply moving average filter
    if method == 'MA':
        return movaver(signal, window, cycles, style='flat')
    
    # apply gaussian filter
    elif method == 'GA':
        return movaver(signal, window, cycles, style='gaussian')
    
    # apply savitzky-golay filter
    elif method == 'SG':
        return savgol(signal, window, cycles)
    
    # unknown smoothing method
    else:
        raise KeyError("Unknown smoothing method! -->").with_traceback(method)
# ----


def movaver(signal, window, cycles=1, style='flat'):
    """Smooth signal by moving average filter. New array is returned.
        signal (numpy array) - signal data points
        window (float) - m/z window size for smoothing
        cycles (int) - number of repeating cycles
    """
    
    # approximate number of points within window
    window = int(window*len(signal)/(signal[-1][0]-signal[0][0]))
    window = min(window, len(signal))
    if window < 3:
        return signal.copy()
    if not window % 2:
        window -= 1
    
    # unpack mz and intensity
    xAxis, yAxis = numpy.hsplit(signal,2)
    xAxis = xAxis.flatten()
    yAxis = yAxis.flatten()
    
    # smooth the points
    while cycles:
        
        CHECK_FORCE_QUIT()
        
        if style == 'flat':
            w = numpy.ones(window,'f')
        elif style == 'gaussian':
            r = numpy.array([(i-(window-1)/2.) for i in range(window)])
            w = numpy.exp(-(r**2/(window/4.)**2))
        else:
            w = eval('numpy.'+style+'(window)')
        
        s = numpy.r_[yAxis[window-1:0:-1], yAxis, yAxis[-2:-window-1:-1]]
        y = numpy.convolve(w/w.sum(), s, mode='same')
        yAxis = y[window-1:-window+1]
        cycles -=1
    
    # return smoothed data
    xAxis.shape = (-1,1)
    yAxis.shape = (-1,1)
    data = numpy.concatenate((xAxis,yAxis), axis=1)
    
    return data.copy()
# ----


def savgol(signal, window, cycles=1, order=3):
    """Smooth signal by Savitzky-Golay filter. New array is returned.
        signal (numpy array) - signal data points
        window (float) - m/z window size for smoothing
        cycles (int) - number of repeating cycles
        order (int) - order of polynom used
    """
    
    # approximate number of points within window
    window = int(window*len(signal)/(signal[-1][0]-signal[0][0]))
    if window <= order:
        return signal.copy()
    
    # unpack axes
    xAxis, yAxis = numpy.hsplit(signal,2)
    yAxis = yAxis.flatten()
    
    # coeficients
    orderRange = list(range(order+1))
    halfWindow = (window-1) // 2
    b = numpy.mat([[k**i for i in orderRange] for k in range(-halfWindow, halfWindow+1)])
    m = numpy.linalg.pinv(b).A[0]
    window = len(m)
    halfWindow = (window-1) // 2
    
    # precompute the offset values for better performance
    offsets = list(range(-halfWindow, halfWindow+1))
    offsetData = list(zip(offsets, m))
    
    # smooth the data
    while cycles:
        smoothData = list()
        
        yAxis = numpy.concatenate((numpy.zeros(halfWindow)+yAxis[0], yAxis, numpy.zeros(halfWindow)+yAxis[-1]))
        for i in range(halfWindow, len(yAxis) - halfWindow):
            
            CHECK_FORCE_QUIT()
            
            value = 0.0
            for offset, weight in offsetData:
                value += weight * yAxis[i + offset]
            smoothData.append(value)
        
        yAxis = smoothData
        cycles -=1
    
    # return smoothed data
    yAxis = numpy.array(yAxis)
    yAxis.shape = (-1,1)
    data = numpy.concatenate((xAxis,yAxis), axis=1)
    
    return data.copy()
# ----


def combine(signalA, signalB):
    """Unify x-raster and combine two arrays (y=yA+yB). New array is returned.
        signalA (numpy array) - signal A data points
        signalB (numpy array) - signal B data points
    """
    
    # check signal type
    if not isinstance(signalA, numpy.ndarray) or not isinstance(signalB, numpy.ndarray):
        raise TypeError("Signals must be NumPy arrays!")
    if signalA.dtype.name != 'float64' or signalB.dtype.name != 'float64':
        raise TypeError("Signals data must be float64!")
    
    # check signal data
    if len(signalA) == 0 and len(signalB) == 0:
        return numpy.array([])
    
    # subtract signals
    return calculations.signal_combine(signalA, signalB)
# ----


def overlay(signalA, signalB):
    """Unify x-raster and overlay two arrays (y=max(yA,yB)). New array is returned.
        signalA (numpy array) - signal A data points
        signalB (numpy array) - signal B data points
    """
    
    # check signal type
    if not isinstance(signalA, numpy.ndarray) or not isinstance(signalB, numpy.ndarray):
        raise TypeError("Signals must be NumPy arrays!")
    if signalA.dtype.name != 'float64' or signalB.dtype.name != 'float64':
        raise TypeError("Signals data must be float64!")
    
    # check signal data
    if len(signalA) == 0 and len(signalB) == 0:
        return numpy.array([])
    
    # subtract signals
    return calculations.signal_overlay(signalA, signalB)
# ----


def subtract(signalA, signalB):
    """Unify x-raster and subtract two arrays (y=yA-yB). New array is returned.
        signalA (numpy array) - signal A data points
        signalB (numpy array) - signal B data points
    """
    
    # check signal type
    if not isinstance(signalA, numpy.ndarray) or not isinstance(signalB, numpy.ndarray):
        raise TypeError("Signals must be NumPy arrays!")
    if signalA.dtype.name != 'float64' or signalB.dtype.name != 'float64':
        raise TypeError("Signals data must be float64!")
    
    # check signal data
    if len(signalA) == 0 and len(signalB) == 0:
        return numpy.array([])
    
    # subtract signals
    return calculations.signal_subtract(signalA, signalB)
# ----


def subbase(signal, baseline):
    """Subtract baseline from signal withou chaning x-raster. New array is returned.
        signal (numpy array) - signal data points
        baseline (numpy array) - baseline data points
    """
    
    # check signal type
    if not isinstance(signal, numpy.ndarray) or not isinstance(baseline, numpy.ndarray):
        raise TypeError("Signals must be NumPy arrays!")
    if signal.dtype.name != 'float64' or baseline.dtype.name != 'float64':
        raise TypeError("Signals data must be float64!")
    
    # check signal data
    if len(signal) == 0:
        return numpy.array([])
    
    # check baseline data
    if len(baseline) == 0:
        return signal.copy()
    
    # check baseline shape
    if baseline.shape[1] > 2:
        baseline = numpy.hsplit(baseline, (2,6))[0].copy()
    
    # subtract signals
    return calculations.signal_subbase(signal, baseline)
# ----


