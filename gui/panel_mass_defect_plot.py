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
import math
import wx

# load modules
from ids import *
import mwx
import images
import config
import mspy
import mspy.plot


# FLOATING PANEL WITH MASS DEFECT PLOT
# ------------------------------------

class panelMassDefectPlot(wx.MiniFrame):
    """Mass defect plot tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Mass Defect Plot', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE)
        
        self.parent = parent
        
        self.currentDocument = None
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        controlbar = self.makeControlbar()
        
        # make panels
        self.makePlotCanvas()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.plotCanvas, 1, wx.EXPAND, 0)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
        self.Layout()
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        yAxis_label = wx.StaticText(panel, -1, "MD type:")
        yAxis_label.SetFont(wx.SMALL_FONT)
        choices = ['Fractional Mass', 'Mass Defect', 'Relative Mass Defect', 'Kendrick Mass Defect']
        self.yAxis_choice = wx.Choice(panel, -1, choices=choices, size=(175, mwx.SMALL_CHOICE_HEIGHT))
        self.yAxis_choice.Select(1)
        choices = ['fraction', 'standard', 'relative', 'kendrick']
        if config.massDefectPlot['yAxis'] in choices:
            self.yAxis_choice.Select(choices.index(config.massDefectPlot['yAxis']))
        self.yAxis_choice.Bind(wx.EVT_CHOICE, self.onAxisChanged)
        
        nominalMass_label = wx.StaticText(panel, -1, "Nominal mass:")
        nominalMass_label.SetFont(wx.SMALL_FONT)
        choices = ['Ceil', 'Round', 'Floor']
        self.nominalMass_choice = wx.Choice(panel, -1, choices=choices, size=(80, mwx.SMALL_CHOICE_HEIGHT))
        self.nominalMass_choice.Select(1)
        if config.massDefectPlot['nominalMass'].title() in choices:
            self.nominalMass_choice.Select(choices.index(config.massDefectPlot['nominalMass'].title()))
        
        kendrickFormula_label = wx.StaticText(panel, -1, "Kendrick formula:")
        kendrickFormula_label.SetFont(wx.SMALL_FONT)
        self.kendrickFormula_value = mwx.formulaCtrl(panel, -1, config.massDefectPlot['kendrickFormula'], size=(80, -1))
        
        # make buttons
        self.plot_butt = wx.Button(panel, -1, "Plot", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.plot_butt.Bind(wx.EVT_BUTTON, self.onPlot)
        
        self.onAxisChanged()
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(yAxis_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.yAxis_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(nominalMass_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.nominalMass_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(kendrickFormula_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.kendrickFormula_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.plot_butt, 0, wx.ALIGN_CENTER_VERTICAL)
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
        relIntCutoff_label = wx.StaticText(panel, -1, "Int. threshold:")
        relIntCutoff_label.SetFont(wx.SMALL_FONT)
        relIntCutoffUnits_label = wx.StaticText(panel, -1, "%")
        relIntCutoffUnits_label.SetFont(wx.SMALL_FONT)
        self.relIntCutoff_value = wx.TextCtrl(panel, -1, str(config.massDefectPlot['relIntCutoff']*100), size=(50, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        self.relIntCutoff_value.SetFont(wx.SMALL_FONT)
        
        self.removeIsotopes_check = wx.CheckBox(panel, -1, "Remove isotopes")
        self.removeIsotopes_check.SetFont(wx.SMALL_FONT)
        self.removeIsotopes_check.SetValue(config.massDefectPlot['removeIsotopes'])
        
        self.ignoreCharge_check = wx.CheckBox(panel, -1, "Ignore charge")
        self.ignoreCharge_check.SetFont(wx.SMALL_FONT)
        self.ignoreCharge_check.SetValue(config.massDefectPlot['ignoreCharge'])
        
        self.showNotations_check = wx.CheckBox(panel, -1, "Highlight annotated")
        self.showNotations_check.SetFont(wx.SMALL_FONT)
        self.showNotations_check.SetValue(config.massDefectPlot['showNotations'])
        self.showNotations_check.Bind(wx.EVT_CHECKBOX, self.onShowNotations)
        
        self.showAllDocuments_check = wx.CheckBox(panel, -1, "Show all documents")
        self.showAllDocuments_check.SetFont(wx.SMALL_FONT)
        self.showAllDocuments_check.SetValue(False)
        self.showAllDocuments_check.Bind(wx.EVT_CHECKBOX, self.onShowAllDocuments)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(relIntCutoff_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.relIntCutoff_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(relIntCutoffUnits_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.removeIsotopes_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.ignoreCharge_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.showNotations_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.showAllDocuments_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makePlotCanvas(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.plotCanvas = mspy.plot.canvas(self, size=(650, 300), style=mwx.PLOTCANVAS_STYLE_PANEL)
        self.plotCanvasContainer = mspy.plot.container([])
        
        # set default params
        self.plotCanvas.setProperties(xLabel='m/z')
        self.plotCanvas.setProperties(yLabel='mass defect')
        self.plotCanvas.setProperties(showLegend=False)
        self.plotCanvas.setProperties(showZero=True)
        self.plotCanvas.setProperties(showGrid=True)
        self.plotCanvas.setProperties(showMinorTicks=False)
        self.plotCanvas.setProperties(showXPosBar=True)
        self.plotCanvas.setProperties(showYPosBar=True)
        self.plotCanvas.setProperties(posBarSize=6)
        self.plotCanvas.setProperties(showGel=False)
        self.plotCanvas.setProperties(zoomAxis='xy')
        self.plotCanvas.setProperties(checkLimits=True)
        self.plotCanvas.setProperties(autoScaleY=False)
        self.plotCanvas.setProperties(xPosDigits=config.main['mzDigits'])
        self.plotCanvas.setProperties(yPosDigits=config.main['mzDigits'])
        self.plotCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.plotCanvas.setProperties(reverseDrawing=True)
        self.plotCanvas.setMFunction('cross')
        self.plotCanvas.setLMBFunction('xDistance')
        
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.plotCanvas.setProperties(axisFont=axisFont)
        
        self.plotCanvas.draw(self.plotCanvasContainer)
        
        self.plotCanvas.Bind(wx.EVT_LEFT_UP, self.onPlotCanvasLMU)
    # ----
    
    
    def onClose(self, evt):
        """Destroy this frame."""
        
        # close self
        self.Destroy()
    # ----
    
    
    def onPlot(self, evt=None):
        """Calculate and show mass defect plot."""
        
        # clear previous data
        self.plotCanvasContainer.empty()
        
        # get params
        if not self.getParams():
            self.plotCanvas.refresh()
            wx.Bell()
            return
        
        # show annotations for current document on top
        if self.currentDocument != None and config.massDefectPlot['showNotations']:
            
            buff = []
            for item in self.currentDocument.annotations:
                buff.append((item.mz, item.charge))
            for sequence in self.currentDocument.sequences:
                for item in sequence.matches:
                    buff.append((item.mz, item.charge))
            
            points = self.makeDataPoints(mspy.peaklist(buff), self.currentDocument.spectrum.polarity)
            obj = mspy.plot.points(points, pointColour=(255,0,0), showPoints=True, showLines=False)
            self.plotCanvasContainer.append(obj)
        
        # show all documents
        if config.massDefectPlot['showAllDocuments']:
            for docData in self.parent.documents:
                if docData.visible:
                    points = self.makeDataPoints(docData.spectrum.peaklist, docData.spectrum.polarity)
                    obj = mspy.plot.points(points, pointColour=docData.colour, showPoints=True, showLines=False)
                    self.plotCanvasContainer.append(obj)
        
        # show current document only
        elif self.currentDocument != None:
            points = self.makeDataPoints(self.currentDocument.spectrum.peaklist, self.currentDocument.spectrum.polarity)
            obj = mspy.plot.points(points, pointColour=(0,255,0), showPoints=True, showLines=False)
            self.plotCanvasContainer.append(obj)
        
        # update plot
        self.updatePlotCanvasLabels()
        self.plotCanvas.draw(self.plotCanvasContainer)
    # ----
    
    
    def onPlotCanvasLMU(self, evt):
        """Highlight selected point in spectrum."""
        
        # check document
        if self.currentDocument == None:
            evt.Skip()
            return
        
        # get cursor positions
        position = self.plotCanvas.getCursorPosition()
        distance = self.plotCanvas.getDistance()
        
        # sent event back to canvas
        self.plotCanvas.onLMU(evt)
        
        # highlight selected point in spectrum
        if position and distance and distance[0] == 0:
            self.parent.updateMassPoints([position[0]])
        
        evt.Skip()
    # ----
    
    
    def onAxisChanged(self, evt=None):
        """Enable / disable Kendrick formula field."""
        
        # get current selection
        yAxis = self.yAxis_choice.GetStringSelection()
        
        # enable/disable Kendrick formula
        if yAxis == 'Kendrick Mass Defect':
            self.kendrickFormula_value.Enable()
        else:
            self.kendrickFormula_value.Disable()
        
        # ensure Kendrick formula is set
        if not self.kendrickFormula_value.GetValue():
            self.kendrickFormula_value.SetValue('CH2')
    # ----
    
    
    def onShowNotations(self, evt):
        """Show / hide annotated points."""
        
        # get value
        config.massDefectPlot['showNotations'] = self.showNotations_check.GetValue()
        
        # update plot
        self.onPlot()
    # ----
    
    
    def onShowAllDocuments(self, evt):
        """Show current document or all visible."""
        
        # get value
        config.massDefectPlot['showAllDocuments'] = self.showAllDocuments_check.GetValue()
        
        # update plot
        self.onPlot()
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set new document
        self.currentDocument = document
        
        # update plot
        self.onPlot()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            choices = ['fraction', 'standard', 'relative', 'kendrick']
            config.massDefectPlot['yAxis'] = choices[self.yAxis_choice.GetSelection()]
            
            config.massDefectPlot['nominalMass'] = self.nominalMass_choice.GetStringSelection().lower()
            config.massDefectPlot['relIntCutoff'] = float(self.relIntCutoff_value.GetValue())/100.
            config.massDefectPlot['removeIsotopes'] = self.removeIsotopes_check.GetValue()
            config.massDefectPlot['ignoreCharge'] = self.ignoreCharge_check.GetValue()
            config.massDefectPlot['showNotations'] = self.showNotations_check.GetValue()
            config.massDefectPlot['showAllDocuments'] = self.showAllDocuments_check.GetValue()
            
            formula = self.kendrickFormula_value.GetValue()
            cmpd = mspy.compound(formula)
            config.massDefectPlot['kendrickFormula'] = str(formula)
            if config.massDefectPlot['yAxis'] == 'kendrick' and cmpd.mass(0) == 0:
                raise ValueError
            
            return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateDocuments(self):
        """Reload all visible documents."""
        
        # skip if current document only is shown
        if not config.massDefectPlot['showAllDocuments']:
            return
        
        # reload visible documents
        self.onPlot()
    # ----
    
    
    def updatePlotCanvasLabels(self):
        """Update plot canvas axes labels."""
        
        xLabel = 'm/z'
        yLabel = 'mass defect'
        
        # set x axis
        if config.massDefectPlot['xAxis'] == 'mz':
            xLabel = 'm/z'
        elif config.massDefectPlot['xAxis'] == 'nominal':
            xLabel = 'nominal mass'
        elif config.massDefectPlot['xAxis'] == 'kendrick':
            xLabel = 'kendrick mass'
        
        # set y axis
        if config.massDefectPlot['yAxis'] == 'fraction':
            yLabel = 'fractional mass'
        elif config.massDefectPlot['yAxis'] == 'standard':
            yLabel = 'mass defect'
        elif config.massDefectPlot['yAxis'] == 'relative':
            yLabel = 'relative mass defect'
        elif config.massDefectPlot['yAxis'] == 'kendrick':
            yLabel = 'kendrick mass defect'
        
        self.plotCanvas.setProperties(xLabel=xLabel)
        self.plotCanvas.setProperties(yLabel=yLabel)
    # ----
    
    
    def makeDataPoints(self, peaklist, polarity=1):
        """Make plot points for spectrum peaklist."""
        
        # get spectrum polarity
        if not polarity:
            polarity = 1
        
        # get peaks
        buff = []
        for peak in peaklist:
            
            # remove isotopes
            if config.massDefectPlot['removeIsotopes'] and not peak.isotope in (0, None):
                continue
            
            # remove low abundant peaks
            if peak.ri < config.massDefectPlot['relIntCutoff']:
                continue
            
            # append point to buffer
            buff.append([peak.mz, peak.charge])
        
        # calculate mass and mass defect for each point
        points = self.calcDataPoints(buff, polarity)
        
        return points
    # ----
    
    
    def calcDataPoints(self, peaks, polarity=1):
        """Calculate requested mass and mass defect."""
        
        buff = []
        
        # init Kendrick formula
        kendrickFormula = mspy.compound(config.massDefectPlot['kendrickFormula'])
        
        # calculate data points
        for peak in peaks:
            
            mass = peak[0]
            if not config.massDefectPlot['ignoreCharge'] and peak[1]:
                mass = mspy.mz(peak[0], 1*polarity, peak[1], agentFormula='H', agentCharge=1)
            
            # calc mass defect
            md = mspy.md(
                mass = mass,
                mdType = config.massDefectPlot['yAxis'],
                kendrickFormula = kendrickFormula,
                rounding = config.massDefectPlot['nominalMass']
            )
            
            # re-calculate selected mass
            if config.massDefectPlot['xAxis'] == 'mz':
                mass = peak[0]
            
            elif config.massDefectPlot['xAxis'] == 'nominal':
                mass = mspy.nominalmass(peak[0], config.massDefectPlot['nominalMass'])
            
            elif config.massDefectPlot['xAxis'] == 'kendrick':
                mass = mspy.nominalmass(peak[0] * kendrickFormula.nominalmass()/kendrickFormula.mass(0))
            
            else:
                mass = peak[0]
            
            # append point
            buff.append((mass, md))
        
        return buff
    # ----
    
    
