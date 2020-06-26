import sys
import numpy
from distutils.core import setup
from distutils.extension import Extension

numpyInclude = numpy.get_include() + '/numpy'
pythonInclude = sys.prefix + '/include'

def build(setup_kwargs):
    setup_kwargs.update({
        'ext_modules': [
            Extension('calculations', ['calculations/calculations.c'],
                include_dirs=[numpyInclude, pythonInclude],
                libraries=['m']
            )
        ]
    })
