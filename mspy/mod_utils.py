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
import os.path

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load parsers
from parser_xy import parseXY
from parser_mzxml import parseMZXML
from parser_mzdata import parseMZDATA
from parser_mzml import parseMZML
from parser_mgf import parseMGF
from parser_fasta import parseFASTA


# UTILITIES
# ---------

def load(path, scanID=None, dataType='continuous'):
    """Load scan from given document."""
    
    # check path
    if not os.path.exists(path):
        raise IOError, 'File not found! --> ' + path
    
    # get filename and extension
    dirName, fileName = os.path.split(path)
    baseName, extension = os.path.splitext(fileName)
    fileName = fileName.lower()
    baseName = baseName.lower()
    extension = extension.lower()
    
    # get document type
    if extension == '.mzdata':
        docType = 'mzData'
    elif extension == '.mzxml':
        docType = 'mzXML'
    elif extension == '.mzml':
        docType = 'mzML'
    elif extension == '.mgf':
        docType = 'MGF'
    elif extension in ('.xy', '.txt', '.asc'):
        docType = 'XY'
    elif extension == '.xml':
        doc = open(path, 'r')
        data = doc.read(500)
        if '<mzData' in data:
            docType = 'mzData'
        elif '<mzXML' in data:
            docType = 'mzXML'
        elif '<mzML' in data:
            docType = 'mzML'
        doc.close()
    
    # check document type
    if not docType:
        raise ValueError, 'Unknown document type! --> ' + path
    
    # load document data
    if docType == 'mzData':
        parser = parseMZDATA(path)
        scan = parser.scan(scanID)
    elif docType == 'mzXML':
        parser = parseMZXML(path)
        scan = parser.scan(scanID)
    elif docType == 'mzML':
        parser = parseMZML(path)
        scan = parser.scan(scanID)
    elif docType == 'MGF':
        parser = parseMGF(path)
        scan = parser.scan(scanID)
    elif docType == 'XY':
        parser = parseXY(path)
        scan = parser.scan(dataType)
    
    return scan
# ----


def save(data, path):
    """"""
    
    buff = ''
    for point in data:
        buff += "%f\t%f\n" % tuple(point)
    
    save = file(path, 'w')
    save.write(buff.encode("utf-8"))
    save.close()
# ----

