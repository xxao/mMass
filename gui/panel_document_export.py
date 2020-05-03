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
import os.path
import wx

# load modules
from ids import *
import mwx
import images
import config
import mspy


# FLOATING PANEL WITH EXPORTING TOOLS
# -----------------------------------

class panelDocumentExport(wx.MiniFrame):
    """Document export tools."""
    
    def __init__(self, parent, tool='image'):
        wx.MiniFrame.__init__(self, parent, -1, 'Export', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.processing = None
        
        self.currentTool = tool
        
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
        
        # make panel
        image = self.makeImagePanel()
        peaklist = self.makePeaklistPanel()
        spectrum = self.makeSpectrumPanel()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(image, 1, wx.EXPAND, 0)
        self.mainSizer.Add(peaklist, 1, wx.EXPAND, 0)
        self.mainSizer.Add(spectrum, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
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
        self.image_butt = wx.BitmapButton(panel, ID_documentExportImage, images.lib['documentExportImageOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.image_butt.SetToolTip(wx.ToolTip("Export spectrum image"))
        self.image_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.peaklist_butt = wx.BitmapButton(panel, ID_documentExportPeaklist, images.lib['documentExportPeaklistOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.peaklist_butt.SetToolTip(wx.ToolTip("Export peak list"))
        self.peaklist_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.spectrum_butt = wx.BitmapButton(panel, ID_documentExportSpectrum, images.lib['documentExportSpectrumOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.spectrum_butt.SetToolTip(wx.ToolTip("Export spectrum data"))
        self.spectrum_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        # make controls
        self.export_butt = wx.Button(panel, -1, "Export", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.export_butt.Bind(wx.EVT_BUTTON, self.onExport)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.image_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.peaklist_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.spectrum_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.export_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeImagePanel(self):
        """Image export panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        imageWidth_label = wx.StaticText(panel, -1, "Width:")
        self.imageWidth_value = wx.TextCtrl(panel, -1, str(config.export['imageWidth']), size=(140, -1), validator=mwx.validator('floatPos'))
        
        imageHeight_label = wx.StaticText(panel, -1, "Height:")
        self.imageHeight_value = wx.TextCtrl(panel, -1, str(config.export['imageHeight']), size=(140, -1), validator=mwx.validator('floatPos'))
        
        self.imageUnits_choice = wx.Choice(panel, -1, choices=['cm', 'in', 'px'], size=(60, mwx.CHOICE_HEIGHT))
        self.imageUnits_choice.SetStringSelection(config.export['imageUnits'])
        
        imageFormat_label = wx.StaticText(panel, -1, "Format:")
        self.imageFormat_choice = wx.Choice(panel, -1, choices=['PNG', 'TIFF', 'JPEG'], size=(140, mwx.CHOICE_HEIGHT))
        self.imageFormat_choice.SetStringSelection(config.export['imageFormat'])
        
        imageResolution_label = wx.StaticText(panel, -1, "Resolution:")
        imageResolutionUnits_label = wx.StaticText(panel, -1, "dpi")
        choices = ['72', '150', '200', '300', '600']
        self.imageResolution_choice = wx.Choice(panel, -1, choices=choices, size=(140, mwx.CHOICE_HEIGHT))
        self.imageResolution_choice.Select(0)
        if str(config.export['imageResolution']) in choices:
            self.imageResolution_choice.Select(choices.index(str(config.export['imageResolution'])))
        self.imageResolution_choice.Bind(wx.EVT_CHOICE, self.onImageResolutionChanged)
        
        imageFontsScale_label = wx.StaticText(panel, -1, "Font scale:")
        self.imageFontsScale_slider = wx.Slider(panel, -1, config.export['imageFontsScale'], 1, 10, size=(140, -1), style=mwx.SLIDER_STYLE)
        self.imageFontsScale_slider.SetTickFreq(1,1)
        
        imageDrawingsScale_label = wx.StaticText(panel, -1, "Line scale:")
        self.imageDrawingsScale_slider = wx.Slider(panel, -1, config.export['imageDrawingsScale'], 1, 10, size=(140, -1), style=mwx.SLIDER_STYLE)
        self.imageDrawingsScale_slider.SetTickFreq(1,1)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(imageWidth_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageWidth_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.imageUnits_choice, (0,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        grid.Add(imageHeight_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageHeight_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(imageResolution_label, (2,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageResolution_choice, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(imageResolutionUnits_label, (2,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        grid.Add(imageFontsScale_label, (3,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageFontsScale_slider, (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(imageDrawingsScale_label, (4,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageDrawingsScale_slider, (4,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(imageFormat_label, (5,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.imageFormat_choice, (5,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makePeaklistPanel(self):
        """Peaklist export panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.peaklistColumnMz_check = wx.CheckBox(panel, -1, "m/z")
        self.peaklistColumnMz_check.SetValue(config.export['peaklistColumns'].count('mz'))
        
        self.peaklistColumnAi_check = wx.CheckBox(panel, -1, "a.i.")
        self.peaklistColumnAi_check.SetValue(config.export['peaklistColumns'].count('ai'))
        
        self.peaklistColumnBase_check = wx.CheckBox(panel, -1, "Baseline")
        self.peaklistColumnBase_check.SetValue(config.export['peaklistColumns'].count('base'))
        
        self.peaklistColumnInt_check = wx.CheckBox(panel, -1, "Intensity")
        self.peaklistColumnInt_check.SetValue(config.export['peaklistColumns'].count('int'))
        
        self.peaklistColumnRel_check = wx.CheckBox(panel, -1, "Relative intensity")
        self.peaklistColumnRel_check.SetValue(config.export['peaklistColumns'].count('rel'))
        
        self.peaklistColumnSn_check = wx.CheckBox(panel, -1, "s/n")
        self.peaklistColumnSn_check.SetValue(config.export['peaklistColumns'].count('sn'))
        
        self.peaklistColumnZ_check = wx.CheckBox(panel, -1, "Charge")
        self.peaklistColumnZ_check.SetValue(config.export['peaklistColumns'].count('z'))
        
        self.peaklistColumnMass_check = wx.CheckBox(panel, -1, "Mass")
        self.peaklistColumnMass_check.SetValue(config.export['peaklistColumns'].count('mass'))
        
        self.peaklistColumnFwhm_check = wx.CheckBox(panel, -1, "FWHM")
        self.peaklistColumnFwhm_check.SetValue(config.export['peaklistColumns'].count('fwhm'))
        
        self.peaklistColumnResol_check = wx.CheckBox(panel, -1, "Resolution")
        self.peaklistColumnResol_check.SetValue(config.export['peaklistColumns'].count('resol'))
        
        self.peaklistColumnGroup_check = wx.CheckBox(panel, -1, "Group")
        self.peaklistColumnGroup_check.SetValue(config.export['peaklistColumns'].count('group'))
        
        peaklistSelect_label = wx.StaticText(panel, -1, "Export:")
        self.peaklistSelect_choice = wx.Choice(panel, -1, choices=['All Peaks', 'Selected Peaks'], size=(200, mwx.CHOICE_HEIGHT))
        self.peaklistSelect_choice.Select(0)
        
        peaklistFormat_label = wx.StaticText(panel, -1, "Format:")
        self.peaklistFormat_choice = wx.Choice(panel, -1, choices=['ASCII', 'ASCII with Headers', 'MGF'], size=(200, mwx.CHOICE_HEIGHT))
        self.peaklistFormat_choice.SetStringSelection(config.export['peaklistFormat'])
        self.peaklistFormat_choice.Bind(wx.EVT_CHOICE, self.onPeaklistFormatChanged)
        
        peaklistSeparator_label = wx.StaticText(panel, -1, "Separator:")
        self.peaklistSeparator_choice = wx.Choice(panel, -1, choices=['Comma', 'Semicolon', 'Tab'], size=(200, mwx.CHOICE_HEIGHT))
        self.peaklistSeparator_choice.SetStringSelection(config.export['peaklistSeparator'])
        choices = {',':0, ';':1, 'tab':2}
        self.peaklistSeparator_choice.Select(choices[config.export['peaklistSeparator']])
        
        self.onPeaklistFormatChanged()
        
        # pack elements
        grid1 = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid1.Add(self.peaklistColumnMz_check, (0,0))
        grid1.Add(self.peaklistColumnAi_check, (1,0))
        grid1.Add(self.peaklistColumnBase_check, (2,0))
        grid1.Add(self.peaklistColumnInt_check, (3,0))
        grid1.Add(self.peaklistColumnRel_check, (4,0))
        grid1.Add(self.peaklistColumnSn_check, (5,0))
        grid1.Add(self.peaklistColumnZ_check, (0,2))
        grid1.Add(self.peaklistColumnMass_check, (1,2))
        grid1.Add(self.peaklistColumnFwhm_check, (2,2))
        grid1.Add(self.peaklistColumnResol_check, (3,2))
        grid1.Add(self.peaklistColumnGroup_check, (4,2))
        
        grid2 = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid2.Add(peaklistSelect_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid2.Add(self.peaklistSelect_choice, (0,1))
        grid2.Add(peaklistFormat_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid2.Add(self.peaklistFormat_choice, (1,1))
        grid2.Add(peaklistSeparator_label, (2,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid2.Add(self.peaklistSeparator_choice, (2,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid1, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(grid2, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSpectrumPanel(self):
        """Spectrum export panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        spectrumRange_label = wx.StaticText(panel, -1, "Range:")
        self.spectrumRange_choice = wx.Choice(panel, -1, choices=['Full Spectrum', 'Current View'], size=(130, mwx.CHOICE_HEIGHT))
        self.spectrumRange_choice.Select(0)
        
        spectrumSeparator_label = wx.StaticText(panel, -1, "Separator:")
        self.spectrumSeparator_choice = wx.Choice(panel, -1, choices=['Comma', 'Semicolon', 'Tab'], size=(130, mwx.CHOICE_HEIGHT))
        self.spectrumSeparator_choice.SetStringSelection(config.export['spectrumSeparator'])
        choices = {',':0, ';':1, 'tab':2}
        self.spectrumSeparator_choice.Select(choices[config.export['spectrumSeparator']])
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(spectrumRange_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.spectrumRange_choice, (0,1))
        grid.Add(spectrumSeparator_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.spectrumSeparator_choice, (1,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeGaugePanel(self):
        """Make processing gauge."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.gauge = mwx.gauge(panel, -1)
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.gauge, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.GAUGE_SPACE)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Destroy this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # get the tool
        if evt != None:
            tool = 'image'
            if evt.GetId() == ID_documentExportImage:
                tool = 'image'
            elif evt.GetId() == ID_documentExportPeaklist:
                tool = 'peaklist'
            elif evt.GetId() == ID_documentExportSpectrum:
                tool = 'spectrum'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # set icons off
        self.image_butt.SetBitmapLabel(images.lib['documentExportImageOff'])
        self.peaklist_butt.SetBitmapLabel(images.lib['documentExportPeaklistOff'])
        self.spectrum_butt.SetBitmapLabel(images.lib['documentExportSpectrumOff'])
        
        # set panel
        if tool == 'image':
            self.SetTitle("Export Spectrum Image")
            self.mainSizer.Show(1)
            self.image_butt.SetBitmapLabel(images.lib['documentExportImageOn'])
            
        elif tool == 'peaklist':
            self.SetTitle("Export Peak List")
            self.mainSizer.Show(2)
            self.peaklist_butt.SetBitmapLabel(images.lib['documentExportPeaklistOn'])
            
        elif tool == 'spectrum':
            self.SetTitle("Export Spectrum Data")
            self.mainSizer.Show(3)
            self.spectrum_butt.SetBitmapLabel(images.lib['documentExportSpectrumOn'])
        
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
        
        # fit layout
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
    # ----
    
    
    def onImageResolutionChanged(self, evt=None):
        """Get new image resolution."""
        
        # get resolution
        resolution = int(self.imageResolution_choice.GetStringSelection())
        
        # set scales
        if resolution == 72:
            self.imageFontsScale_slider.SetValue(1)
            self.imageDrawingsScale_slider.SetValue(1)
        elif resolution == 150:
            self.imageFontsScale_slider.SetValue(2)
            self.imageDrawingsScale_slider.SetValue(2)
        elif resolution == 200:
            self.imageFontsScale_slider.SetValue(2)
            self.imageDrawingsScale_slider.SetValue(2)
        elif resolution == 300:
            self.imageFontsScale_slider.SetValue(2)
            self.imageDrawingsScale_slider.SetValue(3)
        elif resolution == 600:
            self.imageFontsScale_slider.SetValue(4)
            self.imageDrawingsScale_slider.SetValue(5)
    # ----
    
    
    def onPeaklistFormatChanged(self, evt=None):
        """Get new peaklist format."""
        
        # get format
        config.export['peaklistFormat'] = self.peaklistFormat_choice.GetStringSelection()
        
        # enable/disable columns and separator
        enable = True
        if config.export['peaklistFormat'] == 'MGF':
            enable = False
            
        self.peaklistColumnMz_check.Enable(enable)
        self.peaklistColumnAi_check.Enable(enable)
        self.peaklistColumnBase_check.Enable(enable)
        self.peaklistColumnInt_check.Enable(enable)
        self.peaklistColumnRel_check.Enable(enable)
        self.peaklistColumnSn_check.Enable(enable)
        self.peaklistColumnZ_check.Enable(enable)
        self.peaklistColumnMass_check.Enable(enable)
        self.peaklistColumnFwhm_check.Enable(enable)
        self.peaklistColumnResol_check.Enable(enable)
        self.peaklistColumnGroup_check.Enable(enable)
        self.peaklistSeparator_choice.Enable(enable)
    # ----
    
    
    def onExport(self, evt):
        """Export data."""
        
        # check processing
        if self.processing:
            return
        
        # get params
        if not self.getParams():
            return
        
        # export data
        if self.currentTool == 'image':
            self.onExportImage()
            
        elif self.currentTool == 'peaklist':
            self.onExportPeaklist()
            
        elif self.currentTool == 'spectrum':
            self.onExportSpectrum()
    # ----
    
    
    def onExportImage(self):
        """Export image."""
        
        # get format
        if config.export['imageFormat'] == 'PNG':
            fileName = 'spectrum.png'
            fileType = "PNG image file|*.png"
        elif config.export['imageFormat'] == 'TIFF':
            fileName = 'spectrum.tif'
            fileType = "TIFF image file|*.tif"
        elif config.export['imageFormat'] == 'JPEG':
            fileName = 'spectrum.jpg'
            fileType = "JPEG image file|*.jpg"
        
        # raise export dialog
        dlg = wx.FileDialog(self, "Export Spectrum Image", config.main['lastDir'], fileName, fileType, wx.SAVE|wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            config.main['lastDir'] = os.path.split(path)[0]
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.export_butt.Enable(False)
        self.gauge.pulse()
        
        # make image
        # (do not do this processing in separate thread because of wx)
        self.runExportImage(path)
        
        # hide processing gauge
        self.onProcessing(False)
        self.export_butt.Enable(True)
    # ----
    
    
    def onExportPeaklist(self):
        """Export peeaklist data."""
        
        # get format
        if config.export['peaklistFormat'] in ('ASCII' 'ASCII with Headers'):
            fileName = 'peaklist.txt'
            fileType = "ASCII file|*.txt"
        elif config.export['peaklistFormat'] == 'MGF':
            fileName = 'peaklist.mgf'
            fileType = "MGF file|*.mgf"
        
        # raise export dialog
        dlg = wx.FileDialog(self, "Export Peak List", config.main['lastDir'], fileName, fileType, wx.SAVE|wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            config.main['lastDir'] = os.path.split(path)[0]
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.export_butt.Enable(False)
        
        # make image
        self.processing = threading.Thread(target=self.runExportPeaklist, kwargs={'path':path})
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # hide processing gauge
        self.onProcessing(False)
        self.export_butt.Enable(True)
    # ----
    
    
    def onExportSpectrum(self):
        """Export spectrum data."""
        
        # set default filename
        fileName = 'spectrum.txt'
        fileType = "ASCII file|*.txt"
        
        # raise export dialog
        dlg = wx.FileDialog(self, "Export Spectrum Data", config.main['lastDir'], fileName, fileType, wx.SAVE|wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            config.main['lastDir'] = os.path.split(path)[0]
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.export_butt.Enable(False)
        
        # make image
        self.processing = threading.Thread(target=self.runExportSpectrum, kwargs={'path':path})
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # hide processing gauge
        self.onProcessing(False)
        self.export_butt.Enable(True)
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        try:
            
            # image
            config.export['imageWidth'] = float(self.imageWidth_value.GetValue())
            config.export['imageHeight'] = float(self.imageHeight_value.GetValue())
            config.export['imageUnits'] = self.imageUnits_choice.GetStringSelection()
            config.export['imageFormat'] = self.imageFormat_choice.GetStringSelection()
            config.export['imageResolution'] = int(self.imageResolution_choice.GetStringSelection())
            config.export['imageFontsScale'] = int(self.imageFontsScale_slider.GetValue())
            config.export['imageDrawingsScale'] = int(self.imageDrawingsScale_slider.GetValue())
            
            # peaklist data
            config.export['peaklistColumns'] = []
            if self.peaklistColumnMz_check.IsChecked():
                config.export['peaklistColumns'].append('mz')
            if self.peaklistColumnAi_check.IsChecked():
                config.export['peaklistColumns'].append('ai')
            if self.peaklistColumnBase_check.IsChecked():
                config.export['peaklistColumns'].append('base')
            if self.peaklistColumnInt_check.IsChecked():
                config.export['peaklistColumns'].append('int')
            if self.peaklistColumnRel_check.IsChecked():
                config.export['peaklistColumns'].append('rel')
            if self.peaklistColumnZ_check.IsChecked():
                config.export['peaklistColumns'].append('z')
            if self.peaklistColumnMass_check.IsChecked():
                config.export['peaklistColumns'].append('mass')
            if self.peaklistColumnSn_check.IsChecked():
                config.export['peaklistColumns'].append('sn')
            if self.peaklistColumnFwhm_check.IsChecked():
                config.export['peaklistColumns'].append('fwhm')
            if self.peaklistColumnResol_check.IsChecked():
                config.export['peaklistColumns'].append('resol')
            if self.peaklistColumnGroup_check.IsChecked():
                config.export['peaklistColumns'].append('group')
            
            choices = {'Comma':',', 'Semicolon':';', 'Tab':'tab'}
            config.export['peaklistSeparator'] = choices[self.peaklistSeparator_choice.GetStringSelection()]
            
            # spectrum data
            choices = {'Comma':',', 'Semicolon':';', 'Tab':'tab'}
            config.export['spectrumSeparator'] = choices[self.spectrumSeparator_choice.GetStringSelection()]
        
        # ring error bell if error
        except:
            wx.Bell()
            return False
        
        return True
    # ----
    
    
    def runExportImage(self, path):
        """Make spectrum image."""
        
        # get format
        if config.export['imageFormat'] == 'PNG':
            fileFormat = wx.BITMAP_TYPE_PNG
        elif config.export['imageFormat'] == 'TIFF':
            fileFormat = wx.BITMAP_TYPE_TIF
        elif config.export['imageFormat'] == 'JPEG':
            fileFormat = wx.BITMAP_TYPE_JPEG
        
        # get image size in pixels
        width = float(config.export['imageWidth'])
        height = float(config.export['imageHeight'])
        resolution = config.export['imageResolution']
        
        if config.export['imageUnits'] == 'in':
            width = width * resolution
            height = height * resolution
        elif config.export['imageUnits'] == 'cm':
            width = width * resolution * 0.3937
            height = height * resolution * 0.3937
        
        # set printer scale
        printerScale = {
            'drawings':config.export['imageDrawingsScale'],
            'fonts':config.export['imageFontsScale']
        }
        
        # make image
        bitmap = self.parent.getSpectrumBitmap(width, height, printerScale)
        if not bitmap:
            wx.Bell()
            return
        else:
            image = bitmap.ConvertToImage()
            image.SetOption(wx.IMAGE_OPTION_QUALITY, '100')
            image.SetOption(wx.IMAGE_OPTION_RESOLUTION, str(resolution))
            image.SetOption(wx.IMAGE_OPTION_RESOLUTIONX, str(resolution))
            image.SetOption(wx.IMAGE_OPTION_RESOLUTIONY, str(resolution))
            image.SetOption(wx.IMAGE_OPTION_RESOLUTIONUNIT, '1')
        
        # save image
        try:
            image.SaveFile(path, fileFormat)
        except:
            wx.Bell()
    # ----
    
    
    def runExportPeaklist(self, path):
        """Export peeaklist data."""
        
        # get peaklist
        selection = {'All Peaks':'', 'Selected Peaks':'S'}
        filters = selection[self.peaklistSelect_choice.GetStringSelection()]
        peaklist = self.parent.getCurrentPeaklist(filters)
        
        # check peaklist
        if not peaklist:
            wx.Bell()
            return
        
        # export to ascii
        if config.export['peaklistFormat'] in ('ASCII', 'ASCII with Headers'):
            
            buff = ''
            
            # set separator
            separator = config.export['peaklistSeparator']
            if config.export['peaklistSeparator'] == 'tab':
                separator = '\t'
            
            # export headers
            if config.export['peaklistFormat'] == 'ASCII with Headers':
                header = ''
                if 'mz' in config.export['peaklistColumns']:
                    header += "m/z" + separator
                if 'ai' in config.export['peaklistColumns']:
                    header += "a.i." + separator
                if 'base' in config.export['peaklistColumns']:
                    header += "base" + separator
                if 'int' in config.export['peaklistColumns']:
                    header += "int" + separator
                if 'rel' in config.export['peaklistColumns']:
                    header += "r.int." + separator
                if 'sn' in config.export['peaklistColumns']:
                    header += "s/n" + separator
                if 'z' in config.export['peaklistColumns']:
                    header += "z" + separator
                if 'mass' in config.export['peaklistColumns']:
                    header += "mass" + separator
                if 'fwhm' in config.export['peaklistColumns']:
                    header += "fwhm" + separator
                if 'resol' in config.export['peaklistColumns']:
                    header += "resol." + separator
                if 'group' in config.export['peaklistColumns']:
                    header += "group" + separator
                
                buff += '%s\n' % (header.rstrip())
            
            # export data
            for peak in peaklist:
                line = ''
                if 'mz' in config.export['peaklistColumns']:
                    line += str(peak.mz) + separator
                if 'ai' in config.export['peaklistColumns']:
                    line += str(peak.ai) + separator
                if 'base' in config.export['peaklistColumns']:
                    line += str(peak.base) + separator
                if 'int' in config.export['peaklistColumns']:
                    line += str(peak.intensity) + separator
                if 'rel' in config.export['peaklistColumns']:
                    line += str(peak.ri*100) + separator
                if 'sn' in config.export['peaklistColumns']:
                    line += str(peak.sn) + separator
                if 'z' in config.export['peaklistColumns']:
                    line += str(peak.charge) + separator
                if 'mass' in config.export['peaklistColumns']:
                    line += str(peak.mass()) + separator
                if 'fwhm' in config.export['peaklistColumns']:
                    line += str(peak.fwhm) + separator
                if 'resol' in config.export['peaklistColumns']:
                    line += str(peak.resolution) + separator
                if 'group' in config.export['peaklistColumns']:
                    line += str(peak.group) + separator
                
                buff += '%s\n' % (line.replace("None","").rstrip())
        
        # export to mgf
        elif config.export['peaklistFormat'] == 'MGF':
            
            # export data
            buff = 'BEGIN IONS\n'
            for peak in peaklist:
                buff += '%f %f\n' % (peak.mz, peak.intensity)
            buff += 'END IONS'
            
        # save file
        try:
            save = file(path, 'w')
            save.write(buff.encode("utf-8"))
            save.close()
        except IOError:
            wx.Bell()
    # ----
    
    
    def runExportSpectrum(self, path):
        """Export spectrum data."""
        
        # get spectrum
        if self.spectrumRange_choice.GetStringSelection() == 'Full Spectrum':
            spectrum = self.parent.getCurrentSpectrumPoints()
        elif self.spectrumRange_choice.GetStringSelection() == 'Current View':
            spectrum = self.parent.getCurrentSpectrumPoints(currentView=True)
        
        # check spectrum
        if spectrum == None:
            wx.Bell()
            return
        
        # set separator
        separator = config.export['spectrumSeparator']
        if config.export['spectrumSeparator'] == 'tab':
            separator = '\t'
        
        # export data
        buff = ''
        for point in spectrum:
            buff += '%f%s%f\n' % (point[0], separator, point[1])
        
        # save file
        try:
            save = file(path, 'w')
            save.write(buff.encode("utf-8"))
            save.close()
        except IOError:
            wx.Bell()
    # ----
    
    
