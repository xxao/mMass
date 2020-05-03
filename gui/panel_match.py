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
import threading
import wx

# load modules
from ids import *
import mwx
import images
import config
import mspy
import mspy.plot
import doc


# FLOATING PANEL WITH MATCH TOOLS
# -------------------------------

class panelMatch(wx.MiniFrame):
    """Data match tool."""
    
    def __init__(self, parentTool, mainFrame, module):
        wx.MiniFrame.__init__(self, parentTool, -1, 'Match Data', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parentTool = parentTool
        self.mainFrame = mainFrame
        
        self.processing = None
        
        self.currentModule = module
        self.currentTool = 'errors'
        self.currentData = None
        self.currentPeaklist = None
        self.currentSummary = None
        self.currentErrors = []
        self.currentCalibrationPoints = []
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # select default tool
        self.onToolSelected(tool=self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # set frame title
        if self.currentModule == 'massfilter':
            self.SetTitle('Match References')
        elif self.currentModule == 'digest':
            self.SetTitle('Match Peptides')
        elif self.currentModule == 'fragment':
            self.SetTitle('Match Fragments')
        elif self.currentModule == 'compounds':
            self.SetTitle('Match Compounds')
        else:
            self.SetTitle('Match Data')
        
        # make toolbars
        toolbar = self.makeToolbar()
        controlbar = self.makeControlbar()
        
        # make panels
        self.makeErrorCanvas()
        self.makeSummaryList()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.errorCanvas, 1, wx.EXPAND, 0)
        self.mainSizer.Add(self.summaryList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make buttons
        self.errors_butt = wx.BitmapButton(panel, ID_matchErrors, images.lib['matchErrorsOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.errors_butt.SetToolTip(wx.ToolTip("Error plot"))
        self.errors_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.summary_butt = wx.BitmapButton(panel, ID_matchSummary, images.lib['matchSummaryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.summary_butt.SetToolTip(wx.ToolTip("Match summary"))
        self.summary_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        # make match fields
        tolerance_label = wx.StaticText(panel, -1, "Tolerance:")
        tolerance_label.SetFont(wx.SMALL_FONT)
        
        self.tolerance_value = wx.TextCtrl(panel, -1, str(config.match['tolerance']), size=(60, -1), validator=mwx.validator('floatPos'))
        
        self.unitsDa_radio = wx.RadioButton(panel, -1, "Da", style=wx.RB_GROUP)
        self.unitsDa_radio.SetFont(wx.SMALL_FONT)
        self.unitsDa_radio.SetValue(True)
        self.unitsDa_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        
        self.unitsPpm_radio = wx.RadioButton(panel, -1, "ppm")
        self.unitsPpm_radio.SetFont(wx.SMALL_FONT)
        self.unitsPpm_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        self.unitsPpm_radio.SetValue((config.match['units'] == 'ppm'))
        
        self.ignoreCharge_check = wx.CheckBox(panel, -1, "Ignore charge")
        self.ignoreCharge_check.SetFont(wx.SMALL_FONT)
        self.ignoreCharge_check.SetValue(config.match['ignoreCharge'])
        if self.currentModule == 'massfilter':
            self.ignoreCharge_check.Disable()
        
        self.match_butt = wx.Button(panel, -1, "Match", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.match_butt.Bind(wx.EVT_BUTTON, self.onMatch)
        
        self.calibrate_butt = wx.Button(panel, -1, "Calibrate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.calibrate_butt.Bind(wx.EVT_BUTTON, self.onCalibrate)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.errors_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.summary_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(20)
        sizer.Add(tolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.tolerance_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(self.unitsDa_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.unitsPpm_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.ignoreCharge_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.match_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.calibrate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeControlbar(self):
        """Make controlbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make elements
        filter_label = wx.StaticText(panel, -1, "Remove:")
        filter_label.SetFont(wx.SMALL_FONT)
        
        self.filterAnnotations_check = wx.CheckBox(panel, -1, "Annotated")
        self.filterAnnotations_check.SetFont(wx.SMALL_FONT)
        self.filterAnnotations_check.SetValue(config.match['filterAnnotations'])
        self.filterAnnotations_check.Bind(wx.EVT_CHECKBOX, self.onFilter)
        
        self.filterMatches_check = wx.CheckBox(panel, -1, "Matched")
        self.filterMatches_check.SetFont(wx.SMALL_FONT)
        self.filterMatches_check.SetValue(config.match['filterMatches'])
        self.filterMatches_check.Bind(wx.EVT_CHECKBOX, self.onFilter)
        
        self.filterUnselected_check = wx.CheckBox(panel, -1, "Unselected")
        self.filterUnselected_check.SetFont(wx.SMALL_FONT)
        self.filterUnselected_check.SetValue(config.match['filterUnselected'])
        self.filterUnselected_check.Bind(wx.EVT_CHECKBOX, self.onFilter)
        
        self.filterIsotopes_check = wx.CheckBox(panel, -1, "Isotopes")
        self.filterIsotopes_check.SetFont(wx.SMALL_FONT)
        self.filterIsotopes_check.SetValue(config.match['filterIsotopes'])
        self.filterIsotopes_check.Bind(wx.EVT_CHECKBOX, self.onFilter)
        
        self.filterUnknown_check = wx.CheckBox(panel, -1, "Unknown")
        self.filterUnknown_check.SetFont(wx.SMALL_FONT)
        self.filterUnknown_check.SetValue(config.match['filterUnknown'])
        self.filterUnknown_check.Bind(wx.EVT_CHECKBOX, self.onFilter)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(filter_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.filterAnnotations_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.filterMatches_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.filterUnselected_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.filterIsotopes_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.filterUnknown_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeErrorCanvas(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.errorCanvas = mspy.plot.canvas(self, size=(621, 220), style=mwx.PLOTCANVAS_STYLE_PANEL)
        self.errorCanvas.draw(mspy.plot.container([]))
        
        # set default params
        self.errorCanvas.setProperties(xLabel='m/z')
        self.errorCanvas.setProperties(yLabel='error (%s)' % config.match['units'])
        self.errorCanvas.setProperties(showZero=True)
        self.errorCanvas.setProperties(showGrid=True)
        self.errorCanvas.setProperties(showMinorTicks=False)
        self.errorCanvas.setProperties(showLegend=False)
        self.errorCanvas.setProperties(showXPosBar=True)
        self.errorCanvas.setProperties(posBarSize=6)
        self.errorCanvas.setProperties(showGel=False)
        self.errorCanvas.setProperties(zoomAxis='x')
        self.errorCanvas.setProperties(checkLimits=True)
        self.errorCanvas.setProperties(autoScaleY=False)
        self.errorCanvas.setProperties(xPosDigits=config.main['mzDigits'])
        self.errorCanvas.setProperties(yPosDigits=2)
        self.errorCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.errorCanvas.setProperties(reverseDrawing=True)
        self.errorCanvas.setMFunction('cross')
        
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.errorCanvas.setProperties(axisFont=axisFont)
        
        self.errorCanvas.draw(mspy.plot.container([]))
    # ----
    
    
    def makeSummaryList(self):
        """Make match summary list."""
        
        # init list
        self.summaryList = mwx.sortListCtrl(self, -1, size=(631, 200), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.summaryList.SetFont(wx.SMALL_FONT)
        self.summaryList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # make columns
        self.summaryList.InsertColumn(0, "parameter", wx.LIST_FORMAT_LEFT)
        self.summaryList.InsertColumn(1, "value", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((250,360)):
            self.summaryList.SetColumnWidth(col, width)
    # ----
    
    
    def makeGaugePanel(self):
        """Make processing gauge."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.gauge = mwx.gauge(panel, -1)
        
        stop_butt = wx.BitmapButton(panel, -1, images.lib['stopper'], style=wx.BORDER_NONE)
        stop_butt.Bind(wx.EVT_BUTTON, self.onStop)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.gauge, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(stop_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # fit layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        if wx.Platform == '__WXMAC__':
            mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP, -1)
        mainSizer.Add(sizer, 1, wx.EXPAND|wx.ALL, mwx.GAUGE_SPACE)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Destroy this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close self
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'errors'
            if evt and evt.GetId() == ID_matchErrors:
                tool = 'errors'
            elif evt and evt.GetId() == ID_matchSummary:
                tool = 'summary'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # set icons off
        self.errors_butt.SetBitmapLabel(images.lib['matchErrorsOff'])
        self.summary_butt.SetBitmapLabel(images.lib['matchSummaryOff'])
        
        # set panel
        if tool == 'errors':
            self.mainSizer.Show(2)
            self.errors_butt.SetBitmapLabel(images.lib['matchErrorsOn'])
            
        elif tool == 'summary':
            self.mainSizer.Show(3)
            self.summary_butt.SetBitmapLabel(images.lib['matchSummaryOn'])
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(4)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(4)
            self.processing = None
            mspy.start()
        
        # fit layout
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
    # ----
    
    
    def onStop(self, evt):
        """Cancel current processing."""
        
        if self.processing and self.processing.isAlive():
            mspy.stop()
        else:
            wx.Bell()
    # ----
    
    
    def onFilter(self, evt):
        """Apply peaklist filter."""
        
        # get current filters
        config.match['filterAnnotations'] = 0
        if self.filterAnnotations_check.GetValue():
            config.match['filterAnnotations'] = 1
        
        config.match['filterMatches'] = 0
        if self.filterMatches_check.GetValue():
            config.match['filterMatches'] = 1
        
        config.match['filterUnselected'] = 0
        if self.filterUnselected_check.GetValue():
            config.match['filterUnselected'] = 1
        
        config.match['filterIsotopes'] = 0
        if self.filterIsotopes_check.GetValue():
            config.match['filterIsotopes'] = 1
        
        config.match['filterUnknown'] = 0
        if self.filterUnknown_check.GetValue():
            config.match['filterUnknown'] = 1
        
        # clear values
        self.currentPeaklist = None
        self.currentSummary = None
        self.currentErrors = []
        self.currentCalibrationPoints = []
        
        # get peaklist
        self.getPeaklist()
        
        # update gui
        self.updateErrorCanvas()
        self.updateMatchSummary()
    # ----
    
    
    def onMatch(self, evt=None):
        """Match data to peaklist."""
        
        # check processing
        if self.processing:
            return
        
        # get params
        if not self.getParams():
            self.currentSummary = None
            self.currentErrors = []
            self.currentCalibrationPoints = []
            self.updateErrorCanvas()
            self.updateMatchSummary()
            wx.Bell()
            return
        
        # get current peaklist
        self.getPeaklist()
        
        # check data
        if self.currentData==None or self.currentPeaklist==None:
            self.currentSummary = None
            self.currentErrors = []
            self.currentCalibrationPoints = []
            self.updateErrorCanvas()
            self.updateMatchSummary()
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.match_butt.Enable(False)
        self.calibrate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runMatch)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        self.parentTool.updateMatches(self.currentModule)
        self.updateErrorCanvas()
        self.updateMatchSummary()
        
        # hide processing gauge
        self.onProcessing(False)
        self.match_butt.Enable(True)
        self.calibrate_butt.Enable(True)
    # ----
    
    
    def onCalibrate(self, evt):
        """Use matches for calibration."""
        
        # check references
        if not self.currentCalibrationPoints:
            wx.Bell()
            return
        
        # show calibration panel
        self.parentTool.calibrateByMatches(self.currentCalibrationPoints)
    # ----
    
    
    def onUnitsChanged(self, evt=None):
        """Change units in error plot."""
        
        # get units
        if self.unitsDa_radio.GetValue():
            config.match['units'] = 'Da'
        else:
            config.match['units'] = 'ppm'
        
        # recalc errors
        if config.match['units'] == 'ppm':
            for x in range(len(self.currentErrors)):
                self.currentErrors[x][1] = self.currentErrors[x][1] / (self.currentErrors[x][0] / 1000000)
        elif config.match['units'] == 'Da':
            for x in range(len(self.currentErrors)):
                self.currentErrors[x][1] = self.currentErrors[x][1] * (self.currentErrors[x][0] / 1000000)
        
        # update plot
        self.updateErrorCanvas()
    # ----
    
    
    def setData(self, matchData, summaryData=None):
        """Set data."""
        
        # update values
        self.currentData = matchData
        self.currentSummaryData = summaryData
        self.currentPeaklist = None
        self.currentSummary = None
        self.currentErrors = []
        self.currentCalibrationPoints = []
        
        # get current peaklist
        self.getPeaklist()
        
        # clear error canvas and summary
        self.updateErrorCanvas()
        self.updateMatchSummary()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            config.match['tolerance'] = float(self.tolerance_value.GetValue())
            
            config.match['units'] = 'ppm'
            if self.unitsDa_radio.GetValue():
                config.match['units'] = 'Da'
            
            config.match['ignoreCharge'] = 0
            if self.ignoreCharge_check.GetValue():
                config.match['ignoreCharge'] = 1
            
            config.match['filterAnnotations'] = 0
            if self.filterAnnotations_check.GetValue():
                config.match['filterAnnotations'] = 1
            
            config.match['filterMatches'] = 0
            if self.filterMatches_check.GetValue():
                config.match['filterMatches'] = 1
            
            config.match['filterUnselected'] = 0
            if self.filterUnselected_check.GetValue():
                config.match['filterUnselected'] = 1
            
            config.match['filterIsotopes'] = 0
            if self.filterIsotopes_check.GetValue():
                config.match['filterIsotopes'] = 1
            
            config.match['filterUnknown'] = 0
            if self.filterUnknown_check.GetValue():
                config.match['filterUnknown'] = 1
            
            return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def getPeaklist(self):
        """Get current peaklist according to specified filter."""
        
        # get filters
        filters = ''
        if config.match['filterAnnotations']:
            filters += 'A'
        if config.match['filterMatches']:
            filters += 'M'
        if config.match['filterUnselected']:
            filters += 'S'
        if config.match['filterIsotopes']:
            filters += 'I'
        if config.match['filterUnknown']:
            filters += 'X'
        
        # get peaklist
        self.currentPeaklist = self.mainFrame.getCurrentPeaklist(filters)
    # ----
    
    
    def runMatch(self):
        """Match data to peaklist."""
        
        # run task
        try:
            
            # set columns
            if self.currentModule == 'massfilter':
                massCol = 1
                chargeCol = None
                errorCol = 2
                matchObject = doc.annotation
            elif self.currentModule == 'digest':
                massCol = 2
                chargeCol = 3
                errorCol = 5
                matchObject = doc.match
            elif self.currentModule == 'fragment':
                massCol = 2
                chargeCol = 3
                errorCol = 5
                matchObject = doc.match
            elif self.currentModule == 'compounds':
                massCol = 1
                chargeCol = 2
                errorCol = 5
                matchObject = doc.annotation
            
            # clear previous match
            for item in self.currentData:
                item[errorCol] = None
                item[-1] = []
            
            # match data
            self.currentErrors = []
            self.currentCalibrationPoints = []
            
            digits = '%0.' + `config.main['mzDigits']` + 'f'
            for pIndex, peak in enumerate(self.currentPeaklist):
                for x, item in enumerate(self.currentData):
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    # check charge
                    if (chargeCol==None or peak.charge==None or config.match['ignoreCharge'] or peak.charge==item[chargeCol]):
                        
                        # check mass tolerance
                        error = mspy.delta(peak.mz, item[massCol], config.match['units'])
                        if abs(error) <= config.match['tolerance']:
                            
                            # create new match object
                            match = matchObject(label='', mz=peak.mz, ai=peak.ai, base=peak.base, theoretical=item[massCol])
                            match.peakIndex = pIndex
                            self.currentData[x][-1].append(match)
                            
                            # errors and calibration points
                            label = 'Peak ' + digits % peak.mz
                            self.currentErrors.append([peak.mz, error])
                            self.currentCalibrationPoints.append([label, item[massCol], peak.mz])
            
            # show best error only
            for item in self.currentData:
                for match in item[-1]:
                    error = match.delta(config.match['units'])
                    if item[errorCol] == None or abs(item[errorCol]) > abs(error):
                        item[errorCol] = error
            
            # get match summary
            self.makeMatchSummary()
        
        # task canceled
        except mspy.ForceQuit:
            self.currentErrors = []
            self.currentCalibrationPoints = []
            self.currentSummary = []
            for item in self.currentData:
                item[errorCol] = None
                item[-1] = []
            return
    # ----
    
    
    def clear(self):
        """Clear all."""
        
        self.currentData = None
        self.currentSummaryData = None
        self.currentPeaklist = None
        self.currentSummary = None
        self.currentErrors = []
        self.currentCalibrationPoints = []
        self.updateErrorCanvas()
        self.updateMatchSummary()
    # ----
    
    
    def updateErrorCanvas(self):
        """Update error canvas."""
        
        # make container
        container = mspy.plot.container([])
        
        # make points object
        self.currentErrors.sort()
        points = mspy.plot.points(self.currentErrors, pointColour=(0,255,0), showPoints=True, showLines=False)
        container.append(points)
        
        # make peaklist object
        if self.currentPeaklist:
            peaks = self.makeCurrentPeaklist()
            peaklist = mspy.plot.spectrum(mspy.scan(peaklist=peaks), tickColour=(170,170,170), showLabels=False)
            container.append(peaklist)
        
        # set units
        self.errorCanvas.setProperties(yLabel='error (%s)' % (config.match['units']))
        
        # draw container
        self.errorCanvas.draw(container)
    # ----
    
    
    def updateMatchSummary(self):
        """Update match summary list."""
        
        # clear previous data and set new
        self.summaryList.DeleteAllItems()
        self.summaryList.setDataMap(self.currentSummary)
        
        # check data
        if not self.currentSummary:
            return
        
        # add new data
        for row, item in enumerate(self.currentSummary):
            self.summaryList.InsertStringItem(row, item[0])
            self.summaryList.SetStringItem(row, 1, str(item[1]))
            self.summaryList.SetItemData(row, row)
        
        # update background
        self.summaryList.updateItemsBackground()
        
        # scroll top
        self.summaryList.EnsureVisible(0)
    # ----
    
    
    def makeCurrentPeaklist(self):
        """Convert peaklist for current error range."""
        
        # get error range
        minY = 0
        maxY = 1
        if self.currentErrors:
            errors = [x[1] for x in self.currentErrors]
            minY = min(errors)
            maxY = max(errors)
            if minY == maxY:
                minY -= abs(minY*0.1)
                maxY += abs(maxY*0.1)
            minY -= 0.05 * abs(maxY - minY)
        
        # convert peaklist
        peaklist = []
        basePeak = self.currentPeaklist.basepeak
        f = abs(maxY - minY) / basePeak.intensity
        for peak in self.currentPeaklist:
            intensity = (peak.intensity * f) + minY
            peaklist.append(mspy.peak(mz=peak.mz, ai=intensity, base=minY))
        
        # convert to mspy.peaklist
        return mspy.peaklist(peaklist)
    # ----
    
    
    def makeMatchSummary(self):
        """Make summary info for current match."""
        
        self.currentSummary = []
        
        # get items name
        if self.currentModule == 'massfilter':
            itemName = 'reference masses'
        elif self.currentModule == 'digest':
            itemName = 'peptides'
        elif self.currentModule == 'fragment':
            itemName = 'fragments'
        elif self.currentModule == 'compounds':
            itemName = 'compounds'
        
        # get searched peaks
        self.currentSummary.append(('Number of peaks searched', len(self.currentPeaklist)))
        
        # get searched items
        value = '%d' % len(self.currentData)
        label = 'Number of %s searched' % itemName
        self.currentSummary.append((label, value))
        
        # get matched peaks
        sumMatched = 0
        for item in self.currentData:
            if item[-1]:
                sumMatched += 1
        label = 'Number of %s matched' % itemName
        self.currentSummary.append((label, sumMatched))
        
        # get matched intensity
        totalInt = 0
        buff = {}
        for peak in self.currentPeaklist:
            totalInt += peak.intensity
            buff[round(peak.mz, 6)] = peak.intensity
        matchedInt = 0
        for item in self.currentData:
            for n in item[-1]:
                mz = round(n.mz,6)
                if mz in buff:
                    matchedInt += buff[mz]
                    del buff[mz]
        if totalInt:
            value = '%0.f %s' % ((100*matchedInt/totalInt), '%')
        else:
            value = '0 %'
        self.currentSummary.append(('Intensity matched', value))
        
        # get sequence coverage
        if self.currentModule == 'digest':
            sumPeptides = []
            for item in self.currentData:
                if item[-1]:
                    sumPeptides.append([item[6].history[-1][1]+1, item[6].history[-1][2]])
            coverage = mspy.coverage(sumPeptides, self.currentSummaryData['sequenceLength'])
            value = '%0.f %s' % (coverage, '%')
            self.currentSummary.append(('Sequence length', self.currentSummaryData['sequenceLength']))
            self.currentSummary.append(('Sequence coverage', value))
        
        # get ion series
        elif self.currentModule == 'fragment':
            self.currentSummary.append(('Sequence length', self.currentSummaryData['sequenceLength']))
            
            series = {}
            for item in self.currentData:
                frag = item[6]
                
                if not frag.fragmentSerie in ('a','b','c','x','y','z','n-ladder','c-ladder'):
                    continue
                elif 'break' in [x[0] for x in frag.history]:
                    continue
                
                name = frag.fragmentSerie
                for loss in frag.fragmentLosses:
                    name += ' -'+loss
                for gain in frag.fragmentGains:
                    name += ' +'+gain
                
                if not name in series:
                    series[name] = []
                if item[-1]:
                    series[name].append(frag.fragmentIndex)
                
            for serie in sorted(series.keys()):
                matches = series[serie]
                matches.sort()
                value = ', '.join(str(n) for n in matches)
                label = 'Ion serie matches for "%s"' % serie
                self.currentSummary.append((label, value))
    # ----
    

