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
import re
import os.path

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak
import obj_peaklist
import obj_scan


# PARSE SIMPLE ASCII XY
# ---------------------

class parseXY():
    """Parse data from ASCII XY."""
    
    def __init__(self, path):
        self.path = path
        
        # check path
        if not os.path.exists(path):
            raise IOError, 'File not found! --> ' + self.path
    # ----
    
    
    def info(self):
        """Get document info."""
        
        data = {
            'title': '',
            'operator': '',
            'contact': '',
            'institution': '',
            'date': '',
            'instrument': '',
            'notes': '',
        }
        
        return data
    # ----
    
    
    def scan(self, dataType='continuous'):
        """Get spectrum from document."""
        
        # parse file
        data = self._parseData()
        
        # check data
        if not data:
            return False
        
        # return scan
        return self._makeScan(data, dataType)
    # ----
    
    
    def _parseData(self):
        """Parse data."""
        
        # open document
        try:
            document = file(self.path)
            rawData = document.readlines()
            document.close()
        except IOError:
            return False
        
        pattern = re.compile('^([-0-9\.eE+]+)[ \t]*(;|,)?[ \t]*([-0-9\.eE+]*)$')
        
        # read lines
        data = []
        for line in rawData:
            line = line.strip()
            
            # discard comment lines
            if not line or line[0] == '#' or line[0:3] == 'm/z':
                continue
            
            # check pattern
            parts = pattern.match(line)
            if parts:
                try:
                    mass = float(parts.group(1))
                    intensity = float(parts.group(3))
                except ValueError:
                    return False
                data.append([mass, intensity])
            else:
                return False
        
        return data
    # ----
    
    
    def _makeScan(self, scanData, dataType):
        """Make scan object from raw data."""
        
        # parse data as peaklist (discrete points)
        if dataType == 'discrete':
            buff = []
            for point in scanData:
                buff.append(obj_peak.peak(point[0], point[1]))
            scan = obj_scan.scan(peaklist=obj_peaklist.peaklist(buff))
        
        # parse data as spectrum (continuous line)
        else:
            scan = obj_scan.scan(profile=scanData)
        
        return scan
    # ----
    
    
