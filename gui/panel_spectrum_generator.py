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
import numpy

# load modules
import mwx
import images
import config
import mspy
import mspy.plot


# FLOATING PANEL WITH SPECTRUM GENERATOR TOOL
# -------------------------------------------

class panelSpectrumGenerator(wx.MiniFrame):
    """Spectrum generator tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Spectrum Generator', size=(700, 400), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.processing = None
        
        self.currentDocument = None
        self.currentProfile = None
        self.currentPeaks = None
        
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
        canvas = self.makeSpectrumCanvas()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(canvas, 1, wx.EXPAND, 0)
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
        peakShape_label = wx.StaticText(panel, -1, "Peak shape:")
        peakShape_label.SetFont(wx.SMALL_FONT)
        self.peakShape_choice = wx.Choice(panel, -1, choices=['Symmetrical', 'Asymmetrical'], size=(125, mwx.CHOICE_HEIGHT))
        self.peakShape_choice.Select(0)
        if config.spectrumGenerator['peakShape'] == 'gausslorentzian':
            self.peakShape_choice.Select(1)
        
        fwhm_label = wx.StaticText(panel, -1, "Default FWHM:")
        fwhm_label.SetFont(wx.SMALL_FONT)
        self.fwhm_value = wx.TextCtrl(panel, -1, str(config.spectrumGenerator['fwhm']), size=(60, -1), validator=mwx.validator('floatPos'))
        
        self.forceFwhm_check = wx.CheckBox(panel, -1, "Force")
        self.forceFwhm_check.SetFont(wx.SMALL_FONT)
        self.forceFwhm_check.SetValue(config.spectrumGenerator['forceFwhm'])
        
        points_label = wx.StaticText(panel, -1, "Points/peak:")
        points_label.SetFont(wx.SMALL_FONT)
        self.points_value = wx.TextCtrl(panel, -1, str(config.spectrumGenerator['points']), size=(60, -1), validator=mwx.validator('intPos'))
        
        noise_label = wx.StaticText(panel, -1, "Noise width:")
        noise_label.SetFont(wx.SMALL_FONT)
        self.noise_value = wx.TextCtrl(panel, -1, str(config.spectrumGenerator['noise']), size=(80, -1), validator=mwx.validator('floatPos'))
        
        self.generate_butt = wx.Button(panel, -1, "Generate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.generate_butt.Bind(wx.EVT_BUTTON, self.onGenerate)
        
        self.apply_butt = wx.Button(panel, -1, "Apply", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.apply_butt.Bind(wx.EVT_BUTTON, self.onApply)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(peakShape_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.peakShape_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(fwhm_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fwhm_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.forceFwhm_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(points_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.points_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(noise_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.noise_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.AddStretchSpacer()
        sizer.Add(self.generate_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.apply_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
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
        self.collapse_butt = wx.BitmapButton(panel, -1, images.lib['arrowsDown'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.collapse_butt.Bind(wx.EVT_BUTTON, self.onCollapse)
        
        self.showPeaks_check = wx.CheckBox(panel, -1, "Show peaks")
        self.showPeaks_check.SetFont(wx.SMALL_FONT)
        self.showPeaks_check.SetValue(config.spectrumGenerator['showPeaks'])
        self.showPeaks_check.Bind(wx.EVT_CHECKBOX, self.onShowPeaks)
        
        self.showOverlay_check = wx.CheckBox(panel, -1, "Show overlay")
        self.showOverlay_check.SetFont(wx.SMALL_FONT)
        self.showOverlay_check.SetValue(config.spectrumGenerator['showOverlay'])
        self.showOverlay_check.Bind(wx.EVT_CHECKBOX, self.onShowOverlay)
        
        self.showFlipped_check = wx.CheckBox(panel, -1, "Flip overlay")
        self.showFlipped_check.SetFont(wx.SMALL_FONT)
        self.showFlipped_check.SetValue(config.spectrumGenerator['showFlipped'])
        self.showFlipped_check.Bind(wx.EVT_CHECKBOX, self.onShowFlipped)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(self.collapse_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(self.showPeaks_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.showOverlay_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.showFlipped_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSpectrumCanvas(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.spectrumCanvas = mspy.plot.canvas(self, size=(700, 350), style=mwx.PLOTCANVAS_STYLE_PANEL)
        
        # set default params
        self.updateCanvasProperties(refresh=False)
        self.spectrumCanvas.setProperties(showZero=True)
        self.spectrumCanvas.setProperties(showLegend=False)
        self.spectrumCanvas.setProperties(showGel=False)
        self.spectrumCanvas.setProperties(showCurXPos=True)
        self.spectrumCanvas.setProperties(showCurYPos=True)
        self.spectrumCanvas.setProperties(showCurCharge=True)
        self.spectrumCanvas.setProperties(zoomAxis='x')
        self.spectrumCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.spectrumCanvas.setProperties(reverseDrawing=True)
        
        self.spectrumCanvas.setLMBFunction('xDistance')
        
        self.spectrumCanvas.draw(self.spectrumContainer)
        
        return self.spectrumCanvas
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
        
        self.parent.updateTmpSpectrum(None)
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
    
    
    def onGenerate(self, evt):
        """Generate compounds ions."""
        
        # check processing
        if self.processing:
            return
        
        # clear recent
        self.currentProfile = None
        self.currentPeaks = None
        
        # check document
        if not self.currentDocument or len(self.currentDocument.spectrum.peaklist) == 0:
            wx.Bell()
            return
        
        # get params
        if not self.getParams():
            self.updateSpectrumCanvas()
            self.parent.updateTmpSpectrum(None)
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.generate_butt.Enable(False)
        self.apply_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runSpectrumGenerator)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update spectrum canvas
        self.updateSpectrumCanvas(rescale=False)
        
        # update spectrum overlay
        self.updateSpectrumOverlay()
        
        # hide processing gauge
        self.onProcessing(False)
        self.generate_butt.Enable(True)
        self.apply_butt.Enable(True)
    # ----
    
    
    def onApply(self, evt):
        """Apply current profile to current document."""
        
        # check data and document
        if self.currentDocument == None or self.currentProfile == None:
            wx.Bell()
            return
        
        # ask to owerwrite spectrum
        if self.currentDocument.spectrum.hasprofile():
            title = 'Do you really want to apply generated spectrum\nto current document?'
            message = 'Original profile data will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Apply", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # backup document
        self.currentDocument.backup(('spectrum'))
        
        # set profile to document
        points = self.currentProfile.copy()
        self.currentDocument.spectrum.setprofile(points)
        
        # update document
        self.parent.onDocumentChanged(items=('spectrum'))
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
    
    
    def onShowPeaks(self, evt):
        """Show / hide individual peaks."""
        
        # get value
        config.spectrumGenerator['showPeaks'] = self.showPeaks_check.GetValue()
        
        # update spectrum canvas
        self.updateSpectrumCanvas(rescale=False)
    # ----
    
    
    def onShowOverlay(self, evt):
        """Show / hide profile overlay in main viewer."""
        
        # get value
        config.spectrumGenerator['showOverlay'] = self.showOverlay_check.GetValue()
        
        # update tmp spectrum
        self.updateSpectrumOverlay()
    # ----
    
    
    def onShowFlipped(self, evt):
        """Flip profile overlay in main viewer."""
        
        # get value
        config.spectrumGenerator['showFlipped'] = self.showFlipped_check.GetValue()
        
        # update tmp spectrum
        self.updateSpectrumOverlay()
    # ----
    
    
    def setData(self, document):
        """Set data."""
        
        # set new document
        self.currentDocument = document
        self.currentProfile = None
        self.currentPeaks = None
        
        # update gui
        self.updateSpectrumCanvas()
        self.parent.updateTmpSpectrum(None)
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            config.spectrumGenerator['fwhm'] = abs(float(self.fwhm_value.GetValue()))
            config.spectrumGenerator['points'] = abs(int(self.points_value.GetValue()))
            config.spectrumGenerator['noise'] = abs(float(self.noise_value.GetValue()))
            config.spectrumGenerator['forceFwhm'] = self.forceFwhm_check.GetValue()
            
            config.spectrumGenerator['peakShape'] = 'gaussian'
            if self.peakShape_choice.GetStringSelection() == 'Asymmetrical':
                config.spectrumGenerator['peakShape'] = 'gausslorentzian'
            
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateCanvasProperties(self, refresh=True):
        """Set current canvas properties."""
        
        # set common properties
        self.spectrumCanvas.setProperties(xLabel=config.spectrum['xLabel'])
        self.spectrumCanvas.setProperties(yLabel=config.spectrum['yLabel'])
        self.spectrumCanvas.setProperties(showGrid=config.spectrum['showGrid'])
        self.spectrumCanvas.setProperties(showMinorTicks=config.spectrum['showMinorTicks'])
        self.spectrumCanvas.setProperties(showXPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(showYPosBar=config.spectrum['showPosBars'])
        self.spectrumCanvas.setProperties(posBarSize=config.spectrum['posBarSize'])
        self.spectrumCanvas.setProperties(showCurImage=config.spectrum['showCursorImage'])
        self.spectrumCanvas.setProperties(checkLimits=config.spectrum['checkLimits'])
        self.spectrumCanvas.setProperties(autoScaleY=config.spectrum['autoscale'])
        self.spectrumCanvas.setProperties(overlapLabels=config.spectrum['overlapLabels'])
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
        
        # set spectum properties
        if len(self.spectrumContainer):
            self.spectrumContainer[0].setProperties(showPoints=config.spectrum['showDataPoints'])
            self.spectrumContainer[0].setProperties(showLabels=config.spectrum['showLabels'])
            self.spectrumContainer[0].setProperties(labelBgr=config.spectrum['labelBgr'])
            self.spectrumContainer[0].setProperties(labelAngle=config.spectrum['labelAngle'])
        
        # refresh canvas
        if refresh:
            self.spectrumCanvas.refresh()
    # ----
    
    
    def updateSpectrumCanvas(self, rescale=True):
        """Show current profile and peaks in canvas."""
        
        # clear container
        self.spectrumContainer.empty()
        
        # check document
        if not self.currentDocument:
            self.spectrumCanvas.draw(self.spectrumContainer)
            return
        
        # get current peaklist
        peaklist = self.currentDocument.spectrum.peaklist
        
        # get current profile data
        profile = []
        if self.currentProfile != None:
            profile = self.currentProfile
        
        # add main profile spectrum to container
        labelFont = wx.Font(config.spectrum['labelFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        spectrum = mspy.plot.spectrum(
            scan = mspy.scan(profile=profile, peaklist=peaklist),
            spectrumColour = (16,71,185),
            tickColour = (255,0,0),
            showPoints = config.spectrum['showDataPoints'],
            showLabels = config.spectrum['showLabels'],
            showTicks = True,
            labelDigits = config.main['mzDigits'],
            labelBgr = config.spectrum['labelBgr'],
            labelAngle = config.spectrum['labelAngle'],
            labelFont = labelFont
        )
        self.spectrumContainer.append(spectrum)
        
        # add individual peaks to container
        if config.spectrumGenerator['showPeaks']:
            if self.currentPeaks != None:
                for peak in self.currentPeaks:
                    spectrum = mspy.plot.points(
                        points = peak,
                        lineColour = (50,140,0),
                        showLines = True,
                        showPoints = False,
                        exactFit = True
                    )
                    self.spectrumContainer.append(spectrum)
        
        # get current axis
        if not rescale:
            xAxis = self.spectrumCanvas.getCurrentXRange()
            yAxis = self.spectrumCanvas.getCurrentYRange()
        else:
            xAxis = None
            yAxis = None
        
        # draw spectra
        self.spectrumCanvas.draw(self.spectrumContainer, xAxis=xAxis, yAxis=yAxis)
    # ----
    
    
    def updateSpectrumOverlay(self):
        """Show / hide profile overlay in main viewer."""
        
        # update tmp spectrum
        if self.currentProfile == None or not config.spectrumGenerator['showOverlay']:
            self.parent.updateTmpSpectrum(None)
        else:
            self.parent.updateTmpSpectrum(self.currentProfile, flipped=config.spectrumGenerator['showFlipped'])
    # ----
    
    
    def runSpectrumGenerator(self):
        """Generate spectrum."""
        
        self.currentProfile = None
        self.currentPeaks = None
        
        # run task
        try:
            
            # make profile spectrum
            self.currentProfile = mspy.profile(
                peaklist = self.currentDocument.spectrum.peaklist,
                fwhm = config.spectrumGenerator['fwhm'],
                points = config.spectrumGenerator['points'],
                noise = config.spectrumGenerator['noise'],
                forceFwhm = config.spectrumGenerator['forceFwhm'],
                model = config.spectrumGenerator['peakShape'],
            )
            
            # make peak spectra
            self.currentPeaks = []
            for peak in self.currentDocument.spectrum.peaklist:
                
                # get fwhm
                fwhm = config.spectrumGenerator['fwhm']
                if peak.fwhm and not config.spectrumGenerator['forceFwhm']:
                    fwhm = peak.fwhm
                
                # gaussian shape
                if config.spectrumGenerator['peakShape'] == 'gaussian':
                    points = mspy.gaussian(
                        x = peak.mz,
                        minY = peak.base,
                        maxY = peak.ai,
                        fwhm = fwhm
                    )
                
                # lorentzian shape
                elif config.spectrumGenerator['peakShape'] == 'lorentzian':
                    points = mspy.lorentzian(
                        x = peak.mz,
                        minY = peak.base,
                        maxY = peak.ai,
                        fwhm = fwhm
                    )
                
                # gauss-lorentzian shape
                elif config.spectrumGenerator['peakShape'] == 'gausslorentzian':
                    points = mspy.gausslorentzian(
                        x = peak.mz,
                        minY = peak.base,
                        maxY = peak.ai,
                        fwhm = fwhm
                    )
                
                self.currentPeaks.append(points)
        
        # task canceled
        except mspy.ForceQuit:
            self.currentProfile = None
            self.currentPeaks = None
    # ----
    
    

