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
from copy import deepcopy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak
import obj_peaklist
import obj_scan


# PARSE MGF DATA
# --------------

class parseMGF():
    """Parse data from MGF."""
    
    def __init__(self, path):
        self.path = path
        self._scans = None
        self._scanlist = None
        
        # check path
        if not os.path.exists(path):
            raise IOError, 'File not found! --> ' + self.path
    # ----
    
    
    def load(self):
        """Load all scans into memory."""
        self._parseData()
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
    
    
    def scanlist(self):
        """Get list of all scans in the document."""
        
        # use preloaded data if available
        if self._scanlist:
            return self._scanlist
        
        # parse data
        self._parseData()
        
        return self._scanlist
    # ----
    
    
    def scan(self, scanID=None, dataType=None):
        """Get spectrum from document."""
        
        # parse file
        if not self._scans:
            self._parseData()
        
        # check data
        if not self._scans:
            return False
        
        # check selected scan
        if scanID in self._scans:
            data = self._scans[scanID]
        elif scanID == None:
            data = self._scans[0]
        
        # return scan
        return self._makeScan(data, dataType)
    # ----
    
    
    def _parseData(self):
        """Parse data."""
        
        # clear buffers
        self._scans = {}
        self._scanlist = None
        
        # open document
        try:
            document = file(self.path)
            rawData = document.readlines()
            document.close()
        except IOError:
            return False
        
        headerPattern = re.compile('^([A-Z]+)=(.+)')
        pointPattern = re.compile('[ \t]?')
        currentID = None
        
        # parse each line
        for line in rawData:
            line = line.strip()
            
            # discard comments
            if not line or line[0] in ('#', ';', '!', '/'):
                continue
            
            # append default scan
            if currentID == None or line == 'BEGIN IONS':
                currentID = len(self._scans)
                scan = {
                    'title': '',
                    'scanNumber': currentID,
                    'parentScanNumber': None,
                    'msLevel': None,
                    'pointsCount': 0,
                    'polarity': None,
                    'retentionTime': None,
                    'lowMZ': None,
                    'highMZ': None,
                    'basePeakMZ': None,
                    'basePeakIntensity': None,
                    'totIonCurrent': None,
                    'precursorMZ': None,
                    'precursorIntensity': None,
                    'precursorCharge': None,
                    'spectrumType': 'unknown',
                    'data': [],
                }
                self._scans[currentID] = scan
            
            # scan ended, use default scan
            if line == 'END IONS':
                currentID = 0
                continue
            
            # get header data
            parts = headerPattern.match(line)
            if parts:
                if parts.group(1) == 'TITLE':
                    self._scans[currentID]['title'] = parts.group(2).strip()
                elif parts.group(1) == 'PEPMASS':
                    try: self._scans[currentID]['precursorMZ'] = float(pointPattern.split(parts.group(2))[0])
                    except: pass
                elif parts.group(1) == 'CHARGE':
                    charge = parts.group(2).strip()
                    if charge[-1] in ('+', '-'):
                        charge = charge[-1]+charge[:-1]
                    try: self._scans[currentID]['precursorCharge'] = int(charge)
                    except: pass
                continue
            
            # append datapoint
            parts = pointPattern.split(line)
            if parts:
                point = [0,100.]
                try: point[0] = float(parts[0])
                except ValueError: continue
                try: point[1] = float(parts[1])
                except ValueError, IndexError: pass
                self._scans[currentID]['data'].append(point)
                self._scans[currentID]['pointsCount'] += 1
                continue
        
        # make scanlist
        if self._scans:
            self._scanlist = deepcopy(self._scans)
            for scanNumber in self._scanlist:
                del self._scanlist[scanNumber]['data']
    # ----
    
    
    def _makeScan(self, scanData, dataType):
        """Make scan object from raw data."""
        
        # parse data as peaklist (discrete points)
        if dataType == 'peaklist' or (dataType==None and len(scanData['data'])<3000):
            buff = []
            for point in scanData['data']:
                buff.append(obj_peak.peak(point[0], point[1]))
            scan = obj_scan.scan(peaklist=obj_peaklist.peaklist(buff))
        
        # parse data as spectrum (continuous line)
        else:
            scan = obj_scan.scan(profile=scanData['data'])
        
        # set metadata
        scan.title = scanData['title']
        scan.scanNumber = scanData['scanNumber']
        scan.parentScanNumber = scanData['parentScanNumber']
        scan.msLevel = scanData['msLevel']
        scan.polarity = scanData['polarity']
        scan.retentionTime = scanData['retentionTime']
        scan.totIonCurrent = scanData['totIonCurrent']
        scan.basePeakMZ = scanData['basePeakMZ']
        scan.basePeakIntensity = scanData['basePeakIntensity']
        scan.precursorMZ = scanData['precursorMZ']
        scan.precursorIntensity = scanData['precursorIntensity']
        scan.precursorCharge = scanData['precursorCharge']
        
        return scan
    # ----
    
    
