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
import libs
import mspy


# FLOATING PANEL WITH ENVELOPE FIT TOOL
# -------------------------------------

class panelEnvelopeFit(wx.MiniFrame):
    """Envelope fit tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Envelope Fit', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.processing = None
        
        self.currentDocument = None
        self.currentCompound = None
        self.currentFit = None
        
        # init container
        self.spectrumContainer = mspy.plot.container([])
        
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
        results = self.makeResultsPanel()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(results, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide gauge
        self.mainSizer.Hide(3)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make elements
        formula_label = wx.StaticText(panel, -1, "Formula:")
        formula_label.SetFont(wx.SMALL_FONT)
        self.formula_value = mwx.formulaCtrl(panel, -1, "", size=(220, -1))
        
        charge_label = wx.StaticText(panel, -1, "Charge:")
        charge_label.SetFont(wx.SMALL_FONT)
        self.charge_value = wx.TextCtrl(panel, -1, str(config.envelopeFit['charge']), size=(35,  -1), validator=mwx.validator('int'))
        
        exchange_label = wx.StaticText(panel, -1, "Exchange:")
        exchange_label.SetFont(wx.SMALL_FONT)
        self.exchangeLoss_value = mwx.formulaCtrl(panel, -1, str(config.envelopeFit['loss']), size=(60,  -1))
        exchangeVs_label = wx.StaticText(panel, -1, " vs.")
        exchangeVs_label.SetFont(wx.SMALL_FONT)
        self.exchangeGain_value = mwx.formulaCtrl(panel, -1, str(config.envelopeFit['gain']), size=(60,  -1))
        
        scale_label = wx.StaticText(panel, -1, "Range:")
        scale_label.SetFont(wx.SMALL_FONT)
        scaleDash_label = wx.StaticText(panel, -1, "-")
        scaleDash_label.SetFont(wx.SMALL_FONT)
        self.scaleMin_value = wx.TextCtrl(panel, -1, str(config.envelopeFit['scaleMin']), size=(35,  -1), validator=mwx.validator('intPos'))
        self.scaleMax_value = wx.TextCtrl(panel, -1, str(config.envelopeFit['scaleMax']), size=(35,  -1), validator=mwx.validator('intPos'))
        
        self.calculate_butt = wx.Button(panel, -1, "Calculate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.calculate_butt.Bind(wx.EVT_BUTTON, self.onCalculate)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(formula_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.formula_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(charge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.charge_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(exchange_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.exchangeLoss_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(exchangeVs_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.exchangeGain_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(scale_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.scaleMin_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(scaleDash_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.scaleMax_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.calculate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeControlbar(self):
        """Make controlbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make elements
        self.collapse_butt = wx.BitmapButton(panel, -1, images.lib['arrowsDown'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.collapse_butt.Bind(wx.EVT_BUTTON, self.onCollapse)
        
        fitTo_label = wx.StaticText(panel, -1, "Fit to:")
        fitTo_label.SetFont(wx.SMALL_FONT)
        
        self.fitToPeaklist_radio = wx.RadioButton(panel, -1, "Peak list", style=wx.RB_GROUP)
        self.fitToPeaklist_radio.SetFont(wx.SMALL_FONT)
        
        self.fitToSpectrum_radio = wx.RadioButton(panel, -1, "Spectrum")
        self.fitToSpectrum_radio.SetFont(wx.SMALL_FONT)
        
        self.fitToPeaklist_radio.SetValue(True)
        if config.envelopeFit['fit'] == 'spectrum':
            self.fitToSpectrum_radio.SetValue(True)
        
        fwhm_label = wx.StaticText(panel, -1, "Default FWHM:")
        fwhm_label.SetFont(wx.SMALL_FONT)
        self.fwhm_value = wx.TextCtrl(panel, -1, str(config.envelopeFit['fwhm']), size=(50, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        self.fwhm_value.SetFont(wx.SMALL_FONT)
        
        self.forceFwhm_check = wx.CheckBox(panel, -1, "Force")
        self.forceFwhm_check.SetFont(wx.SMALL_FONT)
        self.forceFwhm_check.SetValue(config.envelopeFit['forceFwhm'])
        
        relThreshold_label = wx.StaticText(panel, -1, "Rel. int. threshold:")
        relThreshold_label.SetFont(wx.SMALL_FONT)
        relThresholdUnits_label = wx.StaticText(panel, -1, "%")
        relThresholdUnits_label.SetFont(wx.SMALL_FONT)
        self.relThreshold_value = wx.TextCtrl(panel, -1, str(config.envelopeFit['relThreshold']*100), size=(50, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        self.relThreshold_value.SetFont(wx.SMALL_FONT)
        
        self.autoAlign_check = wx.CheckBox(panel, -1, "Auto align")
        self.autoAlign_check.SetFont(wx.SMALL_FONT)
        self.autoAlign_check.SetValue(config.envelopeFit['autoAlign'])
        
        self.average_label = wx.StaticText(panel, -1, "", size=(100, -1))
        self.average_label.SetFont(wx.SMALL_FONT)
        self.updateAverageLabel()
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(self.collapse_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(fitTo_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fitToPeaklist_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fitToSpectrum_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(fwhm_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fwhm_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.forceFwhm_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(relThreshold_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.relThreshold_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(relThresholdUnits_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.autoAlign_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.average_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeResultsPanel(self):
        """Make results panel."""
        
        panel = wx.Panel(self, -1)
        
        # make table
        self.makeSpectrumCanvas(panel)
        self.makeResultsList(panel)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.spectrumCanvas, 1, wx.EXPAND)
        mainSizer.AddSpacer(mwx.SASH_SIZE)
        mainSizer.Add(self.resultsList, 0, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        # fit layout
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSpectrumCanvas(self, panel):
        """Make spectrum canvas and set defalt parameters."""
        
        # init canvas
        self.spectrumCanvas = mspy.plot.canvas(panel, size=(600, 350), style=mwx.PLOTCANVAS_STYLE_PANEL)
        
        # set default params
        self.updateCanvasProperties(refresh=False)
        self.spectrumCanvas.setProperties(showZero=False)
        self.spectrumCanvas.setProperties(showLegend=True)
        self.spectrumCanvas.setProperties(showXPosBar=False)
        self.spectrumCanvas.setProperties(showYPosBar=True)
        self.spectrumCanvas.setProperties(showGel=False)
        self.spectrumCanvas.setProperties(zoomAxis='x')
        self.spectrumCanvas.setProperties(checkLimits=True)
        self.spectrumCanvas.setProperties(autoScaleY=True)
        self.spectrumCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.spectrumCanvas.setProperties(reverseDrawing=False)
        
        self.spectrumCanvas.setLMBFunction('xDistance')
        
        self.spectrumCanvas.draw(self.spectrumContainer)
        
        return self.spectrumCanvas
    # ----
    
    
    def makeResultsList(self, panel):
        """Make results list."""
        
        # init results list
        self.resultsList = mwx.sortListCtrl(panel, -1, size=(171, 350), style=mwx.LISTCTRL_STYLE_MULTI)
        self.resultsList.SetFont(wx.SMALL_FONT)
        self.resultsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        self.resultsList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        
        # make columns
        self.resultsList.InsertColumn(0, "# of X", wx.LIST_FORMAT_LEFT)
        self.resultsList.InsertColumn(1, "%", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((75,75)):
            self.resultsList.SetColumnWidth(col, width)
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
        """Close panel."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # clear tmp spectrum
        self.parent.updateTmpSpectrum(None)
        
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
            mspy.start()
        
        # fit layout
        self.spectrumCanvas.SetMinSize(self.spectrumCanvas.GetSize())
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
        self.spectrumCanvas.SetMinSize((-1,-1))
    # ----
    
    
    def onStop(self, evt):
        """Cancel current processing."""
        
        if self.processing and self.processing.isAlive():
            mspy.stop()
        else:
            wx.Bell()
    # ----
    
    
    def onListKey(self, evt):
        """Export list if Ctrl+C."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.resultsList.copyToClipboard()
        
        # select all
        elif key == 65 and evt.CmdDown():
            for x in range(self.resultsList.GetItemCount()):
                self.resultsList.SetItemState(x, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onCalculate(self, evt):
        """Generate compounds ions."""
        
        # check processing
        if self.processing:
            return
        
        # clear recent
        self.currentCompound = None
        self.currentFit = None
        
        # check document
        if not self.currentDocument or not (self.currentDocument.spectrum.hasprofile() or self.currentDocument.spectrum.haspeaks()):
            wx.Bell()
            return
        
        # get params
        if not self.getParams():
            self.updateAverageLabel()
            self.updateSpectrumCanvas()
            self.updateResultsList()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.calculate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runEnvelopeFit)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # check error
        error = False
        if self.currentFit is False:
            self.currentFit = None
            error = True
        
        # update gui
        self.updateAverageLabel()
        self.updateSpectrumCanvas()
        self.updateResultsList()
        
        # hide processing gauge
        self.onProcessing(False)
        self.calculate_butt.Enable(True)
        
        # check errors
        if error:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="No data to fit.", message="There are no data in relevant mass range. Please check\nspecified formula, charge and default FWHM.")
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onCollapse(self, evt):
        """Collapse spectrum panel."""
        
        # Show / hide panel
        if self.mainSizer.IsShown(2):
            self.mainSizer.Hide(2)
            self.collapse_butt.SetBitmapLabel(images.lib['arrowsRight'])
        else:
            self.mainSizer.Show(2)
            self.collapse_butt.SetBitmapLabel(images.lib['arrowsDown'])
        
        # fit layout
        self.SetMinSize((-1,-1))
        self.Layout()
        self.mainSizer.Fit(self)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def setData(self, document=None, formula=None, charge=None, fwhm=None, scale=None):
        """Set current data."""
        
        self.currentCompound = None
        self.currentFit = None
        
        # set values
        self.currentDocument = document
        if formula:
            self.formula_value.SetValue(str(formula))
        if charge:
            self.charge_value.SetValue(str(charge))
        if fwhm:
            self.fwhm_value.SetValue(str(fwhm))
        if scale:
            self.scaleMin_value.SetValue(str(scale[0]))
            self.scaleMax_value.SetValue(str(scale[1]))
        
        # update fitting options
        if self.currentDocument and not self.currentDocument.spectrum.hasprofile():
            self.fitToPeaklist_radio.SetValue(True)
            self.fitToSpectrum_radio.Disable()
        elif self.currentDocument and not self.currentDocument.spectrum.haspeaks():
            self.fitToPeaklist_radio.Disable()
            self.fitToSpectrum_radio.SetValue(True)
        else:
            self.fitToPeaklist_radio.Enable()
            self.fitToSpectrum_radio.Enable()
        
        # clear gui
        self.updateAverageLabel()
        self.updateSpectrumCanvas()
        self.updateResultsList()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            formula = self.formula_value.GetValue()
            loss = self.exchangeLoss_value.GetValue()
            gain = self.exchangeGain_value.GetValue()
            
            if not formula or not loss or not gain:
                raise ValueError
            
            self.currentCompound = mspy.compound(formula)
            lossCmpd = mspy.compound(loss)
            gainCmpd = mspy.compound(gain)
            
            config.envelopeFit['loss'] = str(loss)
            config.envelopeFit['gain'] = str(gain)
            
            config.envelopeFit['fit'] = 'peaklist'
            if self.fitToSpectrum_radio.GetValue():
                config.envelopeFit['fit'] = 'spectrum'
            
            config.envelopeFit['charge'] = int(self.charge_value.GetValue())
            config.envelopeFit['scaleMin'] = int(self.scaleMin_value.GetValue())
            config.envelopeFit['scaleMax'] = int(self.scaleMax_value.GetValue())
            config.envelopeFit['fwhm'] = float(self.fwhm_value.GetValue())
            config.envelopeFit['forceFwhm'] = self.forceFwhm_check.GetValue()
            config.envelopeFit['autoAlign'] = self.autoAlign_check.GetValue()
            config.envelopeFit['relThreshold'] = float(self.relThreshold_value.GetValue())/100.
            
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateAverageLabel(self):
        """Update average label value."""
        
        # get label
        label = "Average X: "
        if self.currentFit != None:
            label += '%0.1f' % (self.currentFit.average)
        
        # set label
        self.average_label.SetLabel(label)
    # ----
    
    
    def updateCanvasProperties(self, refresh=True):
        """Set current canvas properties."""
        
        # set common properties
        self.spectrumCanvas.setProperties(xLabel=config.spectrum['xLabel'])
        self.spectrumCanvas.setProperties(yLabel=config.spectrum['yLabel'])
        self.spectrumCanvas.setProperties(showGrid=config.spectrum['showGrid'])
        self.spectrumCanvas.setProperties(showMinorTicks=config.spectrum['showMinorTicks'])
        self.spectrumCanvas.setProperties(posBarSize=config.spectrum['posBarSize'])
        self.spectrumCanvas.setProperties(xPosDigits=config.main['mzDigits'])
        self.spectrumCanvas.setProperties(yPosDigits=config.main['intDigits'])
        self.spectrumCanvas.setProperties(distanceDigits=config.main['mzDigits'])
        
        # set font
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.spectrumCanvas.setProperties(axisFont=axisFont)
        
        # set cursor
        cursor = (wx.StockCursor(wx.CURSOR_ARROW), images.lib['cursorsCrossMeasure'])
        self.spectrumCanvas.setCursorImage(cursor[bool(config.spectrum['showTracker'])])
        self.spectrumCanvas.setMFunction([None, 'cross'][config.spectrum['showTracker']])
        
        # refresh canvas
        if refresh:
            self.spectrumCanvas.refresh()
    # ----
    
    
    def updateSpectrumCanvas(self):
        """Update spectrum canvas."""
        
        # clear container
        self.spectrumContainer.empty()
        
        # check fit
        if self.currentFit == None:
            self.spectrumCanvas.draw(self.spectrumContainer)
            self.parent.updateTmpSpectrum(None)
            return
        
        # get data
        spectrum = self.currentFit.spectrum
        data = self.currentFit.data
        model = self.currentFit.model
        envelope = self.currentFit.envelope()
        
        # show results
        self.spectrumContainer.append(mspy.plot.points(spectrum, legend='measured', showPoints=False, exactFit=True, lineColour=(16, 71, 185)))
        self.spectrumContainer.append(mspy.plot.points(envelope, legend='model', showPoints=False, exactFit=True, lineColour=(241,144,0)))
        self.spectrumContainer.append(mspy.plot.points(data, legend='', showLines=False, pointColour=(16, 71, 185)))
        self.spectrumContainer.append(mspy.plot.points(model, legend='', showLines=False, pointColour=(241,144,0)))
        
        # draw container
        self.spectrumCanvas.draw(self.spectrumContainer)
        
        # update spectrum overlay
        self.parent.updateTmpSpectrum(envelope)
    # ----
    
    
    def updateResultsList(self):
        """Update results list."""
        
        # make data map
        if self.currentFit == None:
            data = []
        else:
            data = self.currentFit.ncomposition.items()
            data.sort()
        
        # clear previous data and set new
        self.resultsList.DeleteAllItems()
        self.resultsList.setDataMap(data)
        
        # check data
        if not data:
            return
        
        # add new data
        for row, item in enumerate(data):
            self.resultsList.InsertStringItem(row, str(item[0]))
            self.resultsList.SetStringItem(row, 1, str(round(item[1]*100, 1)))
            self.resultsList.SetItemData(row, row)
        
        # sort data
        self.resultsList.sort()
        
        # scroll top
        if self.resultsList.GetItemCount():
            self.resultsList.EnsureVisible(0)
    # ----
    
    
    def runEnvelopeFit(self):
        """Run envelope fitting."""
        
        # run task
        try:
            
            # get scales
            scaleMin = max(0, min(config.envelopeFit['scaleMin'], config.envelopeFit['scaleMax']))
            scaleMax = max(0, max(config.envelopeFit['scaleMin'], config.envelopeFit['scaleMax']))
            scales = [(x) for x in range(scaleMin, scaleMax+1)]
            
            # init module
            self.currentFit = mspy.envfit(
                formula = self.currentCompound.formula(),
                charge = config.envelopeFit['charge'],
                scales = scales,
                loss = config.envelopeFit['loss'],
                gain = config.envelopeFit['gain'],
                peakShape = config.envelopeFit['peakShape']
            )
            
            # fit data to peaklist
            if config.envelopeFit['fit'] == 'peaklist':
                success = self.currentFit.topeaklist(
                    peaklist = self.currentDocument.spectrum.peaklist,
                    fwhm = config.envelopeFit['fwhm'],
                    forceFwhm = config.envelopeFit['forceFwhm'],
                    autoAlign = config.envelopeFit['autoAlign'],
                    iterLimit =  100*config.envelopeFit['scaleMax'],
                    relThreshold = config.envelopeFit['relThreshold']
                )
            
            # fit data to spectrum
            elif config.envelopeFit['fit'] == 'spectrum':
                
                # get baseline window
                baselineWindow = 1.
                if config.processing['peakpicking']['baseline']:
                    baselineWindow = 1./config.processing['baseline']['precision']
                
                # get baseline
                baseline = self.currentDocument.spectrum.baseline(
                    window = baselineWindow,
                    offset = config.processing['baseline']['offset']
                )
                
                # fit data to spectrum
                success = self.currentFit.tospectrum(
                    signal = self.currentDocument.spectrum.profile,
                    fwhm = config.envelopeFit['fwhm'],
                    forceFwhm = config.envelopeFit['forceFwhm'],
                    autoAlign = config.envelopeFit['autoAlign'],
                    iterLimit =  100*config.envelopeFit['scaleMax'],
                    pickingHeight = config.processing['peakpicking']['pickingHeight'],
                    relThreshold = config.envelopeFit['relThreshold'],
                    baseline = baseline
                )
            
            # erase if not success
            if not success:
                self.currentFit = False
            
        # task canceled
        except mspy.ForceQuit:
            self.currentFit = None
            return
    # ----
    
    
    