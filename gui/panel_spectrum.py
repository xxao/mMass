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

# load modules
from ids import *
import mwx
import images
import config
import mspy
import mspy.plot


# SPECTRUM PANEL WITH CANVAS AND TOOLBAR
# --------------------------------------

class panelSpectrum(wx.Panel):
    """Make spectrum panel."""
    
    def __init__(self, parent, documents):
        wx.Panel.__init__(self, parent, -1, size=(100, 100), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.parent = parent
        
        self.documents = documents
        self.currentDocument = None
        self.currentTmpSpectrum = None
        self.currentTmpSpectrumFlip = False
        self.currentNotationMarks = None
        self.currentTool = 'ruler'
        
        # init container
        self.container = mspy.plot.container([])
        obj = mspy.plot.points([], showInGel=False)
        self.container.append(obj)
        obj = mspy.plot.points([], showInGel=False)
        self.container.append(obj)
        
        # make GUI
        self.makeGUI()
        
        # select default tool
        self.setCurrentTool(self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # init spectrum canvas
        self.makeSpectrumCanvas()
        
        # init toolbar
        toolbar = self.makeToolbar()
        
        # pack gui elements
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.spectrumCanvas, 1, wx.EXPAND)
        sizer.Add(toolbar, 0, wx.EXPAND)
        
        # fit layout
        sizer.Fit(self)
        self.SetSizer(sizer)
    # ----
    
    
    def makeSpectrumCanvas(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.spectrumCanvas = mspy.plot.canvas(self, style=mwx.PLOTCANVAS_STYLE_PANEL)
        self.spectrumCanvas.draw(self.container)
        
        # set default params
        self.spectrumCanvas.setProperties(xLabel=config.spectrum['xLabel'])
        self.spectrumCanvas.setProperties(yLabel=config.spectrum['yLabel'])
        self.spectrumCanvas.setProperties(showZero=True)
        self.spectrumCanvas.setProperties(showGrid=config.spectrum['showGrid'])
        self.spectrumCanvas.setProperties(showMinorTicks=config.spectrum['showMinorTicks'])
        self.spectrumCanvas.setProperties(showLegend=config.spectrum['showLegend'])
        self.spectrumCanvas.setProperties(showXPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(showYPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(posBarSize=config.spectrum['posBarSize'])
        self.spectrumCanvas.setProperties(showGel=config.spectrum['showGel'])
        self.spectrumCanvas.setProperties(gelHeight=config.spectrum['gelHeight'])
        self.spectrumCanvas.setProperties(showCurXPos=True)
        self.spectrumCanvas.setProperties(showCurYPos=True)
        self.spectrumCanvas.setProperties(showCurCharge=True)
        self.spectrumCanvas.setProperties(showCurImage=config.spectrum['showCursorImage'])
        self.spectrumCanvas.setProperties(autoScaleY=config.spectrum['autoscale'])
        self.spectrumCanvas.setProperties(overlapLabels=config.spectrum['overlapLabels'])
        self.spectrumCanvas.setProperties(zoomAxis='x')
        self.spectrumCanvas.setProperties(checkLimits=config.spectrum['checkLimits'])
        self.spectrumCanvas.setProperties(xPosDigits=config.main['mzDigits'])
        self.spectrumCanvas.setProperties(yPosDigits=config.main['intDigits'])
        self.spectrumCanvas.setProperties(distanceDigits=config.main['mzDigits'])
        self.spectrumCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.spectrumCanvas.setProperties(reverseDrawing=True)
        
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.spectrumCanvas.setProperties(axisFont=axisFont)
        
        # set events
        self.spectrumCanvas.Bind(wx.EVT_MOTION, self.onCanvasMMotion)
        self.spectrumCanvas.Bind(wx.EVT_MOUSEWHEEL, self.onCanvasMScroll)
        self.spectrumCanvas.Bind(wx.EVT_LEFT_UP, self.onCanvasLMU)
        
        # set DnD
        dropTarget = fileDropTarget(self.parent.onDocumentDropped)
        self.spectrumCanvas.SetDropTarget(dropTarget)
    # ----
    
    
    def makeToolbar(self):
        """Make bottom toolbar."""
        
        # init toolbar panel
        panel = mwx.bgrPanel(self, -1, images.lib['bgrBottombar'], size=(-1, mwx.BOTTOMBAR_HEIGHT))
        
        # make canvas toolset
        image = (images.lib['spectrumLabelsOff'], images.lib['spectrumLabelsOn'])[config.spectrum['showLabels']]
        self.showLabels_butt = wx.BitmapButton(panel, ID_viewLabels, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showLabels_butt.SetToolTip(wx.ToolTip("Show / hide labels"))
        self.showLabels_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumTicksOff'], images.lib['spectrumTicksOn'])[config.spectrum['showTicks']]
        self.showTicks_butt = wx.BitmapButton(panel, ID_viewTicks, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showTicks_butt.SetToolTip(wx.ToolTip("Show / hide ticks"))
        self.showTicks_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumNotationsOff'], images.lib['spectrumNotationsOn'])[config.spectrum['showNotations']]
        self.showNotations_butt = wx.BitmapButton(panel, ID_viewNotations, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showNotations_butt.SetToolTip(wx.ToolTip("Show / hide notations"))
        self.showNotations_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumLabelAngleOff'], images.lib['spectrumLabelAngleOn'])[bool(config.spectrum['labelAngle'])]
        self.labelAngle_butt = wx.BitmapButton(panel, ID_viewLabelAngle, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.labelAngle_butt.SetToolTip(wx.ToolTip("Labels orientation"))
        self.labelAngle_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumPosBarsOff'], images.lib['spectrumPosBarsOn'])[config.spectrum['showPosBars']]
        self.showPosBars_butt = wx.BitmapButton(panel, ID_viewPosBars, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showPosBars_butt.SetToolTip(wx.ToolTip("Show / hide position bars"))
        self.showPosBars_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumGelOff'], images.lib['spectrumGelOn'])[config.spectrum['showGel']]
        self.showGel_butt = wx.BitmapButton(panel, ID_viewGel, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showGel_butt.SetToolTip(wx.ToolTip("Show / hide gel"))
        self.showGel_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumTrackerOff'], images.lib['spectrumTrackerOn'])[config.spectrum['showTracker']]
        self.showTracker_butt = wx.BitmapButton(panel, ID_viewTracker, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.showTracker_butt.SetToolTip(wx.ToolTip("Show / hide cursor tracker"))
        self.showTracker_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumAutoscaleOff'], images.lib['spectrumAutoscaleOn'])[config.spectrum['autoscale']]
        self.autoscale_butt = wx.BitmapButton(panel, ID_viewAutoscale, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.autoscale_butt.SetToolTip(wx.ToolTip("Autoscale intensity"))
        self.autoscale_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        image = (images.lib['spectrumNormalizeOff'], images.lib['spectrumNormalizeOn'])[config.spectrum['normalize']]
        self.normalize_butt = wx.BitmapButton(panel, ID_viewNormalize, image, size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.normalize_butt.SetToolTip(wx.ToolTip("Normalize intensity"))
        self.normalize_butt.Bind(wx.EVT_BUTTON, self.parent.onView)
        
        # make processing toolset
        self.toolsRuler_butt = wx.BitmapButton(panel, ID_toolsRuler, images.lib['spectrumRulerOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsRuler_butt.SetToolTip(wx.ToolTip("Spectrum ruler"))
        self.toolsRuler_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        self.toolsLabelPeak_butt = wx.BitmapButton(panel, ID_toolsLabelPeak, images.lib['spectrumLabelPeakOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsLabelPeak_butt.SetToolTip(wx.ToolTip("Label peak"))
        self.toolsLabelPeak_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        self.toolsLabelPoint_butt = wx.BitmapButton(panel, ID_toolsLabelPoint, images.lib['spectrumLabelPointOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsLabelPoint_butt.SetToolTip(wx.ToolTip("Label point"))
        self.toolsLabelPoint_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        self.toolsLabelEnvelope_butt = wx.BitmapButton(panel, ID_toolsLabelEnvelope, images.lib['spectrumLabelEnvelopeOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsLabelEnvelope_butt.SetToolTip(wx.ToolTip("Label envelope"))
        self.toolsLabelEnvelope_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        self.toolsDeleteLabel_butt = wx.BitmapButton(panel, ID_toolsDeleteLabel, images.lib['spectrumDeleteLabelOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsDeleteLabel_butt.SetToolTip(wx.ToolTip("Delete label"))
        self.toolsDeleteLabel_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        self.toolsOffset_butt = wx.BitmapButton(panel, ID_toolsOffset, images.lib['spectrumOffsetOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.toolsOffset_butt.SetToolTip(wx.ToolTip("Offset spectrum"))
        self.toolsOffset_butt.Bind(wx.EVT_BUTTON, self.parent.onToolsSpectrum)
        
        # make cursor info
        self.cursorInfo = wx.StaticText(panel, -1, "")
        self.cursorInfo.SetFont(wx.SMALL_FONT)
        self.cursorInfo.Bind(wx.EVT_RIGHT_UP, self.onCursorInfoRMU)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.BOTTOMBAR_LSPACE)
        sizer.Add(self.showLabels_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.showTicks_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.showNotations_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.labelAngle_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.showPosBars_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.showGel_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.showTracker_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.autoscale_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.normalize_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(20)
        sizer.Add(self.toolsRuler_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.toolsLabelPeak_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.toolsLabelPoint_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.toolsLabelEnvelope_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.toolsDeleteLabel_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.toolsOffset_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(20)
        sizer.Add(self.cursorInfo, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.AddSpacer(mwx.BOTTOMBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def onCanvasMMotion(self, evt):
        """Update cursor info on mouse motion."""
        
        # update cursor
        self.spectrumCanvas.onMMotion(evt)
        self.updateCursorInfo()
    # ----
    
    
    def onCanvasMScroll(self, evt):
        """Update cursor info on mouse scroll."""
        
        # update cursor
        self.spectrumCanvas.onMScroll(evt)
        self.updateCursorInfo()
    # ----
    
    
    def onCanvasLMU(self, evt):
        """Process selected mouse function."""
        
        # check document
        if self.currentDocument == None:
            evt.Skip()
            if self.currentTool not in ('ruler'):
                wx.Bell()
            return
        
        # get cursor positions
        selection = self.spectrumCanvas.getSelectionBox()
        position = self.spectrumCanvas.getCursorPosition()
        distance = self.spectrumCanvas.getDistance()
        isotopes = self.spectrumCanvas.getIsotopes()
        charge = self.spectrumCanvas.getCharge()
        
        # sent event back to canvas
        self.spectrumCanvas.onLMU(evt)
        
        # convert selection for flipped documents
        if selection and self.documents[self.currentDocument].flipped:
            y1 = -1 * selection[1]
            y2 = -1 * selection[3]
            selection = (selection[0], y2, selection[2], y1)
        
        # convert normalized selection to real values
        if selection and config.spectrum['normalize']:
            f = self.documents[self.currentDocument].spectrum.normalization()
            y1 = selection[1] * f
            y2 = selection[3] * f
            selection = (selection[0], y1, selection[2], y2)
        
        # convert selection for offset documents
        if selection and not config.spectrum['normalize']:
            x1 = selection[0] - self.documents[self.currentDocument].offset[0]
            x2 = selection[2] - self.documents[self.currentDocument].offset[0]
            y1 = selection[1] - self.documents[self.currentDocument].offset[1]
            y2 = selection[3] - self.documents[self.currentDocument].offset[1]
            selection = (x1, y1, x2, y2)
        
        # label peak
        if self.currentTool == 'labelpeak' and selection:
            self.labelPeak(selection)
        
        # label point
        elif self.currentTool == 'labelpoint' and position:
            self.labelPoint(position[0])
        
        # label isotopes
        elif self.currentTool == 'labelenvelope' and isotopes:
            self.labelEnvelope(isotopes, charge)
        
        # delete peaks
        elif self.currentTool == 'deletelabel' and selection:
            self.deleteLabel(selection)
        
        # offset spectrum
        elif self.currentTool == 'offset' and distance and distance != [0,0]:
            if not config.spectrum['normalize']:
                if self.documents[self.currentDocument].flipped:
                    self.documents[self.currentDocument].offset[1] -= distance[1]
                else:
                    self.documents[self.currentDocument].offset[1] += distance[1]
                self.updateSpectrumProperties(self.currentDocument)
            else:
                wx.Bell()
        
        else:
            evt.Skip()
    # ----
    
    
    def onCanvasProperties(self, evt=None):
        """Show canvas properties dialog."""
        
        # raise dialog
        dlg = dlgCanvasProperties(self.parent, self.updateCanvasProperties)
        dlg.ShowModal()
        dlg.Destroy()
    # ----
    
    
    def onCursorInfoRMU(self, evt):
        """Set items to show in cursor info."""
        
        # only while active spectrum ruler
        if self.currentTool != 'ruler':
            return
        
        # popup menu
        menu = wx.Menu()
        menu.Append(ID_viewSpectrumRulerMz, "m/z", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerDist, "Distance", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerPpm, "ppm", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerZ, "Charge", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerCursorMass, "Mass (c)", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerParentMass, "Mass (p)", "", wx.ITEM_CHECK)
        menu.Append(ID_viewSpectrumRulerArea, "Area", "", wx.ITEM_CHECK)
        
        # set values
        menu.Check(ID_viewSpectrumRulerMz, bool('mz' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerDist, bool('dist' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerPpm, bool('ppm' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerZ, bool('z' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerCursorMass, bool('cmass' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerParentMass, bool('pmass' in config.main['cursorInfo']))
        menu.Check(ID_viewSpectrumRulerArea, bool('area' in config.main['cursorInfo']))
        
        # set events
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerMz)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerDist)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerPpm)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerZ)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerCursorMass)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerParentMass)
        self.Bind(wx.EVT_MENU, self.parent.onViewSpectrumRuler, id=ID_viewSpectrumRulerArea)
        
        self.PopupMenu(menu)
        menu.Destroy()
    # ----
    
    
    def setCurrentTool(self, tool):
        """Slect spectrum tool."""
        
        # set current tool
        self.currentTool = tool
        
        # set icons off
        self.toolsRuler_butt.SetBitmapLabel(images.lib['spectrumRulerOff'])
        self.toolsLabelPeak_butt.SetBitmapLabel(images.lib['spectrumLabelPeakOff'])
        self.toolsLabelPoint_butt.SetBitmapLabel(images.lib['spectrumLabelPointOff'])
        self.toolsLabelEnvelope_butt.SetBitmapLabel(images.lib['spectrumLabelEnvelopeOff'])
        self.toolsDeleteLabel_butt.SetBitmapLabel(images.lib['spectrumDeleteLabelOff'])
        self.toolsOffset_butt.SetBitmapLabel(images.lib['spectrumOffsetOff'])
        
        # set cursor tracker
        cursorTracker = None
        if config.spectrum['showTracker']:
            cursorTracker = 'cross'
        
        # set tool
        if tool == 'ruler':
            self.toolsRuler_butt.SetBitmapLabel(images.lib['spectrumRulerOn'])
            self.spectrumCanvas.setMFunction(cursorTracker)
            self.spectrumCanvas.setLMBFunction('xDistance')
            cursor = (wx.StockCursor(wx.CURSOR_ARROW), images.lib['cursorsCrossMeasure'])
        
        elif tool == 'labelpeak':
            self.toolsLabelPeak_butt.SetBitmapLabel(images.lib['spectrumLabelPeakOn'])
            self.spectrumCanvas.setMFunction(None)
            self.spectrumCanvas.setLMBFunction('range')
            cursor = (images.lib['cursorsArrowPeak'], images.lib['cursorsArrowPeak'])
            
        elif tool == 'labelpoint':
            self.toolsLabelPoint_butt.SetBitmapLabel(images.lib['spectrumLabelPointOn'])
            self.spectrumCanvas.setMFunction(cursorTracker)
            self.spectrumCanvas.setLMBFunction('point')
            cursor = (images.lib['cursorsArrowPoint'], images.lib['cursorsCrossPoint'])
        
        elif tool == 'labelenvelope':
            self.toolsLabelEnvelope_butt.SetBitmapLabel(images.lib['spectrumLabelEnvelopeOn'])
            self.spectrumCanvas.setMFunction('isotoperuler')
            self.spectrumCanvas.setLMBFunction('isotopes')
            cursor = (images.lib['cursorsCrossPeak'], images.lib['cursorsCrossPeak'])
        
        elif tool == 'deletelabel':
            self.toolsDeleteLabel_butt.SetBitmapLabel(images.lib['spectrumDeleteLabelOn'])
            self.spectrumCanvas.setMFunction(None)
            self.spectrumCanvas.setLMBFunction('rectangle')
            cursor = (images.lib['cursorsArrowDelete'], images.lib['cursorsArrowDelete'])
        
        elif tool == 'offset':
            self.toolsOffset_butt.SetBitmapLabel(images.lib['spectrumOffsetOn'])
            self.spectrumCanvas.setMFunction(cursorTracker)
            self.spectrumCanvas.setLMBFunction('yDistance')
            cursor = (images.lib['cursorsArrowOffset'], images.lib['cursorsCrossOffset'])
        
        # set cursor
        self.spectrumCanvas.setCursorImage(cursor[bool(config.spectrum['showTracker'])])
    # ----
    
    
    def setSpectrumProperties(self, docIndex):
        """Set spectrum properties."""
        
        # check document
        if docIndex == None:
            return
        
        # get document
        docData = self.documents[docIndex]
        spectrum = self.container[docIndex+2]
        
        spectrum.setProperties(legend=docData.title)
        spectrum.setProperties(visible=docData.visible)
        spectrum.setProperties(flipped=docData.flipped)
        spectrum.setProperties(xOffset=docData.offset[0])
        spectrum.setProperties(yOffset=docData.offset[1])
        spectrum.setProperties(normalized=config.spectrum['normalize'])
        spectrum.setProperties(xOffsetDigits=config.main['mzDigits'])
        spectrum.setProperties(yOffsetDigits=config.main['intDigits'])
        
        spectrum.setProperties(showInGel=True)
        spectrum.setProperties(showSpectrum=True)
        spectrum.setProperties(showTicks=config.spectrum['showTicks'])
        spectrum.setProperties(showPoints=config.spectrum['showDataPoints'])
        spectrum.setProperties(showGelLegend=config.spectrum['showGelLegend'])
        spectrum.setProperties(spectrumColour=docData.colour)
        spectrum.setProperties(spectrumStyle=docData.style)
        
        spectrum.setProperties(labelAngle=config.spectrum['labelAngle'])
        spectrum.setProperties(labelCharge=config.spectrum['labelCharge'])
        spectrum.setProperties(labelGroup=config.spectrum['labelGroup'])
        spectrum.setProperties(labelDigits=config.main['mzDigits'])
        spectrum.setProperties(labelBgr=config.spectrum['labelBgr'])
        spectrum.setProperties(isotopeColour=None)
        
        labelFont = wx.Font(config.spectrum['labelFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        spectrum.setProperties(labelFont=labelFont)
        
        if docIndex == self.currentDocument:
            spectrum.setProperties(showLabels=config.spectrum['showLabels'])
            spectrum.setProperties(tickColour=config.spectrum['tickColour'])
        else:
            spectrum.setProperties(showLabels=(config.spectrum['showLabels'] and config.spectrum['showAllLabels']))
            spectrum.setProperties(tickColour=docData.colour)
    # ----
    
    
    def setCanvasRange(self, xAxis=None, yAxis=None):
        """Set canvas range."""
        self.spectrumCanvas.zoom(xAxis, yAxis)
    # ----
    
    
    def updateCanvasProperties(self, ID=None, refresh=True):
        """Update canvas properties."""
        
        # update button image
        if ID != None:
            if ID == ID_viewLabels:
                image = (images.lib['spectrumLabelsOff'], images.lib['spectrumLabelsOn'])[bool(config.spectrum['showLabels'])]
                self.showLabels_butt.SetBitmapLabel(image)
            elif ID == ID_viewTicks:
                image = (images.lib['spectrumTicksOff'], images.lib['spectrumTicksOn'])[bool(config.spectrum['showTicks'])]
                self.showTicks_butt.SetBitmapLabel(image)
            elif ID == ID_viewNotations:
                image = (images.lib['spectrumNotationsOff'], images.lib['spectrumNotationsOn'])[bool(config.spectrum['showNotations'])]
                self.showNotations_butt.SetBitmapLabel(image)
            elif ID == ID_viewLabelAngle:
                image = (images.lib['spectrumLabelAngleOff'], images.lib['spectrumLabelAngleOn'])[bool(config.spectrum['labelAngle'])]
                self.labelAngle_butt.SetBitmapLabel(image)
            elif ID == ID_viewPosBars:
                image = (images.lib['spectrumPosBarsOff'], images.lib['spectrumPosBarsOn'])[bool(config.spectrum['showPosBars'])]
                self.showPosBars_butt.SetBitmapLabel(image)
            elif ID == ID_viewGel:
                image = (images.lib['spectrumGelOff'], images.lib['spectrumGelOn'])[bool(config.spectrum['showGel'])]
                self.showGel_butt.SetBitmapLabel(image)
            elif ID == ID_viewTracker:
                image = (images.lib['spectrumTrackerOff'], images.lib['spectrumTrackerOn'])[bool(config.spectrum['showTracker'])]
                self.showTracker_butt.SetBitmapLabel(image)
            elif ID == ID_viewAutoscale:
                image = (images.lib['spectrumAutoscaleOff'], images.lib['spectrumAutoscaleOn'])[bool(config.spectrum['autoscale'])]
                self.autoscale_butt.SetBitmapLabel(image)
            elif ID == ID_viewNormalize:
                image = (images.lib['spectrumNormalizeOff'], images.lib['spectrumNormalizeOn'])[bool(config.spectrum['normalize'])]
                self.normalize_butt.SetBitmapLabel(image)
        
        # set canvas properties
        self.spectrumCanvas.setProperties(gelHeight=config.spectrum['gelHeight'])
        self.spectrumCanvas.setProperties(xPosDigits=config.main['mzDigits'])
        self.spectrumCanvas.setProperties(yPosDigits=config.main['intDigits'])
        self.spectrumCanvas.setProperties(distanceDigits=config.main['mzDigits'])
        self.spectrumCanvas.setProperties(overlapLabels=config.spectrum['overlapLabels'])
        self.spectrumCanvas.setProperties(checkLimits=config.spectrum['checkLimits'])
        self.spectrumCanvas.setProperties(autoScaleY=config.spectrum['autoscale'])
        self.spectrumCanvas.setProperties(showGel=config.spectrum['showGel'])
        self.spectrumCanvas.setProperties(showXPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(showYPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(posBarSize=config.spectrum['posBarSize'])
        self.spectrumCanvas.setProperties(showLegend=config.spectrum['showLegend'])
        self.spectrumCanvas.setProperties(showGrid=config.spectrum['showGrid'])
        self.spectrumCanvas.setProperties(showMinorTicks=config.spectrum['showMinorTicks'])
        
        # set y-axis label
        self.spectrumCanvas.setProperties(yLabel=config.spectrum['yLabel'])
        if config.spectrum['normalize']:
            self.spectrumCanvas.setProperties(yLabel="r. int. (%)")
        
        # set font
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.spectrumCanvas.setProperties(axisFont=axisFont)
        
        # set cursor tracker according to current tool
        self.setCurrentTool(self.currentTool)
        
        # set properties for documents
        labelFont = wx.Font(config.spectrum['labelFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        for docIndex in range(len(self.documents)):
            self.setSpectrumProperties(docIndex)
        
        # update tmp spectra
        self.updateNotationMarks(self.currentNotationMarks, refresh=False)
        self.updateTmpSpectrum(self.currentTmpSpectrum, flipped=self.currentTmpSpectrumFlip, refresh=False)
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def updateCursorInfo(self):
        """Update cursor info on MS scan canvas"""
        
        label = ''
        
        # get spectrum polarity
        polarity = 1
        if self.currentDocument != None and self.documents[self.currentDocument].spectrum.polarity == -1:
            polarity = -1
            return
        
        # get baseline window (for area calculation)
        baselineWindow = 1.
        if config.processing['peakpicking']['baseline']:
            baselineWindow = 1./config.processing['baseline']['precision']
        
        # get basic values
        position = self.spectrumCanvas.getCursorPosition()
        distance = self.spectrumCanvas.getDistance()
        
        # format numbers
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        intFormat = '%0.' + `config.main['intDigits']` + 'f'
        distFormat = '%0.' + `config.main['mzDigits']` + 'f'
        ppmFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        areaFormat = '%0.' + `config.main['intDigits']` + 'f'
        chargeFormat = '%0.' + `config.main['chargeDigits']` + 'f'
        
        if position and abs(position[1]) > 10000:
            intFormat = '%.2e'
        
        # offset dragging
        if self.currentTool == 'offset' and distance and position:
            format = 'a.i.: %s   dist: %s' % (intFormat, intFormat)
            label += format % (position[1], distance[1])
        
        # isotope ruler
        elif self.currentTool == 'labelenvelope' and position:
            charge = self.spectrumCanvas.getCharge()
            mass = mspy.mz(position[0], charge=0, currentCharge=charge*polarity)
            format = 'm/z: %s   z: %s   mass: %s' % (mzFormat, '%d', mzFormat)
            label = format % (position[0] , charge*polarity, mass)
        
        # distance measurement
        elif distance and position:
            
            # get charge and mass from distance
            if distance[0] != 0 and abs(distance[0]) <= 2:
                charge = abs(1/distance[0])
                cmass = mspy.mz(position[0], 0, round(charge)*polarity)
                pmass = mspy.mz(position[0]-distance[0], 0, round(charge)*polarity)
            elif distance[0] > 10:
                charge = abs(((position[0]-distance[0]) - 1.00728) / distance[0])
                cmass = mspy.mz(position[0], 0, round(charge)*polarity)
                pmass = mspy.mz(position[0]-distance[0], 0, round(charge+1)*polarity)
            elif distance[0] < -10:
                charge = abs((position[0] - 1.00728) / distance[0])
                cmass = mspy.mz(position[0], 0, round(charge+1)*polarity)
                pmass = mspy.mz(position[0]-distance[0], 0, round(charge)*polarity)
            else:
                charge = 0
                cmass = 0
                pmass = 0
            
            if 'mz' in config.main['cursorInfo']:
                format = 'm/z: %s   ' % mzFormat
                label += format % position[0]
            
            if 'dist' in config.main['cursorInfo']:
                format = 'dist: %s   ' % distFormat
                label += format % distance[0]
            
            if 'ppm' in config.main['cursorInfo']:
                format = 'ppm: %s   ' % ppmFormat
                label += format % (1e6*distance[0]/position[0])
            
            if 'z' in config.main['cursorInfo'] and charge:
                if abs(distance[0]) > 10:
                    format = 'z: %s/%s   ' % (chargeFormat, chargeFormat)
                    label += format % ((charge+1)*polarity, charge*polarity)
                else:
                    format = 'z: %%d (%s)   ' % chargeFormat
                    label += format % (round(charge*polarity), charge*polarity)
            
            if 'cmass' in config.main['cursorInfo'] and cmass > 0:
                format = 'mass (c): %s   ' % mzFormat
                label += format % cmass
            
            if 'pmass' in config.main['cursorInfo'] and pmass > 0:
                format = 'mass (p): %s   ' % mzFormat
                label += format % pmass
            
            if 'area' in config.main['cursorInfo'] and self.currentDocument != None:
                area = self.documents[self.currentDocument].spectrum.area(
                    minX = position[0]-distance[0],
                    maxX = position[0],
                    baselineWindow = baselineWindow,
                    baselineOffset = config.processing['baseline']['offset']
                )
                format = 'area: %s   ' % areaFormat
                label += format % area
        
        # no specific function
        elif position:
            format = 'm/z: %s   a.i.: %s' % (mzFormat, intFormat)
            label = format % (position[0], position[1])
        
        # ensure some label size to enable popup menu
        if len(label) < 100:
            label += ' ' * (100 - len(label))
        
        # show info
        self.cursorInfo.SetLabel(label)
    # ----
    
    
    def updateTmpSpectrum(self, points, flipped=False, refresh=True):
        """Set new data to tmp spectrum."""
        
        self.currentTmpSpectrum = points
        self.currentTmpSpectrumFlip = flipped
        
        # check spectrum
        if points == None:
            points = []
        
        # snap to current spectrum
        normalization = None
        xOffset = 0
        yOffset = 0
        if self.currentDocument != None and len(points):
            
            # get normalization
            if config.spectrum['normalize']:
                normalization = self.documents[self.currentDocument].spectrum.normalization()
            
            # offset points
            else:
                xOffset = self.documents[self.currentDocument].offset[0]
                yOffset = self.documents[self.currentDocument].offset[1]
            
            # flip points
            if flipped:
                flipped = not self.documents[self.currentDocument].flipped
            else:
                flipped = self.documents[self.currentDocument].flipped
        
        # make tmp spectrum
        obj = mspy.plot.points(
            points = points,
            normalized = config.spectrum['normalize'],
            flipped = flipped,
            xOffset = xOffset,
            yOffset = yOffset,
            showInGel = False,
            showLines = True,
            showPoints = False,
            exactFit = True,
            pointColour = config.spectrum['tmpSpectrumColour'],
            lineColour = config.spectrum['tmpSpectrumColour']
        )
        
        # set normalization
        if normalization:
            obj.setNormalization(normalization)
        
        # add to container
        self.container[0] = obj
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def updateNotationMarks(self, notations, refresh=True):
        """Set new data to notation marks."""
        
        self.currentNotationMarks = notations
        
        # check spectrum and view option
        if notations == None or not config.spectrum['showNotations']:
            notations = []
        
        # snap data to current spectrum
        normalization = None
        flipped = False
        xOffset = 0
        yOffset = 0
        if self.currentDocument != None and len(notations):
            
            # normalize points
            if config.spectrum['normalize']:
                normalization = self.documents[self.currentDocument].spectrum.normalization()
            
            # offset points
            else:
                xOffset = self.documents[self.currentDocument].offset[0]
                yOffset = self.documents[self.currentDocument].offset[1]
            
            # flip points
            flipped = self.documents[self.currentDocument].flipped
        
        # add points to container
        labelFont = wx.Font(config.spectrum['labelFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        obj = mspy.plot.annotations(
            points = notations,
            normalized = config.spectrum['normalize'],
            flipped = flipped,
            xOffset = xOffset,
            yOffset = yOffset,
            exactFit = True,
            showInGel = False,
            showPoints = config.spectrum['notationMarks'],
            showLabels = config.spectrum['notationLabels'],
            showXPos = config.spectrum['notationMZ'],
            xPosDigits = config.main['mzDigits'],
            pointColour = config.spectrum['notationMarksColour'],
            labelAngle = config.spectrum['labelAngle'],
            labelBgr = config.spectrum['labelBgr'],
            labelFont = labelFont,
            labelMaxLength = config.spectrum['notationMaxLength']
        )
        
        # set normalization
        if normalization:
            obj.setNormalization(normalization)
        
        # add to container
        self.container[1] = obj
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def updateSpectrum(self, docIndex, refresh=True):
        """Reload spectrum data."""
        
        # make spectrum
        docData = self.documents[docIndex]
        spectrum = mspy.plot.spectrum(docData.spectrum)
        
        # update container
        self.container[docIndex+2] = spectrum
        
        # set spectrum properties
        self.setSpectrumProperties(docIndex)
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def updateSpectrumProperties(self, docIndex, refresh=True):
        """Update all spectrum properties."""
        
        # update spectrum properties
        self.setSpectrumProperties(docIndex)
        
        # update tmp spectra
        self.updateNotationMarks(self.currentNotationMarks, refresh=False)
        self.updateTmpSpectrum(self.currentTmpSpectrum, flipped=self.currentTmpSpectrumFlip, refresh=False)
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def selectSpectrum(self, docIndex, refresh=True):
        """Set document as active."""
        
        # hide labels on last active document
        if self.currentDocument != None:
            self.container[self.currentDocument+2].setProperties(showLabels=(config.spectrum['showLabels'] and config.spectrum['showAllLabels']))
            self.container[self.currentDocument+2].setProperties(tickColour=self.documents[self.currentDocument].colour)
        
        # set current document
        self.currentDocument = docIndex
        if self.currentDocument != None:
            self.spectrumCanvas.setCurrentObject(self.currentDocument+2)
            self.container[self.currentDocument+2].setProperties(showLabels=config.spectrum['showLabels'])
            self.container[self.currentDocument+2].setProperties(tickColour=config.spectrum['tickColour'])
        else:
            self.spectrumCanvas.setCurrentObject(None)
        
        # update tmp spectra
        self.updateTmpSpectrum(None, refresh=False)
        self.updateNotationMarks(None, refresh=False)
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def appendLastSpectrum(self, refresh=True):
        """Append new spectrum to container."""
        
        # get document
        docIndex = len(self.documents) - 1
        docData = self.documents[docIndex]
        
        # append spectrum
        spectrum = mspy.plot.spectrum(docData.spectrum)
        self.container.append(spectrum)
        
        # set spectrum properties
        self.setSpectrumProperties(docIndex)
        
        # redraw plot
        if refresh:
            self.refresh(fullsize=True)
    # ----
    
    
    def deleteSpectrum(self, docIndex, refresh=True):
        """Remove selected spectrum from container."""
        
        # remove spectrum
        del self.container[docIndex+2]
        
        # set current document
        if docIndex == self.currentDocument:
            self.currentDocument = None
            self.spectrumCanvas.setCurrentObject(None)
            self.updateTmpSpectrum(None, refresh=False)
            self.updateNotationMarks(None, refresh=False)
        
        # redraw plot
        if refresh:
            self.refresh()
    # ----
    
    
    def highlightPoints(self, points):
        """Highlight specified points in the spectrum."""
        self.spectrumCanvas.highlightXPoints(points)
    # ----
    
    
    def labelPeak(self, selection):
        """Label peak in selection."""
        
        # check document
        if self.currentDocument == None or not self.documents[self.currentDocument].spectrum.hasprofile():
            return
        
        # get baseline window
        baselineWindow = 1.
        if config.processing['peakpicking']['baseline']:
            baselineWindow = 1./config.processing['baseline']['precision']
        
        # get baseline
        baseline = self.documents[self.currentDocument].spectrum.baseline(
            window = baselineWindow,
            offset = config.processing['baseline']['offset']
        )
        
        # label peak
        peak = mspy.labelpeak(
            signal = self.documents[self.currentDocument].spectrum.profile,
            minX = selection[0],
            maxX = selection[2],
            pickingHeight = config.processing['peakpicking']['pickingHeight'],
            baseline = baseline
        )
        
        if peak:
            
            # set as monoisotopic
            if config.processing['deisotoping']['setAsMonoisotopic']:
                peak.setisotope(0)
            
            # update document
            self.documents[self.currentDocument].backup(('spectrum'))
            self.documents[self.currentDocument].spectrum.peaklist.append(peak)
            self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def labelPoint(self, mz):
        """Label point at position."""
        
        # check document
        if self.currentDocument == None or not self.documents[self.currentDocument].spectrum.hasprofile():
            return
        
        # get baseline window
        baselineWindow = 1.
        if config.processing['peakpicking']['baseline']:
            baselineWindow = 1./config.processing['baseline']['precision']
        
        # get baseline
        baseline = self.documents[self.currentDocument].spectrum.baseline(
            window = baselineWindow,
            offset = config.processing['baseline']['offset']
        )
        
        # label point
        peak = mspy.labelpoint(
            signal = self.documents[self.currentDocument].spectrum.profile,
            mz = mz,
            baseline = baseline
        )
        
        if peak:
            
            # set as monoisotopic
            if config.processing['deisotoping']['setAsMonoisotopic']:
                peak.setisotope(0)
            
            # update document
            self.documents[self.currentDocument].backup(('spectrum'))
            self.documents[self.currentDocument].spectrum.peaklist.append(peak)
            self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def labelEnvelope(self, isotopes, charge):
        """Label isotopes."""
        
        # check document
        if self.currentDocument == None or not self.documents[self.currentDocument].spectrum.hasprofile():
            return
        
        # get baseline window
        baselineWindow = 1.
        if config.processing['peakpicking']['baseline']:
            baselineWindow = 1./config.processing['baseline']['precision']
        
        # get baseline
        baseline = self.documents[self.currentDocument].spectrum.baseline(
            window = baselineWindow,
            offset = config.processing['baseline']['offset']
        )
        
        # label isotopes
        peaks = []
        buff = []
        for isotope in isotopes:
            peak = mspy.labelpeak(
                signal = self.documents[self.currentDocument].spectrum.profile,
                mz = isotope,
                pickingHeight = config.processing['peakpicking']['pickingHeight'],
                baseline = baseline
            )
            if peak and not peak.mz in buff:
                peaks.append(peak)
                buff.append(peak.mz)
        
        # check peaks
        if not peaks:
            return
        
        # backup document
        self.documents[self.currentDocument].backup(('spectrum'))
        
        # get polarity
        polarity = 1
        if self.documents[self.currentDocument].spectrum.polarity == -1:
            polarity = -1
        
        # label 1st isotope
        if config.processing['deisotoping']['labelEnvelope'] == '1st':
            
            basepeak = peaks[0]
            sumIntensity = 0
            sumBase = 0
            for peak in peaks:
                sumIntensity += peak.intensity
                sumBase += peak.base
                if peak.intensity > basepeak.intensity:
                    basepeak = peak
            
            base = basepeak.base
            ai = basepeak.ai
            sn = basepeak.sn
            if config.processing['deisotoping']['envelopeIntensity'] == 'sum':
                base = sumBase / len(peaks)
                ai = base + sumIntensity
                sn = (ai - base) * basepeak.sn / (basepeak.ai - basepeak.base)
            elif config.processing['deisotoping']['envelopeIntensity'] == 'average':
                base = sumBase / len(peaks)
                ai = base + sumIntensity / len(isotopes)
                sn = (ai - base) * basepeak.sn / (basepeak.ai - basepeak.base)
            
            peak = mspy.peak(
                mz = peaks[0].mz,
                ai = ai,
                base = base,
                sn = sn,
                charge = charge*polarity,
                isotope = 0,
                fwhm = None
            )
            
            self.documents[self.currentDocument].spectrum.peaklist.append(peak)
        
        # label monoisotopic peak
        elif config.processing['deisotoping']['labelEnvelope'] == 'monoisotope':
            peak = mspy.envmono(peaks, charge=charge*polarity, intensity=config.processing['deisotoping']['envelopeIntensity'])
            if peak:
                peak.setcharge(charge*polarity)
                self.documents[self.currentDocument].spectrum.peaklist.append(peak)
        
        # label envelope centroid
        elif config.processing['deisotoping']['labelEnvelope'] == 'centroid':
            peak = mspy.envcentroid(peaks, pickingHeight=0.5, intensity=config.processing['deisotoping']['envelopeIntensity'])
            if peak:
                peak.setcharge(charge*polarity)
                self.documents[self.currentDocument].spectrum.peaklist.append(peak)
        
        # label all isotopes
        if config.processing['deisotoping']['labelEnvelope'] == 'isotopes':
            groupname = self.documents[self.currentDocument].spectrum.peaklist.groupname()
            for x, peak in enumerate(peaks):
                peak.setisotope(x)
                peak.setcharge(charge*polarity)
                peak.setgroup(groupname)
                self.documents[self.currentDocument].spectrum.peaklist.append(peak)
        
        # update gui
        self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def deleteLabel(self, selection):
        """Delete all labels within selection."""
        
        # check document
        if self.currentDocument == None:
            return
        
        # remove peaks
        indexes = []
        for x, peak in enumerate(self.documents[self.currentDocument].spectrum.peaklist):
            if (selection[0] < peak.mz < selection[2]) and (selection[1] < peak.ai < selection[3]):
                indexes.append(x)
        
        # update document
        if indexes:
            self.documents[self.currentDocument].backup(('spectrum'))
            self.documents[self.currentDocument].spectrum.peaklist.delete(indexes)
            self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def refresh(self, fullsize=False):
        """Redraw spectrum."""
        
        # check for flipped documents and update canvas symmetry
        self.spectrumCanvas.setProperties(ySymmetry=False)
        for docData in self.documents:
            if docData.visible and docData.flipped:
                self.spectrumCanvas.setProperties(ySymmetry=True)
                break
        
        # redraw canvas
        self.spectrumCanvas.refresh(fullsize=fullsize)
    # ----
    
    
    def getBitmap(self, width, height, printerScale):
        """Get spectrum image."""
        return self.spectrumCanvas.getBitmap(width, height, printerScale)
    # ----
    
    
    def getPrintout(self, filterSize, title):
        """Get spectrum printout."""
        return self.spectrumCanvas.getPrintout(filterSize, title)
    # ----
    
    
    def getCurrentRange(self):
        """Get current X range."""
        return self.spectrumCanvas.getCurrentXRange()
    # ----
    
    


class dlgCanvasProperties(wx.Dialog):
    """Set canvas properties."""
    
    def __init__(self, parent, onChangeFn):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, "Canvas Properties", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        self.onChangeFn = onChangeFn
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.CentreOnParent()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make canvas params
        mzDigits_label = wx.StaticText(self, -1, "m/z precision:")
        self.mzDigits_slider = wx.Slider(self, -1, config.main['mzDigits'], 0, 6, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.mzDigits_slider.SetTickFreq(1,1)
        self.mzDigits_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        intDigits_label = wx.StaticText(self, -1, "Intensity precision:")
        self.intDigits_slider = wx.Slider(self, -1, config.main['intDigits'], 0, 6, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.intDigits_slider.SetTickFreq(1,1)
        self.intDigits_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        posBarSize_label = wx.StaticText(self, -1, "Bars height:")
        self.posBarSize_slider = wx.Slider(self, -1, config.spectrum['posBarSize'], 5, 20, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.posBarSize_slider.SetTickFreq(5,1)
        self.posBarSize_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        gelHeight_label = wx.StaticText(self, -1, "Gel height:")
        self.gelHeight_slider = wx.Slider(self, -1, config.spectrum['gelHeight'], 10, 50, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.gelHeight_slider.SetTickFreq(5,1)
        self.gelHeight_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        axisFontSize_label = wx.StaticText(self, -1, "Canvas font size:")
        self.axisFontSize_slider = wx.Slider(self, -1, config.spectrum['axisFontSize'], 5, 15, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.axisFontSize_slider.SetTickFreq(2,1)
        self.axisFontSize_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        labelFontSize_label = wx.StaticText(self, -1, "Label font size:")
        self.labelFontSize_slider = wx.Slider(self, -1, config.spectrum['labelFontSize'], 5, 15, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.labelFontSize_slider.SetTickFreq(2,1)
        self.labelFontSize_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        notationMaxLength_label = wx.StaticText(self, -1, "Notation length:")
        self.notationMaxLength_slider = wx.Slider(self, -1, config.spectrum['notationMaxLength'], 1, 100, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.notationMaxLength_slider.SetTickFreq(10,1)
        self.notationMaxLength_slider.Bind(wx.EVT_SCROLL, self.onChange)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(mzDigits_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mzDigits_slider, (0,1))
        grid.Add(intDigits_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.intDigits_slider, (1,1))
        grid.Add(posBarSize_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.posBarSize_slider, (2,1))
        grid.Add(gelHeight_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.gelHeight_slider, (3,1))
        grid.Add(axisFontSize_label, (4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.axisFontSize_slider, (4,1))
        grid.Add(labelFontSize_label, (5,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.labelFontSize_slider, (5,1))
        grid.Add(notationMaxLength_label, (6,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.notationMaxLength_slider, (6,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onChange(self, evt):
        """Set parameter and update canvas while scrolling."""
        
        # get canvas params
        config.main['mzDigits'] = self.mzDigits_slider.GetValue()
        config.main['intDigits'] = self.intDigits_slider.GetValue()
        config.spectrum['posBarSize'] = self.posBarSize_slider.GetValue()
        config.spectrum['gelHeight'] = self.gelHeight_slider.GetValue()
        config.spectrum['axisFontSize'] = self.axisFontSize_slider.GetValue()
        config.spectrum['labelFontSize'] = self.labelFontSize_slider.GetValue()
        config.spectrum['notationMaxLength'] = self.notationMaxLength_slider.GetValue()
        
        # set params to canvas and update
        self.onChangeFn()
    # ----
    
    


class dlgViewRange(wx.Dialog):
    """Set canvas view range."""
    
    def __init__(self, parent, data):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, 'Mass Range', style=wx.DEFAULT_DIALOG_STYLE)
        
        self.parent = parent
        self.data = data
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.HORIZONTAL)
        
        # make elements
        minX_label = wx.StaticText(self, -1, "Min:", style=wx.ALIGN_RIGHT)
        self.minX_value = wx.TextCtrl(self, -1, str(self.data[0]), size=(100,-1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('float'))
        self.minX_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        maxX_label = wx.StaticText(self, -1, "Max:", style=wx.ALIGN_RIGHT)
        self.maxX_value = wx.TextCtrl(self, -1, str(self.data[1]), size=(100,-1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('float'))
        self.maxX_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, "OK")
        ok_butt.Bind(wx.EVT_BUTTON, self.onOK)
        ok_butt.SetDefault()
        
        # pack elements
        staticSizer.Add(minX_label, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        staticSizer.Add(self.minX_value, 1, wx.TOP|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        staticSizer.Add(maxX_label, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        staticSizer.Add(self.maxX_value, 1, wx.TOP|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        
        buttSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttSizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttSizer.Add(ok_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.EXPAND|wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttSizer, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onOK(self, evt=None):
        """Get values."""
        
        # get data
        try:
            minX = float(self.minX_value.GetValue())
            maxX = float(self.maxX_value.GetValue())
            if minX < maxX:
                self.data = (minX, maxX)
                self.EndModal(wx.ID_OK)
            else:
                wx.Bell()
        except:
            wx.Bell()
    # ----
    
    


class dlgSpectrumOffset(wx.Dialog):
    """Set spectrum offset."""
    
    def __init__(self, parent, offset):
        wx.Dialog.__init__(self, parent, -1, "Spectrum offset", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        
        self.parent = parent
        self.offset = offset
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        offset_label = wx.StaticText(self, -1, "Intensity offset:")
        self.offset_value = wx.TextCtrl(self, -1, str(self.offset[1]), size=(120, -1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('float'))
        self.offset_value.Bind(wx.EVT_TEXT, self.onChange)
        self.offset_value.Bind(wx.EVT_TEXT_ENTER, self.onOffset)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        offset_butt = wx.Button(self, wx.ID_OK, "Offset")
        offset_butt.Bind(wx.EVT_BUTTON, self.onOffset)
        offset_butt.SetDefault()
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(offset_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.offset_value, (0,1))
        staticSizer.Add(grid, 0, wx.ALL, 5)
        
        buttSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttSizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttSizer.Add(offset_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttSizer, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onChange(self, evt):
        """Check data."""
        
        # get data
        try:
            self.offset = [0, float(self.offset_value.GetValue())]
        except:
            self.offset = None
    # ----
    
    
    def onOffset(self, evt):
        """Offset."""
        
        # check value and end
        if self.offset != None:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
    
    def getData(self):
        """Return values."""
        return self.offset
    # ----
    
    


class fileDropTarget(wx.FileDropTarget):
    """Generic drop target for files."""
    
    def __init__(self, fn):
        wx.FileDropTarget.__init__(self)
        self.fn = fn
    # ----
    
    
    def OnDropFiles(self, x, y, paths):
        """Open dropped files."""
        self.fn(paths=paths)
    # ----
    

