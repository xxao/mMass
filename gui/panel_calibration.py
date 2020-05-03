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
import math
import wx
import numpy

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy
import mspy.plot


# FLOATING PANEL WITH CALIBRATION TOOL
# ------------------------------------

class panelCalibration(wx.MiniFrame):
    """Calibration tool."""
    
    def __init__(self, parent, tool='references'):
        wx.MiniFrame.__init__(self, parent, -1, 'Calibration', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.processing = None
        
        self.currentTool = tool
        self.currentDocument = None
        self.currentCalibration = None
        self.currentReferences = None
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # select default tool
        self.onToolSelected(tool=self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        references = self.makeReferencesPanel()
        errors = self.makeErrorsPanel()
        gauge = self.makeGaugePanel()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(references, 1, wx.EXPAND, 0)
        self.mainSizer.Add(errors, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make buttons
        self.references_butt = wx.BitmapButton(panel, ID_calibrationReferences, images.lib['calibrationReferencesOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.references_butt.SetToolTip(wx.ToolTip("Calibration references"))
        self.references_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.errors_butt = wx.BitmapButton(panel, ID_calibrationErrors, images.lib['calibrationErrorsOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.errors_butt.SetToolTip(wx.ToolTip("Calibration error plot"))
        self.errors_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        # make controls
        fitting_label = wx.StaticText(panel, -1, "Fitting:")
        fitting_label.SetFont(wx.SMALL_FONT)
        
        self.linearFit_radio = wx.RadioButton(panel, -1, "Linear", style=wx.RB_GROUP)
        self.linearFit_radio.SetFont(wx.SMALL_FONT)
        self.linearFit_radio.SetValue(True)
        self.linearFit_radio.Bind(wx.EVT_RADIOBUTTON, self.onModelChanged)
        
        self.quadraticFit_radio = wx.RadioButton(panel, -1, "Quadratic")
        self.quadraticFit_radio.SetFont(wx.SMALL_FONT)
        self.quadraticFit_radio.SetValue((config.calibration['fitting'] == 'quadratic'))
        self.quadraticFit_radio.Bind(wx.EVT_RADIOBUTTON, self.onModelChanged)
        
        units_label = wx.StaticText(panel, -1, "Units:")
        units_label.SetFont(wx.SMALL_FONT)
        
        self.unitsDa_radio = wx.RadioButton(panel, -1, "Da", style=wx.RB_GROUP)
        self.unitsDa_radio.SetFont(wx.SMALL_FONT)
        self.unitsDa_radio.SetValue(True)
        self.unitsDa_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        
        self.unitsPpm_radio = wx.RadioButton(panel, -1, "ppm")
        self.unitsPpm_radio.SetFont(wx.SMALL_FONT)
        self.unitsPpm_radio.SetValue((config.calibration['units'] == 'ppm'))
        self.unitsPpm_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        
        self.assign_butt = wx.Button(panel, -1, "Assign", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.assign_butt.Bind(wx.EVT_BUTTON, self.onAssign)
        
        self.apply_butt = wx.Button(panel, -1, "Apply", size=(100, mwx.SMALL_BUTTON_HEIGHT))
        self.apply_butt.Bind(wx.EVT_BUTTON, self.onApply)
        self.apply_butt.Disable()
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.references_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.errors_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(20)
        sizer.Add(fitting_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.linearFit_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.quadraticFit_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(units_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.unitsDa_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.unitsPpm_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.assign_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.apply_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeReferencesPanel(self):
        """Make references selection panel."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        references_label = wx.StaticText(ctrlPanel, -1, "References:")
        references_label.SetFont(wx.SMALL_FONT)
        choices = libs.references.keys()
        choices.sort()
        choices.insert(0,'Reference lists')
        self.references_choice = wx.Choice(ctrlPanel, -1, choices=choices, size=(250, mwx.SMALL_CHOICE_HEIGHT))
        self.references_choice.Select(0)
        self.references_choice.Bind(wx.EVT_CHOICE, self.onReferencesSelected)
        
        tolerance_label = wx.StaticText(ctrlPanel, -1, "Tolerance:")
        tolerance_label.SetFont(wx.SMALL_FONT)
        self.tolerance_value = wx.TextCtrl(ctrlPanel, -1, str(config.calibration['tolerance']), size=(50, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        self.tolerance_value.SetFont(wx.SMALL_FONT)
        self.toleranceUnits_label = wx.StaticText(ctrlPanel, -1, config.calibration['units'])
        self.toleranceUnits_label.SetFont(wx.SMALL_FONT)
        
        self.statCalibration_check = wx.CheckBox(ctrlPanel, -1, "Statistical only")
        self.statCalibration_check.SetFont(wx.SMALL_FONT)
        self.statCalibration_check.Bind(wx.EVT_CHECKBOX, self.onStatCalibration)
        
        self.makeReferencesList()
        
        # pack controls
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(references_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.references_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(tolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.tolerance_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.toleranceUnits_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.statCalibration_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        controls = wx.BoxSizer(wx.VERTICAL)
        controls.Add(sizer, 1, wx.EXPAND)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND, 0)
        mainSizer.Add(self.referencesList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makeReferencesList(self):
        """Make references list."""
        
        # init list
        self.referencesList = mwx.sortListCtrl(self, -1, size=(651, 250), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.referencesList.SetFont(wx.SMALL_FONT)
        self.referencesList.setSecondarySortColumn(2)
        self.referencesList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.referencesList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.referencesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        
        # make columns
        self.referencesList.InsertColumn(0, "reference", wx.LIST_FORMAT_LEFT)
        self.referencesList.InsertColumn(1, "theoretical", wx.LIST_FORMAT_RIGHT)
        self.referencesList.InsertColumn(2, "measured", wx.LIST_FORMAT_RIGHT)
        self.referencesList.InsertColumn(3, "calibrated", wx.LIST_FORMAT_RIGHT)
        self.referencesList.InsertColumn(4, "error before", wx.LIST_FORMAT_RIGHT)
        self.referencesList.InsertColumn(5, "error after", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((180,90,90,90,90,90)):
            self.referencesList.SetColumnWidth(col, width)
    # ----
    
    
    def makeErrorsPanel(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.errorCanvas = mspy.plot.canvas(self, size=(-1, 250), style=mwx.PLOTCANVAS_STYLE_PANEL)
        
        # set default params
        self.errorCanvas.setProperties(xLabel='m/z')
        self.errorCanvas.setProperties(yLabel='error')
        self.errorCanvas.setProperties(showZero=True)
        self.errorCanvas.setProperties(showGrid=True)
        self.errorCanvas.setProperties(showMinorTicks=False)
        self.errorCanvas.setProperties(showLegend=True)
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
        
        return self.errorCanvas
    # ----
    
    
    def makeGaugePanel(self):
        """Make processing gauge."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.gauge = mwx.gauge(panel, -1)
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        if wx.Platform == '__WXMAC__':
            mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP, -1)
        mainSizer.Add(self.gauge, 0, wx.EXPAND|wx.ALL, mwx.GAUGE_SPACE)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close self
        self.Destroy()
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(3)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(3)
            self.processing = None
        
        # fit layout
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'references'
            if evt.GetId() == ID_calibrationReferences:
                tool = 'references'
            elif evt.GetId() == ID_calibrationErrors:
                tool = 'errors'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        
        # set icons off
        self.references_butt.SetBitmapLabel(images.lib['calibrationReferencesOff'])
        self.errors_butt.SetBitmapLabel(images.lib['calibrationErrorsOff'])
        
        # set panel
        if tool == 'references':
            self.SetTitle("Calibration")
            self.references_butt.SetBitmapLabel(images.lib['calibrationReferencesOn'])
            self.mainSizer.Show(1)
            
        elif tool == 'errors':
            self.SetTitle("Error Plot")
            self.errors_butt.SetBitmapLabel(images.lib['calibrationErrorsOn'])
            self.mainSizer.Show(2)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onModelChanged(self, evt):
        """Fitting model has been changed."""
        
        # get model
        config.calibration['fitting'] = 'linear'
        if self.quadraticFit_radio.GetValue():
            config.calibration['fitting'] = 'quadratic'
        
        # check data
        if not self.currentReferences:
            return
        
        # recalculate calibration
        self.calcCalibration()
        
        # update GUI
        self.updateReferencesList()
        self.updateErrorPlot()
    # ----
    
    
    def onUnitsChanged(self, evt):
        """Set current units and update data."""
        
        # get units
        config.calibration['units'] = 'Da'
        if self.unitsPpm_radio.GetValue():
            config.calibration['units'] = 'ppm'
        
        # update tolerance units label
        self.toleranceUnits_label.SetLabel(config.calibration['units'])
        
        # recalculate errors
        if self.currentReferences:
            for x, item in enumerate(self.currentReferences):
                if item[2] != None and item[3] != None:
                    self.currentReferences[x][4] = mspy.delta(item[2], item[1], config.calibration['units'])
                    self.currentReferences[x][5] = mspy.delta(item[3], item[1], config.calibration['units'])
        
        # update GUI
        self.updateReferencesList()
        self.updateErrorPlot()
    # ----
    
    
    def onReferencesSelected(self, evt=None):
        """Update reference list."""
        
        # clear last calibration
        self.currentCalibration = None
        self.currentReferences = None
        
        # disable button
        self.apply_butt.SetLabel('Apply')
        self.apply_butt.Enable(False)
        
        # get references
        group = self.references_choice.GetStringSelection()
        if group and group in libs.references:
            self.currentReferences = []
            for item in libs.references[group]:
                self.currentReferences.append([item[0], item[1], None, None, None, None, True])
                # 0 title, 1 theoretical, 2 measured, 3 calibrated, 4 error before, 5 error after, 6 use
        
        # update GUI
        self.updateReferencesList(scroll=True)
        self.updateErrorPlot()
    # ----
    
    
    def onStatCalibration(self, evt):
        """Use statistical calibration."""
        
        # enable statistical calibration
        if self.statCalibration_check.GetValue():
            self.references_choice.Enable(False)
            self.tolerance_value.Enable(False)
            self.onAssign()
            
        # disable statistical calibration
        else:
            self.references_choice.Enable(True)
            self.tolerance_value.Enable(True)
            self.onReferencesSelected()
    # ----
    
    
    def onItemSelected(self, evt):
        """Show selected mass in spectrum canvas."""
        
        # get points
        points = []
        theoretical = self.currentReferences[evt.GetData()][1]
        points.append(theoretical)
        measured = self.currentReferences[evt.GetData()][2]
        if measured:
            points.append(measured)
        
        # show points
        self.parent.updateMassPoints(points)
    # ----
    
    
    def onItemActivated(self, evt):
        """Discard selected item from calibration."""
        
        # get item
        index = evt.GetData()
        row = evt.GetIndex()
        
        # update item
        self.currentReferences[index][6] = not self.currentReferences[index][6]
        
        # recalculate calibration
        self.calcCalibration()
        
        # update GUI
        self.updateReferencesList()
        self.updateErrorPlot()
        
        # scroll to see selected reference
        self.referencesList.EnsureVisible(row)
    # ----
    
    
    def onAssign(self, evt=None):
        """Assign reference masses to peaks."""
        
        # clear last calibration
        self.currentCalibration = None
        
        # disable buttons
        self.apply_butt.SetLabel('Apply')
        self.apply_butt.Enable(False)
        
        # check document
        if not self.currentDocument:
            wx.Bell()
            return
        
        # statistical calibration
        if self.statCalibration_check.GetValue():
            self.statisticalCalibration()
        
        # internal calibration
        else:
            self.internalCalibration()
        
        # update GUI
        self.updateReferencesList()
        self.updateErrorPlot()
    # ----
    
    
    def onApply(self, evt):
        """Apply current calibration to document."""
        
        # check processing
        if self.processing:
            return
        
        # check document
        if not self.currentDocument:
            wx.Bell()
            return
        
        # check calibration
        if not self.currentCalibration:
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.assign_butt.Enable(False)
        self.apply_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.applyCalibration, kwargs={'fn':self.currentCalibration[0], 'params':self.currentCalibration[1]})
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # empty references
        if self.statCalibration_check.GetValue():
            self.currentReferences = None
        elif self.currentReferences:
            for x in range(len(self.currentReferences)):
                self.currentReferences[x][2:] = [None, None, None, None, True]
        
        # update GUI
        self.updateReferencesList(scroll=True)
        self.updateErrorPlot()
        
        # update document
        self.parent.onDocumentChanged(items=('spectrum', 'notations'))
        
        # hide processing gauge
        self.onProcessing(False)
        self.assign_butt.Enable(True)
    # ----
    
    
    def updateReferencesList(self, scroll=False):
        """Update reference mass list."""
        
        # clear previous data and set new
        self.referencesList.DeleteAllItems()
        self.referencesList.setDataMap(self.currentReferences)
        
        # check data
        if not self.currentReferences:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        ppmFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        fontSkipped = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.NORMAL)
        fontUsed = wx.SMALL_FONT
        for row, item in enumerate(self.currentReferences):
            
            # format data
            theoretical = mzFormat % (item[1])
            measured = ''
            calibrated = ''
            errorBefore = ''
            errorAfter = ''
            if item[2] != None:
                measured = mzFormat % (item[2])
            if item[3] != None:
                calibrated = mzFormat % (item[3])
            if item[4] != None and item[5] != None:
                if config.calibration['units'] == 'Da':
                    errorBefore = mzFormat % (item[4])
                    errorAfter = mzFormat % (item[5])
                else:
                    errorBefore = ppmFormat % (item[4])
                    errorAfter = ppmFormat % (item[5])
            
            # add data
            self.referencesList.InsertStringItem(row, '')
            self.referencesList.SetStringItem(row, 0, item[0])
            self.referencesList.SetStringItem(row, 1, theoretical)
            self.referencesList.SetStringItem(row, 2, measured)
            self.referencesList.SetStringItem(row, 3, calibrated)
            self.referencesList.SetStringItem(row, 4, errorBefore)
            self.referencesList.SetStringItem(row, 5, errorAfter)
            self.referencesList.SetItemData(row, row)
            
            # mark skipped
            if not item[6]:
                self.referencesList.SetItemTextColour(row, (150,150,150))
                self.referencesList.SetItemFont(row, fontSkipped)
            else:
                self.referencesList.SetItemTextColour(row, (0,0,0))
                self.referencesList.SetItemFont(row, fontUsed)
        
        # sort data
        self.referencesList.sort()
        
        # scroll top
        if scroll:
            self.referencesList.EnsureVisible(0)
    # ----
    
    
    def updateErrorPlot(self):
        """Update error plot."""
        
        # make container
        container = mspy.plot.container([])
        minY = 0
        maxY = 1
        
        # make points
        if self.currentReferences:
            intensities = []
            
            # get after points
            pointsAfter = []
            for item in self.currentReferences:
                if item[6] and item[5] != None:
                    pointsAfter.append([item[2], item[5]])
                    intensities.append(item[5])
            if pointsAfter:
                pointsAfter.sort()
                obj = mspy.plot.points(pointsAfter, pointColour=(0,255,0), legend='after', showLines=False, showPoints=True)
                container.append(obj)
            
            # get before points
            pointsBefore = []
            for item in self.currentReferences:
                if item[6] and item[4] != None:
                    pointsBefore.append([item[2], item[4]])
                    intensities.append(item[4])
            if pointsBefore:
                pointsBefore.sort()
                obj = mspy.plot.points(pointsBefore, pointColour=(255,100,100), legend='before', showLines=False, showPoints=True)
                container.append(obj)
            
            # set range
            if intensities:
                minY = min(intensities)
                maxY = max(intensities)
                if minY == maxY:
                    minY -= minY*0.1
                    maxY += maxY*0.1
            
            # make calibration curve
            if self.currentCalibration and self.currentDocument and self.currentDocument.spectrum.peaklist:
                curvePoints = self.makeCalibrationCurve()
                curvePoints = numpy.array(curvePoints)
                if config.calibration['units'] == 'ppm':
                    obj = mspy.plot.points(curvePoints, lineColour=(255,100,100), showLines=True, showPoints=False, lineStyle=mwx.DASHED_LINE)
                else:
                    obj = mspy.plot.points(curvePoints, lineColour=(255,100,100), showLines=True, showPoints=False)
                container.append(obj)
                
                # set range
                if intensities:
                    minY = min(minY, float(numpy.minimum.reduce(curvePoints)[1]))
                    maxY = max(maxY, float(numpy.maximum.reduce(curvePoints)[1]))
                else:
                    minY = float(numpy.minimum.reduce(curvePoints)[1])
                    maxY = float(numpy.maximum.reduce(curvePoints)[1])
        
        # make peaklist
        if self.currentDocument and self.currentDocument.spectrum.peaklist:
            peaks = self.makeCurrentPeaklist(minY, maxY)
            obj = mspy.plot.spectrum(mspy.scan(peaklist=peaks), tickColour=(170,170,170), showLabels=False)
            container.append(obj)
        
        # set units
        self.errorCanvas.setProperties(yLabel='error (%s)' % (config.calibration['units']))
        
        # draw container
        self.errorCanvas.draw(container)
    # ----
    
    
    def setData(self, document, references=None):
        """Set current document."""
        
        # set new document
        self.currentDocument = document
        
        # disable buttons
        self.apply_butt.SetLabel('Apply')
        self.apply_butt.Enable(False)
        
        # clear references
        if self.statCalibration_check.GetValue():
            self.currentReferences = None
        elif self.currentReferences:
            for x in range(len(self.currentReferences)):
                self.currentReferences[x][2:] = [None,None,None,None,True]
        
        # internal calibration on given references
        if references:
            
            # set GUI
            self.onToolSelected(tool='references')
            self.statCalibration_check.SetValue(False)
            self.references_choice.Enable(True)
            self.tolerance_value.Enable(True)
            self.references_choice.Select(0)
            
            # set references
            self.currentReferences = []
            for ref in references:
                delta = mspy.delta(ref[2], ref[1], config.calibration['units'])
                self.currentReferences.append([ref[0], ref[1], ref[2], None, delta, None, True])
            
            # get calibration
            self.calcCalibration()
        
        # enable clipboard
        elif self.currentCalibration and document!=None:
            self.apply_butt.SetLabel('Apply Recent')
            self.apply_butt.Enable(True)
        
        # update GUI
        self.updateReferencesList(scroll=True)
        self.updateErrorPlot()
    # ----
    
    
    def calcCalibration(self):
        """Get calibration based on currently assigned masses."""
        
        # clear last calibration
        self.currentCalibration = None
        
        # disable buttons
        self.apply_butt.SetLabel('Apply')
        self.apply_butt.Enable(False)
        
        # get calibration points
        points = []
        for item in self.currentReferences:
            item[3] = None
            item[5] = None
            if item[6] and item[2]!=None:
                points.append([item[2], item[1]])
        
        # get calibration
        model = config.calibration['fitting']
        if (model=='linear' and len(points)>=1) or (model=='quadratic' and len(points)>=3):
            self.currentCalibration = mspy.calibration(points, model)
            model = self.currentCalibration[0]
            params = self.currentCalibration[1]
            
            # recalculate assigned peaks
            for x, item in enumerate(self.currentReferences):
                if item[2]!=None:
                    calibrated = model(params, item[2])
                    self.currentReferences[x][3] = calibrated
                    self.currentReferences[x][5] = mspy.delta(calibrated, item[1], config.calibration['units'])
            
            # enable buttons
            self.apply_butt.Enable(True)
    # ----
    
    
    def internalCalibration(self):
        """Assign reference masses to peaks."""
        
        # check references
        if not self.currentReferences:
            wx.Bell()
            return
        else:
            for x in range(len(self.currentReferences)):
                self.currentReferences[x][2:7] = (None, None, None, None, True)
        
        # get peaklist
        peaklist = self.currentDocument.spectrum.peaklist
        if not peaklist:
            wx.Bell()
            return
        
        # get tolerance
        try:
            config.calibration['tolerance'] = float(self.tolerance_value.GetValue())
        except:
            wx.Bell()
            return
        
        # find peaks within tolerance
        for x, item in enumerate(self.currentReferences):
            for peak in peaklist:
                delta = mspy.delta(peak.mz, item[1], config.calibration['units'])
                if abs(delta) <= config.calibration['tolerance']:
                    if self.currentReferences[x][2]==None or abs(delta) < abs(self.currentReferences[x][4]):
                        self.currentReferences[x][2] = peak.mz
                        self.currentReferences[x][4] = delta
                if delta > config.calibration['tolerance']:
                    break
        
        # get calibration
        self.calcCalibration()
    # ----
    
    
    def statisticalCalibration(self):
        """Do statistical calibration."""
        
        # get peaklist
        peaklist = self.currentDocument.spectrum.peaklist
        if not peaklist:
            wx.Bell()
            return
        
        # get reference masses
        self.currentReferences = []
        for peak in peaklist:
            
            # check statCutOff
            if peak.mz < config.calibration['statCutOff']:
                continue
            
            # get theoretical mass
            theoretical = math.modf(peak.mz)[1] + math.modf(round(peak.mz)*1.00048)[0]
            if (peak.mz - theoretical) > 0.5:
                theoretical += 1
            elif (peak.mz - theoretical) < -0.5:
                theoretical -= 1
            
            title = 'Peak %.2f' % (peak.mz)
            delta = mspy.delta(peak.mz, theoretical, config.calibration['units'])
            self.currentReferences.append([title, theoretical, peak.mz, None, delta, None, True])
        
        # get calibration
        self.calcCalibration()
    # ----
    
    
    def applyCalibration(self, fn, params):
        """Calibrate document."""
        
        # backup data
        self.currentDocument.backup(('spectrum', 'notations'))
        
        # recalibrate spectrum
        self.currentDocument.spectrum.recalibrate(fn, params)
        
        # recalibrate annotations
        for annotation in self.currentDocument.annotations:
            annotation.mz = fn(params, annotation.mz)
        
        # recalibrate matches
        for sequence in self.currentDocument.sequences:
            for match in sequence.matches:
                match.mz = fn(params, match.mz)
    # ----
    
    
    def makeCalibrationCurve(self):
        """Make calibration curve to show in plot."""
        
        # get range
        minX = self.currentDocument.spectrum.peaklist[0].mz
        maxX = self.currentDocument.spectrum.peaklist[-1].mz
        
        # init params
        step = (maxX-minX)/100.
        fn = self.currentCalibration[0]
        params = self.currentCalibration[1]
        
        # make points in Da
        points = []
        for x in range(100):
            mz = minX+step*x
            error = mspy.delta(mz, fn(params, mz), config.calibration['units'])
            points.append((mz, error))
        
        return points
    # ----
    
    
    def makeCurrentPeaklist(self, minY, maxY):
        """Convert peaklist for current error range."""
        
        # shift peaklist
        if (minY,maxY) != (0,1):
            minY -= 0.05 * abs(maxY - minY)
        
        # convert peaklist
        peaklist = []
        basePeak = self.currentDocument.spectrum.peaklist.basepeak
        f = abs(maxY - minY) / basePeak.intensity
        for peak in self.currentDocument.spectrum.peaklist:
            intensity = (peak.intensity * f) + minY
            peaklist.append(mspy.peak(mz=peak.mz, ai=intensity, base=minY))
        
        # convert to mspy.peaklist
        return mspy.peaklist(peaklist)
    # ----
    
    

