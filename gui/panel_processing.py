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
import numpy
import wx
import copy

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy
import doc


# FLOATING PANEL WITH PROCESSING TOOLS
# ------------------------------------

class panelProcessing(wx.MiniFrame):
    """Data processing tools."""
    
    def __init__(self, parent, tool='peakpicking'):
        wx.MiniFrame.__init__(self, parent, -1, 'Processing', size=(300, -1), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.processing = None
        
        self.currentTool = tool
        self.currentDocument = None
        self.previewData = None
        self.batchChanged = []
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # update documents lists
        self.updateAvailableDocuments()
        
        # select default tool
        self.onToolSelected(tool=self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        math = self.makeMathPanel()
        crop = self.makeCropPanel()
        baseline = self.makeBaselinePanel()
        smoothing = self.makeSmoothingPanel()
        peakpicking = self.makePeakpickingPanel()
        deisotoping = self.makeDeisotopingPanel()
        deconvolution = self.makeDeconvolutionPanel()
        batch = self.makeBatchPanel()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(math, 1, wx.EXPAND, 0)
        self.mainSizer.Add(crop, 1, wx.EXPAND, 0)
        self.mainSizer.Add(baseline, 1, wx.EXPAND, 0)
        self.mainSizer.Add(smoothing, 1, wx.EXPAND, 0)
        self.mainSizer.Add(peakpicking, 1, wx.EXPAND, 0)
        self.mainSizer.Add(deisotoping, 1, wx.EXPAND, 0)
        self.mainSizer.Add(deconvolution, 1, wx.EXPAND, 0)
        self.mainSizer.Add(batch, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        self.mainSizer.Hide(5)
        self.mainSizer.Hide(6)
        self.mainSizer.Hide(7)
        self.mainSizer.Hide(8)
        self.mainSizer.Hide(9)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        self.math_butt = wx.BitmapButton(panel, ID_processingMath, images.lib['processingMathOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.math_butt.SetToolTip(wx.ToolTip("Math operations"))
        self.math_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.crop_butt = wx.BitmapButton(panel, ID_processingCrop, images.lib['processingCropOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.crop_butt.SetToolTip(wx.ToolTip("Crop data"))
        self.crop_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.baseline_butt = wx.BitmapButton(panel, ID_processingBaseline, images.lib['processingBaselineOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.baseline_butt.SetToolTip(wx.ToolTip("Baseline correction"))
        self.baseline_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.smoothing_butt = wx.BitmapButton(panel, ID_processingSmoothing, images.lib['processingSmoothingOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.smoothing_butt.SetToolTip(wx.ToolTip("Smoothing"))
        self.smoothing_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.peakpicking_butt = wx.BitmapButton(panel, ID_processingPeakpicking, images.lib['processingPeakpickingOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.peakpicking_butt.SetToolTip(wx.ToolTip("Peak picking"))
        self.peakpicking_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.deisotoping_butt = wx.BitmapButton(panel, ID_processingDeisotoping, images.lib['processingDeisotopingOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.deisotoping_butt.SetToolTip(wx.ToolTip("Deisotoping"))
        self.deisotoping_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.deconvolution_butt = wx.BitmapButton(panel, ID_processingDeconvolution, images.lib['processingDeconvolutionOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.deconvolution_butt.SetToolTip(wx.ToolTip("Deconvolution"))
        self.deconvolution_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.batch_butt = wx.BitmapButton(panel, ID_processingBatch, images.lib['processingBatchOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.batch_butt.SetToolTip(wx.ToolTip("Batch processing"))
        self.batch_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.presets_butt = wx.BitmapButton(panel, -1, images.lib['toolsPresets'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.presets_butt.SetToolTip(wx.ToolTip("Processing presets"))
        self.presets_butt.Bind(wx.EVT_BUTTON, self.onPresets)
        
        self.preview_butt = wx.Button(panel, -1, "Preview", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.preview_butt.Bind(wx.EVT_BUTTON, self.onPreview)
        
        self.apply_butt = wx.Button(panel, -1, "Apply", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.apply_butt.Bind(wx.EVT_BUTTON, self.onApply)
        
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_LSPACE)
        self.toolbar.Add(self.math_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.crop_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.baseline_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.smoothing_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.peakpicking_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.deisotoping_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.deconvolution_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.batch_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.presets_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddStretchSpacer()
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.preview_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        self.toolbar.Add(self.apply_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeMathPanel(self):
        """Make controls for math operations."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        
        mathOperationMulti_label = wx.StaticText(panel, -1, "Global operations:")
        mathOperationSingle_label = wx.StaticText(panel, -1, "Basic operations:")
        
        self.mathOperationAverageAll_radio = wx.RadioButton(panel, -1, "Average all visible", style=wx.RB_GROUP)
        self.mathOperationCombineAll_radio = wx.RadioButton(panel, -1, "Sum all visible")
        self.mathOperationOverlayAll_radio = wx.RadioButton(panel, -1, "Overlay all visible")
        
        self.mathOperationNorm_radio = wx.RadioButton(panel, -1, "Normalize A")
        self.mathOperationCombine_radio = wx.RadioButton(panel, -1, "Combine A + B")
        self.mathOperationSubtract_radio = wx.RadioButton(panel, -1, "Subtract A - B")
        self.mathOperationOverlay_radio = wx.RadioButton(panel, -1, "Overlay max(A, B)")
        self.mathOperationMultiply_radio = wx.RadioButton(panel, -1, "Multiply A * ")
        
        self.mathMultiply_value = wx.TextCtrl(panel, -1, '1', size=(80, -1), validator=mwx.validator('floatPos'))
        self.mathMultiply_value.Disable()
        
        self.mathOperationNorm_radio.SetValue(True)
        
        self.mathOperationAverageAll_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationCombineAll_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationOverlayAll_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationNorm_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationCombine_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationSubtract_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationOverlay_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        self.mathOperationMultiply_radio.Bind(wx.EVT_RADIOBUTTON, self.onMathChanged)
        
        mathSpectrumA_label = wx.StaticText(panel, -1, "Spectrum A:")
        self.mathSpectrumA_choice = wx.Choice(panel, -1, choices=[], size=(200, mwx.CHOICE_HEIGHT))
        self.mathSpectrumA_choice.Disable()
        
        mathSpectrumB_label = wx.StaticText(panel, -1, "Spectrum B:")
        self.mathSpectrumB_choice = wx.Choice(panel, -1, choices=[], size=(200, mwx.CHOICE_HEIGHT))
        self.mathSpectrumB_choice.Disable()
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.SetEmptyCellSize((-1,0))
        
        grid.Add(mathOperationMulti_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mathOperationAverageAll_radio, (0,1), (1,2))
        grid.Add(self.mathOperationCombineAll_radio, (1,1), (1,2))
        grid.Add(self.mathOperationOverlayAll_radio, (2,1), (1,2))
        
        grid.Add(mathOperationSingle_label, (4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mathOperationNorm_radio, (4,1), (1,2))
        grid.Add(self.mathOperationCombine_radio, (5,1), (1,2))
        grid.Add(self.mathOperationSubtract_radio, (6,1), (1,2))
        grid.Add(self.mathOperationOverlay_radio, (7,1), (1,2))
        grid.Add(self.mathOperationMultiply_radio, (8,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mathMultiply_value, (8,2), flag=wx.EXPAND)
        
        grid.Add(mathSpectrumA_label, (10,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mathSpectrumA_choice, (10,1), (1,2))
        grid.Add(mathSpectrumB_label, (11,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.mathSpectrumB_choice, (11,1), (1,2))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeCropPanel(self):
        """Make controls for crop."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        cropLowMass_label = wx.StaticText(panel, -1, "Low mass:")
        self.cropLowMass_value = wx.TextCtrl(panel, -1, str(config.processing['crop']['lowMass']), size=(70, -1), validator=mwx.validator('floatPos'))
        cropLowMassUnits_label = wx.StaticText(panel, -1, "m/z")
        
        cropHighMass_label = wx.StaticText(panel, -1, "High mass:")
        self.cropHighMass_value = wx.TextCtrl(panel, -1, str(config.processing['crop']['highMass']), size=(70, -1), validator=mwx.validator('floatPos'))
        cropHighMassUnits_label = wx.StaticText(panel, -1, "m/z")
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(cropLowMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.cropLowMass_value, (0,1))
        grid.Add(cropLowMassUnits_label, (0,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(cropHighMass_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.cropHighMass_value, (1,1))
        grid.Add(cropHighMassUnits_label, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeBaselinePanel(self):
        """Make controls for baseline subtraction."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        baselinePrecision_label = wx.StaticText(panel, -1, "Precision:")
        self.baselinePrecision_slider = wx.Slider(panel, -1, config.processing['baseline']['precision'], 1, 100, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.baselinePrecision_slider.SetTickFreq(10,1)
        self.baselinePrecision_slider.Bind(wx.EVT_SCROLL, self.onBaselineChanged)
        
        baselineOffset_label = wx.StaticText(panel, -1, "Relative offset:")
        self.baselineOffset_slider = wx.Slider(panel, -1, config.processing['baseline']['offset']*100, 0, 100, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.baselineOffset_slider.SetTickFreq(10,1)
        self.baselineOffset_slider.Bind(wx.EVT_SCROLL, self.onBaselineChanged)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(baselinePrecision_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.baselinePrecision_slider, (0,1))
        grid.Add(baselineOffset_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.baselineOffset_slider, (1,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSmoothingPanel(self):
        """Make controls for smoothing."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        smoothingMethod_label = wx.StaticText(panel, -1, "Method:")
        self.smoothingMethod_choice = wx.Choice(panel, -1, choices=['Moving Average', 'Gaussian', 'Savitzky-Golay'], size=(150, mwx.CHOICE_HEIGHT))
        self.smoothingMethod_choice.Select(0)
        if config.processing['smoothing']['method']=='GA':
            self.smoothingMethod_choice.Select(1)
        elif config.processing['smoothing']['method']=='SG':
            self.smoothingMethod_choice.Select(2)
        self.smoothingMethod_choice.Bind(wx.EVT_CHOICE, self.onSmoothingChanged)
        
        smoothingWindow_label = wx.StaticText(panel, -1, "Window size:")
        self.smoothingWindow_value = wx.TextCtrl(panel, -1, str(config.processing['smoothing']['windowSize']), size=(90, -1), validator=mwx.validator('floatPos'))
        smoothingWindowUnits_label = wx.StaticText(panel, -1, "m/z")
        self.smoothingWindow_value.Bind(wx.EVT_TEXT, self.onSmoothingChanged)
        
        smoothingCycles_label = wx.StaticText(panel, -1, "Cycles:")
        self.smoothingCycles_slider = wx.Slider(panel, -1, config.processing['smoothing']['cycles'], 1, 5, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.smoothingCycles_slider.SetTickFreq(1,1)
        self.smoothingCycles_slider.Bind(wx.EVT_SCROLL, self.onSmoothingChanged)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(smoothingMethod_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.smoothingMethod_choice, (0,1), (1,2))
        grid.Add(smoothingWindow_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.smoothingWindow_value, (1,1))
        grid.Add(smoothingWindowUnits_label, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(smoothingCycles_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.smoothingCycles_slider, (2,1), (1,2))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makePeakpickingPanel(self):
        """Make controls for peak picking."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        peakpickingSNThreshold_label = wx.StaticText(panel, -1, "S/N threshold:")
        self.peakpickingSNThreshold_value = mwx.scrollTextCtrl(panel, -1, str(config.processing['peakpicking']['snThreshold']), multiplier=0.1, limits=(1,100), digits=1, size=(70, -1), validator=mwx.validator('floatPos'))
        self.peakpickingSNThreshold_value.Bind(wx.EVT_TEXT, self.onPeakpickingChanged)
        
        peakpickingAbsIntThreshold_label = wx.StaticText(panel, -1, "Abs. intensity threshold:")
        self.peakpickingAbsIntThreshold_value = wx.TextCtrl(panel, -1, str(config.processing['peakpicking']['absIntThreshold']), size=(70, -1), validator=mwx.validator('floatPos'))
        self.peakpickingAbsIntThreshold_value.Bind(wx.EVT_TEXT, self.onPeakpickingChanged)
        
        peakpickingRelIntThreshold_label = wx.StaticText(panel, -1, "Rel. intensity threshold:")
        self.peakpickingRelIntThreshold_value = mwx.scrollTextCtrl(panel, -1, str(config.processing['peakpicking']['relIntThreshold']*100), multiplier=0.1, limits=(0.01,100), digits=3, size=(70, -1), validator=mwx.validator('floatPos'))
        self.peakpickingRelIntThreshold_value.Bind(wx.EVT_TEXT, self.onPeakpickingChanged)
        peakpickingRelIntThresholdUnits_label = wx.StaticText(panel, -1, "%")
        
        peakpickingHeight_label = wx.StaticText(panel, -1, "Picking height:")
        self.peakpickingHeight_slider = wx.Slider(panel, -1, config.processing['peakpicking']['pickingHeight']*100, 1, 100, size=(150, -1), style=mwx.SLIDER_STYLE)
        self.peakpickingHeight_slider.SetTickFreq(10,1)
        self.peakpickingHeight_slider.Bind(wx.EVT_SCROLL, self.onPeakpickingChanged)
        
        peakpickingBaseline_label = wx.StaticText(panel, -1, "Apply baseline:")
        self.peakpickingBaseline_check = wx.CheckBox(panel, -1, " See baseline panel")
        self.peakpickingBaseline_check.SetFont(wx.SMALL_FONT)
        self.peakpickingBaseline_check.SetValue(bool(config.processing['peakpicking']['baseline']))
        self.peakpickingBaseline_check.Bind(wx.EVT_CHECKBOX, self.onPeakpickingChanged)
        
        peakpickingSmoothing_label = wx.StaticText(panel, -1, "Apply smoothing:")
        self.peakpickingSmoothing_check = wx.CheckBox(panel, -1, " See smoothing panel")
        self.peakpickingSmoothing_check.SetFont(wx.SMALL_FONT)
        self.peakpickingSmoothing_check.SetValue(bool(config.processing['peakpicking']['smoothing']))
        self.peakpickingSmoothing_check.Bind(wx.EVT_CHECKBOX, self.onPeakpickingChanged)
        
        peakpickingDeisotoping_label = wx.StaticText(panel, -1, "Apply deisotoping:")
        self.peakpickingDeisotoping_check = wx.CheckBox(panel, -1, " See deisotoping panel")
        self.peakpickingDeisotoping_check.SetFont(wx.SMALL_FONT)
        self.peakpickingDeisotoping_check.SetValue(bool(config.processing['peakpicking']['deisotoping']))
        self.peakpickingDeisotoping_check.Bind(wx.EVT_CHECKBOX, self.onPeakpickingChanged)
        
        peakpickingRemoveShoulders_label = wx.StaticText(panel, -1, "Remove shoulder peaks:")
        peakpickingRemoveShoulders_label.SetToolTip(wx.ToolTip("For FTMS data only."))
        self.peakpickingRemoveShoulders_check = wx.CheckBox(panel, -1, "")
        self.peakpickingRemoveShoulders_check.SetValue(bool(config.processing['peakpicking']['removeShoulders']))
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(peakpickingSNThreshold_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingSNThreshold_value, (0,1))
        grid.Add(peakpickingAbsIntThreshold_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingAbsIntThreshold_value, (1,1))
        grid.Add(peakpickingRelIntThreshold_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingRelIntThreshold_value, (2,1))
        grid.Add(peakpickingRelIntThresholdUnits_label, (2,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(peakpickingHeight_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingHeight_slider, (3,1), (1,2))
        grid.Add(peakpickingBaseline_label, (4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingBaseline_check, (4,1), (1,2))
        grid.Add(peakpickingSmoothing_label, (5,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingSmoothing_check, (5,1), (1,2))
        grid.Add(peakpickingDeisotoping_label, (6,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingDeisotoping_check, (6,1), (1,2))
        grid.Add(peakpickingRemoveShoulders_label, (7,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakpickingRemoveShoulders_check, (7,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeDeisotopingPanel(self):
        """Make controls for charge calculations and deisotoping."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        deisotopingMaxCharge_label = wx.StaticText(panel, -1, "Maximum charge:")
        self.deisotopingMaxCharge_value = wx.TextCtrl(panel, -1, str(config.processing['deisotoping']['maxCharge']), size=(70, -1), validator=mwx.validator('int'))
        
        deisotopingMassTolerance_label = wx.StaticText(panel, -1, "Isotope mass tolerance:")
        self.deisotopingMassTolerance_value = wx.TextCtrl(panel, -1, str(config.processing['deisotoping']['massTolerance']), size=(70, -1), validator=mwx.validator('floatPos'))
        deisotopingMassToleranceUnits_label = wx.StaticText(panel, -1, "m/z")
        
        deisotopingIntTolerance_label = wx.StaticText(panel, -1, "Isotope intensity tolerance:")
        self.deisotopingIntTolerance_value = wx.TextCtrl(panel, -1, str(config.processing['deisotoping']['intTolerance']*100), size=(70, -1), validator=mwx.validator('floatPos'))
        deisotopingIntToleranceUnits_label = wx.StaticText(panel, -1, "%")
        
        deisotopingIsotopeShift_label = wx.StaticText(panel, -1, "Isotope mass shift:")
        self.deisotopingIsotopeShift_value = wx.TextCtrl(panel, -1, str(config.processing['deisotoping']['isotopeShift']), size=(70, -1), validator=mwx.validator('float'))
        self.deisotopingIsotopeShift_value.Bind(wx.EVT_TEXT, self.getParams)
        
        deisotopingRemoveIsotopes_label = wx.StaticText(panel, -1, "Remove isotopes:")
        self.deisotopingRemoveIsotopes_check = wx.CheckBox(panel, -1, "")
        self.deisotopingRemoveIsotopes_check.SetValue(bool(config.processing['deisotoping']['removeIsotopes']))
        
        deisotopingRemoveUnknown_label = wx.StaticText(panel, -1, "Remove unknown:")
        self.deisotopingRemoveUnknown_check = wx.CheckBox(panel, -1, "")
        self.deisotopingRemoveUnknown_check.SetValue(bool(config.processing['deisotoping']['removeUnknown']))
        
        deisotopingLabelEnvelopeTool_label = wx.StaticText(panel, -1, "Label envelope tool:")
        self.deisotopingLabelEnvelopeTool_choice = wx.Choice(panel, -1, choices=['1st Selected', 'Monoisotopic Mass', 'Envelope Centroid', 'All Isotopes'], size=(160, mwx.CHOICE_HEIGHT))
        self.deisotopingLabelEnvelopeTool_choice.Select(1)
        choices=['1st', 'monoisotope', 'centroid', 'isotopes']
        if config.processing['deisotoping']['labelEnvelope'] in choices:
            self.deisotopingLabelEnvelopeTool_choice.Select(choices.index(config.processing['deisotoping']['labelEnvelope']))
        self.deisotopingLabelEnvelopeTool_choice.Bind(wx.EVT_CHOICE, self.getParams)
        
        deisotopingEnvelopeIntensity_label = wx.StaticText(panel, -1, "Envelope intensity:")
        self.deisotopingEnvelopeIntensity_choice = wx.Choice(panel, -1, choices=['Envelope Maximum', 'Summed Isotopes', 'Averaged Isotopes'], size=(160, mwx.CHOICE_HEIGHT))
        self.deisotopingEnvelopeIntensity_choice.Select(0)
        choices=['maximum', 'sum', 'average']
        if config.processing['deisotoping']['envelopeIntensity'] in choices:
            self.deisotopingEnvelopeIntensity_choice.Select(choices.index(config.processing['deisotoping']['envelopeIntensity']))
        self.deisotopingEnvelopeIntensity_choice.Bind(wx.EVT_CHOICE, self.getParams)
        if config.processing['deisotoping']['labelEnvelope'] == 'isotopes':
            self.deisotopingEnvelopeIntensity_choice.Disable()
        
        deisotopingSetAsMonoisotopic_label = wx.StaticText(panel, -1, "Set labels as monoisotopes:")
        self.deisotopingSetAsMonoisotopic_check = wx.CheckBox(panel, -1, "")
        self.deisotopingSetAsMonoisotopic_check.SetValue(config.processing['deisotoping']['setAsMonoisotopic'])
        self.deisotopingSetAsMonoisotopic_check.Bind(wx.EVT_CHECKBOX, self.getParams)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(deisotopingMaxCharge_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingMaxCharge_value, (0,1))
        grid.Add(deisotopingMassTolerance_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingMassTolerance_value, (1,1))
        grid.Add(deisotopingMassToleranceUnits_label, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(deisotopingIntTolerance_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingIntTolerance_value, (2,1))
        grid.Add(deisotopingIntToleranceUnits_label, (2,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(deisotopingIsotopeShift_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingIsotopeShift_value, (3,1))
        grid.Add(deisotopingRemoveIsotopes_label, (4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingRemoveIsotopes_check, (4,1))
        grid.Add(deisotopingRemoveUnknown_label, (5,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingRemoveUnknown_check, (5,1))
        grid.Add(wx.StaticLine(panel), (6,0), (1,3), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(deisotopingLabelEnvelopeTool_label, (7,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingLabelEnvelopeTool_choice, (7,1), (1,2))
        grid.Add(deisotopingEnvelopeIntensity_label, (8,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingEnvelopeIntensity_choice, (8,1), (1,2))
        grid.Add(deisotopingSetAsMonoisotopic_label, (9,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deisotopingSetAsMonoisotopic_check, (9,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeDeconvolutionPanel(self):
        """Make controls for deconvolution."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        deconvolutionMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.deconvolutionMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.deconvolutionMassType_choice.Select(config.processing['deconvolution']['massType'])
        
        deconvolutionGroupWindow_label = wx.StaticText(panel, -1, "Grouping window:")
        self.deconvolutionGroupWindow_value = wx.TextCtrl(panel, -1, str(config.processing['deconvolution']['groupWindow']), size=(90, -1), validator=mwx.validator('floatPos'))
        deconvolutionGroupWindowUnits_label = wx.StaticText(panel, -1, "m/z")
        
        deconvolutionGroupPeaks_label = wx.StaticText(panel, -1, "Group peaks:")
        self.deconvolutionGroupPeaks_check = wx.CheckBox(panel, -1, "")
        self.deconvolutionGroupPeaks_check.SetValue(config.processing['deconvolution']['groupPeaks'])
        
        deconvolutionForceGroupWindow_label = wx.StaticText(panel, -1, "Force window:")
        self.deconvolutionForceGroupWindow_check = wx.CheckBox(panel, -1, "")
        self.deconvolutionForceGroupWindow_check.SetValue(config.processing['deconvolution']['forceGroupWindow'])
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(deconvolutionMassType_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deconvolutionMassType_choice, (0,1), (1,2))
        grid.Add(deconvolutionGroupPeaks_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deconvolutionGroupPeaks_check, (1,1))
        grid.Add(deconvolutionGroupWindow_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deconvolutionGroupWindow_value, (2,1))
        grid.Add(deconvolutionGroupWindowUnits_label, (2,2), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(deconvolutionForceGroupWindow_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.deconvolutionForceGroupWindow_check, (3,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeBatchPanel(self):
        """Make controls for batch processing."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.batchSwap_check = wx.CheckBox(panel, -1, "Swap data")
        self.batchMath_check = wx.CheckBox(panel, -1, "Math")
        self.batchCrop_check = wx.CheckBox(panel, -1, "Crop")
        self.batchBaseline_check = wx.CheckBox(panel, -1, "Baseline correction")
        self.batchSmoothing_check = wx.CheckBox(panel, -1, "Smoothing")
        self.batchPeakpicking_check = wx.CheckBox(panel, -1, "Peak Picking")
        self.batchDeisotoping_check = wx.CheckBox(panel, -1, "Deisotoping")
        self.batchDeconvolution_check = wx.CheckBox(panel, -1, "Deconvolution")
        
        self.batchPeakpicking_check.Bind(wx.EVT_CHECKBOX, self.onBatchChanged)
        
        self.makeDocumentsList(panel)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(self.batchSwap_check, (0,0))
        grid.Add(self.batchMath_check, (1,0))
        grid.Add(self.batchCrop_check, (2,0))
        grid.Add(self.batchBaseline_check, (3,0))
        grid.Add(self.batchSmoothing_check, (4,0))
        grid.Add(self.batchPeakpicking_check, (5,0))
        grid.Add(self.batchDeisotoping_check, (6,0))
        grid.Add(self.batchDeconvolution_check, (7,0))
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.batchDocumentsList, 1, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(grid, 0, wx.TOP|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
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
        
        stop_butt = wx.BitmapButton(panel, -1, images.lib['stopper'], style=wx.BORDER_NONE)
        stop_butt.Bind(wx.EVT_BUTTON, self.onStop)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.gauge, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(stop_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # fit layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND|wx.RIGHT|wx.LEFT|wx.BOTTOM, mwx.GAUGE_SPACE)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeDocumentsList(self, panel):
        """Make list for documents batch."""
        
        # init list
        self.batchDocumentsList = mwx.sortListCtrl(panel, -1, size=(251, 100), style=mwx.LISTCTRL_STYLE_MULTI)
        self.batchDocumentsList.SetFont(wx.SMALL_FONT)
        self.batchDocumentsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # make columns
        self.batchDocumentsList.InsertColumn(0, "document title", wx.LIST_FORMAT_LEFT)
        self.batchDocumentsList.SetColumnWidth(0, 268)
    # ----
    
    
    def onClose(self, evt):
        """Close panel."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        self.clearPreview()
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
            tool = 'peakpicking'
            if evt.GetId() == ID_processingMath:
                tool = 'math'
            elif evt.GetId() == ID_processingCrop:
                tool = 'crop'
            elif evt.GetId() == ID_processingBaseline:
                tool = 'baseline'
            elif evt.GetId() == ID_processingSmoothing:
                tool = 'smoothing'
            elif evt.GetId() == ID_processingPeakpicking:
                tool = 'peakpicking'
            elif evt.GetId() == ID_processingDeisotoping:
                tool = 'deisotoping'
            elif evt.GetId() == ID_processingDeconvolution:
                tool = 'deconvolution'
            elif evt.GetId() == ID_processingBatch:
                tool = 'batch'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        self.mainSizer.Hide(5)
        self.mainSizer.Hide(6)
        self.mainSizer.Hide(7)
        self.mainSizer.Hide(8)
        self.mainSizer.Hide(9)
        
        # hide presets button
        self.toolbar.Hide(10)
        
        # set icons off
        self.math_butt.SetBitmapLabel(images.lib['processingMathOff'])
        self.crop_butt.SetBitmapLabel(images.lib['processingCropOff'])
        self.baseline_butt.SetBitmapLabel(images.lib['processingBaselineOff'])
        self.smoothing_butt.SetBitmapLabel(images.lib['processingSmoothingOff'])
        self.peakpicking_butt.SetBitmapLabel(images.lib['processingPeakpickingOff'])
        self.deisotoping_butt.SetBitmapLabel(images.lib['processingDeisotopingOff'])
        self.deconvolution_butt.SetBitmapLabel(images.lib['processingDeconvolutionOff'])
        self.batch_butt.SetBitmapLabel(images.lib['processingBatchOff'])
        
        # clear preview
        self.clearPreview()
        
        # set panel
        if tool == 'math':
            self.SetTitle("Math Operations")
            self.mainSizer.Show(1)
            self.math_butt.SetBitmapLabel(images.lib['processingMathOn'])
            self.preview_butt.Enable(True)
            
        elif tool == 'crop':
            self.SetTitle("Crop")
            self.toolbar.Show(10)
            self.mainSizer.Show(2)
            self.crop_butt.SetBitmapLabel(images.lib['processingCropOn'])
            self.preview_butt.Enable(False)
            
        elif tool == 'baseline':
            self.SetTitle("Baseline Correction")
            self.toolbar.Show(10)
            self.mainSizer.Show(3)
            self.baseline_butt.SetBitmapLabel(images.lib['processingBaselineOn'])
            self.preview_butt.Enable(True)
            self.onBaselineChanged()
            
        elif tool == 'smoothing':
            self.SetTitle("Smoothing")
            self.toolbar.Show(10)
            self.mainSizer.Show(4)
            self.smoothing_butt.SetBitmapLabel(images.lib['processingSmoothingOn'])
            self.preview_butt.Enable(True)
            
        elif tool == 'peakpicking':
            self.SetTitle("Peak Picking")
            self.toolbar.Show(10)
            self.mainSizer.Show(5)
            self.peakpicking_butt.SetBitmapLabel(images.lib['processingPeakpickingOn'])
            self.preview_butt.Enable(False)
            self.onPeakpickingChanged()
            
        elif tool == 'deisotoping':
            self.SetTitle("Deisotoping")
            self.toolbar.Show(10)
            self.mainSizer.Show(6)
            self.deisotoping_butt.SetBitmapLabel(images.lib['processingDeisotopingOn'])
            self.preview_butt.Enable(False)
            
        elif tool == 'deconvolution':
            self.SetTitle("Deconvolution")
            self.toolbar.Show(10)
            self.mainSizer.Show(7)
            self.deconvolution_butt.SetBitmapLabel(images.lib['processingDeconvolutionOn'])
            self.preview_butt.Enable(False)
            
        elif tool == 'batch':
            self.SetTitle("Batch Processing")
            self.toolbar.Show(10)
            self.mainSizer.Show(8)
            self.batch_butt.SetBitmapLabel(images.lib['processingBatchOn'])
            self.preview_butt.Enable(False)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(9)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(9)
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
    
    
    def onPresets(self, evt):
        """Show presets."""
        
        # get presets
        presets = libs.presets['processing'].keys()
        presets.sort()
        
        # make menu
        self.presets_popup = wx.Menu()
        for name in presets:
            item = self.presets_popup.Append(-1, name)
            self.presets_popup.Bind(wx.EVT_MENU, self.onPresetsSelected, item)
        
        self.presets_popup.AppendSeparator()
        item = self.presets_popup.Append(-1, "Save as Presets...")
        self.presets_popup.Bind(wx.EVT_MENU, self.onPresetsSave, item)
        
        # popup menu
        self.PopupMenu(self.presets_popup)
        self.presets_popup.Destroy()
    # ----
    
    
    def onPresetsSelected(self, evt):
        """Load selected presets."""
        
        # get presets
        item = self.presets_popup.FindItemById(evt.GetId())
        presets = libs.presets['processing'][item.GetText()]
        
        # set crop
        self.cropLowMass_value.SetValue(str(presets['crop']['lowMass']))
        self.cropHighMass_value.SetValue(str(presets['crop']['highMass']))
        
        # set baseline
        self.baselinePrecision_slider.SetValue(presets['baseline']['precision'])
        self.baselineOffset_slider.SetValue(presets['baseline']['offset']*100)
        
        # set smoothing
        if presets['smoothing']['method'] == 'MA':
            self.smoothingMethod_choice.Select(0)
        elif presets['smoothing']['method'] == 'GA':
            self.smoothingMethod_choice.Select(1)
        else:
            self.smoothingMethod_choice.Select(2)
        
        self.smoothingWindow_value.SetValue(str(presets['smoothing']['windowSize']))
        self.smoothingCycles_slider.SetValue(presets['smoothing']['cycles'])
        
        # set peakpicking
        self.peakpickingSNThreshold_value.SetValue(str(presets['peakpicking']['snThreshold']))
        self.peakpickingAbsIntThreshold_value.SetValue(str(presets['peakpicking']['absIntThreshold']))
        self.peakpickingRelIntThreshold_value.SetValue(str(presets['peakpicking']['relIntThreshold']*100))
        self.peakpickingHeight_slider.SetValue(presets['peakpicking']['pickingHeight']*100)
        self.peakpickingBaseline_check.SetValue(bool(presets['peakpicking']['baseline']))
        self.peakpickingSmoothing_check.SetValue(bool(presets['peakpicking']['smoothing']))
        self.peakpickingDeisotoping_check.SetValue(bool(presets['peakpicking']['deisotoping']))
        self.peakpickingRemoveShoulders_check.SetValue(bool(presets['peakpicking']['removeShoulders']))
        
        # set deisotoping
        self.deisotopingMaxCharge_value.SetValue(str(presets['deisotoping']['maxCharge']))
        self.deisotopingMassTolerance_value.SetValue(str(presets['deisotoping']['massTolerance']))
        self.deisotopingIntTolerance_value.SetValue(str(presets['deisotoping']['intTolerance']*100))
        self.deisotopingIsotopeShift_value.SetValue(str(presets['deisotoping']['isotopeShift']))
        self.deisotopingRemoveIsotopes_check.SetValue(bool(presets['deisotoping']['removeIsotopes']))
        self.deisotopingRemoveUnknown_check.SetValue(bool(presets['deisotoping']['removeUnknown']))
        self.deisotopingSetAsMonoisotopic_check.SetValue(bool(presets['deisotoping']['setAsMonoisotopic']))
        
        choices=['1st', 'monoisotope', 'centroid', 'isotopes']
        if presets['deisotoping']['labelEnvelope'] in choices:
            self.deisotopingLabelEnvelopeTool_choice.Select(choices.index(presets['deisotoping']['labelEnvelope']))
        else:
            self.deisotopingLabelEnvelopeTool_choice.Select(1)
        
        choices=['maximum', 'sum', 'average']
        if presets['deisotoping']['envelopeIntensity'] in choices:
            self.deisotopingEnvelopeIntensity_choice.Select(choices.index(presets['deisotoping']['envelopeIntensity']))
        else:
            self.deisotopingEnvelopeIntensity_choice.Select(0)
        
        # set deconvolution
        self.deconvolutionMassType_choice.Select(presets['deconvolution']['massType'])
        self.deconvolutionGroupWindow_value.SetValue(str(presets['deconvolution']['groupWindow']))
        self.deconvolutionGroupPeaks_check.SetValue(bool(presets['deconvolution']['groupPeaks']))
        self.deconvolutionForceGroupWindow_check.SetValue(bool(presets['deconvolution']['forceGroupWindow']))
        
        # batch processing
        self.batchSwap_check.SetValue(bool(presets['batch']['swap']))
        self.batchMath_check.SetValue(bool(presets['batch']['math']))
        self.batchCrop_check.SetValue(bool(presets['batch']['crop']))
        self.batchBaseline_check.SetValue(bool(presets['batch']['baseline']))
        self.batchSmoothing_check.SetValue(bool(presets['batch']['smoothing']))
        self.batchPeakpicking_check.SetValue(bool(presets['batch']['peakpicking']))
        self.batchDeisotoping_check.SetValue(bool(presets['batch']['deisotoping']))
        self.batchDeconvolution_check.SetValue(bool(presets['batch']['deconvolution']))
        
        # readback all params
        self.getParams()
        
        # update gui
        self.onMathChanged()
        self.onBaselineChanged()
        self.onPeakpickingChanged()
    # ----
    
    
    def onPresetsSave(self, evt):
        """Save current params as presets."""
        
        # check params
        if not self.getParams():
            wx.Bell()
            return
        
        # get presets name
        dlg = dlgPresetsName(self)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # save presets
        libs.presets['processing'][name] = copy.deepcopy(config.processing)
        libs.savePresets()
    # ----
    
    
    def onMathChanged(self, evt=None):
        """Disable / enable related items in math panel."""
        
        # disable / enable items
        if self.mathOperationAverageAll_radio.GetValue():
            self.mathSpectrumB_choice.Disable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationCombineAll_radio.GetValue():
            self.mathSpectrumB_choice.Disable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationOverlayAll_radio.GetValue():
            self.mathSpectrumB_choice.Disable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationNorm_radio.GetValue():
            self.mathSpectrumB_choice.Disable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationCombine_radio.GetValue():
            self.mathSpectrumB_choice.Enable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationOverlay_radio.GetValue():
            self.mathSpectrumB_choice.Enable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationSubtract_radio.GetValue():
            self.mathSpectrumB_choice.Enable()
            self.mathMultiply_value.Disable()
        elif self.mathOperationMultiply_radio.GetValue():
            self.mathSpectrumB_choice.Disable()
            self.mathMultiply_value.Enable()
        
        # update batch processing options
        self.onBatchChanged()
        
        # clear tmp spectrum
        self.clearPreview()
    # ----
    
    
    def onBaselineChanged(self, evt=None):
        """Show baseline while params are changing."""
        
        # check tool
        if self.currentTool != 'baseline':
            return
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            return
        
        # get params
        if not self.getParams():
            return
        
        # get baseline
        baseline = self.currentDocument.spectrum.baseline(
            window = (1./config.processing['baseline']['precision']),
            offset = config.processing['baseline']['offset']
        )
        
        # make tmp spectrum
        points = []
        for x in baseline:
            points.append([x[0], x[1]])
        
        # send tmp spectrum to plot canvas
        self.previewData = points
        self.parent.updateTmpSpectrum(points)
    # ----
    
    
    def onSmoothingChanged(self, evt=None):
        """Clear smoothing preview while params changed."""
        
        # check tool
        if self.currentTool != 'smoothing':
            return
        
        # clear preview
        self.clearPreview()
    # ----
    
    
    def onPeakpickingChanged(self, evt=None):
        """Show intensity threshold while params are changing."""
        
        # update batch processing options
        self.onBatchChanged()
        
        # check tool
        if self.currentTool != 'peakpicking':
            return
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            return
        
        # get params
        if not self.getParams():
            return
        
        # get threshold line
        points = self.makeThresholdLine()
        
        # send tmp spectrum to plot canvas
        self.previewData = points
        self.parent.updateTmpSpectrum(points)
    # ----
    
    
    def onBatchChanged(self, evt=None):
        """Check math operation, double baseline correction, smoothing and deisotoping."""
        
        # enable tools
        self.batchMath_check.Enable(True)
        self.batchBaseline_check.Enable(True)
        self.batchSmoothing_check.Enable(True)
        self.batchDeisotoping_check.Enable(True)
        
        # disable math if multi-document math operation is selected
        if self.mathOperationAverageAll_radio.GetValue() \
        or self.mathOperationCombineAll_radio.GetValue() \
        or self.mathOperationOverlayAll_radio.GetValue():
            self.batchMath_check.SetValue(False)
            self.batchMath_check.Enable(False)
        
        # check processing if peak picking is turned on
        if self.batchPeakpicking_check.GetValue():
            
            if self.peakpickingBaseline_check.GetValue():
                self.batchBaseline_check.SetValue(False)
                self.batchBaseline_check.Enable(False)
            
            if self.peakpickingSmoothing_check.GetValue():
                self.batchSmoothing_check.SetValue(False)
                self.batchSmoothing_check.Enable(False)
            
            if self.peakpickingDeisotoping_check.GetValue():
                self.batchDeisotoping_check.SetValue(False)
                self.batchDeisotoping_check.Enable(False)
    # ----
    
    
    def onPreview(self, evt=None):
        """Recalculate data and show preview."""
        
        # check processing
        if self.processing:
            return
        
        # clear preview
        self.clearPreview()
        
        # get all params
        if not self.getParams():
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.preview_butt.Enable(False)
        self.apply_butt.Enable(False)
        
        # show preview
        if self.currentTool == 'math':
            self.processing = threading.Thread(target=self.runPreviewMath)
        elif self.currentTool == 'baseline':
            self.processing = threading.Thread(target=self.runPreviewBaseline)
        elif self.currentTool == 'smoothing':
            self.processing = threading.Thread(target=self.runPreviewSmoothing)
        else:
            return
        
        # pulse gauge while working
        self.processing.start()
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # send tmp spectrum to plot canvas
        self.parent.updateTmpSpectrum(self.previewData)
        
        # hide processing gauge
        self.onProcessing(False)
        self.preview_butt.Enable(True)
        self.apply_butt.Enable(True)
    # ----
    
    
    def onApply(self, evt=None):
        """Apply processing to the data."""
        
        # check processing
        if self.processing:
            return
        
        # check document
        if self.currentDocument == None and not self.currentTool in ('math', 'batch'):
            wx.Bell()
            return
        
        # clear tmp spectrum
        self.clearPreview()
        
        # get all params
        if not self.getParams():
            return
        
        # check data
        if self.currentTool in ('baseline', 'smoothing', 'peakpicking') \
            and not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        if self.currentTool in ('deisotoping', 'deconvolution') \
            and not self.currentDocument.spectrum.haspeaks():
            wx.Bell()
            return
        if self.currentTool in ('peakpicking', 'deisotoping') \
            and not self.checkIsotopeMassTolerance():
            return
        if self.currentTool == 'deconvolution' \
            and not self.checkChargedPeaks():
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.preview_butt.Enable(False)
        self.apply_butt.Enable(False)
        
        # process data
        if self.currentTool == 'math':
            self.processing = threading.Thread(target=self.runApplyMath)
        elif self.currentTool == 'crop':
            self.processing = threading.Thread(target=self.runApplyCrop)
        elif self.currentTool == 'baseline':
            self.processing = threading.Thread(target=self.runApplyBaseline)
        elif self.currentTool == 'smoothing':
            self.processing = threading.Thread(target=self.runApplySmoothing)
        elif self.currentTool == 'peakpicking':
            self.processing = threading.Thread(target=self.runApplyPeakpicking)
        elif self.currentTool == 'deisotoping':
            self.processing = threading.Thread(target=self.runApplyDeisotoping)
        elif self.currentTool == 'deconvolution':
            self.processing = threading.Thread(target=self.runApplyDeconvolution)
        elif self.currentTool == 'batch':
            self.processing = threading.Thread(target=self.runApplyBatch)
        else:
            return
        
        # pulse gauge while working
        self.processing.start()
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        if self.currentTool == 'batch':
            self.parent.onDocumentChangedMulti(indexes=self.batchChanged, items=('spectrum', 'notations'))
        elif self.currentTool == 'math' and config.processing['math']['operation'] in ('normalize', 'combine', 'overlay', 'subtract', 'multiply'):
            self.parent.onDocumentChanged(items=('spectrum', 'notations'))
        elif self.currentTool == 'deconvolution':
            pass
        else:
            self.parent.onDocumentChanged(items=('spectrum', 'notations'))
        
        # hide processing gauge
        self.onProcessing(False)
        self.apply_butt.Enable(True)
        if self.currentTool in ('math', 'baseline', 'smoothing'):
            self.preview_butt.Enable(True)
        
        # update tmp spectrum
        if self.currentTool == 'baseline':
            self.onBaselineChanged()
        elif self.currentTool == 'peakpicking':
            self.onPeakpickingChanged()
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set document
        self.currentDocument = document
        self.updateCurrentDocument()
        
        # clear preview
        self.clearPreview()
        
        # update gui
        self.onBaselineChanged()
        self.onPeakpickingChanged()
    # ----
    
    
    def getParams(self, evt=None):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            # math operations
            if self.mathOperationAverageAll_radio.GetValue():
                config.processing['math']['operation'] = 'averageall'
            elif self.mathOperationCombineAll_radio.GetValue():
                config.processing['math']['operation'] = 'combineall'
            elif self.mathOperationOverlayAll_radio.GetValue():
                config.processing['math']['operation'] = 'overlayall'
            elif self.mathOperationNorm_radio.GetValue():
                config.processing['math']['operation'] = 'normalize'
            elif self.mathOperationCombine_radio.GetValue():
                config.processing['math']['operation'] = 'combine'
            elif self.mathOperationOverlay_radio.GetValue():
                config.processing['math']['operation'] = 'overlay'
            elif self.mathOperationSubtract_radio.GetValue():
                config.processing['math']['operation'] = 'subtract'
            elif self.mathOperationMultiply_radio.GetValue():
                config.processing['math']['operation'] = 'multiply'
            
            config.processing['math']['multiplier'] = float(self.mathMultiply_value.GetValue())
            
            # crop
            config.processing['crop']['lowMass'] = float(self.cropLowMass_value.GetValue())
            config.processing['crop']['highMass'] = float(self.cropHighMass_value.GetValue())
            
            # baseline
            config.processing['baseline']['precision'] = float(self.baselinePrecision_slider.GetValue())
            config.processing['baseline']['offset'] = float(self.baselineOffset_slider.GetValue())/100.
            
            # smoothing
            config.processing['smoothing']['windowSize'] = float(self.smoothingWindow_value.GetValue())
            config.processing['smoothing']['cycles'] = int(self.smoothingCycles_slider.GetValue())
            
            config.processing['smoothing']['method'] = 'MA'
            if self.smoothingMethod_choice.GetStringSelection() == 'Gaussian':
                config.processing['smoothing']['method'] = 'GA'
            elif self.smoothingMethod_choice.GetStringSelection() == 'Savitzky-Golay':
                config.processing['smoothing']['method'] = 'SG'
            
            # peak picking
            config.processing['peakpicking']['snThreshold'] = float(self.peakpickingSNThreshold_value.GetValue())
            config.processing['peakpicking']['absIntThreshold'] = float(self.peakpickingAbsIntThreshold_value.GetValue())
            config.processing['peakpicking']['relIntThreshold'] = float(self.peakpickingRelIntThreshold_value.GetValue())/100.
            config.processing['peakpicking']['pickingHeight'] = float(self.peakpickingHeight_slider.GetValue())/100.
            config.processing['peakpicking']['baseline'] = bool(self.peakpickingBaseline_check.GetValue())
            config.processing['peakpicking']['smoothing'] = bool(self.peakpickingSmoothing_check.GetValue())
            config.processing['peakpicking']['deisotoping'] = bool(self.peakpickingDeisotoping_check.GetValue())
            config.processing['peakpicking']['removeShoulders'] = bool(self.peakpickingRemoveShoulders_check.GetValue())
            
            # deisotoping
            config.processing['deisotoping']['maxCharge'] = int(self.deisotopingMaxCharge_value.GetValue())
            config.processing['deisotoping']['massTolerance'] = float(self.deisotopingMassTolerance_value.GetValue())
            config.processing['deisotoping']['intTolerance'] = float(self.deisotopingIntTolerance_value.GetValue())/100.
            config.processing['deisotoping']['isotopeShift'] = float(self.deisotopingIsotopeShift_value.GetValue())
            config.processing['deisotoping']['removeIsotopes'] = bool(self.deisotopingRemoveIsotopes_check.GetValue())
            config.processing['deisotoping']['removeUnknown'] = bool(self.deisotopingRemoveUnknown_check.GetValue())
            config.processing['deisotoping']['setAsMonoisotopic'] = bool(self.deisotopingSetAsMonoisotopic_check.GetValue())
            
            labelEnvelope = self.deisotopingLabelEnvelopeTool_choice.GetStringSelection()
            if labelEnvelope == '1st Selected':
                config.processing['deisotoping']['labelEnvelope'] = '1st'
            elif labelEnvelope == 'Monoisotopic Mass':
                config.processing['deisotoping']['labelEnvelope'] = 'monoisotope'
            elif labelEnvelope == 'Envelope Centroid':
                config.processing['deisotoping']['labelEnvelope'] = 'centroid'
            elif labelEnvelope == 'All Isotopes':
                config.processing['deisotoping']['labelEnvelope'] = 'isotopes'
            
            envelopeIntensity = self.deisotopingEnvelopeIntensity_choice.GetStringSelection()
            if envelopeIntensity == 'Envelope Maximum':
                config.processing['deisotoping']['envelopeIntensity'] = 'maximum'
            elif envelopeIntensity == 'Summed Isotopes':
                config.processing['deisotoping']['envelopeIntensity'] = 'sum'
            elif envelopeIntensity == 'Averaged Isotopes':
                config.processing['deisotoping']['envelopeIntensity'] = 'average'
            
            if config.processing['deisotoping']['labelEnvelope'] == 'isotopes':
                self.deisotopingEnvelopeIntensity_choice.Disable()
            else:
                self.deisotopingEnvelopeIntensity_choice.Enable()
            
            if config.processing['deisotoping']['maxCharge'] == 0:
                wx.Bell()
                return False
            
            # deconvolution
            config.processing['deconvolution']['massType'] = 0
            if self.deconvolutionMassType_choice.GetStringSelection() == 'Average':
                config.processing['deconvolution']['massType'] = 1
            
            config.processing['deconvolution']['groupWindow'] = float(self.deconvolutionGroupWindow_value.GetValue())
            config.processing['deconvolution']['groupPeaks'] = bool(self.deconvolutionGroupPeaks_check.GetValue())
            config.processing['deconvolution']['forceGroupWindow'] = bool(self.deconvolutionForceGroupWindow_check.GetValue())
            
            # batch processing
            config.processing['batch']['swap'] = bool(self.batchSwap_check.GetValue())
            config.processing['batch']['math'] = bool(self.batchMath_check.GetValue())
            config.processing['batch']['crop'] = bool(self.batchCrop_check.GetValue())
            config.processing['batch']['baseline'] = bool(self.batchBaseline_check.GetValue())
            config.processing['batch']['smoothing'] = bool(self.batchSmoothing_check.GetValue())
            config.processing['batch']['peakpicking'] = bool(self.batchPeakpicking_check.GetValue())
            config.processing['batch']['deisotoping'] = bool(self.batchDeisotoping_check.GetValue())
            config.processing['batch']['deconvolution'] = bool(self.batchDeconvolution_check.GetValue())
            
        # ring error bell if error
        except:
            wx.Bell()
            return False
        
        # apply isotope shift to spectrum canvas
        distance = mspy.ISOTOPE_DISTANCE + config.processing['deisotoping']['isotopeShift']
        self.parent.spectrumPanel.spectrumCanvas.setProperties(isotopeDistance=distance)
        
        return True
    # ----
    
    
    def updateCurrentDocument(self):
        """Show selected document title as Spectrum A."""
        
        # clear choice
        self.mathSpectrumA_choice.Clear()
        
        # check document
        if self.currentDocument == None:
            self.mathSpectrumA_choice.Append('None')
            self.mathSpectrumA_choice.Select(0)
            return
        
        # show selected document
        for x, document in enumerate(self.parent.documents):
            if document is self.currentDocument:
                title = '#%d: %s' % (x+1, document.title)
                self.mathSpectrumA_choice.Append(title)
                self.mathSpectrumA_choice.Select(0)
                return
    # ----
    
    
    def updateAvailableDocuments(self):
        """Update list of documents in math and batch panels."""
        
        # check processing
        if self.processing:
            return
        
        # update available documents in math panel
        self.mathSpectrumB_choice.Clear()
        self.mathSpectrumB_choice.Append('None')
        
        for x, document in enumerate(self.parent.documents):
            title = '#%d: %s' % (x+1, document.title)
            self.mathSpectrumB_choice.Append(title)
        
        self.mathSpectrumB_choice.Select(0)
        
        # update available documents in batch panel
        documentsMap = []
        for x, document in enumerate(self.parent.documents):
            documentsMap.append([document.title, document.colour])
        
        self.batchDocumentsList.DeleteAllItems()
        self.batchDocumentsList.setDataMap(documentsMap)
        
        row = 0
        for title, colour in documentsMap:
            self.batchDocumentsList.InsertStringItem(row, title)
            self.batchDocumentsList.SetItemData(row, row)
            self.batchDocumentsList.SetItemTextColour(row, colour)
            row += 1
        self.batchDocumentsList.updateItemsBackground()
    # ----
    
    
    def runPreviewMath(self):
        """Preview operations results."""
        
        # run task
        try:
            
            # get spectrum A
            if config.processing['math']['operation'] in ('averageall', 'combineall', 'overlayall'):
                self.previewData = numpy.array([])
            elif not self.currentDocument:
                wx.Bell()
                return
            else:
                self.previewData = self.currentDocument.spectrum.profile
            
            # get spectrum B
            if config.processing['math']['operation'] in ('combine', 'overlay', 'subtract'):
                title = self.mathSpectrumB_choice.GetStringSelection()
                if title != 'None':
                    index = int(title.split(':')[0][1:])
                    spectrumB = self.parent.documents[index-1].spectrum.profile
                else:
                    wx.Bell()
                    return
            
            # process spectrum
            if config.processing['math']['operation'] == 'normalize':
                self.previewData = mspy.normalize(self.previewData)
                self.previewData = mspy.multiply(self.previewData, y=100)
            
            elif config.processing['math']['operation'] == 'combine':
                self.previewData = mspy.combine(self.previewData, spectrumB)
            
            elif config.processing['math']['operation'] == 'overlay':
                self.previewData = mspy.overlay(self.previewData, spectrumB)
            
            elif config.processing['math']['operation'] == 'subtract':
                self.previewData = mspy.subtract(self.previewData, spectrumB)
            
            elif config.processing['math']['operation'] == 'multiply':
                self.previewData = mspy.multiply(self.previewData, y=config.processing['math']['multiplier'])
            
            elif config.processing['math']['operation'] == 'averageall':
                count = 0
                for item in self.parent.documents:
                    if item.visible:
                        self.previewData = mspy.combine(self.previewData, item.spectrum.profile)
                        count += 1
                self.previewData = mspy.multiply(self.previewData, y=1./count)
            
            elif config.processing['math']['operation'] == 'combineall':
                for item in self.parent.documents:
                    if item.visible:
                        self.previewData = mspy.combine(self.previewData, item.spectrum.profile)
            
            elif config.processing['math']['operation'] == 'overlayall':
                for item in self.parent.documents:
                    if item.visible:
                        self.previewData = mspy.overlay(self.previewData, item.spectrum.profile)
            
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def runPreviewBaseline(self):
        """Preview smoothing results."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        
        # run task
        try:
            
            # get baseline
            baseline = self.currentDocument.spectrum.baseline(
                window = (1./config.processing['baseline']['precision']),
                offset = config.processing['baseline']['offset']
            )
            
            # correct baseline
            self.previewData = mspy.subbase(
                signal = self.currentDocument.spectrum.profile,
                baseline = baseline
            )
            
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def runPreviewSmoothing(self):
        """Preview smoothing results."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        
        # run task
        try:
            
            # smooth data
            self.previewData = mspy.smooth(
                signal = self.currentDocument.spectrum.profile,
                method = config.processing['smoothing']['method'],
                window = config.processing['smoothing']['windowSize'],
                cycles = config.processing['smoothing']['cycles']
            )
            
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def runApplySwap(self, batch=False):
        """Crop data."""
        
        # check current spectrum
        if not self.currentDocument:
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # swap spectrum data
            self.currentDocument.spectrum.swap()
            
            # remove notations
            del self.currentDocument.annotations[:]
            for sequence in self.currentDocument.sequences:
                del sequence.matches[:]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyMath(self, batch=False):
        """Math operations."""
        
        # run task
        try:
            
            # apply math to multiple documents
            if config.processing['math']['operation'] in ('averageall', 'combineall', 'overlayall'):
                
                # make document
                docData = doc.document()
                docData.format = 'mSD'
                docData.path = ''
                docData.dirty = True
                docData.backup(None)
                
                # average spectra
                if config.processing['math']['operation'] == 'averageall':
                    docData.title = 'Averaged Spectra'
                    docData.notes = 'Averaged Spectra:\n'
                    count = 0
                    for item in self.parent.documents:
                        if item.visible:
                            docData.spectrum.combine(item.spectrum)
                            docData.notes += '- '+item.title+'\n'
                            count += 1
                    docData.spectrum.multiply(1./count)
                
                # combine spectra
                elif config.processing['math']['operation'] == 'combineall':
                    docData.title = 'Combined Spectra'
                    docData.notes = 'Combined Spectra:\n'
                    for item in self.parent.documents:
                        if item.visible:
                            docData.spectrum.combine(item.spectrum)
                            docData.notes += '- '+item.title+'\n'
                
                # overlay spectra
                elif config.processing['math']['operation'] == 'overlayall':
                    docData.title = 'Overlaid Spectra'
                    docData.notes = 'Overlaid Spectra:\n'
                    for item in self.parent.documents:
                        if item.visible:
                            docData.spectrum.overlay(item.spectrum)
                            docData.notes += '- '+item.title+'\n'
                
                # append new document
                self.parent.onDocumentNew(document=docData, select=False)
            
            # apply math on single document
            elif config.processing['math']['operation'] in ('normalize', 'combine', 'overlay', 'subtract', 'multiply'):
                
                # check current spectrum
                if not self.currentDocument:
                    wx.Bell()
                    return
                
                # get spectrum B
                if config.processing['math']['operation'] in ('combine', 'overlay', 'subtract'):
                    title = self.mathSpectrumB_choice.GetStringSelection()
                    if title != 'None':
                        index = int(title.split(':')[0][1:])
                        spectrumB = self.parent.documents[index-1].spectrum
                    else:
                        wx.Bell()
                        return
                
                # backup document
                if not batch:
                    self.currentDocument.backup(('spectrum', 'notations'))
                
                # process spectrum
                if config.processing['math']['operation'] == 'normalize':
                    self.currentDocument.spectrum.normalize()
                
                elif config.processing['math']['operation'] == 'combine':
                    self.currentDocument.spectrum.combine(spectrumB)
                
                elif config.processing['math']['operation'] == 'overlay':
                    self.currentDocument.spectrum.overlay(spectrumB)
                
                elif config.processing['math']['operation'] == 'subtract':
                    self.currentDocument.spectrum.subtract(spectrumB)
                
                elif config.processing['math']['operation'] == 'multiply':
                    self.currentDocument.spectrum.multiply(y=config.processing['math']['multiplier'])
                
                # remove notations
                del self.currentDocument.annotations[:]
                for sequence in self.currentDocument.sequences:
                    del sequence.matches[:]
        
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyCrop(self, batch=False):
        """Crop data."""
        
        # check current spectrum
        if not self.currentDocument:
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # crop spectrum
            self.currentDocument.spectrum.crop(config.processing['crop']['lowMass'], config.processing['crop']['highMass'])
            
            # crop annotations
            indexes = []
            for x, annotation in enumerate(self.currentDocument.annotations):
                if annotation.mz < config.processing['crop']['lowMass'] or annotation.mz > config.processing['crop']['highMass']:
                    indexes.append(x)
            indexes.reverse()
            for x in indexes:
                del self.currentDocument.annotations[x]
            
            # crop matches
            for sequence in self.currentDocument.sequences:
                indexes = []
                for x, match in enumerate(sequence.matches):
                    if match.mz < config.processing['crop']['lowMass'] or match.mz > config.processing['crop']['highMass']:
                        indexes.append(x)
                indexes.reverse()
                for x in indexes:
                    del sequence.matches[x]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyBaseline(self, batch=False):
        """Subtract baseline."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # correct baseline
            self.currentDocument.spectrum.subbase(
                window = (1./config.processing['baseline']['precision']),
                offset = config.processing['baseline']['offset']
            )
            
            # remove notations
            del self.currentDocument.annotations[:]
            for sequence in self.currentDocument.sequences:
                del sequence.matches[:]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplySmoothing(self, batch=False):
        """Smooth data."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # smooth spectrum
            self.currentDocument.spectrum.smooth(
                method = config.processing['smoothing']['method'],
                window = config.processing['smoothing']['windowSize'],
                cycles = config.processing['smoothing']['cycles']
            )
            
            # remove notations
            del self.currentDocument.annotations[:]
            for sequence in self.currentDocument.sequences:
                del sequence.matches[:]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyPeakpicking(self, batch=False):
        """Find peaks."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # get baseline window
            baselineWindow = 1.
            if config.processing['peakpicking']['baseline']:
                baselineWindow = 1./config.processing['baseline']['precision']
            
            # get smoothing method
            smoothMethod = None
            if config.processing['peakpicking']['smoothing']:
                smoothMethod = config.processing['smoothing']['method']
            
            # label spectrum
            self.currentDocument.spectrum.labelscan(
                pickingHeight = config.processing['peakpicking']['pickingHeight'],
                absThreshold = config.processing['peakpicking']['absIntThreshold'],
                relThreshold = config.processing['peakpicking']['relIntThreshold'],
                snThreshold = config.processing['peakpicking']['snThreshold'],
                baselineWindow = baselineWindow,
                baselineOffset = config.processing['baseline']['offset'],
                smoothMethod = smoothMethod,
                smoothWindow = config.processing['smoothing']['windowSize'],
                smoothCycles = config.processing['smoothing']['cycles']
            )
            
            # remove shoulder peaks
            if config.processing['peakpicking']['removeShoulders']:
                self.currentDocument.spectrum.remshoulders(window=2.5, relThreshold=0.05, fwhm=0.01)
            
            # find isotopes and calculate charges
            if config.processing['peakpicking']['deisotoping']:
                self.currentDocument.spectrum.deisotope(
                    maxCharge = config.processing['deisotoping']['maxCharge'],
                    mzTolerance = config.processing['deisotoping']['massTolerance'],
                    intTolerance = config.processing['deisotoping']['intTolerance'],
                    isotopeShift = config.processing['deisotoping']['isotopeShift']
                )
                
                # remove isotopes
                if config.processing['deisotoping']['removeIsotopes']:
                    self.currentDocument.spectrum.remisotopes()
                
                # remove unknown
                if config.processing['deisotoping']['removeUnknown']:
                    self.currentDocument.spectrum.remuncharged()
            
            # remove notations
            del self.currentDocument.annotations[:]
            for sequence in self.currentDocument.sequences:
                del sequence.matches[:]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyDeisotoping(self, batch=False):
        """Calculate charges for peaks."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.haspeaks():
            wx.Bell()
            return
        
        # run task
        try:
            
            # backup document
            if not batch:
                self.currentDocument.backup(('spectrum', 'notations'))
            
            # find isotopes and calculate charges
            self.currentDocument.spectrum.deisotope(
                maxCharge = config.processing['deisotoping']['maxCharge'],
                mzTolerance = config.processing['deisotoping']['massTolerance'],
                intTolerance = config.processing['deisotoping']['intTolerance'],
                isotopeShift = config.processing['deisotoping']['isotopeShift']
            )
            
            # remove isotopes
            if config.processing['deisotoping']['removeIsotopes']:
                self.currentDocument.spectrum.remisotopes()
            
            # remove unknown
            if config.processing['deisotoping']['removeUnknown']:
                self.currentDocument.spectrum.remuncharged()
            
            # remove notations
            del self.currentDocument.annotations[:]
            for sequence in self.currentDocument.sequences:
                del sequence.matches[:]
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyDeconvolution(self, batch=False):
        """Recalculate peak list to singly-charged and make new document."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.haspeaks():
            wx.Bell()
            return
        
        # run task
        try:
            
            # copy current document
            docData = copy.deepcopy(self.currentDocument)
            docData.title += ' - Deconvoluted'
            docData.format = 'mSD'
            docData.path = ''
            docData.dirty = True
            docData.backup(None)
            
            # remove notations
            del docData.annotations[:]
            for sequence in docData.sequences:
                del sequence.matches[:]
            
            # deconvolute peaklist
            docData.spectrum.deconvolute(massType=config.processing['deconvolution']['massType'])
            
            # group peaks
            if config.processing['deconvolution']['groupPeaks']:
                docData.spectrum.consolidate(
                    window = config.processing['deconvolution']['groupWindow'],
                    forceWindow = config.processing['deconvolution']['forceGroupWindow']
                )
            
            # append new document
            self.parent.onDocumentNew(document=docData, select=False)
            
        # task canceled
        except mspy.ForceQuit:
            if batch: mspy.stop()
            return
    # ----
    
    
    def runApplyBatch(self):
        """Batch process selected documents."""
        
        self.batchChanged = []
        current = self.currentDocument
        
        # run task
        try:
            
            # get selected documents
            documents = []
            for x in self.batchDocumentsList.getSelected():
                docIndex = self.batchDocumentsList.GetItemData(x)
                documents.append(docIndex)
            
            # process selected documents
            for docIndex in documents:
                
                # select document
                self.currentDocument = self.parent.documents[docIndex]
                self.batchChanged.append(docIndex)
                
                # backup document
                self.currentDocument.backup(('spectrum', 'notations'))
                
                # apply swap
                if self.batchSwap_check.GetValue():
                    self.runApplySwap(batch=True)
                
                # apply math
                if self.batchMath_check.GetValue():
                    self.runApplyMath(batch=True)
                
                # apply crop
                if self.batchCrop_check.GetValue():
                    self.runApplyCrop(batch=True)
                
                # apply baseline correction
                if self.batchBaseline_check.GetValue():
                    self.runApplyBaseline(batch=True)
                
                # apply smoothing
                if self.batchSmoothing_check.GetValue():
                    self.runApplySmoothing(batch=True)
                
                # apply peak picking
                if self.batchPeakpicking_check.GetValue():
                    self.runApplyPeakpicking(batch=True)
                
                # apply deisotoping
                if self.batchDeisotoping_check.GetValue():
                    self.runApplyDeisotoping(batch=True)
                
                # apply deconvolution
                if self.batchDeconvolution_check.GetValue():
                    self.runApplyDeconvolution(batch=True)
            
            # select original document
            self.currentDocument = current
            
        # task canceled
        except mspy.ForceQuit:
            self.currentDocument = current
            return
    # ----
    
    
    def checkIsotopeMassTolerance(self):
        """Check isotope mass tolerance for cuurent max charge."""
        
        # get max tolerance
        z = float(abs(config.processing['deisotoping']['maxCharge']))
        if z == 1:
            return True
        else:
            maxTol = (1.00287+config.processing['deisotoping']['isotopeShift'])*(1/(z-1) - 1/z)
        
        # check max tolerance
        if config.processing['deisotoping']['massTolerance'] >= maxTol:
            wx.Bell()
            message = "For the specified charge your isotope mass tolerance must be\nlower than %.4f. Please correct the parameter in deisotoping panel." % maxTol
            dlg = mwx.dlgMessage(self, title="Isotope mass tolerance is too high.", message=message)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        return True
    # ----
    
    
    def checkChargedPeaks(self):
        """Check if at least one peak in current peaklist has charge."""
        
        # check charge
        for peak in self.currentDocument.spectrum.peaklist:
            if peak.charge:
                return True
        
        # show message
        wx.Bell()
        message = "Only the peaks with specified charge can be deconvoluted.\nPlease use deisotoping tool or peak editor to set peak charges\nprior to deconvolution."
        dlg = mwx.dlgMessage(self, title="There are no charged peaks in your peak list.", message=message)
        dlg.ShowModal()
        dlg.Destroy()
        
        return False
    # ----
    
    
    def makeThresholdLine(self):
        """Make peakpicking threshold line."""
        
        # check current spectrum
        if not self.currentDocument or not self.currentDocument.spectrum.hasprofile():
            return []
        
        # get baseline window
        window = 1.
        if config.processing['peakpicking']['baseline']:
            window = 1./config.processing['baseline']['precision']
        
        # get curent baseline
        baseline = self.currentDocument.spectrum.baseline(
            window = window,
            offset = config.processing['baseline']['offset']
        )
        
        # get basepeak (approx. only)
        index = mspy.basepeak(self.currentDocument.spectrum.profile)
        basepeak = self.currentDocument.spectrum.profile[index]
        
        # apply threshold
        points = []
        relThreshold = basepeak[1] * config.processing['peakpicking']['relIntThreshold']
        absThreshold = config.processing['peakpicking']['absIntThreshold']
        for x in range(len(baseline)):
            snThreshold = config.processing['peakpicking']['snThreshold'] * baseline[x][2]
            points.append([baseline[x][0], baseline[x][1] + max(snThreshold, relThreshold, absThreshold)])
        
        return points
    # ----
    
    
    def clearPreview(self):
        """Clear tmp preview spectrum."""
        
        if self.previewData != None:
            self.previewData = None
            self.parent.updateTmpSpectrum(None)
    # ----
    
    


class dlgPresetsName(wx.Dialog):
    """Set presets name."""
    
    def __init__(self, parent):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, "Method Name", style=wx.DEFAULT_DIALOG_STYLE)
        
        self.name = ''
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.HORIZONTAL)
        
        # make elements
        self.name_value = wx.TextCtrl(self, -1, '', size=(300,-1), style=wx.TE_PROCESS_ENTER)
        self.name_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, "Save")
        ok_butt.Bind(wx.EVT_BUTTON, self.onOK)
        
        # pack elements
        staticSizer.Add(self.name_value, 0, wx.ALL, 10)
        
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttons.Add(ok_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.CENTER|wx.TOP|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttons, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onOK(self, evt):
        """Get name."""
        
        self.name = self.name_value.GetValue()
        if self.name:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
