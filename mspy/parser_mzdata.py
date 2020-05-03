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
import struct
import os.path
import numpy
from copy import deepcopy

# load stopper
from mod_stopper import CHECK_FORCE_QUIT

# load objects
import obj_peak
import obj_peaklist
import obj_scan


# PARSE mzData DATA
# -----------------

class parseMZDATA():
    """Parse data from mzData."""
    
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
                del self._scanlist[scanNumber]['mzEndian']
                del self._scanlist[scanNumber]['mzPrecision']
                del self._scanlist[scanNumber]['intData']
                del self._scanlist[scanNumber]['intEndian']
                del self._scanlist[scanNumber]['intPrecision']
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
        
        # get endian
        mzEndian = '!'
        intEndian = '!'
        if scanData['mzEndian'] == 'little':
            mzEndian = '<'
        elif scanData['mzEndian'] == 'big':
            mzEndian = '>'
        if scanData['intEndian'] == 'little':
            intEndian = '<'
        elif scanData['intEndian'] == 'big':
            intEndian = '>'
        
        # get precision
        mzPrecision = 'f'
        intPrecision = 'f'
        if scanData['mzPrecision'] == 64:
            mzPrecision = 'd'
        if scanData['intPrecision'] == 64:
            intPrecision = 'd'
        
        # convert from binary
        count = len(mzData) / struct.calcsize(mzEndian + mzPrecision)
        mzData = struct.unpack(mzEndian + mzPrecision * count, mzData[0:len(mzData)])
        count = len(intData) / struct.calcsize(intEndian + intPrecision)
        intData = struct.unpack(intEndian + intPrecision * count, intData[0:len(intData)])
        
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
        
        self._isSampleName = False
        self._isContact = False
        self._isName = False
        self._isInstitution = False
        self._isContactInfo = False
        self._isInstrumentName = False
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get instrument
        if name == 'sampleName':
             self._isSampleName = True
        if name == 'contact':
             self._isContact = True
        elif name == 'name' and self._isContact:
             self._isName = True
        elif name == 'institution':
             self._isInstitution = True
        elif name == 'contactInfo':
             self._isContactInfo = True
        elif name == 'instrumentName':
             self._isInstrumentName = True
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'description':
            raise stopParsing()
        
        # stop elements
        if name == 'sampleName':
             self._isSampleName = False
        if name == 'contact':
             self._isContact = False
             self._isName = False
        elif name == 'name':
             self._isName = False
        elif name == 'institution':
             self._isInstitution = False
        elif name == 'contactInfo':
             self._isContactInfo = False
        elif name == 'instrumentName':
             self._isInstrumentName = False
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get data
        if self._isSampleName:
            self.data['title'] += ch
        elif self._isName:
            self.data['operator'] += ch
        elif self._isInstitution:
            self.data['institution'] += ch
        elif self._isContactInfo:
            self.data['contact'] += ch
        elif self._isInstrumentName:
            self.data['instrument'] += ch
    # ----
    
    

class scanlistHandler(xml.sax.handler.ContentHandler):
    """Get list of all scans in the document."""
    
    def __init__(self):
        self.data = {}
        self.currentID = None
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan metadata
        if name == 'spectrum':
            
            # get scan ID
            self.currentID = attrs.get('id', None)
            if self.currentID != None:
                self.currentID = int(self.currentID)
            
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
            
            # add scan
            self.data[self.currentID] = scan
        
        # get spectrum type
        elif name == 'acqSpecification':
            attribute = attrs.get('spectrumType', False)
            if attribute:
                self.data[self.currentID]['spectrumType'] = attribute
        
        # get other params
        elif name == 'spectrumInstrument':
            
            # get ms level
            attribute = attrs.get('msLevel', 1)
            if attribute:
                self.data[self.currentID]['msLevel'] = int(attribute)
            
            # get low m/z
            attribute = attrs.get('mzRangeStart', None)
            if attribute != None:
                self.data[self.currentID]['lowMZ'] = float(attribute)
            
            # get high m/z
            attribute = attrs.get('mzRangeStop', None)
            if attribute != None:
                self.data[self.currentID]['highMZ'] = float(attribute)
        
        # get other params
        elif name == 'userParam' or name == 'cvParam':
            paramName = attrs.get('name', None)
            paramValue = attrs.get('value', None)
            
            # get retention time
            if paramName == 'TimeInMinutes' and paramValue != None:
                try: self.data[self.currentID]['retentionTime'] = float(paramValue)*60
                except ValueError: pass
            
            # get total ion current
            elif paramName == 'TotalIonCurrent' and paramValue != None:
                try: self.data[self.currentID]['totIonCurrent'] = float(paramValue)
                except ValueError: pass
            
            # get precursor m/z
            elif paramName == 'MassToChargeRatio' and paramValue != None:
                try: self.data[self.currentID]['precursorMZ'] = float(paramValue)
                except ValueError: pass
            
            # get precursor charge
            elif paramName == 'ChargeState' and paramValue != None:
                try: self.data[self.currentID]['precursorCharge'] = int(paramValue)
                except ValueError: pass
            
            # get polarity
            elif paramName == 'Polarity':
                if paramValue in ('positive', 'Positive', '+'):
                    self.data[self.currentID]['polarity'] = 1
                elif paramValue == ('negative', 'Negative', '-'):
                    self.data[self.currentID]['polarity'] = -1
        
        # get parent scan
        elif name == 'precursor':
            attribute = attrs.get('spectrumRef', None)
            if attribute != None:
                self.data[self.currentID]['parentScanNumber'] = int(attribute)
        
        # get spectrum length
        elif name == 'data':
            attribute = attrs.get('length', None)
            if attribute != None:
                self.data[self.currentID]['pointsCount'] = int(attribute)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        pass
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
        self._isMzArray = False
        self._isIntArray = False
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan metadata
        if name == 'spectrum':
            self._isMatch = False
            
            # get scan ID
            scanID = attrs.get('id', None)
            if scanID != None:
                scanID = int(scanID)
            
            # selected scan
            if self.scanID == None or scanID == self.scanID:
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
                    'mzEndian': None,
                    'mzPrecision': None,
                    'intData': None,
                    'intEndian': None,
                    'intPrecision': None,
                }
        
        # get spectrum type
        elif name == 'acqSpecification' and self._isMatch:
            attribute = attrs.get('spectrumType', False)
            if attribute:
                self.data['spectrumType'] = attribute
        
        # get other params
        elif name == 'spectrumInstrument' and self._isMatch:
            
            # get ms level
            attribute = attrs.get('msLevel', 1)
            if attribute:
                self.data['msLevel'] = int(attribute)
            
            # get low m/z
            attribute = attrs.get('mzRangeStart', None)
            if attribute != None:
                self.data['lowMZ'] = float(attribute)
            
            # get high m/z
            attribute = attrs.get('mzRangeStop', None)
            if attribute != None:
                self.data['highMZ'] = float(attribute)
        
        # get other params
        elif (name == 'userParam' or name == 'cvParam') and self._isMatch:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value', None)
            
            # get retention time
            if paramName == 'TimeInMinutes' and paramValue != None:
                try: self.data['retentionTime'] = float(paramValue)*60
                except ValueError: pass
            
            # get total ion current
            elif paramName == 'TotalIonCurrent' and paramValue != None:
                try: self.data['totIonCurrent'] = float(paramValue)
                except ValueError: pass
            
            # get precursor m/z
            elif paramName == 'MassToChargeRatio' and paramValue != None:
                try: self.data['precursorMZ'] = float(paramValue)
                except ValueError: pass
            
            # get precursor charge
            elif paramName == 'ChargeState' and paramValue != None:
                try: self.data['precursorCharge'] = int(paramValue)
                except ValueError: pass
            
            # get polarity
            elif paramName == 'Polarity':
                if paramValue in ('positive', 'Positive', '+'):
                    self.data['polarity'] = 1
                elif paramValue == ('negative', 'Negative', '-'):
                    self.data['polarity'] = -1
        
        # get parent scan
        elif name == 'precursor' and self._isMatch:
            attribute = attrs.get('spectrumRef', None)
            if attribute != None:
                self.data['parentScanNumber'] = int(attribute)
        
        # get mz data
        elif name == 'mzArrayBinary' and self._isMatch:
            self._isMzArray = True
            self.data['mzData'] = []
        
        # get int data
        elif name == 'intenArrayBinary' and self._isMatch:
            self._isIntArray = True
            self.data['intData'] = []
        
        # get data
        elif name == 'data' and self._isMatch:
            
            # get points count
            attribute = attrs.get('length', None)
            if attribute != None:
                self.data['pointsCount'] = int(attribute)
            
            # get array params
            endian = attrs.get('endian','network')
            precision = attrs.get('precision', 32)
            
            if self._isMzArray:
                self.data['mzEndian'] = endian
                if precision:
                    self.data['mzPrecision'] = int(precision)
            
            elif self._isIntArray:
                self.data['intEndian'] = endian
                if precision:
                    self.data['intPrecision'] = int(precision)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop parsing
        if name == 'spectrum' and self._isMatch:
            raise stopParsing()
        
        # stop reading mz data
        elif name == 'mzArrayBinary' and self._isMatch:
            self._isMzArray = False
            if not self.data['mzData']:
                self.data['mzData'] = None
            else:
                self.data['mzData'] = ''.join(self.data['mzData'])
        
        # stop reading int data
        elif name == 'intenArrayBinary' and self._isMatch:
            self._isIntArray = False
            if not self.data['intData']:
                self.data['intData'] = None
            else:
                self.data['intData'] = ''.join(self.data['intData'])
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get m/z array
        if self._isMzArray:
            self.data['mzData'].append(ch)
        
        # get intensity array
        elif self._isIntArray:
            self.data['intData'].append(ch)
    # ----
    
    

class runHandler(xml.sax.handler.ContentHandler):
    """Get whole run."""
    
    def __init__(self):
        self.data = {}
        self.currentID = None
        
        self._isMzArray = False
        self._isIntArray = False
    # ----
    
    
    def startElement(self, name, attrs):
        """Element started."""
        
        # get scan metadata
        if name == 'spectrum':
            
            # get scan ID
            self.currentID = attrs.get('id', None)
            if self.currentID != None:
                self.currentID = int(self.currentID)
            
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
                'mzEndian': None,
                'mzPrecision': None,
                'intData': None,
                'intEndian': None,
                'intPrecision': None,
            }
            
            # add scan
            self.data[self.currentID] = scan
        
        # get spectrum type
        elif name == 'acqSpecification':
            attribute = attrs.get('spectrumType', False)
            if attribute:
                self.data[self.currentID]['spectrumType'] = attribute
        
        # get other params
        elif name == 'spectrumInstrument':
            
            # get ms level
            attribute = attrs.get('msLevel', 1)
            if attribute:
                self.data[self.currentID]['msLevel'] = int(attribute)
            
            # get low m/z
            attribute = attrs.get('mzRangeStart', None)
            if attribute != None:
                self.data[self.currentID]['lowMZ'] = float(attribute)
            
            # get high m/z
            attribute = attrs.get('mzRangeStop', None)
            if attribute != None:
                self.data[self.currentID]['highMZ'] = float(attribute)
        
        # get other params
        elif (name == 'userParam' or name == 'cvParam'):
            paramName = attrs.get('name','')
            paramValue = attrs.get('value', None)
            
            # get retention time
            if paramName == 'TimeInMinutes' and paramValue != None:
                try: self.data[self.currentID]['retentionTime'] = float(paramValue)*60
                except ValueError: pass
            
            # get total ion current
            elif paramName == 'TotalIonCurrent' and paramValue != None:
                try: self.data[self.currentID]['totIonCurrent'] = float(paramValue)
                except ValueError: pass
            
            # get precursor m/z
            elif paramName == 'MassToChargeRatio' and paramValue != None:
                try: self.data[self.currentID]['precursorMZ'] = float(paramValue)
                except ValueError: pass
            
            # get precursor m/z
            elif paramName == 'ChargeState' and paramValue != None:
                try: self.data[self.currentID]['precursorCharge'] = int(paramValue)
                except ValueError: pass
            
            # get polarity
            elif paramName == 'Polarity':
                if paramValue in ('positive', 'Positive', '+'):
                    self.data[self.currentID]['polarity'] = 1
                elif paramValue == ('negative', 'Negative', '-'):
                    self.data[self.currentID]['polarity'] = -1
        
        # get parent scan
        elif name == 'precursor':
            attribute = attrs.get('spectrumRef', None)
            if attribute != None:
                self.data[self.currentID]['parentScanNumber'] = int(attribute)
        
        # get mz data
        elif name == 'mzArrayBinary':
            self._isMzArray = True
            self.data[self.currentID]['mzData'] = []
        
        # get int data
        elif name == 'intenArrayBinary':
            self._isIntArray = True
            self.data[self.currentID]['intData'] = []
        
        # get data
        elif name == 'data':
            
            # get points count
            attribute = attrs.get('length', None)
            if attribute != None:
                self.data[self.currentID]['pointsCount'] = int(attribute)
            
            # get array params
            endian = attrs.get('endian','network')
            precision = attrs.get('precision', 32)
            
            if self._isMzArray:
                self.data[self.currentID]['mzEndian'] = endian
                if precision:
                    self.data[self.currentID]['mzPrecision'] = int(precision)
            
            elif self._isIntArray:
                self.data[self.currentID]['intEndian'] = endian
                if precision:
                    self.data[self.currentID]['intPrecision'] = int(precision)
    # ----
    
    
    def endElement(self, name):
        """Element ended."""
        
        # stop reading mz data
        if name == 'mzArrayBinary':
            self._isMzArray = False
            if not self.data[self.currentID]['mzData']:
                self.data[self.currentID]['mzData'] = None
            else:
                self.data[self.currentID]['mzData'] = ''.join(self.data[self.currentID]['mzData'])
        
        # stop reading int data
        elif name == 'intenArrayBinary':
            self._isIntArray = False
            if not self.data[self.currentID]['intData']:
                self.data[self.currentID]['intData'] = None
            else:
                self.data[self.currentID]['intData'] = ''.join(self.data[self.currentID]['intData'])
    # ----
    
    
    def characters(self, ch):
        """Grab characters."""
        
        # get m/z array
        if self._isMzArray:
            self.data[self.currentID]['mzData'].append(ch)
        
        # get intensity array
        elif self._isIntArray:
            self.data[self.currentID]['intData'].append(ch)
    # ----
    
    

class stopParsing(Exception):
    """Exeption to stop parsing XML data."""
    pass
