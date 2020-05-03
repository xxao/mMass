# -------------------------------------------------------------------------
#     Copyright (C) 2008-2011 Martin Strohalm <www.mmass.org>

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
SCAN_NUMBER_PATTERN = re.compile('scan=([0-9]+)')


# PARSE mzML DATA
# ---------------

class parseMZML():
    """Parse data from mzML."""
    
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
                del self._scanlist[scanNumber]['mzData']
                del self._scanlist[scanNumber]['mzPrecision']
                del self._scanlist[scanNumber]['mzCompression']
                del self._scanlist[scanNumber]['intData']
                del self._scanlist[scanNumber]['intPrecision']
                del self._scanlist[scanNumber]['intCompression']
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
        if not scanData['mzData'] or not scanData['intData']:
            return []
        
        # decode data
        mzData = base64.b64decode(scanData['mzData'])
        intData = base64.b64decode(scanData['intData'])
        
        # decompress data
        if scanData['mzCompression'] == 'zlib':
            mzData = zlib.decompress(mzData)
        if scanData['intCompression'] == 'zlib':
            intData = zlib.decompress(intData)
        
        # get precision
        mzPrecision = 'f'
        intPrecision = 'f'
        if scanData['mzPrecision'] == 64:
            mzPrecision = 'd'
        if scanData['intPrecision'] == 64:
            intPrecision = 'd'
        
        # convert from binary
        count = len(mzData) / struct.calcsize('<' + mzPrecision)
        mzData = struct.unpack('<' + mzPrecision * count, mzData[0:len(mzData)])
        count = len(intData) / struct.calcsize('<' + intPrecision)
        intData = struct.unpack('<' + intPrecision * count, intData[0:len(intData)])
        
        # format
        if scanData['spectrumType'] == 'discrete':
            data = map(list, zip(mzData, intData))
        else:
            mzData = numpy.array(mzData)
            mzData.shape = (-1,1)
            intData = numpy.array(intData)
            intData.shape = (-1,1)
            data = numpy.concatenate((mzData,intData), axis=1)
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
        
        self._isDescription = False
        self._isConfig = False
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get file description
        if name == 'fileDescription':
            self._isDescription = True
        elif self._isDescription and name == 'cvParam':
            if attrs.get('accession', '') == 'MS:1000580':
                self.data['title'] = attrs.get('name', '')
            elif attrs.get('accession', '') == 'MS:1000586':
                self.data['operator'] = attrs.get('value', '')
            elif attrs.get('accession', '') == 'MS:1000590':
                self.data['institution'] = attrs.get('value', '')
            elif attrs.get('accession', '') == 'MS:1000589':
                self.data['contact'] = attrs.get('value', '')
        
        # get instrument
        elif name == 'instrumentConfiguration':
            self._isConfig = True
        elif self._isConfig and name == 'cvParam' and attrs.get('accession', '') == 'MS:1000169':
             self.data['instrument'] = attrs.get('name', '')
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'instrumentConfiguration':
            raise stopParsing()
    # ----
    
    

class scanlistHandler(xml.sax.handler.ContentHandler):
    """Get list of all scans in the document."""
    
    def __init__(self):
        self.data = {}
        self._isSpectrum = False
        self._isPrecursor = False
        self._scanHierarchy = [None]
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan data
        if name == 'spectrum':
            self._isSpectrum = True
            
            # get scan ID
            self.currentID = None
            attribute = attrs.get('id', False)
            if attribute:
                self.currentID = _parseScanNumber(attribute)
            
            scan = {
                'title': '',
                'scanNumber': self.currentID,
                'parentScanNumber': None,
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
                'spectrumType': 'unknown',
            }
            
            # get points count
            attribute = attrs.get('defaultArrayLength', False)
            if attribute:
                scan['pointsCount'] = int(attribute)
            
            # append scan
            self.data[self.currentID] = scan
        
        # precursor tag
        elif name == 'precursor' and self._isSpectrum:
            self._isPrecursor = True
            
            # get parent scan number
            attribute = attrs.get('spectrumRef', False)
            if attribute:
                self.data[self.currentID]['parentScanNumber'] = _parseScanNumber(attribute)
        
        # get precursor
        elif name == 'cvParam' and self._isPrecursor:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            if paramName == 'selected ion m/z' and paramValue != None:
                self.data[self.currentID]['precursorMZ'] = float(paramValue)
            elif paramName == 'intensity' and paramValue != None:
                self.data[self.currentID]['precursorIntensity'] = float(paramValue)
            elif paramName == 'possible charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)
            elif paramName == 'charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)
        
        # get scan metadata
        elif name == 'cvParam' and self._isSpectrum:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            # data type
            if paramName == 'centroid spectrum':
                self.data[self.currentID]['spectrumType'] = 'discrete'
            elif paramName == 'profile spectrum':
                self.data[self.currentID]['spectrumType'] = 'continuous'
            
            # MS level
            elif paramName == 'ms level' and paramValue != None:
                self.data[self.currentID]['msLevel'] = int(paramValue)
            
            # polarity
            elif paramName == 'positive scan':
                self.data[self.currentID]['polarity'] = 1
            elif paramName == 'negative scan':
                self.data[self.currentID]['polarity'] = -1
            
            # total ion current
            elif paramName == 'total ion current' and paramValue != None:
                self.data[self.currentID]['totIonCurrent'] = max(0.0, float(paramValue))
            
            # base peak
            elif paramName == 'base peak m/z' and paramValue != None:
                self.data[self.currentID]['basePeakMZ'] = float(paramValue)
            elif paramName == 'base peak intensity' and paramValue != None:
                self.data[self.currentID]['basePeakIntensity'] = max(0.0, float(paramValue))
            
            # mass range
            elif paramName == 'lowest observed m/z' and paramValue != None:
                self.data[self.currentID]['lowMZ'] = float(paramValue)
            elif paramName == 'highest observed m/z' and paramValue != None:
                self.data[self.currentID]['highMZ'] = float(paramValue)
            
            # retention time
            elif paramName == 'scan start time' and paramValue != None:
                if attrs.get('unitName','') == 'minute':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
                elif attrs.get('unitName','') == 'second':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)
                else:
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # end spectrum element
        if name == 'spectrum':
            self._isSpectrum = False
        
        # end precursor element
        elif name == 'precursor':
            self._isPrecursor = False
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        pass
    # ----
    
    

class scanHandler(xml.sax.handler.ContentHandler):
    """Get scan data."""
    
    def __init__(self, scanID):
        self.data = False
        self.scanID = scanID
        
        self._isMatch = False
        self._isPrecursor = False
        self._isBinaryDataArray = False
        self._isData = False
        self._scanHierarchy = [None]
        
        self.tmpBinaryData = None
        self.tmpPrecision = None
        self.tmpCompression = None
        self.tmpArrayType = None
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan metadata
        if name == 'spectrum':
            self._isMatch = False
            
            # get scan ID
            scanID = None
            attribute = attrs.get('id', False)
            if attribute:
                scanID = _parseScanNumber(attribute)
            
            # selected scan
            if self.scanID == None or self.scanID == scanID:
                self._isMatch = True
                
                self.data = {
                    'title': '',
                    'scanNumber': scanID,
                    'parentScanNumber': None,
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
                    'spectrumType': 'unknown',
                    
                    'mzData': None,
                    'mzPrecision': None,
                    'mzCompression': None,
                    'intData': None,
                    'intPrecision': None,
                    'intCompression': None,
                }
                
                # get points count
                attribute = attrs.get('defaultArrayLength', False)
                if attribute:
                    self.data['pointsCount'] = int(attribute)
        
        # precursor tag
        elif name == 'precursor' and self._isMatch:
            self._isPrecursor = True
            
            # get parent scan number
            attribute = attrs.get('spectrumRef', False)
            if attribute:
                self.data['parentScanNumber'] = _parseScanNumber(attribute)
        
        # binary aray tag
        elif name == 'binaryDataArray' and self._isMatch:
            self._isBinaryDataArray = True
            self.tmpBinaryData = []
            self.tmpPrecision = None
            self.tmpCompression = None
            self.tmpArrayType = None
        
        # data array tag
        elif name == 'binary' and self._isBinaryDataArray:
            self._isData = True
        
        # get precursor
        elif name == 'cvParam' and self._isPrecursor:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            if paramName == 'selected ion m/z' and paramValue != None:
                self.data['precursorMZ'] = float(paramValue)
            elif paramName == 'intensity' and paramValue != None:
                self.data['precursorIntensity'] = float(paramValue)
            elif paramName == 'possible charge state' and paramValue != None:
                self.data['precursorCharge'] = int(paramValue)
            elif paramName == 'charge state' and paramValue != None:
                self.data['precursorCharge'] = int(paramValue)
        
        # get binary data metadata
        elif name == 'cvParam' and self._isBinaryDataArray:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            # precision
            if paramName == '64-bit float':
                self.tmpPrecision = 64
            elif paramName == '32-bit float':
                self.tmpPrecision = 32
            
            # compression
            elif paramName == 'zlib compression':
                self.tmpCompression = 'zlib'
            elif paramName == 'no compression':
                self.tmpCompression = None
            
            # array type
            elif paramName == 'm/z array':
                self.tmpArrayType = 'mzArray'
            elif paramName == 'intensity array':
                self.tmpArrayType = 'intArray'
        
        # get scan metadata
        elif name == 'cvParam' and self._isMatch:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            # data type
            if paramName == 'centroid spectrum':
                self.data['spectrumType'] = 'discrete'
            elif paramName == 'profile spectrum':
                self.data['spectrumType'] = 'continuous'
            
            # MS level
            elif paramName == 'ms level' and paramValue != None:
                self.data['msLevel'] = int(paramValue)
            
            # polarity
            elif paramName == 'positive scan':
                self.data['polarity'] = 1
            elif paramName == 'negative scan':
                self.data['polarity'] = -1
            
            # total ion current
            elif paramName == 'total ion current' and paramValue != None:
                self.data['totIonCurrent'] = max(0.0, float(paramValue))
            
            # base peak
            elif paramName == 'base peak m/z' and paramValue != None:
                self.data['basePeakMZ'] = float(paramValue)
            elif paramName == 'base peak intensity' and paramValue != None:
                self.data['basePeakIntensity'] = max(0.0, float(paramValue))
            
            # mass range
            elif paramName == 'lowest observed m/z' and paramValue != None:
                self.data['lowMZ'] = float(paramValue)
            elif paramName == 'highest observed m/z' and paramValue != None:
                self.data['highMZ'] = float(paramValue)
            
            # retention time
            elif paramName == 'scan start time' and paramValue != None:
                if attrs.get('unitName','') == 'minute':
                    self.data['retentionTime'] = float(paramValue)*60
                elif attrs.get('unitName','') == 'second':
                    self.data['retentionTime'] = float(paramValue)
                else:
                    self.data['retentionTime'] = float(paramValue)*60
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'spectrum' and self._isMatch:
            raise stopParsing()
        
        # end spectrum element
        elif name == 'spectrum':
            self._isMatch = False
        
        # end precursor element
        elif name == 'precursor' and self._isMatch:
            self._isPrecursor = False
        
        # stop reading peaks data
        elif name == 'binaryDataArray' and self._isMatch:
            self._isBinaryDataArray = False
            
            # mz array
            if self.tmpArrayType == 'mzArray':
                self.data['mzData'] = ''.join(self.tmpBinaryData)
                self.data['mzPrecision'] = self.tmpPrecision
                self.data['mzCompression'] = self.tmpCompression
            
            # intensity array
            elif self.tmpArrayType == 'intArray':
                self.data['intData'] = ''.join(self.tmpBinaryData)
                self.data['intPrecision'] = self.tmpPrecision
                self.data['intCompression'] = self.tmpCompression
            
            self.tmpBinaryData = None
            self.tmpPrecision = None
            self.tmpCompression = None
        
        # stop reading binary array
        elif name == 'binary' and self._isMatch:
            self._isData = False
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get peaks
        if self._isData:
            self.tmpBinaryData.append(ch)
    # ----
    
    

class runHandler(xml.sax.handler.ContentHandler):
    """Get whole run."""
    
    def __init__(self):
        self.data = {}
        self.currentID = None
        
        self._isSpectrum = False
        self._isPrecursor = False
        self._isBinaryDataArray = False
        self._isData = False
        
        self.tmpBinaryData = None
        self.tmpPrecision = None
        self.tmpCompression = None
        self.tmpArrayType = None
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan metadata
        if name == 'spectrum':
            self._isSpectrum = True
            
            # get scan ID
            self.currentID = None
            attribute = attrs.get('id', False)
            if attribute:
                self.currentID = _parseScanNumber(attribute)
            
            scan = {
                'title': '',
                'scanNumber': self.currentID,
                'parentScanNumber': None,
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
                'spectrumType': 'unknown',
                
                'mzData': None,
                'mzPrecision': None,
                'mzCompression': None,
                'intData': None,
                'intPrecision': None,
                'intCompression': None,
            }
            
            # get points count
            attribute = attrs.get('defaultArrayLength', False)
            if attribute:
                scan['pointsCount'] = int(attribute)
            
            # add scan
            self.data[self.currentID] = scan
        
        # precursor tag
        elif name == 'precursor' and self._isSpectrum:
            self._isPrecursor = True
            
            # get parent scan number
            attribute = attrs.get('spectrumRef', False)
            if attribute:
                self.data[self.currentID]['parentScanNumber'] = _parseScanNumber(attribute)
        
        # binary aray tag
        elif name == 'binaryDataArray' and self._isSpectrum:
            self._isBinaryDataArray = True
            self.tmpBinaryData = []
            self.tmpPrecision = None
            self.tmpCompression = None
            self.tmpArrayType = None
        
        # data array tag
        elif name == 'binary' and self._isBinaryDataArray:
            self._isData = True
        
        # get precursor
        elif name == 'cvParam' and self._isPrecursor:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            if paramName == 'selected ion m/z' and paramValue != None:
                self.data[self.currentID]['precursorMZ'] = float(paramValue)
            elif paramName == 'intensity' and paramValue != None:
                self.data[self.currentID]['precursorIntensity'] = float(paramValue)
            elif paramName == 'possible charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)
            elif paramName == 'charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)
        
        # get binary data metadata
        elif name == 'cvParam' and self._isBinaryDataArray:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            # precision
            if paramName == '64-bit float':
                self.tmpPrecision = 64
            elif paramName == '32-bit float':
                self.tmpPrecision = 32
            
            # compression
            elif paramName == 'zlib compression':
                self.tmpCompression = 'zlib'
            elif paramName == 'no compression':
                self.tmpCompression = None
            
            # array type
            elif paramName == 'm/z array':
                self.tmpArrayType = 'mzArray'
            elif paramName == 'intensity array':
                self.tmpArrayType = 'intArray'
        
        # get scan metadata
        elif name == 'cvParam' and self._isSpectrum:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            # data type
            if paramName == 'centroid spectrum':
                self.data[self.currentID]['spectrumType'] = 'discrete'
            elif paramName == 'profile spectrum':
                self.data[self.currentID]['spectrumType'] = 'continuous'
            
            # MS level
            elif paramName == 'ms level' and paramValue != None:
                self.data[self.currentID]['msLevel'] = int(paramValue)
            
            # polarity
            elif paramName == 'positive scan':
                self.data[self.currentID]['polarity'] = 1
            elif paramName == 'negative scan':
                self.data[self.currentID]['polarity'] = -1
            
            # total ion current
            elif paramName == 'total ion current' and paramValue != None:
                self.data[self.currentID]['totIonCurrent'] = max(0.0, float(paramValue))
            
            # base peak
            elif paramName == 'base peak m/z' and paramValue != None:
                self.data[self.currentID]['basePeakMZ'] = float(paramValue)
            elif paramName == 'base peak intensity' and paramValue != None:
                self.data[self.currentID]['basePeakIntensity'] = max(0.0, float(paramValue))
            
            # mass range
            elif paramName == 'lowest observed m/z' and paramValue != None:
                self.data[self.currentID]['lowMZ'] = float(paramValue)
            elif paramName == 'highest observed m/z' and paramValue != None:
                self.data[self.currentID]['highMZ'] = float(paramValue)
            
            # retention time
            elif paramName == 'scan start time' and paramValue != None:
                if attrs.get('unitName','') == 'minute':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
                elif attrs.get('unitName','') == 'second':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)
                else:
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # end spectrum element
        if name == 'spectrum':
            self._isSpectrum = False
        
        # end precursor element
        elif name == 'precursor':
            self._isPrecursor = False
        
        # stop reading peaks data
        elif name == 'binaryDataArray' and self._isSpectrum:
            self._isBinaryDataArray = False
            
            # mz array
            if self.tmpArrayType == 'mzArray':
                self.data[self.currentID]['mzData'] = ''.join(self.tmpBinaryData)
                self.data[self.currentID]['mzPrecision'] = self.tmpPrecision
                self.data[self.currentID]['mzCompression'] = self.tmpCompression
            
            # intensity array
            elif self.tmpArrayType == 'intArray':
                self.data[self.currentID]['intData'] = ''.join(self.tmpBinaryData)
                self.data[self.currentID]['intPrecision'] = self.tmpPrecision
                self.data[self.currentID]['intCompression'] = self.tmpCompression
            
            self.tmpBinaryData = None
            self.tmpPrecision = None
            self.tmpCompression = None
        
        # stop reading binary array
        elif name == 'binary':
            self._isData = False
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get peaks
        if self._isData:
            self.tmpBinaryData.append(ch)
    # ----
    
    

class stopParsing(Exception):
    """Exeption to stop parsing XML data."""
    pass


def _parseScanNumber(string):
    """Parse real scan number from id tag."""
    
    # match scan number pattern
    match = SCAN_NUMBER_PATTERN.search(string)
    if not match:
        return None
    
    # convert to int
    try: return int(match.group(1))
    except: return None
# ----

