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
import xml.sax
import xml.dom.minidom
import base64
import zlib
import struct
import re
import os.path
import numpy
from copy import deepcopy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak
import obj_peaklist
import obj_scan

# compile basic patterns
RETENTION_TIME_PATTERN = re.compile('^PT((\d*\.?\d*)M)?((\d*\.?\d*)S)?$')


# PARSE mzXML DATA
# ----------------

class parseMZXML():
    """Parse data from mzXML."""
    
    def __init__(self, path):
        self.path = path
        self._scans = None
        self._scanlist = None
        self._info = None
        
        # check path
        if not os.path.exists(path):
            raise IOError, 'File not found! --> ' + self.path
    # ----
    
    
    def load(self):
        """Load all scans into memory."""
        
        # init parser
        handler = runHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        
        # parse document
        try:
            document = file(self.path)
            parser.parse(document)
            document.close()
            self._scans = handler.data
        except xml.sax.SAXException:
            self._scans = False
        
        # make scanlist
        if self._scans:
            self._scanlist = deepcopy(self._scans)
            for scanNumber in self._scanlist:
                del self._scanlist[scanNumber]['points']
                del self._scanlist[scanNumber]['byteOrder']
                del self._scanlist[scanNumber]['compression']
                del self._scanlist[scanNumber]['precision']
    # ----
    
    
    def info(self):
        """Get document info."""
        
        # get preloaded data if available
        if self._info:
            return self._info
        
        # init parser
        handler = infoHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        
        # parse document
        try:
            document = file(self.path)
            parser.parse(document)
            document.close()
        except stopParsing:
            self._info = handler.data
        except xml.sax.SAXException:
            self._info = False
        
        return self._info
    # ----
    
    
    def scanlist(self):
        """Get list of all scans in the document."""
        
        # use preloaded data if available
        if self._scanlist:
            return self._scanlist
        
        # init parser
        handler = scanlistHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        
        # parse document
        try:
            document = file(self.path)
            parser.parse(document)
            document.close()
            self._scanlist = handler.data
        except xml.sax.SAXException:
            self._scanlist = False
        
        return self._scanlist
    # ----
    
    
    def scan(self, scanID=None):
        """Get spectrum from document."""
        
        # use preloaded data if available
        if self._scans and scanID in self._scans:
            data = self._scans[scanID]
        
        # parse file
        else:
            handler = scanHandler(scanID)
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            try:
                document = file(self.path)
                parser.parse(document)
                document.close()
                data = handler.data
            except stopParsing:
                data = handler.data
            except xml.sax.SAXException:
                return False
        
        # check data
        if not data:
            return False
        
        # return scan
        return self._makeScan(data)
    # ----
    
    
    def _makeScan(self, scanData):
        """Make scan object from raw data."""
        
        # parse peaks
        points = self._parsePoints(scanData)
        if scanData['spectrumType'] == 'discrete':
            for x, p in enumerate(points):
                points[x] = obj_peak.peak(p[0], p[1])
            scan = obj_scan.scan(peaklist=obj_peaklist.peaklist(points))
        else:
            scan = obj_scan.scan(profile=points)
        
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
    
    
    def _parsePoints(self, scanData):
        """Parse spectrum data."""
        
        # check data
        if not scanData['points']:
            return []
        
        # get precision
        precision = 'f'
        if scanData['precision'] == 64:
            precision = 'd'
        
        # get endian
        endian = '!'
        if scanData['byteOrder'] == 'little':
            endian = '<'
        elif scanData['byteOrder'] == 'big':
            endian = '>'
        
        # decode data
        data = base64.b64decode(scanData['points'])
        
        # decompress data
        if scanData['compression'] == 'zlib':
            data = zlib.decompress(data)
        
        # convert from binary
        count = len(data) / struct.calcsize(endian + precision)
        data = struct.unpack(endian + precision * count, data[0:len(data)])
        
        # format
        if scanData['spectrumType'] == 'discrete':
            data = map(list, zip(data[::2], data[1::2]))
        else:
            data = numpy.array(data)
            data.shape = (-1,2)
            data = data.copy()
        
        return data
    # ----
    
    

class infoHandler(xml.sax.handler.ContentHandler):
    """Get info data."""
    
    def __init__(self):
        
        self.data = {
            'title': '',
            'operator': '',
            'contact': '',
            'institution': '',
            'date': '',
            'instrument': '',
            'notes': '',
        }
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get instrument
        if name == 'msManufacturer':
             self.data['instrument'] += attrs.get('value', '') + ' '
        elif name == 'msModel':
             self.data['instrument'] += attrs.get('value', '') + ' '
        elif name == 'msIonisation':
             self.data['instrument'] += attrs.get('value', '') + ' '
        elif name == 'msMassAnalyzer':
             self.data['instrument'] += attrs.get('value', '') + ' '
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'msInstrument':
            raise stopParsing()
    # ----
    
    

class scanlistHandler(xml.sax.handler.ContentHandler):
    """Get list of all scans in the document."""
    
    def __init__(self):
        self.data = {}
        self.currentID = None
        self._isPrecursor = False
        self._scanHierarchy = [None]
        self._spectrumType = 'unknown'
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get data type
        if name == 'dataProcessing':
            centroided = attrs.get('centroided', False)
            if centroided and centroided != '0':
                self._spectrumType = 'discrete'
        
        # get scan data
        elif name == 'scan':
            
            # get scan ID
            self.currentID = attrs.get('num', None)
            if self.currentID != None:
                self.currentID = int(self.currentID)
            
            # add scan to hierarchy
            self._scanHierarchy.append(self.currentID)
            
            scan = {
                'title': '',
                'scanNumber': self.currentID,
                'parentScanNumber': self._scanHierarchy[-2],
                'msLevel': None,
                'pointsCount': None,
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
                'spectrumType': self._spectrumType,
            }
            
            # get ms level
            attribute = attrs.get('msLevel', 1)
            if attribute:
                scan['msLevel'] = int(attribute)
            
            # get number of points
            attribute = attrs.get('peaksCount', None)
            if attribute != None:
                scan['pointsCount'] = int(attribute)
            
            # get polarity
            attribute = attrs.get('polarity', None)
            if attribute in ('positive', 'Positive', '+'):
                scan['polarity'] = 1
            elif attribute in ('negative', 'Negative', '-'):
                scan['polarity'] = -1
            
            # get scan retention time
            attribute = attrs.get('retentionTime', None)
            if attribute != None:
                scan['retentionTime'] = _convertRetentionTime(attribute)
            
            # get low m/z
            attribute = attrs.get('lowMz', None)
            if attribute != None:
                scan['lowMZ'] = float(attribute)
            
            # get high m/z
            attribute = attrs.get('highMz', None)
            if attribute != None:
                scan['highMZ'] = float(attribute)
            
            # get base peak m/z
            attribute = attrs.get('basePeakMz', None)
            if attribute != None:
                scan['basePeakMZ'] = float(attribute)
            
            # get base peak intensity
            attribute = attrs.get('basePeakIntensity', None)
            if attribute != None:
                scan['basePeakIntensity'] = max(0.0, float(attribute))
            
            # get total ion current
            attribute = attrs.get('totIonCurrent', None)
            if attribute != None:
                scan['totIonCurrent'] = max(0.0, float(attribute))
            
            # add scan
            self.data[self.currentID] = scan
        
        # get precursor data
        elif name == 'precursorMz':
            self._isPrecursor = True
            self.data[self.currentID]['precursorMZ'] = ''
            
            # get precursor intensity
            attribute = attrs.get('precursorIntensity', None)
            if attribute != None:
                self.data[self.currentID]['precursorIntensity'] = max(0.0, float(attribute))
            
            # get precursor charge
            attribute = attrs.get('precursorCharge', None)
            if attribute != None:
                self.data[self.currentID]['precursorCharge'] = int(attribute)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # remove scan from hierarchy
        if name == 'scan':
            del self._scanHierarchy[-1]
            self.currentID = self._scanHierarchy[-1]
        
        # stop reading precursor data
        elif name == 'precursorMz':
            self._isPrecursor = False
            
            # get precursor m/z
            if self.data[self.currentID]['precursorMZ']:
                self.data[self.currentID]['precursorMZ'] = float(self.data[self.currentID]['precursorMZ'])
            else:
                self.data[self.currentID]['precursorMZ'] = None
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get precursor mz
        if self._isPrecursor:
            self.data[self.currentID]['precursorMZ'] += ch
    # ----
    
    

class scanHandler(xml.sax.handler.ContentHandler):
    """Get scan data."""
    
    def __init__(self, scanID):
        self.data = False
        self.scanID = scanID
        
        self._isMatch = False
        self._isPeaks = False
        self._isPrecursor = False
        self._scanHierarchy = [None]
        self._spectrumType = 'unknown'
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get data type
        if name == 'dataProcessing':
            centroided = attrs.get('centroided', False)
            if centroided and centroided != '0':
                self._spectrumType = 'discrete'
        
        # get scan metadata
        elif name == 'scan':
            self._isMatch = False
            
            # get scan ID
            scanID = attrs.get('num', None)
            if scanID != None:
                scanID = int(scanID)
            
            # add scan to hierarchy
            self._scanHierarchy.append(scanID)
            
            # selected scan
            if self.scanID == None or self.scanID == scanID:
                self._isMatch = True
                
                self.data = {
                    'title': '',
                    'scanNumber': scanID,
                    'parentScanNumber': self._scanHierarchy[-2],
                    'msLevel': None,
                    'pointsCount': None,
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
                    'spectrumType': self._spectrumType,
                    
                    'points': None,
                    'byteOrder': None,
                    'compression': None,
                    'precision': None,
                }
                
                # get ms level
                attribute = attrs.get('msLevel', 1)
                if attribute:
                    self.data['msLevel'] = int(attribute)
                
                # get number of points
                attribute = attrs.get('peaksCount', None)
                if attribute != None:
                    self.data['pointsCount'] = int(attribute)
                
                # get polarity
                attribute = attrs.get('polarity', None)
                if attribute in ('positive', 'Positive', '+'):
                    self.data['polarity'] = 1
                elif attribute in ('negative', 'Negative', '-'):
                    self.data['polarity'] = -1
                
                # get scan retention time
                attribute = attrs.get('retentionTime', None)
                if attribute != None:
                    self.data['retentionTime'] = _convertRetentionTime(attribute)
                
                # get low m/z
                attribute = attrs.get('lowMz', None)
                if attribute != None:
                    self.data['lowMZ'] = float(attribute)
                
                # get high m/z
                attribute = attrs.get('highMz', None)
                if attribute != None:
                    self.data['highMZ'] = float(attribute)
                
                # get base peak m/z
                attribute = attrs.get('basePeakMz', None)
                if attribute != None:
                    self.data['basePeakMZ'] = float(attribute)
                
                # get base peak intensity
                attribute = attrs.get('basePeakIntensity', None)
                if attribute != None:
                    self.data['basePeakIntensity'] = max(0.0, float(attribute))
                
                # get total ion current
                attribute = attrs.get('totIonCurrent', None)
                if attribute != None:
                    self.data['totIonCurrent'] = max(0.0, float(attribute))
        
        # get peaks data
        elif name == 'peaks' and self._isMatch:
            self._isPeaks = True
            self.data['points'] = []
            
            # get byte order
            self.data['byteOrder'] = attrs.get('byteOrder','network')
            
            # get compression
            attribute = attrs.get('compressionType', None)
            if attribute and attribute != 'none':
                self.data['compression'] = attribute
            
            # get precision
            attribute = attrs.get('precision', 32)
            if attribute:
                self.data['precision'] = int(attribute)
        
        # get precursor data
        elif name == 'precursorMz' and self._isMatch:
            self._isPrecursor = True
            self.data['precursorMZ'] = ''
            
            # get precursor intensity
            attribute = attrs.get('precursorIntensity', None)
            if attribute != None:
                self.data['precursorIntensity'] = max(0.0, float(attribute))
            
            # get precursor charge
            attribute = attrs.get('precursorCharge', None)
            if attribute != None:
                self.data['precursorCharge'] = int(attribute)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'scan' and self._isMatch:
            raise stopParsing()
        
        # remove scan from hierarchy
        elif name == 'scan':
            del self._scanHierarchy[-1]
            if self._scanHierarchy[-1] == self.scanID:
                self._isMatch = True
        
        # stop reading peaks data
        elif name == 'peaks' and self._isMatch:
            self._isPeaks = False
            self.data['points'] = ''.join(self.data['points'])
            if not self.data['points']:
                self.data['points'] = None
        
        # stop reading precursor data
        elif name == 'precursorMz' and self._isMatch:
            self._isPrecursor = False
            
            # get precursor m/z
            if self.data['precursorMZ']:
                self.data['precursorMZ'] = float(self.data['precursorMZ'])
            else:
                self.data['precursorMZ'] = None
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get peaks
        if self._isPeaks:
            self.data['points'].append(ch)
        
        # get precursor
        if self._isPrecursor:
            self.data['precursorMZ'] += ch
    # ----
    
    

class runHandler(xml.sax.handler.ContentHandler):
    """Get whole run."""
    
    def __init__(self):
        self.data = {}
        self.currentID = None
        
        self._isPeaks = False
        self._isPrecursor = False
        self._scanHierarchy = [None]
        self._spectrumType = 'unknown'
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get data type
        if name == 'dataProcessing':
            centroided = attrs.get('centroided', False)
            if centroided and centroided != '0':
                self._spectrumType = 'discrete'
        
        # get scan data
        elif name == 'scan':
            
            # get scan ID
            self.currentID = attrs.get('num', None)
            if self.currentID != None:
                self.currentID = int(self.currentID)
            
            # add scan to hierarchy
            self._scanHierarchy.append(self.currentID)
            
            scan = {
                'title': '',
                'scanNumber': self.currentID,
                'parentScanNumber': self._scanHierarchy[-2],
                'msLevel': None,
                'pointsCount': None,
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
                'spectrumType': self._spectrumType,
                
                'points': None,
                'byteOrder': None,
                'compression': None,
                'precision': None,
            }
            
            # get ms level
            attribute = attrs.get('msLevel', 1)
            if attribute:
                scan['msLevel'] = int(attribute)
            
            # get number of points
            attribute = attrs.get('peaksCount', None)
            if attribute != None:
                scan['pointsCount'] = int(attribute)
            
            # get polarity
            attribute = attrs.get('polarity', None)
            if attribute in ('positive', 'Positive', '+'):
                scan['polarity'] = 1
            elif attribute in ('negative', 'Negative', '-'):
                scan['polarity'] = -1
            
            # get scan retention time
            attribute = attrs.get('retentionTime', None)
            if attribute != None:
                scan['retentionTime'] = _convertRetentionTime(attribute)
            
            # get low m/z
            attribute = attrs.get('lowMz', None)
            if attribute != None:
                scan['lowMZ'] = float(attribute)
            
            # get high m/z
            attribute = attrs.get('highMz', None)
            if attribute != None:
                scan['highMZ'] = float(attribute)
            
            # get base peak m/z
            attribute = attrs.get('basePeakMz', None)
            if attribute != None:
                scan['basePeakMZ'] = float(attribute)
            
            # get base peak intensity
            attribute = attrs.get('basePeakIntensity', None)
            if attribute != None:
                scan['basePeakIntensity'] = max(0.0, float(attribute))
            
            # get total ion current
            attribute = attrs.get('totIonCurrent', None)
            if attribute != None:
                scan['totIonCurrent'] = max(0.0, float(attribute))
            
            # add scan
            self.data[self.currentID] = scan
        
        # get peaks data
        elif name == 'peaks':
            self._isPeaks = True
            self.data[self.currentID]['points'] = []
            
            # get byte order
            self.data[self.currentID]['byteOrder'] = attrs.get('byteOrder','network')
            
            # get compression
            attribute = attrs.get('compressionType', None)
            if attribute and attribute != 'none':
                self.data[self.currentID]['compression'] = attribute
            
            # get precision
            attribute = attrs.get('precision', 32)
            if attribute:
                self.data[self.currentID]['precision'] = int(attribute)
        
        # get precursor data
        elif name == 'precursorMz':
            self._isPrecursor = True
            self.data[self.currentID]['precursorMZ'] = ''
            
            # get precursor intensity
            attribute = attrs.get('precursorIntensity', None)
            if attribute != None:
                self.data[self.currentID]['precursorIntensity'] = max(0.0, float(attribute))
            
            # get precursor charge
            attribute = attrs.get('precursorCharge', None)
            if attribute != None:
                self.data[self.currentID]['precursorCharge'] = int(attribute)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # remove scan from hierarchy
        if name == 'scan':
            del self._scanHierarchy[-1]
            self.currentID = self._scanHierarchy[-1]
        
        # stop reading peaks data
        elif name == 'peaks':
            self._isPeaks = False
            self.data[self.currentID]['points'] = ''.join(self.data[self.currentID]['points'])
            if not self.data[self.currentID]:
                self.data[self.currentID]['points'] = None
        
        # stop reading precursor data
        elif name == 'precursorMz':
            self._isPrecursor = False
            
            # get precursor m/z
            if self.data[self.currentID]['precursorMZ']:
                self.data[self.currentID]['precursorMZ'] = float(self.data[self.currentID]['precursorMZ'])
            else:
                self.data[self.currentID]['precursorMZ'] = None
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get peaks
        if self._isPeaks:
            self.data[self.currentID]['points'].append(ch)
        
        # get precursor mz
        if self._isPrecursor:
            self.data[self.currentID]['precursorMZ'] += ch
    # ----
    
    

class stopParsing(Exception):
    """Exeption to stop parsing XML data."""
    pass


def _convertRetentionTime(retention):
    """Convert retention time to seconds."""
    
    # match retention
    match = RETENTION_TIME_PATTERN.match(retention)
    if not match:
        return None
    
    # convert to seconds
    seconds = 0
    if match.group(2):
        seconds += float(match.group(2))*60
    if match.group(4):
        seconds += float(match.group(4))
    
    return seconds
# ----


