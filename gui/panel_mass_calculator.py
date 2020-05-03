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
from ids import *
import mwx
import images
import config
import doc
import mspy
import mspy.plot


# FLOATING PANEL WITH MASSCALC TOOLS
# ----------------------------------

class panelMassCalculator(wx.MiniFrame):
    """Mass calculator tools."""
    
    def __init__(self, parent, tool='pattern'):
        wx.MiniFrame.__init__(self, parent, -1, 'Mass Calculator', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.currentTool = tool
        self.currentCompound = None
        self.currentIons = None
        self.currentIon = None
        self.currentPattern = None
        self.currentPatternProfile = None
        self.currentPatternPeaks = None
        self.currentPatternScan = None
        
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
        summary = self.makeSummaryPanel()
        ionseries = self.makeIonseriesPanel()
        pattern = self.makePatternPanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(summary, 1, wx.EXPAND, 0)
        self.mainSizer.Add(ionseries, 1, wx.EXPAND, 0)
        self.mainSizer.Add(pattern, 1, wx.EXPAND, 0)
        
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
        self.summary_butt = wx.BitmapButton(panel, ID_massCalculatorSummary, images.lib['massCalculatorSummaryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.summary_butt.SetToolTip(wx.ToolTip("Compound summary"))
        self.summary_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.ionseries_butt = wx.BitmapButton(panel, ID_massCalculatorIonSeries, images.lib['massCalculatorIonSeriesOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.ionseries_butt.SetToolTip(wx.ToolTip("Ion series"))
        self.ionseries_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.pattern_butt = wx.BitmapButton(panel, ID_massCalculatorPattern, images.lib['massCalculatorPatternOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.pattern_butt.SetToolTip(wx.ToolTip("Isotopic pattern"))
        self.pattern_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        # make compound fields
        compound_label = wx.StaticText(panel, -1, "Formula:")
        self.compound_value = mwx.formulaCtrl(panel, -1, "", size=(250, -1), style=wx.TE_PROCESS_ENTER)
        compound_label.SetFont(wx.SMALL_FONT)
        self.compound_value.Bind(wx.EVT_TEXT, self.onCompoundChanged)
        self.compound_value.Bind(wx.EVT_TEXT_ENTER, self.onCompoundChanged)
        
        # make save button
        self.save_butt = wx.Button(panel, -1, "Save", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.save_butt.Bind(wx.EVT_BUTTON, self.onSave)
        
        # pack elements
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_LSPACE)
        self.toolbar.Add(self.summary_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.ionseries_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.pattern_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(compound_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        self.toolbar.Add(self.compound_value, 1, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.save_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeSummaryPanel(self):
        """Make compound summary panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        summaryFormula_label = wx.StaticText(panel, -1, "Composition:")
        self.summaryFormula_value = wx.TextCtrl(panel, -1, "", size=(200, -1), style=wx.TE_READONLY)
        
        summaryMono_label = wx.StaticText(panel, -1, "Monoisotopic mass:")
        self.summaryMono_value = wx.TextCtrl(panel, -1, "", size=(200, -1), style=wx.TE_READONLY)
        
        summaryAverage = wx.StaticText(panel, -1, "Average mass:")
        self.summaryAverage_value = wx.TextCtrl(panel, -1, "", size=(200, -1), style=wx.TE_READONLY)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(summaryFormula_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.summaryFormula_value, (0,1))
        grid.Add(summaryMono_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.summaryMono_value, (1,1))
        grid.Add(summaryAverage, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.summaryAverage_value, (2,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeIonseriesPanel(self):
        """Make controls for ionseries."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        ionseriesAgent_label = wx.StaticText(ctrlPanel, -1, "Agent:")
        ionseriesAgent_label.SetFont(wx.SMALL_FONT)
        self.ionseriesAgentFormula_value = wx.TextCtrl(ctrlPanel, -1, config.massCalculator['ionseriesAgent'], size=(60, mwx.SMALL_TEXTCTRL_HEIGHT))
        self.ionseriesAgentFormula_value.SetFont(wx.SMALL_FONT)
        self.ionseriesAgentFormula_value.Bind(wx.EVT_TEXT, self.onCompoundChanged)
        
        ionseriesAgentCharge_label = wx.StaticText(ctrlPanel, -1, "Agent charge:")
        ionseriesAgentCharge_label.SetFont(wx.SMALL_FONT)
        self.ionseriesAgentCharge_value = wx.TextCtrl(ctrlPanel, -1, str(config.massCalculator['ionseriesAgentCharge']), size=(40, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('int'))
        self.ionseriesAgentCharge_value.SetFont(wx.SMALL_FONT)
        self.ionseriesAgentCharge_value.Bind(wx.EVT_TEXT, self.onCompoundChanged)
        
        ionseriesPolarity_label = wx.StaticText(ctrlPanel, -1, "Polarity:")
        ionseriesPolarity_label.SetFont(wx.SMALL_FONT)
        
        self.ionseriesPositive_radio = wx.RadioButton(ctrlPanel, -1, "Positive", style=wx.RB_GROUP)
        self.ionseriesPositive_radio.SetFont(wx.SMALL_FONT)
        self.ionseriesPositive_radio.Bind(wx.EVT_RADIOBUTTON, self.onCompoundChanged)
        
        self.ionseriesNegative_radio = wx.RadioButton(ctrlPanel, -1, "Negative")
        self.ionseriesNegative_radio.SetFont(wx.SMALL_FONT)
        self.ionseriesNegative_radio.Bind(wx.EVT_RADIOBUTTON, self.onCompoundChanged)
        
        if config.massCalculator['ionseriesPolarity'] == -1:
            self.ionseriesNegative_radio.SetValue(True)
        else:
            self.ionseriesPositive_radio.SetValue(True)
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(ionseriesAgent_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.ionseriesAgentFormula_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(ionseriesAgentCharge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.ionseriesAgentCharge_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(ionseriesPolarity_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.ionseriesPositive_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.ionseriesNegative_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # make ions list
        self.makeIonsList()
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(self.ionsList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makePatternPanel(self):
        """Make controls for pattern simulation."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        self.patternCollapse_butt = wx.BitmapButton(ctrlPanel, ID_massCalculatorCollapse, images.lib['arrowsDown'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.patternCollapse_butt.Bind(wx.EVT_BUTTON, self.onCollapse)
        
        patternPeakShape_label = wx.StaticText(ctrlPanel, -1, "Shape:")
        patternPeakShape_label.SetFont(wx.SMALL_FONT)
        self.patternPeakShape_choice = wx.Choice(ctrlPanel, -1, choices=['Symmetrical', 'Asymmetrical'], size=(125, mwx.CHOICE_HEIGHT))
        self.patternPeakShape_choice.Select(0)
        if config.massCalculator['patternPeakShape'] == 'gausslorentzian':
            self.patternPeakShape_choice.Select(1)
        self.patternPeakShape_choice.Bind(wx.EVT_CHOICE, self.onProfileChanged)
        
        patternFwhm_label = wx.StaticText(ctrlPanel, -1, "FWHM:")
        patternFwhm_label.SetFont(wx.SMALL_FONT)
        self.patternFwhm_value = mwx.scrollTextCtrl(ctrlPanel, -1, str(config.massCalculator['patternFwhm']), multiplier=0.1, limits=(0.001,10), digits=4, size=(60, mwx.SMALL_TEXTCTRL_HEIGHT))
        self.patternFwhm_value.SetFont(wx.SMALL_FONT)
        self.patternFwhm_value.Bind(wx.EVT_TEXT, self.onPatternChanged)
        
        patternIntensity_label = wx.StaticText(ctrlPanel, -1, "Intensity:")
        patternIntensity_label.SetFont(wx.SMALL_FONT)
        self.patternIntensity_value = mwx.scrollTextCtrl(ctrlPanel, -1, str(config.massCalculator['patternIntensity']), multiplier=0.1, limits=(1,None), size=(60, mwx.SMALL_TEXTCTRL_HEIGHT))
        self.patternIntensity_value.SetFont(wx.SMALL_FONT)
        self.patternIntensity_value.Bind(wx.EVT_TEXT, self.onProfileChanged)
        
        patternBaseline_label = wx.StaticText(ctrlPanel, -1, "Baseline:")
        patternBaseline_label.SetFont(wx.SMALL_FONT)
        self.patternBaseline_value = mwx.scrollTextCtrl(ctrlPanel, -1, str(config.massCalculator['patternBaseline']), multiplier=0.1, limits=(0,None), size=(60, mwx.SMALL_TEXTCTRL_HEIGHT))
        self.patternBaseline_value.SetFont(wx.SMALL_FONT)
        self.patternBaseline_value.Bind(wx.EVT_TEXT, self.onProfileChanged)
        
        patternShift_label = wx.StaticText(ctrlPanel, -1, "Shift:")
        patternShift_label.SetFont(wx.SMALL_FONT)
        self.patternShift_value = mwx.scrollTextCtrl(ctrlPanel, -1, "0", step=0.001, digits=3, limits=(-1.,1.), size=(60, mwx.SMALL_TEXTCTRL_HEIGHT))
        self.patternShift_value.SetFont(wx.SMALL_FONT)
        self.patternShift_value.Bind(wx.EVT_TEXT, self.onProfileChanged)
        
        self.showPeaks_check = wx.CheckBox(ctrlPanel, -1, "Peaks")
        self.showPeaks_check.SetFont(wx.SMALL_FONT)
        self.showPeaks_check.SetValue(config.massCalculator['patternShowPeaks'])
        self.showPeaks_check.Bind(wx.EVT_CHECKBOX, self.onProfileChanged)
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Add(self.patternCollapse_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(10)
        controls.Add(patternPeakShape_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.patternPeakShape_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(patternFwhm_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.patternFwhm_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(patternIntensity_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.patternIntensity_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(patternBaseline_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.patternBaseline_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(patternShift_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.patternShift_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(self.showPeaks_check, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # make plot canvas
        self.makePatternCanvas()
        
        # pack main
        self.patternSizer = wx.BoxSizer(wx.VERTICAL)
        self.patternSizer.Add(ctrlPanel, 0, wx.EXPAND, 0)
        self.patternSizer.Add(self.patternCanvas, 1, wx.EXPAND)
        
        return self.patternSizer
    # ----
    
    
    def makeIonsList(self):
        """Make ions list."""
        
        # init list
        self.ionsList = mwx.sortListCtrl(self, -1, size=(531, 200), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.ionsList.SetFont(wx.SMALL_FONT)
        self.ionsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.ionsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onIonSelected)
        self.ionsList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        
        # make columns
        self.ionsList.InsertColumn(0, "ion", wx.LIST_FORMAT_LEFT)
        self.ionsList.InsertColumn(1, "monoisotopic mass", wx.LIST_FORMAT_RIGHT)
        self.ionsList.InsertColumn(2, "average mass", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((190,160,160)):
            self.ionsList.SetColumnWidth(col, width)
    # ----
    
    
    def makePatternCanvas(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.patternCanvas = mspy.plot.canvas(self, size=(550, 300), style=mwx.PLOTCANVAS_STYLE_PANEL)
        self.patternCanvas.draw(mspy.plot.container([]))
        
        # set default params
        self.patternCanvas.setProperties(xLabel='m/z')
        self.patternCanvas.setProperties(yLabel='a.i.')
        self.patternCanvas.setProperties(showZero=False)
        self.patternCanvas.setProperties(showGrid=True)
        self.patternCanvas.setProperties(showMinorTicks=False)
        self.patternCanvas.setProperties(showLegend=True)
        self.patternCanvas.setProperties(showXPosBar=True)
        self.patternCanvas.setProperties(showYPosBar=True)
        self.patternCanvas.setProperties(posBarSize=6)
        self.patternCanvas.setProperties(showGel=False)
        self.patternCanvas.setProperties(zoomAxis='x')
        self.patternCanvas.setProperties(checkLimits=True)
        self.patternCanvas.setProperties(autoScaleY=True)
        self.patternCanvas.setProperties(overlapLabels=False)
        self.patternCanvas.setProperties(xPosDigits=5)
        self.patternCanvas.setProperties(yPosDigits=2)
        self.patternCanvas.setProperties(distanceDigits=5)
        self.patternCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.patternCanvas.setProperties(reverseDrawing=True)
        self.patternCanvas.setLMBFunction('xDistance')
        self.patternCanvas.setMFunction('cross')
        
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.patternCanvas.setProperties(axisFont=axisFont)
        
        self.patternCanvas.draw(mspy.plot.container([]))
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        self.parent.updateTmpSpectrum(None)
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'summary'
            if evt and evt.GetId() == ID_massCalculatorSummary:
                tool = 'summary'
            elif evt and evt.GetId() == ID_massCalculatorIonSeries:
                tool = 'ionseries'
            elif evt and evt.GetId() == ID_massCalculatorPattern:
                tool = 'pattern'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # hide save button
        self.toolbar.Hide(7)
        self.toolbar.Hide(8)
        
        # set icons off
        self.summary_butt.SetBitmapLabel(images.lib['massCalculatorSummaryOff'])
        self.ionseries_butt.SetBitmapLabel(images.lib['massCalculatorIonSeriesOff'])
        self.pattern_butt.SetBitmapLabel(images.lib['massCalculatorPatternOff'])
        
        # set panel
        if tool == 'summary':
            self.SetTitle("Compound Summary")
            self.mainSizer.Show(1)
            self.summary_butt.SetBitmapLabel(images.lib['massCalculatorSummaryOn'])
            
        elif tool == 'ionseries':
            self.SetTitle("Ion Series")
            self.mainSizer.Show(2)
            self.ionseries_butt.SetBitmapLabel(images.lib['massCalculatorIonSeriesOn'])
            
        elif tool == 'pattern':
            self.SetTitle("Isotopic Pattern")
            self.mainSizer.Show(3)
            self.toolbar.Show(7)
            self.toolbar.Show(8)
            self.pattern_butt.SetBitmapLabel(images.lib['massCalculatorPatternOn'])
            self.patternCollapse_butt.SetBitmapLabel(images.lib['arrowsDown'])
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onCollapse(self, evt):
        """Show / hide isotopic pattern panel."""
        
        # Show / hide panel
        if self.patternSizer.IsShown(1):
            self.patternSizer.Hide(1)
            self.patternCollapse_butt.SetBitmapLabel(images.lib['arrowsRight'])
        else:
            self.patternSizer.Show(1)
            self.patternCollapse_butt.SetBitmapLabel(images.lib['arrowsDown'])
        
        # fit layout
        self.SetMinSize((-1,-1))
        self.Layout()
        self.mainSizer.Fit(self)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def onCompoundChanged(self, evt=None):
        """Recalc all if compound changed."""
        
        if evt != None:
            evt.Skip()
        
        # get all params
        if not self.getParams():
            self.currentCompound = None
            self.currentIons = None
            self.currentIon = None
            self.currentPattern = None
            self.currentPatternProfile = None
            self.currentPatternPeaks = None
            self.currentPatternScan = None
            self.updateSummary()
            self.updateIonsList()
            self.updatePatternCanvas()
            self.updateTmpSpectrum()
            return
        
        # calculate ion series
        self.runIonSeries()
        
        # calculate pattern
        self.runPattern()
        
        # update gui
        self.updateSummary()
        self.updateIonsList()
        self.updatePatternCanvas()
        self.updateTmpSpectrum()
    # ----
    
    
    def onPatternChanged(self, evt=None):
        """Recalc pattern if params changed."""
        
        # get all params
        if not self.getParams():
            self.currentPattern = None
            self.currentPatternProfile = None
            self.currentPatternPeaks = None
            self.currentPatternScan = None
            self.updatePatternCanvas()
            self.updateTmpSpectrum()
            return
        
        # calculate pattern
        self.runPattern()
        
        # use current axis
        rescale = False
        if evt == None:
            rescale = True
        
        # update gui
        self.updatePatternCanvas(rescale=rescale)
        self.updateTmpSpectrum()
    # ----
    
    
    def onProfileChanged(self, evt=None):
        """Shift tmp profile."""
        
        # check pattern
        if self.currentPattern == None:
            return
        
        # get all params
        if not self.getParams():
            self.currentPatternProfile = None
            self.currentPatternPeaks = None
            self.currentPatternScan = None
            self.updatePatternCanvas()
            self.updateTmpSpectrum()
            return
        
        # re-calculate pattern profile
        self.makeProfile()
        
        # update gui
        self.updatePatternCanvas(rescale=False)
        self.updateTmpSpectrum()
    # ----
    
    
    def onIonSelected(self, evt):
        """Recalculate pattern and show selected ion in the spectrum."""
        
        # get selected ion
        self.currentIon = self.currentIons[evt.GetData()]
        
        # update pattern
        self.onPatternChanged()
    # ----
    
    
    def onListKey(self, evt):
        """Export list if Ctrl+C."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.ionsList.copyToClipboard()
            
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onSave(self, evt):
        """Save current pattern as doument."""
        
        # check data
        if self.currentPatternScan == None or self.currentCompound == None:
            wx.Bell()
            return
        
        # get ion
        if self.currentIon != None:
            charge = self.currentIon[3]
            ion = self.currentIon[4]
        else:
            charge = 0
            ion = '[M]'
        
        # make document
        document = doc.document()
        document.dirty = True
        document.title = '%s %s' % (self.currentCompound.formula(), ion)
        document.spectrum = copy.deepcopy(self.currentPatternScan)
        
        # make annotations
        mass = self.currentCompound.mass()
        mz = self.currentCompound.mz(charge=charge, agentFormula=config.massCalculator['ionseriesAgent'], agentCharge=config.massCalculator['ionseriesAgentCharge'])
        document.annotations.append(doc.annotation(label='monoisotopic m/z', mz=mz[0], ai=config.massCalculator['patternIntensity'], base=config.massCalculator['patternBaseline']))
        document.annotations.append(doc.annotation(label='average m/z', mz=mz[1], ai=config.massCalculator['patternIntensity'], base=config.massCalculator['patternBaseline']))
        
        # make notes
        document.notes = 'Theoretical isotopic pattern.\n'
        document.notes += 'FWHM: %s\n\n' % (config.massCalculator['patternFwhm'])
        document.notes += 'Compound: %s\n' % (self.currentCompound.formula())
        document.notes += 'Monoisotopic mass: %s\n' % (mass[0])
        document.notes += 'Average mass: %s\n\n' % (mass[1])
        document.notes += 'Ion: %s\n' % (ion)
        document.notes += 'Monoisotopic m/z: %s\n' % (mz[0])
        document.notes += 'Average m/z: %s\n' % (mz[1])
        
        # add document
        self.parent.onDocumentNew(document=document)
    # ----
    
    
    def setData(self, formula='', charge=None, agentFormula='H', agentCharge=1, fwhm=None, intensity=None, baseline=None):
        """Set formula and charge."""
        
        # clear current data
        self.currentCompound = None
        self.currentIons = None
        self.currentIon = None
        self.currentPattern = None
        self.currentPatternProfile = None
        self.currentPatternPeaks = None
        self.currentPatternScan = None
        
        # check
        if not formula:
            formula = ''
        
        # update values
        self.compound_value.ChangeValue(formula)
        if agentFormula:
            self.ionseriesAgentFormula_value.ChangeValue(agentFormula)
        if agentCharge:
            self.ionseriesAgentCharge_value.ChangeValue(str(agentCharge))
        self.patternShift_value.ChangeValue('0')
        
        if fwhm != None:
            fwhm = max(0.001, fwhm)
            fwhm = min(10, fwhm)
            self.patternFwhm_value.ChangeValue(str(round(fwhm,3)))
        
        if intensity != None and baseline != None and baseline >= intensity:
            intensity = 2*baseline
            if intensity == 0.:
                intensity = 1.
        
        if intensity != None:
            intensity = round(intensity)
            if intensity > 10000 or intensity < -10000:
                intensity = '%0.1e' % intensity
            self.patternIntensity_value.ChangeValue(str(intensity))
        
        if baseline != None:
            baseline = round(baseline)
            if baseline > 10000 or baseline < -10000:
                baseline = '%0.1e' % baseline
            self.patternBaseline_value.ChangeValue(str(baseline))
        
        if not charge or charge > 0:
            self.ionseriesPositive_radio.SetValue(True)
        else:
            self.ionseriesNegative_radio.SetValue(True)
        
        try: wx.Yield()
        except: pass
        
        # get all params
        if not self.getParams():
            self.updateSummary()
            self.updateIonsList()
            self.updatePatternCanvas()
            self.updateTmpSpectrum()
            return
        
        # calculate ion series
        self.runIonSeries()
        self.updateSummary()
        self.updateIonsList()
        
        # select propper ion and update pattern
        done = False
        if self.currentIons and charge != None:
            for x, ion in enumerate(self.currentIons):
                if ion[3] == charge:
                    self.ionsList.SetItemState(x, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
                    done = True
                    break
        
        # calculate neutral pattern if not charge specified
        if not done:
            self.runPattern()
            self.updatePatternCanvas()
            self.updateTmpSpectrum()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            # compound
            compound = self.compound_value.GetValue()
            if not compound:
                return False
            
            # charging agent
            ionseriesAgent = self.ionseriesAgentFormula_value.GetValue()
            if not ionseriesAgent:
                return False
            
            # ionseries
            config.massCalculator['ionseriesAgentCharge'] = int(self.ionseriesAgentCharge_value.GetValue())
            if self.ionseriesNegative_radio.GetValue():
                config.massCalculator['ionseriesPolarity'] = -1
            else:
                config.massCalculator['ionseriesPolarity'] = 1
            
            # pattern
            patternFwhm = float(self.patternFwhm_value.GetValue())
            patternIntensity = float(self.patternIntensity_value.GetValue())
            patternBaseline = float(self.patternBaseline_value.GetValue())
            patternShift = float(self.patternShift_value.GetValue())
            config.massCalculator['patternShowPeaks'] = self.showPeaks_check.GetValue()
            
            config.massCalculator['patternPeakShape'] = 'gaussian'
            if self.patternPeakShape_choice.GetStringSelection() == 'Asymmetrical':
                config.massCalculator['patternPeakShape'] = 'gausslorentzian'
        
        except:
            wx.Bell()
            return False
        
        # check compound
        try:
            self.currentCompound = mspy.compound(compound)
        except:
            return False
        
        if not self.currentCompound.isvalid():
            wx.Bell()
            return False
        
        # check charging agent
        try:
            if ionseriesAgent != 'e':
                agent = mspy.compound(ionseriesAgent)
            config.massCalculator['ionseriesAgent'] = ionseriesAgent
        except:
            return False
        
        if ionseriesAgent == 'e':
            config.massCalculator['ionseriesAgentCharge'] = -1
            self.ionseriesAgentCharge_value.ChangeValue('-1')
        
        # check pattern values
        if patternFwhm < 0.001 \
            or patternIntensity < 1 \
            or patternBaseline >= patternIntensity:
            wx.Bell()
            return False
        else:
            config.massCalculator['patternFwhm'] = patternFwhm
            config.massCalculator['patternIntensity'] = patternIntensity
            config.massCalculator['patternBaseline'] = patternBaseline
            config.massCalculator['patternShift'] = patternShift
        
        return True
    # ----
    
    
    def updateSummary(self):
        """Calculate summary for curent compound."""
        
        # check current compound
        if self.currentCompound == None:
            self.summaryFormula_value.SetValue('')
            self.summaryMono_value.SetValue('')
            self.summaryAverage_value.SetValue('')
            return
        
        # get summary
        formula = self.currentCompound.formula()
        mass = self.currentCompound.mass()
        
        # update gui
        self.summaryFormula_value.SetValue(formula)
        self.summaryMono_value.SetValue(str(round(mass[0],config.main['mzDigits'])))
        self.summaryAverage_value.SetValue(str(round(mass[1],config.main['mzDigits'])))
    # ----
    
    
    def updateIonsList(self):
        """Update current ions list."""
        
        self.currentIon = None
        
        # clear previous data and set new
        self.ionsList.DeleteAllItems()
        self.ionsList.setDataMap(self.currentIons)
        
        # check data
        if self.currentIons == None:
            return
        
        # add new data
        format = '%0.' + `config.main['mzDigits']` + 'f'
        for row, ion in enumerate(self.currentIons):
            
            # format data
            title = ion[4]
            mono = format % (ion[1])
            average = format % (ion[2])
            
            # add data
            self.ionsList.InsertStringItem(row, title)
            self.ionsList.SetStringItem(row, 1, mono)
            self.ionsList.SetStringItem(row, 2, average)
            self.ionsList.SetItemData(row, row)
        
        # sort data
        self.ionsList.sort()
        
        # scroll top
        self.ionsList.EnsureVisible(0)
    # ----
    
    
    def updatePatternCanvas(self, rescale=True):
        """Show current profile and peaks in pattern canvas."""
        
        # make spectra container
        container = mspy.plot.container([])
        
        # check data
        if self.currentPatternScan == None:
            self.patternCanvas.draw(container)
            return
        
        # get number of relevant digits
        fwhm = config.massCalculator['patternFwhm']
        digits = int(abs(numpy.floor(numpy.log10(fwhm))))
        if fwhm > 1: digits = 1
        elif round(fwhm, digits-1) == 0: digits += 1
        
        # get selected charge
        legend = '[M]'
        if self.currentIon != None:
            legend = self.currentIon[4]
        
        # add main profile spectrum to container
        labelFont = wx.Font(config.spectrum['labelFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        spectrum = mspy.plot.spectrum(self.currentPatternScan,
            legend = legend,
            spectrumColour = (16,71,185),
            tickColour = (255,0,0),
            showPoints = False,
            showLabels = True,
            showTicks = True,
            labelDigits = digits,
            labelBgr = True,
            labelAngle = 90,
            labelFont = labelFont
        )
        container.append(spectrum)
        
        # add individual peaks to container
        if self.currentPatternPeaks != None:
            for peak in self.currentPatternPeaks:
                spectrum = mspy.plot.points(peak,
                    lineColour = (50,140,0),
                    showLines = True,
                    showPoints = False,
                    exactFit = True
                )
                container.append(spectrum)
        
        # get current axis
        if not rescale:
            xAxis = self.patternCanvas.getCurrentXRange()
            yAxis = self.patternCanvas.getCurrentYRange()
            if xAxis == (0,1) or yAxis == (0,1):
                xAxis = None
                yAxis = None
        else:
            xAxis = None
            yAxis = None
        
        # draw spectra
        self.patternCanvas.draw(container, xAxis=xAxis, yAxis=yAxis)
    # ----
    
    
    def updateTmpSpectrum(self):
        """Show current profile in the main canvas."""
        
        # check data
        if self.currentPatternProfile == None:
            self.parent.updateTmpSpectrum(None)
            return
        
        # apply current shift
        profile = mspy.offset(self.currentPatternProfile, x=config.massCalculator['patternShift'])
        
        # draw tmp spectrum
        self.parent.updateTmpSpectrum(profile)
    # ----
    
    
    def runIonSeries(self):
        """Calculate ion series for current compound."""
        
        self.currentIons = None
        self.currentIon = None
        
        # run task
        try:
            
            # get neutral mass
            mass = self.currentCompound.mass()
            self.currentIons = [(0, mass[0], mass[1], 0, '[M]')]
            
            # get ions
            i = 0
            while True:
                
                # get charge
                i += 1
                charge = i*config.massCalculator['ionseriesPolarity']*abs(config.massCalculator['ionseriesAgentCharge'])
                
                # check ion
                if not self.currentCompound.isvalid(charge=charge, agentFormula=config.massCalculator['ionseriesAgent'], agentCharge=config.massCalculator['ionseriesAgentCharge']):
                    break
                
                # get ion type
                if config.massCalculator['ionseriesPolarity'] == 1 and config.massCalculator['ionseriesAgentCharge'] > 0:
                    iontype = '[M+%d%s] %d+' % (i, config.massCalculator['ionseriesAgent'], abs(charge))
                elif config.massCalculator['ionseriesPolarity'] == 1:
                    iontype = '[M-%d%s] %d+' % (i, config.massCalculator['ionseriesAgent'], abs(charge))
                elif config.massCalculator['ionseriesAgentCharge'] < 0:
                    iontype = '[M+%d%s] %d-' % (i, config.massCalculator['ionseriesAgent'], abs(charge))
                else:
                    iontype = '[M-%d%s] %d-' % (i, config.massCalculator['ionseriesAgent'], abs(charge))
                
                # get mz
                mz = mspy.mz(mass, charge=charge, agentFormula=config.massCalculator['ionseriesAgent'], agentCharge=config.massCalculator['ionseriesAgentCharge'])
                
                # add to list
                self.currentIons.append((abs(charge), mz[0], mz[1], charge, iontype))
                
                # skip next radical ions
                # if config.massCalculator['ionseriesAgent'] == 'e':
                #     break
                
                # check limits
                if mz[0] < 100 or len(self.currentIons) >= 100:
                    break
        
        # task canceled
        except mspy.ForceQuit:
            self.currentIons = None
            self.currentIon = None
    # ----
    
    
    def runPattern(self):
        """Calculate isotopic pattern."""
        
        self.currentPattern = None
        self.currentPatternProfile = None
        self.currentPatternPeaks = None
        self.currentPatternScan = None
        
        # run task
        try:
            
            # get selected charge
            charge = 0
            if self.currentIon != None:
                charge = self.currentIon[3]
            
            # calculate pattern
            self.currentPattern = self.currentCompound.pattern(
                fwhm = min(0.9, config.massCalculator['patternFwhm']),
                threshold = config.massCalculator['patternThreshold'],
                charge = charge,
                agentFormula = config.massCalculator['ionseriesAgent'],
                agentCharge = config.massCalculator['ionseriesAgentCharge'],
                real = False
            )
            
            # make profile
            self.makeProfile()
            
        # task canceled
        except mspy.ForceQuit:
            self.currentPattern = None
            self.currentPatternProfile = None
            self.currentPatternPeaks = None
            self.currentPatternScan = None
    # ----
    
    
    def makeProfile(self):
        """Generate pattern profile."""
        
        self.currentPatternProfile = None
        self.currentPatternPeaks = None
        self.currentPatternScan = None
        
        # check pattern
        if self.currentPattern == None:
            return
        
        # get selected charge
        charge = 0
        if self.currentIon != None:
            charge = self.currentIon[3]
        
        # make profile
        self.currentPatternProfile = mspy.profile(
            peaklist = self.currentPattern,
            fwhm = config.massCalculator['patternFwhm'],
            points = 20,
            model = config.massCalculator['patternPeakShape'],
        )
        
        # get scale and shift for specified intensity and baseline
        basepeak = mspy.basepeak(self.currentPatternProfile)
        scale = (config.massCalculator['patternIntensity'] - config.massCalculator['patternBaseline']) / self.currentPatternProfile[basepeak][1]
        shift = config.massCalculator['patternBaseline']
        
        # rescale profile
        self.currentPatternProfile = mspy.multiply(self.currentPatternProfile, y=scale)
        self.currentPatternProfile = mspy.offset(self.currentPatternProfile, y=shift)
        
        # make real peaklist from profile
        peaklist = []
        for isotope in mspy.maxima(self.currentPatternProfile):
            mz = isotope[0]
            centroid = mspy.centroid(self.currentPatternProfile, isotope[0], isotope[1]*0.99)
            if abs(mz-centroid) < config.massCalculator['patternFwhm']/20:
                mz = centroid
            peak = mspy.peak(
                mz = mz,
                ai = isotope[1],
                base = shift,
                charge = charge
            )
            peaklist.append(peak)
        peaklist = mspy.peaklist(peaklist)
        
        # make individual peak shapes
        self.currentPatternPeaks = []
        if config.massCalculator['patternShowPeaks']:
            
            # gaussian shape
            if config.massCalculator['patternPeakShape'] == 'gaussian':
                for isotope in self.currentPattern:
                    peak = mspy.gaussian(
                        x = isotope[0],
                        minY = shift,
                        maxY = isotope[1]*scale+shift,
                        fwhm = config.massCalculator['patternFwhm']
                    )
                    self.currentPatternPeaks.append(peak)
            
            # lorentzian shape
            elif config.massCalculator['patternPeakShape'] == 'lorentzian':
                for isotope in self.currentPattern:
                    peak = mspy.lorentzian(
                        x = isotope[0],
                        minY = shift,
                        maxY = isotope[1]*scale+shift,
                        fwhm = config.massCalculator['patternFwhm']
                    )
                    self.currentPatternPeaks.append(peak)
            
            # gauss-lorentzian shape
            elif config.massCalculator['patternPeakShape'] == 'gausslorentzian':
                for isotope in self.currentPattern:
                    peak = mspy.gausslorentzian(
                        x = isotope[0],
                        minY = shift,
                        maxY = isotope[1]*scale+shift,
                        fwhm = config.massCalculator['patternFwhm']
                    )
                    self.currentPatternPeaks.append(peak)
        
        # make scan object
        self.currentPatternScan = mspy.scan(profile=self.currentPatternProfile, peaklist=peaklist)
    # ----
    
