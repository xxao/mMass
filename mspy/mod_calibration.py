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
from numpy.linalg import solve as solveLinEq

# load stopper
from mod_stopper import CHECK_FORCE_QUIT


# DATA RE-CALIBRATION
# -------------------

def calibration(data, model='linear'):
    """Calculate calibration constants for given references.
        data (list or (measured mass, reference mass)) - calibration data
        model ('linear' or 'quadratic') - fitting model
    """
    
    # single point calibration
    if model == 'linear' and len(data) == 1:
        shift = data[0][1] - data[0][0]
        return _linearModel, (1., shift), 1.0
    
    # set fitting model and initial values
    if model=='linear':
        model = _linearModel
        initials = (0.5, 0)
    elif model=='quadratic':
        model = _quadraticModel
        initials = (1., 0, 0)
    
    # calculate calibration constants
    params = _leastSquaresFit(model, initials, data)
    
    # fn, parameters, chi-square
    return model, params[0], params[1]
# ----


def _linearModel(params, x):
    """Function for linear model."""
    
    a, b = params
    return a*x + b
# ----


def _quadraticModel(params, x):
    """Function for quadratic model."""
    
    a, b, c = params
    return a*x*x + b*x + c
# ----


def _leastSquaresFit(model, parameters, data, maxIterations=None, limit=1e-7):
    """General non-linear least-squares fit using the
        Levenberg-Marquardt algorithm and automatic derivatives.
        Originally developed by Konrad Hinsen.
    """
    
    n_param = len(parameters)
    p = ()
    i = 0
    for param in parameters:
        p = p + (_DerivVar(param, i),)
        i = i + 1
    id = numpy.identity(n_param)
    l = 0.001
    chi_sq, alpha = _chiSquare(model, p, data)
    niter = 0
    
    while True:
        niter += 1
        
        delta = solveLinEq(alpha+l*numpy.diagonal(alpha)*id,-0.5*numpy.array(chi_sq[1]))
        next_p = map(lambda a,b: a+b, p, delta)
        
        next_chi_sq, next_alpha = _chiSquare(model, next_p, data)
        if next_chi_sq > chi_sq:
            l = 10.*l
        elif chi_sq[0] - next_chi_sq[0] < limit:
            break
        else:
            l = 0.1*l
            p = next_p
            chi_sq = next_chi_sq
            alpha = next_alpha
        
        if maxIterations and niter == maxIterations:
            break
    
    return map(lambda p: p[0], next_p), next_chi_sq[0]
# ----


def _chiSquare(model, parameters, data):
    """Count chi-square."""
    
    n_param = len(parameters)
    alpha = numpy.zeros((n_param, n_param))
    
    chi_sq = _DerivVar(0., [])
    for point in data:
        f = model(parameters, point[0])
        chi_sq += (f-point[1])**2
        d = numpy.array(f[1])
        alpha = alpha + d[:,numpy.newaxis]*d
    
    return chi_sq, alpha
# ----


class _DerivVar:
    """This module provides automatic differentiation for functions with any number of variables."""
    
    def __init__(self, value, index=0):
        self.value = value
        if type(index) == type([]):
            self.deriv = index
        else:
            self.deriv = index*[0] + [1]
    
    def _mapderiv(self, func, a, b):
        nvars = max(len(a), len(b))
        a = a + (nvars-len(a))*[0]
        b = b + (nvars-len(b))*[0]
        return map(func, a, b)
    
    def __getitem__(self, item):
        if item == 0:
            return self.value
        elif item == 1:
            return self.deriv
        else:
            raise IndexError
    
    def __cmp__(self, other):
        if isinstance(other, _DerivVar):
            return cmp(self.value, other.value)
        else:
            return cmp(self.value, other)
    
    def __add__(self, other):
        if isinstance(other, _DerivVar):
            return _DerivVar(self.value + other.value, self._mapderiv(lambda a,b: a+b, self.deriv, other.deriv))
        else:
            return _DerivVar(self.value + other, self.deriv)
    
    def __radd__(self, other):
        if isinstance(other, _DerivVar):
            self.value += other.value
            self.deriv = self._mapderiv(lambda a,b: a+b, self.deriv, other.deriv)
            return self
        else:
            self.value += other
            return self
    
    def __sub__(self, other):
        if isinstance(other, _DerivVar):
            return _DerivVar(self.value - other.value, self._mapderiv(lambda a,b: a-b, self.deriv, other.deriv))
        else:
            return _DerivVar(self.value - other, self.deriv)
    
    def __rsub__(self, other):
        if isinstance(other, _DerivVar):
            self.value -= other.value
            self.deriv = self._mapderiv(lambda a,b: a-b, self.deriv, other.deriv)
            return self
        else:
            self.value -= other
            return self
    
    def __mul__(self, other):
        if isinstance(other, _DerivVar):
            return _DerivVar(self.value * other.value, self._mapderiv(lambda a,b: a+b, map(lambda x,f=self.value:f*x, other.deriv), map(lambda x,f=other.value:f*x, self.deriv)))
        else:
            return _DerivVar(self.value * other, map(lambda x,f=other:f*x, self.deriv))
    
    def __div__(self, other):
        if isinstance(other, _DerivVar):
            inv = 1./other.value
            return _DerivVar(self.value * inv, self._mapderiv(lambda a,b: a-b, map(lambda x,f=inv: f*x, self.deriv), map(lambda x,f=self.value*inv*inv: f*x, other.deriv)))
        else:
            inv = 1./value
            return _DerivVar(self.value * inv, map(lambda x,f=inv:f*x, self.deriv))
    
    def __pow__(self, other):
        val1 = pow(self.value, other-1)
        deriv1 = map(lambda x,f=val1*other: f*x, self.deriv)
        return _DerivVar(val1*self.value, deriv1)
        
    def __abs__(self):
        absvalue = abs(self.value)
        return _DerivVar(absvalue, map(lambda a, d=self.value/absvalue: d*a, self.deriv))
    
# ----


