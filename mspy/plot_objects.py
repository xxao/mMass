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
import wx
import numpy
import copy

# load modules
import mod_signal
import calculations


# MAIN PLOT OBJECTS
# -----------------

class container:
    """Container to hold plot objects."""
    
    def __init__(self, objects):
        self.objects = objects
    # ----
    
    
    def __additem__(self, obj):
        self.objects.append(obj)
    # ----
    
    
    def __delitem__(self, index):
        del self.objects[index]
    # ----
    
    
    def __setitem__(self, index, obj):
        self.objects[index] = obj
    # ----
    
    
    def __getitem__(self, index):
        return self.objects[index]
    # ----
    
    
    def __len__(self):
        return len(self.objects)
    # ----
    
    
    def getBoundingBox(self, minX=None, maxX=None, absolute=False):
        """Get bounding box coverring all visible objects."""
        
        # init values if no data in objects
        rect = [numpy.array([0, 0]), numpy.array([1, 1])]
        
        # get bouding boxes from objects
        have = False
        for obj in self.objects:
            if obj.properties['visible']:
                oRect = obj.getBoundingBox(minX, maxX, absolute)
                
                if not oRect or not numpy.all(numpy.isfinite(oRect)):
                    continue
                elif have and oRect:
                    rect[0] = numpy.minimum(rect[0], oRect[0])
                    rect[1] = numpy.maximum(rect[1], oRect[1])
                elif oRect:
                    rect = oRect
                    have = True
        
        # check scale
        if rect[0][0] == rect[1][0]:
            rect[0][0] -= 0.5
            rect[1][0] += 0.5
        if rect[0][1] == rect[1][1]:
            rect[1][1] += 0.5
        
        return rect
    # ----
    
    
    def getLegend(self):
        """Get a list of legend names."""
        
        # get names
        names = []
        for obj in self.objects:
            if obj.properties['visible']:
                legend = obj.getLegend()
                if legend and legend[0] != '':
                    names.append(obj.getLegend())
            
        return names
    # ----
    
    
    def getPoint(self, obj, xPos, coord='screen'):
        """Get interpolated Y position for given X."""
        return self.objects[obj].getPoint(xPos, coord)
    # ----
    
    
    def countGels(self):
        """Get number of visible gels."""
        
        count = 0
        for obj in self.objects:
            if obj.properties['visible'] and obj.properties['showInGel']:
                count += 1
        
        return max(count,1)
    # ----
    
    
    def cropPoints(self, minX, maxX):
        """Crop points in all visible objects to selected X range."""
        
        for obj in self.objects:
            if obj.properties['visible']:
                obj.cropPoints(minX, maxX)
    # ----
    
    
    def scaleAndShift(self, scale, shift):
        """Scale and shift all visible objects."""
        
        for obj in self.objects:
            if obj.properties['visible']:
                obj.scaleAndShift(scale, shift)
    # ----
    
    
    def filterPoints(self, filterSize):
        """Filter points in all visible objects."""
        
        for obj in self.objects:
            if obj.properties['visible']:
                obj.filterPoints(filterSize)
    # ----
    
    
    def draw(self, dc, printerScale, overlapLabels, reverse):
        """Draw all visible objects."""
        
        # draw in reverse order
        if reverse:
            self.objects.reverse()
            
        # draw objects
        for obj in self.objects:
            if obj.properties['visible']:
                obj.draw(dc, printerScale)
        
        # draw object's labels
        self.drawLabels(dc, printerScale, overlapLabels)
        
        # reverse back order
        if reverse:
            self.objects.reverse()
    # ----
    
    
    def drawLabels(self, dc, printerScale, overlapLabels):
        """Draw labels for all visible objects."""
        
        # get labels from objects
        annots = []
        labels = []
        for obj in self.objects:
            if obj.properties['visible'] and isinstance(obj, annotations):
                annots += obj.makeLabels(dc, printerScale)
            elif obj.properties['visible']:
                labels += obj.makeLabels(dc, printerScale)
        
        # check labels
        if not annots and not labels:
            return
        
        # sort labels
        annots.sort()
        annots.reverse()
        labels.sort()
        labels.reverse()
        labels = annots + labels
        
        # preset font by first label
        font = labels[0][3]['labelFont']
        colour = labels[0][3]['labelColour']
        bgr = labels[0][3]['labelBgr']
        bgrColour = labels[0][3]['labelBgrColour']
        
        dc.SetFont(_scaleFont(font, printerScale['fonts']))
        dc.SetTextForeground(colour)
        dc.SetTextBackground(bgrColour)
        
        if bgr:
            dc.SetBackgroundMode(wx.SOLID)
        
        # draw labels
        occupied = []
        for label in labels:
            text = label[1]
            textCoords = label[2]
            properties = label[3]
            
            # check limits
            if abs(textCoords[1]) > 10000000:
                continue
            
            # check free space and draw label
            if overlapLabels or self._checkFreeSpace(textCoords, occupied):
                
                # check pen
                if properties['labelFont'] != font:
                    font = properties['labelFont']
                    dc.SetFont(_scaleFont(font, printerScale['fonts']))
                
                if properties['labelColour'] != colour:
                    colour = properties['labelColour']
                    dc.SetTextForeground(colour)
                
                #if properties['labelBgrColour'] != bgrColour:
                #    bgrColour = properties['labelBgrColour']
                #    dc.SetTextBackground(bgrColour)
                
                if properties['labelBgr'] != bgr:
                    bgr = properties['labelBgr']
                    if bgr:
                        dc.SetBackgroundMode(wx.SOLID)
                    else:
                        dc.SetBackgroundMode(wx.TRANSPARENT)
                
                # set angle
                angle = properties['labelAngle']
                if angle == 90 and properties['flipped']:
                    angle = -90
                
                # draw label
                dc.DrawRotatedText(text, textCoords[0], textCoords[1], angle)
                occupied.append(textCoords)
        
        dc.SetBackgroundMode(wx.TRANSPARENT)
    # ----
    
    
    def drawGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw gel for all allowed objects."""
        
        # draw objects
        for obj in self.objects:
            if obj.properties['visible'] and obj.properties['showInGel']:
                obj.drawGel(dc, gelCoords, gelHeight, printerScale)
                gelCoords[0] += gelHeight
    # ----
    
    
    def append(self, obj):
        self.objects.append(obj)
    # ----
    
    
    def empty(self):
        del self.objects[:]
    # ----
    
    
    def _checkFreeSpace(self, coords, occupied):
        """Check free space for label."""
        
        curX1, curY1, curX2, curY2 = coords
        
        # check occupied space
        for occX1, occY1, occX2, occY2 in occupied:
            if (curX1 < curX2) and ((occX1 <= curX1 <= occX2) or (occX1 <= curX2 <= occX2) or (curX1 <= occX1 and curX2 >= occX2)):
                if (occY2 <= curY1 <= occY1) or (occY2 <= curY2 <= occY1) or (curY1 >= occY1 and curY2 <= occY2):
                    return False
            elif (curX1 > curX2) and ((occX2 <= curX1 <= occX1) or (occX2 <= curX2 <= occX1) or (curX1 <= occX2 and curX2 >= occX1)):
                if (occY1 <= curY1 <= occY2) or (occY1 <= curY2 <= occY2) or (curY1 >= occY2 and curY2 <= occY1):
                    return False
        
        return True
    # ----
    


class annotations:
    """Base class for annotations drawing."""
    
    def __init__(self, points, **attr):
        
        # set default params
        self.properties = {
                            'visible': True,
                            'flipped': False,
                            'xOffset': 0,
                            'yOffset': 0,
                            'normalized': False,
                            'showInGel': False,
                            'exactFit': False,
                            'showPoints': True,
                            'showLabels': True,
                            'showXPos': True,
                            'pointColour': (0, 0, 255),
                            'pointSize': 3,
                            'labelAngle': 90,
                            'labelBgr': True,
                            'labelColour': (0, 0, 0),
                            'labelBgrColour': (255, 255, 255),
                            'labelFont': wx.Font(10, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0),
                            'labelMaxLength': 20,
                            'xPosDigits': 2,
                            }
        
        self.currentScale = (1., 1.)
        self.currentShift = (0., 0.)
        self.normalization = 1.0
        
        # get new attributes
        for name, value in attr.items():
            self.properties[name] = value
        
        # convert points to array
        self.points = numpy.array([[p[0], p[1]] for p in points])
        self.pointsCropped = self.points
        self.pointsScaled = self.pointsCropped
        if len(self.points):
            self.pointsBox = (numpy.minimum.reduce(self.points), numpy.maximum.reduce(self.points))
        
        # get labels
        self.labels = ['']*len(points)
        for x, point in enumerate(points):
            if len(point) > 2:
                self.labels[x] = point[2]
        self.labelsCropped = self.labels
        
        # calculate normalization
        self._normalization()
    # ----
    
    
    def setProperties(self, **attr):
        """Set object properties."""
        
        for name, value in attr.items():
            self.properties[name] = value
    # ----
    
    
    def setNormalization(self, value):
        """Force specified normalization to be used insted of calculated one."""
        
        value = float(value)
        if value == 0.0:
            value = 1.0
        
        self.normalization = value
    # ----
    
    
    def getBoundingBox(self, minX=None, maxX=None, absolute=False):
        """Get bounding box for whole data or X selection"""
        
        # use relevant data
        if minX != None and maxX != None:
            self.cropPoints(minX, maxX)
            data = self.pointsCropped
        else:
            data = self.points
        
        # check data
        if not len(data):
            return False
        
        # get range
        if minX != None and maxX != None:
            minXY = numpy.minimum.reduce(data)
            maxXY = numpy.maximum.reduce(data)
        else:
            minXY = [self.pointsBox[0][0], self.pointsBox[0][1]]
            maxXY = [self.pointsBox[1][0], self.pointsBox[1][1]]
        
        # extend values slightly to fit data
        if not absolute and not self.properties['exactFit']:
            xExtend = (maxXY[0] - minXY[0]) * 0.05
            yExtend = (maxXY[1] - minXY[1]) * 0.05
            minXY[0] -= xExtend
            maxXY[0] += xExtend
            minXY[1] -= yExtend
            maxXY[1] += yExtend
            
        # extend values to fit labels
        elif not absolute:
            if self.properties['showLabels'] and self.properties['labelAngle']==0:
                maxXY[1] += (maxXY[1] - minXY[1]) * 0.2
            elif self.properties['showLabels'] and self.properties['labelAngle']==90:
                maxXY[1] += (maxXY[1] - minXY[1]) * 0.4
            else:
                maxXY[1] += (maxXY[1] - minXY[1]) * 0.05
        
        # apply normalization
        if self.properties['normalized']:
            minXY[1] = minXY[1] / self.normalization
            maxXY[1] = maxXY[1] / self.normalization
        
        # apply offset
        minXY[0] += self.properties['xOffset']
        minXY[1] += self.properties['yOffset']
        maxXY[0] += self.properties['xOffset']
        maxXY[1] += self.properties['yOffset']
        
        # apply flipping
        if self.properties['flipped']:
            minY = -1 * maxXY[1]
            maxY = -1 * minXY[1]
            minXY[1] = minY
            maxXY[1] = maxY
        
        return [minXY, maxXY]
    # ----
    
    
    def getLegend(self):
        """Get legend."""
        return None
    # ----
    
    
    def cropPoints(self, minX, maxX):
        """Crop points to selected X range."""
        
        # apply offset
        minX -= self.properties['xOffset']
        maxX -= self.properties['xOffset']
        
        # get indexes of points in selection
        i1 = mod_signal.locate(self.points, minX)
        i2 = mod_signal.locate(self.points, maxX)
        
        # crop data
        self.pointsCropped = self.points[i1:i2]
        self.labelsCropped = self.labels[i1:i2]
    # ----
    
    
    def scaleAndShift(self, scale, shift):
        """Scale and shift points to screen coordinations."""
        
        self.pointsScaled = self.pointsCropped
        
        xScale = scale[0]
        yScale = scale[1]
        xShift = shift[0]
        yShift = shift[1]
        
        # apply flipping
        if self.properties['flipped']:
            yScale *= -1
        
        # apply normalization
        if self.properties['normalized']:
            yScale /= self.normalization
        
        # apply offset
        xShift += self.properties['xOffset'] * xScale
        yShift += self.properties['yOffset'] * yScale
        
        # recalculate data
        self.pointsScaled = _scaleAndShift(self.pointsCropped, xScale, yScale, xShift, yShift)
        
        self.currentScale = scale
        self.currentShift = shift
    # ----
    
    
    def filterPoints(self, filterSize):
        """Filter points for printing and exporting"""
        pass
    # ----
    
    
    def draw(self, dc, printerScale):
        """Draw object."""
        
        # check data
        if not len(self.pointsScaled):
            return
        
        # draw points
        if self.properties['showPoints']:
            pencolour = [max(x-70,0) for x in self.properties['pointColour']]
            pen = wx.Pen(pencolour, 1*printerScale['drawings'], wx.SOLID)
            brush = wx.Brush(self.properties['pointColour'], wx.SOLID)
            dc.SetPen(pen)
            dc.SetBrush(brush)
            for point in self.pointsScaled:
                dc.DrawCircle(point[0], point[1], self.properties['pointSize']*printerScale['drawings'])
    # ----
    
    
    def drawGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw gel."""
        pass
    # ----
    
    
    def makeLabels(self, dc, printerScale):
        """Get object labels."""
        
        # check labels
        if not self.properties['showLabels'] or not self.labelsCropped:
            return []
        
        # set font
        dc.SetFont(_scaleFont(self.properties['labelFont'], printerScale['fonts']))
        
        # prepare labels
        labels = []
        format = '%0.'+`self.properties['xPosDigits']`+'f - '
        for x, label in enumerate(self.labelsCropped):
            
            # check max length
            if len(label) > self.properties['labelMaxLength']:
                label = label[:self.properties['labelMaxLength']] + '...'
            
            # add X position
            if self.properties['showXPos']:
                label = (format % self.pointsCropped[x][0]) + label
            
            # get position
            xPos = self.pointsScaled[x][0]
            yPos = self.pointsScaled[x][1]
            
            # get text position
            textSize = dc.GetTextExtent(label)
            if self.properties['labelAngle'] == 90:
                if self.properties['flipped']:
                    textXPos = xPos + textSize[1]*0.5
                    textYPos = yPos + 5*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos-textSize[1], textYPos+textSize[0])
                else:
                    textXPos = xPos - textSize[1]*0.5
                    textYPos = yPos - 5*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[1], textYPos-textSize[0])
            
            elif self.properties['labelAngle'] == 0:
                if self.properties['flipped']:
                    textXPos = xPos - textSize[0]*0.5
                    textYPos = yPos + 4*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[0], textYPos-textSize[1])
                else:
                    textXPos = xPos - textSize[0]*0.5
                    textYPos = yPos - textSize[1] - 4*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[0], textYPos-textSize[1])
            
            # add label and sort by intensity
            labels.append((self.pointsCropped[x][1], label, textCoords, self.properties))
            
        return labels
    # ----
    
    
    def _normalization(self):
        """Calculate normalization constants."""
        
        normalization = 1.0
        
        # calc normalization
        if len(self.points):
            normalization = self.pointsBox[1][1] / 100.
        
        # check value
        if normalization == 0.0:
            normalization = 1.0
        
        # set value
        self.normalization = normalization
    # ----
    


class points:
    """Base class for polypoints and polylines drawing."""
    
    def __init__(self, points, **attr):
        
        # set default params
        self.properties = {
                            'legend': '',
                            'visible': True,
                            'flipped': False,
                            'xOffset': 0,
                            'yOffset': 0,
                            'normalized': False,
                            'showInGel': False,
                            'exactFit': False,
                            'showPoints': True,
                            'pointColour': (0, 0, 255),
                            'pointSize': 3,
                            'fillPoints': True,
                            'showLines': True,
                            'lineColour': (0, 0, 255),
                            'lineWidth': 1,
                            'lineStyle': wx.SOLID,
                            'xOffsetDigits': 2,
                            'yOffsetDigits': 0,
                            }
        
        
        self.currentScale = (1., 1.)
        self.currentShift = (0., 0.)
        self.normalization = 1.0
        
        # get new attributes
        for name, value in attr.items():
            self.properties[name] = value
        
        # convert points to array
        self.points = numpy.array(points)
        self.cropped = self.points
        self.scaled = self.cropped
        if len(self.points):
            self.pointsBox = (numpy.minimum.reduce(self.points), numpy.maximum.reduce(self.points))
        
        # calculate normalization
        self._normalization()
    # ----
    
    
    def setProperties(self, **attr):
        """Set object properties."""
        
        for name, value in attr.items():
            self.properties[name] = value
    # ----
    
    
    def setNormalization(self, value):
        """Force specified normalization to be used insted of calculated one."""
        
        value = float(value)
        if value == 0.0:
            value = 1.0
        
        self.normalization = value
    # ----
    
    
    def getBoundingBox(self, minX=None, maxX=None, absolute=False):
        """Get bounding box for whole data or X selection"""
        
        # use relevant data
        if minX != None and maxX != None:
            self.cropPoints(minX, maxX)
            data = self.cropped
        else:
            data = self.points
        
        # check data
        if not len(data):
            return False
        
        # get range
        if minX != None and maxX != None:
            minXY = numpy.minimum.reduce(data)
            maxXY = numpy.maximum.reduce(data)
        else:
            minXY = [self.pointsBox[0][0], self.pointsBox[0][1]]
            maxXY = [self.pointsBox[1][0], self.pointsBox[1][1]]
        
        # extend values slightly to fit data
        if not absolute and not self.properties['exactFit']:
            xExtend = (maxXY[0] - minXY[0]) * 0.05
            yExtend = (maxXY[1] - minXY[1]) * 0.05
            minXY[0] -= xExtend
            maxXY[0] += xExtend
            minXY[1] -= yExtend
            maxXY[1] += yExtend
        
        # apply normalization
        if self.properties['normalized']:
            minXY[1] = minXY[1] / self.normalization
            maxXY[1] = maxXY[1] / self.normalization
        
        # apply offset
        minXY[0] += self.properties['xOffset']
        minXY[1] += self.properties['yOffset']
        maxXY[0] += self.properties['xOffset']
        maxXY[1] += self.properties['yOffset']
        
        # apply flipping
        if self.properties['flipped']:
            minY = -1 * maxXY[1]
            maxY = -1 * minXY[1]
            minXY[1] = minY
            maxXY[1] = maxY
        
        return [minXY, maxXY]
    # ----
    
    
    def getLegend(self):
        """Get legend."""
        
        # get legend
        legend = self.properties['legend']
        offset = ''
        
        # add current offset
        if not self.properties['normalized']:
            if self.properties['xOffset']:
                format = ' X%0.'+`self.properties['xOffsetDigits']`+'f'
                offset += format % self.properties['xOffset']
            if self.properties['yOffset']:
                format = ' Y%0.'+`self.properties['yOffsetDigits']`+'f'
                offset += format % self.properties['yOffset']
            if legend and offset:
                legend += ' (Offset%s)' % offset
        
        # set colour
        if self.properties['showPoints']:
            return (legend, self.properties['pointColour'])
        else:
            return (legend, self.properties['lineColour'])
    # ----
    
    
    def cropPoints(self, minX, maxX):
        """Crop points to selected X range."""
        
        # apply offset
        minX -= self.properties['xOffset']
        maxX -= self.properties['xOffset']
        
        # crop line
        if self.properties['showLines']:
            self.cropped = mod_signal.crop(self.points, minX, maxX)
        
        # crop points
        else:
            i1 = mod_signal.locate(self.points, minX)
            i2 = mod_signal.locate(self.points, maxX)
            self.cropped = self.points[i1:i2]
    # ----
    
    
    def scaleAndShift(self, scale, shift):
        """Scale and shift points to screen coordinations."""
        
        self.scaled = self.cropped
        
        xScale = scale[0]
        yScale = scale[1]
        xShift = shift[0]
        yShift = shift[1]
        
        # apply flipping
        if self.properties['flipped']:
            yScale *= -1
        
        # apply normalization
        if self.properties['normalized']:
            yScale /= self.normalization
        
        # apply offset
        xShift += self.properties['xOffset'] * xScale
        yShift += self.properties['yOffset'] * yScale
        
        # recalculate data
        if len(self.cropped):
            self.scaled = _scaleAndShift(self.cropped, xScale, yScale, xShift, yShift)
        
        self.currentScale = scale
        self.currentShift = shift
    # ----
    
    
    def filterPoints(self, filterSize):
        """Filter points for printing and exporting"""
        
        # filter data
        if len(self.scaled) and self.properties['showLines']:
            self.scaled = _filterPoints(self.scaled, filterSize)
    # ----
    
    
    def draw(self, dc, printerScale):
        """Draw object."""
        
        # check data
        if not len(self.scaled):
            return
        
        # draw lines
        if self.properties['showLines'] and len(self.scaled) > 1:
            
            pen = wx.Pen(self.properties['lineColour'], self.properties['lineWidth']*printerScale['drawings'], self.properties['lineStyle'])
            brush = wx.Brush(self.properties['lineColour'], wx.SOLID)
            
            dc.SetPen(pen)
            dc.SetBrush(brush)
            dc.DrawLines(self.scaled)
        
        # draw points
        if self.properties['showPoints']:
            
            if self.properties['fillPoints']:
                pencolour = [max(x-70,0) for x in self.properties['pointColour']]
                pen = wx.Pen(pencolour, self.properties['lineWidth']*printerScale['drawings'], wx.SOLID)
                brush = wx.Brush(self.properties['pointColour'], wx.SOLID)
            else:
                pencolour = self.properties['pointColour']
                pen = wx.Pen(pencolour, self.properties['lineWidth']*printerScale['drawings'], wx.SOLID)
                brush = wx.TRANSPARENT_BRUSH
            
            dc.SetPen(pen)
            dc.SetBrush(brush)
            for point in self.scaled:
                dc.DrawCircle(point[0], point[1], self.properties['pointSize']*printerScale['drawings'])
    # ----
    
    
    def drawGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw gel."""
        pass
    # ----
    
    
    def makeLabels(self, dc, printerScale):
        """Get object labels."""
        return []
    # ----
    
    
    def _normalization(self):
        """Calculate normalization constants."""
        
        normalization = 1.0
        
        # calc normalization
        if len(self.points):
            normalization = self.pointsBox[1][1] / 100.
        
        # check value
        if normalization == 0.0:
            normalization = 1.0
        
        # set value
        self.normalization = normalization
    # ----
    


class spectrum:
    """Base class for spectrum drawing."""
    
    def __init__(self, scan, **attr):
        
        # set default params
        self.properties = {
                            'legend': '',
                            'visible': True,
                            'flipped': False,
                            'xOffset': 0,
                            'yOffset': 0,
                            'normalized': False,
                            'showInGel': True,
                            'showSpectrum': True,
                            'showPoints': True,
                            'showLabels': True,
                            'showIsotopicLabels': True,
                            'showTicks': True,
                            'showGelLegend': True,
                            'spectrumColour': (0, 0, 255),
                            'spectrumWidth': 1,
                            'spectrumStyle': wx.SOLID,
                            'labelAngle': 90,
                            'labelDigits': 2,
                            'labelCharge': False,
                            'labelGroup': False,
                            'labelBgr': True,
                            'labelColour': (0, 0, 0),
                            'labelBgrColour': (255, 255, 255),
                            'labelFont': wx.Font(10, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0),
                            'tickColour': (200, 200, 200),
                            'isotopeColour': None,
                            'msmsColour': None,
                            'tickWidth': 1,
                            'tickStyle': wx.SOLID,
                            'xOffsetDigits': 2,
                            'yOffsetDigits': 0,
                            }
        
        self.currentScale = (1., 1.)
        self.currentShift = (0., 0.)
        self.normalization = 1.0
        
        # get new attributes
        for name, value in attr.items():
            self.properties[name] = value
        
        # convert spectrum points to array
        self.spectrumPoints = numpy.array(scan.profile)
        self.spectrumCropped = self.spectrumPoints
        self.spectrumScaled = self.spectrumCropped
        if len(self.spectrumPoints):
            self.spectrumBox = (numpy.minimum.reduce(self.spectrumPoints), numpy.maximum.reduce(self.spectrumPoints))
        
        # convert peaklist points to array
        self.peaklist = copy.deepcopy(scan.peaklist)
        self.peaklistPoints = numpy.array([[peak.mz, peak.ai, peak.base] for peak in scan.peaklist])
        self.peaklistCropped = self.peaklistPoints
        self.peaklistScaled = self.peaklistCropped
        self.peaklistCroppedPeaks = self.peaklist[:]
        if len(self.peaklistPoints):
            self.peaklistBox = (numpy.minimum.reduce(self.peaklistPoints), numpy.maximum.reduce(self.peaklistPoints))
        
        # calculate normalization
        self._normalization()
    # ----
    
    
    def setProperties(self, **attr):
        """Set object properties."""
        
        for name, value in attr.items():
            self.properties[name] = value
    # ----
    
    
    def setNormalization(self, value):
        """Force specified normalization to be used insted of calculated one."""
        
        value = float(value)
        if value == 0.0:
            value = 1.0
        
        self.normalization = value
    # ----
    
    
    def getBoundingBox(self, minX=None, maxX=None, absolute=False):
        """Get bounding box for whole data or X selection."""
        
        spectrumBox = None
        peaklistBox = None
        
        # use relevant data
        if minX != None and maxX != None:
            self.cropPoints(minX, maxX)
            spectrumData = self.spectrumCropped
            peaklistData = self.peaklistCropped
        else:
            spectrumData = self.spectrumPoints
            peaklistData = self.peaklistPoints
        
        # calculate bounding box for spectrum
        if len(spectrumData) and self.properties['showSpectrum']:
            if minX != None and maxX != None:
                minXY = numpy.minimum.reduce(spectrumData)
                maxXY = numpy.maximum.reduce(spectrumData)
            else:
                minXY = [self.spectrumBox[0][0], self.spectrumBox[0][1]]
                maxXY = [self.spectrumBox[1][0], self.spectrumBox[1][1]]
            
            if not absolute:
                maxXY[1] += (maxXY[1] - minXY[1]) * 0.05
            
            spectrumBox = [minXY, maxXY]
        
        # calculate bounding box for peaklist
        if len(peaklistData) and (self.properties['showSpectrum'] or self.properties['showLabels'] or self.properties['showTicks']):
            if minX != None and maxX != None:
                minXY = numpy.minimum.reduce(peaklistData)
                maxXY = numpy.maximum.reduce(peaklistData)
            else:
                minXY = [self.peaklistBox[0][0], self.peaklistBox[0][1], self.peaklistBox[0][2]]
                maxXY = [self.peaklistBox[1][0], self.peaklistBox[1][1], self.peaklistBox[1][2]]
            
            minXY = [minXY[0], min(minXY[1:])]
            maxXY = [maxXY[0], max(maxXY[1:])]
            
            # extend values to fit labels
            if not absolute:
                xExtend = (maxXY[0] - minXY[0]) * 0.02
                minXY[0] -= xExtend
                maxXY[0] += xExtend
                
                if self.properties['showLabels'] and self.properties['labelAngle']==0:
                    maxXY[1] += (maxXY[1] - minXY[1]) * 0.2
                elif self.properties['showLabels'] and self.properties['labelAngle']==90:
                    maxXY[1] += (maxXY[1] - minXY[1]) * 0.4
                else:
                    maxXY[1] += (maxXY[1] - minXY[1]) * 0.05
            
            peaklistBox = [minXY, maxXY]
        
        # use both
        if spectrumBox and peaklistBox:
            minXY, maxXY = [numpy.minimum(spectrumBox[0], peaklistBox[0]), numpy.maximum(spectrumBox[1], peaklistBox[1])]
        elif spectrumBox:
            minXY, maxXY = spectrumBox
        elif peaklistBox:
            minXY, maxXY = peaklistBox
        else:
            return False
        
        # apply normalization
        if self.properties['normalized']:
            minXY[1] = minXY[1] / self.normalization
            maxXY[1] = maxXY[1] / self.normalization
        
        # apply offset
        if not self.properties['normalized']:
            minXY[0] += self.properties['xOffset']
            minXY[1] += self.properties['yOffset']
            maxXY[0] += self.properties['xOffset']
            maxXY[1] += self.properties['yOffset']
        
        # apply flipping
        if self.properties['flipped']:
            minY = -1 * maxXY[1]
            maxY = -1 * minXY[1]
            minXY[1] = minY
            maxXY[1] = maxY
        
        return [minXY, maxXY]
    # ----
    
    
    def getLegend(self):
        """Get legend."""
        
        # get legend
        legend = self.properties['legend']
        offset = ''
        
        # add current offset
        if not self.properties['normalized']:
            if self.properties['xOffset']:
                format = ' X%0.'+`self.properties['xOffsetDigits']`+'f'
                offset += format % self.properties['xOffset']
            if self.properties['yOffset']:
                format = ' Y%0.'+`self.properties['yOffsetDigits']`+'f'
                offset += format % self.properties['yOffset']
            if legend and offset:
                legend += ' (Offset%s)' % offset
        
        # set colour
        if len(self.spectrumPoints) and self.properties['showSpectrum']:
            return (legend, self.properties['spectrumColour'])
        else:
            return (legend, self.properties['tickColour'])
    # ----
    
    
    def getPoint(self, xPos, coord='screen'):
        """Get interpolated Y position for given X."""
        
        # get relevant data
        if coord == 'user':
            points = self.spectrumCropped
        else:
            points = self.spectrumScaled
        
        # check data
        if not len(points):
            return None
        
        # get xPos index
        index = mod_signal.locate(points, xPos)
        if index == 0 or index == len(points):
            return None
        
        # get yPos
        yPos = mod_signal.interpolate(points[index-1], points[index], x=xPos)
        
        return [xPos, yPos]
    # ----
    
    
    def cropPoints(self, minX, maxX):
        """Crop points to selected X range."""
        
        # apply offset
        minX -= self.properties['xOffset']
        maxX -= self.properties['xOffset']
        
        # crop spectrum data
        if self.properties['showSpectrum']:
            self.spectrumCropped = mod_signal.crop(self.spectrumPoints, minX, maxX)
        
        # crop peaklist data
        if self.properties['showSpectrum'] or self.properties['showLabels'] or self.properties['showTicks']:
            i1 = mod_signal.locate(self.peaklistPoints, minX)
            i2 = mod_signal.locate(self.peaklistPoints, maxX)
            self.peaklistCropped = self.peaklistPoints[i1:i2]
            self.peaklistCroppedPeaks = self.peaklist[i1:i2]
    # ----
    
    
    def scaleAndShift(self, scale, shift):
        """Scale and shift points to screen coordinations."""
        
        self.spectrumScaled = self.spectrumCropped
        self.peaklistScaled = self.peaklistCropped
        
        xScale = scale[0]
        yScale = scale[1]
        xShift = shift[0]
        yShift = shift[1]
        
        # apply flipping
        if self.properties['flipped']:
            yScale *= -1
        
        # apply normalization
        if self.properties['normalized']:
            yScale /= self.normalization
        
        # apply offset
        if not self.properties['normalized']:
            xShift += self.properties['xOffset'] * xScale
            yShift += self.properties['yOffset'] * yScale
        
        # scale and shift spectrum data
        if len(self.spectrumCropped):
            self.spectrumScaled = _scaleAndShift(self.spectrumCropped, xScale, yScale, xShift, yShift)
        
        # scale and shift peaklist data
        if len(self.peaklistCropped):
            self.peaklistScaled = numpy.array((xScale, yScale, yScale)) * self.peaklistCropped + numpy.array((xShift, yShift, yShift))
        
        self.currentScale = scale
        self.currentShift = shift
    # ----
    
    
    def filterPoints(self, filterSize):
        """Filter spectrum points invisible in current resolution."""
        
        # filter spectrum data
        if len(self.spectrumScaled) and self.properties['showSpectrum']:
            self.spectrumScaled = _filterPoints(self.spectrumScaled, filterSize)
    # ----
    
    
    def draw(self, dc, printerScale):
        """Draw object."""
        
        # draw line spectrum
        if len(self.spectrumScaled) > 2 and self.properties['showSpectrum']:
            self._drawSpectrum(dc, printerScale)
        
        # draw peaklist ticks
        if len(self.peaklistScaled) and (self.properties['showTicks'] or not len(self.spectrumPoints)):
            self._drawPeaklist(dc, printerScale)
    # ----
    
    
    def drawGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw gel."""
        
        # draw line spectrum gel
        if len(self.spectrumScaled) > 2 and self.properties['showSpectrum']:
            self._drawSpectrumGel(dc, gelCoords, gelHeight, printerScale)
        
        # draw peaklist gel
        elif len(self.peaklistScaled) and (self.properties['showSpectrum'] or self.properties['showLabels'] or self.properties['showTicks']):
            self._drawPeaklistGel(dc, gelCoords, gelHeight, printerScale)
        
        # draw gel legend
        self._drawGelLegend(dc, gelCoords, gelHeight, printerScale)
    # ----
    
    
    def makeLabels(self, dc, printerScale):
        """Get object labels."""
        
        # check labels
        if not self.properties['showLabels'] or not len(self.peaklistScaled):
            return []
        
        # set font
        dc.SetFont(_scaleFont(self.properties['labelFont'], printerScale['fonts']))
        
        # prepare labels
        labels = []
        format = '%0.'+`self.properties['labelDigits']`+'f'
        for x, peak in enumerate(self.peaklistScaled):
            
            # skip isotopes
            if not self.properties['showIsotopicLabels'] and self.peaklistCroppedPeaks[x].isotope != 0:
                continue
            
            # get position
            xPos = peak[0]
            yPos = peak[1]
            
            # get label
            label = format % self.peaklistCroppedPeaks[x].mz
            
            # add charge to label
            if self.properties['labelCharge'] and self.peaklistCroppedPeaks[x].charge != None:
                label += ' (%d)' % self.peaklistCroppedPeaks[x].charge
            
            # add group to label
            if self.properties['labelGroup'] and self.peaklistCroppedPeaks[x].group:
                label += ' [%s]' % self.peaklistCroppedPeaks[x].group
            
            # get text position
            textSize = dc.GetTextExtent(label)
            if self.properties['labelAngle'] == 90:
                if self.properties['flipped']:
                    textXPos = xPos + textSize[1]*0.5
                    textYPos = yPos + 5*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos-textSize[1], textYPos+textSize[0])
                else:
                    textXPos = xPos - textSize[1]*0.5
                    textYPos = yPos - 5*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[1], textYPos-textSize[0])
            
            elif self.properties['labelAngle'] == 0:
                if self.properties['flipped']:
                    textXPos = xPos - textSize[0]*0.5
                    textYPos = yPos + 4*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[0], textYPos-textSize[1])
                else:
                    textXPos = xPos - textSize[0]*0.5
                    textYPos = yPos - textSize[1] - 4*printerScale['drawings']
                    textCoords = (textXPos, textYPos, textXPos+textSize[0], textYPos-textSize[1])
            
            # add label and sort by intensity
            labels.append((self.peaklistCroppedPeaks[x].ai, label, textCoords, self.properties))
            
        return labels
    # ----
    
    
    def _drawSpectrum(self, dc, printerScale):
        """Draw spectrum lines."""
        
        # set pen and brush
        pen = wx.Pen(self.properties['spectrumColour'], self.properties['spectrumWidth']*printerScale['drawings'], self.properties['spectrumStyle'])
        brush = wx.Brush(self.properties['spectrumColour'], wx.SOLID)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        
        # draw lines
        dc.DrawLines(self.spectrumScaled)
        
        # set pen for points
        pen = wx.Pen(self.properties['spectrumColour'], self.properties['spectrumWidth']*printerScale['drawings'], wx.SOLID)
        dc.SetPen(pen)
        
        # draw points if it makes sense
        count = len(self.spectrumScaled)
        if self.properties['showPoints'] \
            and count > 2 \
            and (self.spectrumScaled[2][0] - self.spectrumScaled[1][0]) > (6*printerScale['drawings']) \
            and ((self.spectrumScaled[-1][0] - self.spectrumScaled[0][0]) / count) > (6*printerScale['drawings']):
            
            for point in self.spectrumScaled:
                try: dc.DrawCircle(point[0], point[1], 2*printerScale['drawings'])
                except OverflowError: pass
    # ----
    
    
    def _drawSpectrumGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw spectrum gel."""
        
        # get plot coordinates
        gelY1, plotX1, plotY1, plotX2, plotY2, zeroY = gelCoords
        
        # correct zero
        if self.properties['flipped'] and (plotY1 < zeroY < plotY2):
            plotY1 = zeroY
            shift = zeroY
        elif (plotY1 < zeroY < plotY2):
            plotY2 = zeroY
            shift = plotY1
        else:
            shift = plotY1
        
        # set color step
        step = (plotY2 - plotY1) / 255
        if step == 0:
            return False
        
        # init brush
        dc.SetPen(wx.TRANSPARENT_PEN)
        brush = wx.Brush((255,255,255), wx.SOLID)
        dc.SetBrush(brush)
        
        # get first point and color
        lastX = round(self.spectrumScaled[0][0])
        lastY = 255
        previousX = lastX
        previousY = lastY
        maxY = 255
        
        # draw gel
        for point in self.spectrumScaled:
            
            # get point
            xPos = round(point[0])
            intens = round((point[1] - shift)/step)
            intens = min(intens, 255)
            intens = max(intens, 0)
            
            # reverse color for flipped spectra
            if self.properties['flipped']:
                intens = 255 - intens
            
            # filter points
            if xPos-lastX >= printerScale['drawings']:
                
                # set color if different
                if lastY != maxY:
                    brush.SetColour((maxY, maxY, maxY))
                    dc.SetBrush(brush)
                    
                # draw point rectangle
                try: dc.DrawRectangle(lastX, gelY1, xPos-lastX, gelHeight)
                except: pass
                
                # empty space
                if maxY < previousY and xPos-previousX > printerScale['drawings']:
                    maxY = previousY
                    brush.SetColour((maxY, maxY, maxY))
                    dc.SetBrush(brush)
                    try: dc.DrawRectangle(lastX+printerScale['drawings'], gelY1, xPos-(lastX+printerScale['drawings']), gelHeight)
                    except: pass
                
                # save last
                lastX = xPos
                lastY = maxY
                maxY = intens
            
            # remember previous
            previousX = xPos
            previousY = intens
                
            # get highest intensity
            maxY = min(intens, maxY)
    # ----
    
    
    def _drawPeaklist(self, dc, printerScale):
        """Draw peaklist ticks."""
        
        # set pen params
        peakPen = wx.Pen(self.properties['tickColour'], self.properties['tickWidth']*printerScale['drawings'], self.properties['tickStyle'])
        isotopePen = wx.Pen(self.properties['tickColour'], self.properties['tickWidth']*printerScale['drawings'], self.properties['tickStyle'])
        peakBrush = wx.Brush(self.properties['tickColour'], wx.SOLID)
        msmsBrush = wx.Brush(self.properties['tickColour'], wx.SOLID)
        
        if self.properties['isotopeColour']:
            isotopePen.SetColour(self.properties['isotopeColour'])
        if self.properties['msmsColour']:
            msmsBrush.SetColour(self.properties['msmsColour'])
        
        # draw isotopes
        dc.SetPen(isotopePen)
        for x, peak in enumerate(self.peaklistScaled):
            if self.peaklistCroppedPeaks[x].isotope != 0:
                try:
                    dc.DrawLine(peak[0], peak[2], peak[0], peak[1])
                    dc.DrawLine(peak[0]-3*printerScale['drawings'], peak[2], peak[0]+3*printerScale['drawings'], peak[2])
                except OverflowError:
                    pass
        
        # draw peaks
        dc.SetPen(peakPen)
        dc.SetBrush(peakBrush)
        for x, peak in enumerate(self.peaklistScaled):
            if self.peaklistCroppedPeaks[x].isotope == 0:
                try:
                    dc.DrawLine(peak[0], peak[2], peak[0], peak[1])
                    dc.DrawLine(peak[0]-3*printerScale['drawings'], peak[2], peak[0]+3*printerScale['drawings'], peak[2])
                    dc.DrawRectangle(peak[0]-1*printerScale['drawings'], peak[1]-1*printerScale['drawings'], 3*printerScale['drawings'], 3*printerScale['drawings'])
                except OverflowError:
                    pass
        
        # draw fragmentation mark
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(msmsBrush)
        for x, peak in enumerate(self.peaklistScaled):
            if self.peaklistCroppedPeaks[x].childScanNumber != None:
                try: dc.DrawCircle(peak[0], peak[1], 3*printerScale['drawings'])
                except OverflowError: pass
    # ----
    
    
    def _drawPeaklistGel(self, dc, gelCoords, gelHeight, printerScale):
        """Draw peaklist gel."""
        
        # get plot coordinates
        gelY1, plotX1, plotY1, plotX2, plotY2, zeroY = gelCoords
        
        # correct zero
        if self.properties['flipped'] and (plotY1 < zeroY < plotY2):
            plotY1 = zeroY
            shift = zeroY
        elif (plotY1 < zeroY < plotY2):
            plotY2 = zeroY
            shift = plotY1
        else:
            shift = plotY1
        
        # set color step
        step = (plotY2 - plotY1) / 255
        if step == 0:
            return False
        
        # init brush
        dc.SetPen(wx.TRANSPARENT_PEN)
        brush = wx.Brush((255,255,255), wx.SOLID)
        dc.SetBrush(brush)
        
        # get first point and color
        lastX = round(self.peaklistScaled[0][0])
        lastY = 255
        maxY = 255
        
        # draw rectangles
        last = len(self.peaklistScaled)-1
        for x, point in enumerate(self.peaklistScaled):
            
            # get intensity colour
            xPos = round(point[0])
            intens = round((point[1] - shift)/step)
            intens = min(intens, 255)
            intens = max(intens, 0)
            
            # reverse color for flipped spectra
            if self.properties['flipped']:
                intens = 255 - intens
            
            # draw first
            if x==0:
                brush.SetColour((intens, intens, intens))
                dc.SetBrush(brush)
                try: dc.DrawRectangle(xPos, gelY1, printerScale['drawings'], gelHeight)
                except: pass
                lastY = maxY
                maxY = intens
            
            # filter points
            if xPos-lastX >= printerScale['drawings']:
                
                # set color if different
                if lastY != maxY:
                    brush.SetColour((maxY, maxY, maxY))
                    dc.SetBrush(brush)
                    
                # draw peak line
                try: dc.DrawRectangle(lastX, gelY1, printerScale['drawings'], gelHeight)
                except: pass
                
                # save last
                lastX = xPos
                lastY = maxY
                maxY = intens
                
                # draw last
                if x==last:
                    brush.SetColour((maxY, maxY, maxY))
                    dc.SetBrush(brush)
                    try: dc.DrawRectangle(xPos, gelY1, printerScale['drawings'], gelHeight)
                    except: pass
                
                continue
                
            # get highest intensity
            maxY = min(intens, maxY)
    # ----
    
    
    def _drawGelLegend(self, dc, gelCoords, gelHeight, printerScale):
        """docstring for _drawGelLegend"""
        
        # get plot coordinates
        gelY1, plotX1, plotY1, plotX2, plotY2, zeroY = gelCoords
        
        # get colour
        if len(self.spectrumPoints) and self.properties['showSpectrum']:
            colour = self.properties['spectrumColour']
        else:
            colour = self.properties['tickColour']
        
        # set dc
        pencolour = [max(i-70,0) for i in colour]
        pen = wx.Pen(pencolour, 1*printerScale['drawings'], wx.SOLID)
        dc.SetPen(pen)
        dc.SetTextForeground(colour)
        dc.SetBrush(wx.Brush(colour, wx.SOLID))
        
        # draw legend circle
        x = plotX2 - 9 * printerScale['drawings']
        y = gelY1 + (gelHeight)/2
        dc.DrawCircle(x, y, 3*printerScale['drawings'])
        
        # draw legend text
        if self.properties['showGelLegend'] and self.properties['legend']:
            textSize = dc.GetTextExtent(self.properties['legend'])
            x = plotX2 - textSize[0] - 17*printerScale['drawings']
            y = gelY1 + gelHeight/2 - textSize[1]/2
            dc.DrawText(self.properties['legend'], x, y)
    # ----
    
    
    def _normalization(self):
        """Calculate normalization constants."""
        
        normalization = 0.0
        
        # get range from points and peaklist
        if len(self.spectrumPoints) and len(self.peaklistPoints):
            spectrumMinXY, spectrumMaxXY = self.spectrumBox
            peaklistMinXY, peaklistMaxXY = self.peaklistBox
            normalization = max(spectrumMaxXY[1], peaklistMaxXY[1]) / 100.
        
        # get range from points only
        elif len(self.spectrumPoints):
            minXY, maxXY = self.spectrumBox
            normalization = maxXY[1] / 100.
        
        # get range from peaklist only
        elif len(self.peaklistPoints):
            minXY, maxXY = self.peaklistBox
            normalization = maxXY[1] / 100.
        
        # check value
        if normalization == 0.0:
            normalization = 1.0
        
        # set value
        self.normalization = normalization
    # ----
    
    


# HELPERS
# -------

def _scaleFont(font, scale):
    """Scale font."""
    
    # check printerScale
    if scale == 1:
        return font
    
    # get font
    pointSize = font.GetPointSize()
    family = font.GetFamily()
    style = font.GetStyle()
    weight = font.GetWeight()
    underline = font.GetUnderlined()
    faceName = font.GetFaceName()
    encoding = font.GetDefaultEncoding()
    
    # scale pointSize
    pointSize = pointSize * scale * 1.3
    
    # make print font
    printerFont = wx.Font(pointSize, family, style, weight, underline, faceName, encoding)
    
    return printerFont
# ----


def _scaleAndShift(points, scaleX, scaleY, shiftX, shiftY):
    """Scale and shift signal points used by plot. New array is returned.
        points (numpy array) - data points
        scaleX (float) - x-axis scale
        scaleY (float) - y-axis scale
        shiftX (float) - x-axis shift
        shiftY (float) - y-axis shift
    """
    
    # check signal type
    if not isinstance(points, numpy.ndarray):
        raise TypeError, "Signal points must be NumPy array!"
    if points.dtype.name != 'float64':
        raise TypeError, "Signal points must be float64!"
    
    # check signal data
    if len(points) == 0:
        return numpy.array([])
    
    # scale and shift signal
    return calculations.signal_rescale(points, float(scaleX), float(scaleY), float(shiftX), float(shiftY))
# ----


def _filterPoints(points, resolution):
    """Filter signal points according to resolution. New array is returned.
        points (numpy array) - data points
        resolution (float) - resolution point size
    """
    
    # check signal type
    if not isinstance(points, numpy.ndarray):
        raise TypeError, "Signal points must be NumPy array!"
    if points.dtype.name != 'float64':
        raise TypeError, "Signal points must be float64!"
    
    # check signal data
    if len(points) == 0:
        return numpy.array([])
    
    # filter signal
    return calculations.signal_filter(points, float(resolution))
# ----


