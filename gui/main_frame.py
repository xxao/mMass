#  
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
import pdb

# load libs
import traceback
import sys
import platform
import time
import copy
import os
import os.path
import threading
import subprocess
import re
import random
import mspy
import socket
import http.client
import webbrowser
import tempfile
import wx
import wx.aui
import numpy

# load modules
from .ids import *
from . import mwx
from . import images
from . import config
from . import libs
from . import doc

from .panel_about import panelAbout
from .panel_calibration import panelCalibration
from .panel_compare_peaklists import panelComparePeaklists
from .panel_compounds_search import panelCompoundsSearch
from .panel_document_info import panelDocumentInfo
from .panel_document_export import panelDocumentExport
from .panel_documents import panelDocuments
from .panel_envelope_fit import panelEnvelopeFit
from .panel_mascot import panelMascot
from .panel_mass_calculator import panelMassCalculator
from .panel_mass_filter import panelMassFilter
from .panel_mass_to_formula import panelMassToFormula
from .panel_mass_defect_plot import panelMassDefectPlot
from .panel_peak_differences import panelPeakDifferences
from .panel_periodic_table import panelPeriodicTable
from .panel_peaklist import panelPeaklist
from .panel_processing import panelProcessing
from .panel_profound import panelProfound
from .panel_prospector import panelProspector
from .panel_sequence import panelSequence
from .panel_spectrum import panelSpectrum, dlgViewRange, dlgSpectrumOffset
from .panel_spectrum_generator import panelSpectrumGenerator

from .dlg_compounds_editor import dlgCompoundsEditor
from .dlg_enzymes_editor import dlgEnzymesEditor
from .dlg_mascot_editor import dlgMascotEditor
from .dlg_modifications_editor import dlgModificationsEditor
from .dlg_monomers_editor import dlgMonomersEditor
from .dlg_presets_editor import dlgPresetsEditor
from .dlg_references_editor import dlgReferencesEditor

from .dlg_error import dlgError
from .dlg_preferences import dlgPreferences
from .dlg_select_scans import dlgSelectScans
from .dlg_select_sequences import dlgSelectSequences
from .dlg_clipboard_editor import dlgClipboardEditor


# MAIN FRAME
# ----------

class mainFrame(wx.Frame):
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size=(800,500), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        
        # init error handler
        sys.excepthook = self.onError
        
        # init images
        images.loadImages()
        
        # set icon
        icons = wx.IconBundle()
        icons.AddIcon(images.lib['icon16'])
        icons.AddIcon(images.lib['icon32'])
        icons.AddIcon(images.lib['icon48'])
        icons.AddIcon(images.lib['icon128'])
        icons.AddIcon(images.lib['icon256'])
        self.SetIcons(icons)
        
        # init basics
        self.documents = []
        self.currentDocument = None
        self.currentDocumentXML = None
        self.currentSequence = None
        
        self.documentsSoloCurrent = None
        self.documentsSoloPrevious = {}
        self.usedColours = []
        
        self.bufferedScanlists = {}
        
        self.processingDocumentQueue = False
        self.tmpDocumentQueue = []
        self.tmpScanlist = None
        self.tmpSequenceList = None
        self.tmpCompassXport = None
        self.tmpLibrarySaved = None
        
        # make GUI
        self.makeMenubar()
        self.SetMenuBar(self.menubar)
        
        self.makeToolbar()
        self.SetToolBar(self.toolbar)
        self.toolbar.Realize()
        
        self.makeGUI()
        self.updateControls()
        
        # set size
        maximize = config.main['appMaximized']
        self.SetSize((config.main['appWidth'], config.main['appHeight']))
        self.SetMinSize((855,500))
        if maximize:
            self.Maximize()
        
        # bind events
        self.DragAcceptFiles(True)
        self.Bind(wx.EVT_CLOSE, self.onQuit)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_DROP_FILES, self.onDocumentDropped)
        
        # show app
        self.Layout()
        self.Centre(wx.BOTH)
        self.Show(True)
        
        # check for available updates
        # TODO: work out how updating should work (probably not self-updating)
        # self.checkVersions()
    # ----
    
    
    def makeMenubar(self):
        """Make main application menubar."""
        
        # init menubar
        self.menubar = wx.MenuBar()
        
        # init recent documents
        self.menuRecent = wx.Menu()
        self.updateRecentFiles()
        
        # file
        document = wx.Menu()
        document.Append(ID_documentNew, "New"+HK_documentNew, "")
        document.Append(ID_documentNewFromClipboard, "New from Clipboard"+HK_documentNewFromClipboard, "")
        document.Append(ID_documentOpen, "Open..."+HK_documentOpen, "")
        document.Append(ID_documentRecent, "Open Recent", self.menuRecent)
        document.AppendSeparator()
        document.Append(ID_documentClose, "Close"+HK_documentClose, "")
        document.Append(ID_documentCloseAll, "Close All"+HK_documentCloseAll, "")
        document.Append(ID_documentSave, "Save"+HK_documentSave, "")
        document.Append(ID_documentSaveAs, "Save As..."+HK_documentSaveAs, "")
        document.Append(ID_documentSaveAll, "Save All"+HK_documentSaveAll, "")
        document.AppendSeparator()
        document.Append(ID_documentExport, "Export..."+HK_documentExport, "")
        document.AppendSeparator()
        document.Append(ID_documentPrintSpectrum, "Print Spectrum..."+HK_documentPrintSpectrum, "")
        document.Append(ID_documentReport, "Analysis Report..."+HK_documentReport, "")
        if wx.Platform == '__WXMAC__': document.AppendSeparator()
        document.Append(ID_documentInfo, "Document Info..."+HK_documentInfo, "")
        document.AppendSeparator()
        document.Append(ID_preferences, "Preferences..."+HK_preferences, "")
        document.AppendSeparator()
        document.Append(ID_quit, "Quit"+HK_quit, "Quit mMass")
        
        self.Bind(wx.EVT_MENU, self.onDocumentNew, id=ID_documentNew)
        self.Bind(wx.EVT_MENU, self.onDocumentNewFromClipboard, id=ID_documentNewFromClipboard)
        self.Bind(wx.EVT_MENU, self.onDocumentOpen, id=ID_documentOpen)
        self.Bind(wx.EVT_MENU, self.onDocumentClose, id=ID_documentClose)
        self.Bind(wx.EVT_MENU, self.onDocumentCloseAll, id=ID_documentCloseAll)
        self.Bind(wx.EVT_MENU, self.onDocumentSave, id=ID_documentSave)
        self.Bind(wx.EVT_MENU, self.onDocumentSave, id=ID_documentSaveAs)
        self.Bind(wx.EVT_MENU, self.onDocumentSaveAll, id=ID_documentSaveAll)
        self.Bind(wx.EVT_MENU, self.onDocumentExport, id=ID_documentExport)
        self.Bind(wx.EVT_MENU, self.onDocumentInfo, id=ID_documentInfo)
        self.Bind(wx.EVT_MENU, self.onDocumentPrintSpectrum, id=ID_documentPrintSpectrum)
        self.Bind(wx.EVT_MENU, self.onDocumentReport, id=ID_documentReport)
        self.Bind(wx.EVT_MENU, self.onPreferences, id=ID_preferences)
        self.Bind(wx.EVT_MENU, self.onQuit, id=ID_quit)
        
        self.menubar.Append(document, "File")
        
        # view
        view = wx.Menu()
        
        viewCanvas = wx.Menu()
        viewCanvas.Append(ID_viewLegend, "Legend", "", wx.ITEM_CHECK)
        viewCanvas.Append(ID_viewGrid, "Gridlines", "", wx.ITEM_CHECK)
        viewCanvas.Append(ID_viewMinorTicks, "Minor Ticks", "", wx.ITEM_CHECK)
        viewCanvas.Append(ID_viewDataPoints, "Data Points", "", wx.ITEM_CHECK)
        viewCanvas.AppendSeparator()
        viewCanvas.Append(ID_viewPosBars, "Position Bars"+HK_viewPosBars, "", wx.ITEM_CHECK)
        viewCanvas.AppendSeparator()
        viewCanvas.Append(ID_viewGel, "Gel View"+HK_viewGel, "", wx.ITEM_CHECK)
        viewCanvas.Append(ID_viewGelLegend, "Gel View Legend", "", wx.ITEM_CHECK)
        viewCanvas.AppendSeparator()
        viewCanvas.Append(ID_viewTracker, "Cursor Tracker", "", wx.ITEM_CHECK)
        viewCanvas.Append(ID_viewCheckLimits, "Check Limits", "", wx.ITEM_CHECK)
        view.Append(-1, "Spectrum Canvas", viewCanvas)
        
        viewLabels = wx.Menu()
        title = ("Show Labels", "Hide Labels")
        viewLabels.Append(ID_viewLabels, title[bool(config.spectrum['showLabels'])]+HK_viewLabels, "")
        title = ("Show Ticks", "Hide Ticks")
        viewLabels.Append(ID_viewTicks, title[bool(config.spectrum['showTicks'])]+HK_viewTicks, "")
        viewLabels.AppendSeparator()
        viewLabels.Append(ID_viewLabelCharge, "Charge", "", wx.ITEM_CHECK)
        viewLabels.Append(ID_viewLabelGroup, "Group", "", wx.ITEM_CHECK)
        viewLabels.Append(ID_viewLabelBgr, "Background", "", wx.ITEM_CHECK)
        viewLabels.AppendSeparator()
        title = ("Vertical Labels", "Horizontal Labels")
        viewLabels.Append(ID_viewLabelAngle, title[bool(config.spectrum['labelAngle'])]+HK_viewLabelAngle, "")
        viewLabels.AppendSeparator()
        viewLabels.Append(ID_viewOverlapLabels, "Allow Overlapping"+HK_viewOverlapLabels, "", wx.ITEM_CHECK)
        viewLabels.Append(ID_viewAllLabels, "Labels in All Documents"+HK_viewAllLabels, "", wx.ITEM_CHECK)
        view.Append(-1, "Peak Labels", viewLabels)
        
        viewNotations = wx.Menu()
        title = ("Show Notations", "Hide Notations")
        viewNotations.Append(ID_viewNotations, title[bool(config.spectrum['showNotations'])], "")
        viewNotations.AppendSeparator()
        viewNotations.Append(ID_viewNotationMarks, "Marks", "", wx.ITEM_CHECK)
        viewNotations.Append(ID_viewNotationLabels, "Labels", "", wx.ITEM_CHECK)
        viewNotations.Append(ID_viewNotationMz, "m/z", "", wx.ITEM_CHECK)
        view.Append(-1, "Notations", viewNotations)
        
        viewSpectrumRuler = wx.Menu()
        viewSpectrumRuler.Append(ID_viewSpectrumRulerMz, "m/z", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerDist, "Distance", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerPpm, "ppm", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerZ, "Charge", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerCursorMass, "Neutral Mass (Cursor)", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerParentMass, "Neutral Mass (Parent)", "", wx.ITEM_CHECK)
        viewSpectrumRuler.Append(ID_viewSpectrumRulerArea, "Area", "", wx.ITEM_CHECK)
        view.Append(-1, "Spectrum Ruler", viewSpectrumRuler)
        
        viewPeaklistColumns = wx.Menu()
        viewPeaklistColumns.Append(ID_viewPeaklistColumnMz, "m/z", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnAi, "a.i.", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnInt, "Intensity", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnBase, "Baseline", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnRel, "Rel. Intensity", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnSn, "s/n", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnZ, "Charge", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnMass, "Mass", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnFwhm, "FWHM", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnResol, "Resolution", "", wx.ITEM_CHECK)
        viewPeaklistColumns.Append(ID_viewPeaklistColumnGroup, "Group", "", wx.ITEM_CHECK)
        view.Append(-1, "Peak List Columns", viewPeaklistColumns)
        
        view.AppendSeparator()
        view.Append(ID_viewAutoscale, "Autoscale Intensity"+HK_viewAutoscale, "", wx.ITEM_CHECK)
        view.Append(ID_viewNormalize, "Normalize Intensity"+HK_viewNormalize, "", wx.ITEM_CHECK)
        view.AppendSeparator()
        view.Append(ID_viewRange, "Set Mass Range..."+HK_viewRange, "")
        view.AppendSeparator()
        view.Append(ID_documentFlip, "Flip Spectrum"+HK_documentFlip, "")
        view.Append(ID_documentOffset, "Offset Spectrum...", "")
        view.Append(ID_documentClearOffsets, "Clear All Offsets", "")
        view.AppendSeparator()
        view.Append(ID_viewCanvasProperties, "Canvas Properties..."+HK_viewCanvasProperties, "")
        
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLegend)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewGrid)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewMinorTicks)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewDataPoints)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewPosBars)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewGel)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewGelLegend)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewTracker)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewCheckLimits)
        
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLabels)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewTicks)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLabelCharge)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLabelGroup)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLabelBgr)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewLabelAngle)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewOverlapLabels)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewAllLabels)
        
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewNotations)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewNotationMarks)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewNotationLabels)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewNotationMz)
        
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerMz)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerDist)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerPpm)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerZ)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerCursorMass)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerParentMass)
        self.Bind(wx.EVT_MENU, self.onViewSpectrumRuler, id=ID_viewSpectrumRulerArea)
        
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnMz)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnAi)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnInt)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnBase)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnRel)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnSn)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnZ)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnMass)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnFwhm)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnResol)
        self.Bind(wx.EVT_MENU, self.onViewPeaklistColumns, id=ID_viewPeaklistColumnGroup)
        
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewAutoscale)
        self.Bind(wx.EVT_MENU, self.onView, id=ID_viewNormalize)
        self.Bind(wx.EVT_MENU, self.onViewRange, id=ID_viewRange)
        self.Bind(wx.EVT_MENU, self.onDocumentFlip, id=ID_documentFlip)
        self.Bind(wx.EVT_MENU, self.onDocumentOffset, id=ID_documentOffset)
        self.Bind(wx.EVT_MENU, self.onDocumentOffset, id=ID_documentClearOffsets)
        self.Bind(wx.EVT_MENU, self.onViewCanvasProperties, id=ID_viewCanvasProperties)
        
        self.menubar.Append(view, "View")
        
        self.menubar.Check(ID_viewLegend, bool(config.spectrum['showLegend']))
        self.menubar.Check(ID_viewGrid, bool(config.spectrum['showGrid']))
        self.menubar.Check(ID_viewMinorTicks, bool(config.spectrum['showMinorTicks']))
        self.menubar.Check(ID_viewDataPoints, bool(config.spectrum['showDataPoints']))
        self.menubar.Check(ID_viewPosBars, bool(config.spectrum['showPosBars']))
        self.menubar.Check(ID_viewGel, bool(config.spectrum['showGel']))
        self.menubar.Check(ID_viewGelLegend, bool(config.spectrum['showGelLegend']))
        self.menubar.Check(ID_viewTracker, bool(config.spectrum['showTracker']))
        self.menubar.Check(ID_viewCheckLimits, bool(config.spectrum['checkLimits']))
        
        self.menubar.Check(ID_viewLabelCharge, bool(config.spectrum['labelCharge']))
        self.menubar.Check(ID_viewLabelGroup, bool(config.spectrum['labelGroup']))
        self.menubar.Check(ID_viewLabelBgr, bool(config.spectrum['labelBgr']))
        self.menubar.Check(ID_viewOverlapLabels, bool(config.spectrum['overlapLabels']))
        self.menubar.Check(ID_viewAllLabels, bool(config.spectrum['showAllLabels']))
        
        self.menubar.Check(ID_viewNotationMarks, bool(config.spectrum['notationMarks']))
        self.menubar.Check(ID_viewNotationLabels, bool(config.spectrum['notationLabels']))
        self.menubar.Check(ID_viewNotationMz, bool(config.spectrum['notationMZ']))
        
        self.menubar.Check(ID_viewSpectrumRulerMz, bool('mz' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerDist, bool('dist' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerPpm, bool('ppm' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerZ, bool('z' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerCursorMass, bool('cmass' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerParentMass, bool('pmass' in config.main['cursorInfo']))
        self.menubar.Check(ID_viewSpectrumRulerArea, bool('area' in config.main['cursorInfo']))
        
        self.menubar.Check(ID_viewPeaklistColumnMz, bool('mz' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnAi, bool('ai' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnBase, bool('base' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnInt, bool('int' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnRel, bool('rel' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnSn, bool('sn' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnZ, bool('z' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnMass, bool('mass' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnFwhm, bool('fwhm' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnResol, bool('resol' in config.main['peaklistColumns']))
        self.menubar.Check(ID_viewPeaklistColumnGroup, bool('group' in config.main['peaklistColumns']))
        
        self.menubar.Check(ID_viewAutoscale, bool(config.spectrum['autoscale']))
        self.menubar.Check(ID_viewNormalize, bool(config.spectrum['normalize']))
        
        # processing
        processing = wx.Menu()
        processing.Append(ID_processingUndo, "Undo"+HK_processingUndo, "")
        processing.AppendSeparator()
        processing.Append(ID_processingPeakpicking, "Peak Picking..."+HK_processingPeakpicking, "")
        processing.Append(ID_processingDeisotoping, "Deisotoping..."+HK_processingDeisotoping, "")
        processing.Append(ID_processingDeconvolution, "Deconvolution..."+HK_processingDeconvolution, "")
        processing.AppendSeparator()
        processing.Append(ID_processingBaseline, "Correct Baseline..."+HK_processingBaseline, "")
        processing.Append(ID_processingSmoothing, "Smooth Spectrum..."+HK_processingSmoothing, "")
        processing.Append(ID_processingCrop, "Crop...", "")
        processing.Append(ID_processingMath, "Math Operations...", "")
        processing.AppendSeparator()
        processing.Append(ID_processingBatch, "Batch Processing...", "")
        processing.AppendSeparator()
        processing.Append(ID_toolsCalibration, "Calibration..."+HK_toolsCalibration, "")
        processing.AppendSeparator()
        processing.Append(ID_toolsSwapData, "Swap Data", "")
        
        self.Bind(wx.EVT_MENU, self.onToolsUndo, id=ID_processingUndo)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingPeakpicking)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingDeisotoping)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingDeconvolution)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingBaseline)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingSmoothing)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingCrop)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingMath)
        self.Bind(wx.EVT_MENU, self.onToolsProcessing, id=ID_processingBatch)
        self.Bind(wx.EVT_MENU, self.onToolsCalibration, id=ID_toolsCalibration)
        self.Bind(wx.EVT_MENU, self.onToolsSwapData, id=ID_toolsSwapData)
        
        self.menubar.Append(processing, "Processing")
        
        # sequence
        sequence = wx.Menu()
        sequence.Append(ID_sequenceNew, "New...", "")
        sequence.Append(ID_sequenceImport, "Import...", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceEditor, "Edit Sequence...", "")
        sequence.Append(ID_sequenceModifications, "Edit Modifications...", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceDigest, "Digest Protein...", "")
        sequence.Append(ID_sequenceFragment, "Fragment Peptide...", "")
        sequence.Append(ID_sequenceSearch, "Mass Search...", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceSendToMassCalculator, "Show Isotopic Pattern...", "")
        sequence.Append(ID_sequenceSendToEnvelopeFit, "Send to Envelope Fit...", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceMatchesCalibrateBy, "Calibrate by Matches...", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceMatchesDelete, "Delete All Matches", "")
        sequence.Append(ID_sequenceDelete, "Delete Sequence", "")
        sequence.AppendSeparator()
        sequence.Append(ID_sequenceSort, "Sort by Titles", "")
        
        self.Bind(wx.EVT_MENU, self.onSequenceNew, id=ID_sequenceNew)
        self.Bind(wx.EVT_MENU, self.onSequenceImport, id=ID_sequenceImport)
        self.Bind(wx.EVT_MENU, self.onToolsSequence, id=ID_sequenceEditor)
        self.Bind(wx.EVT_MENU, self.onToolsSequence, id=ID_sequenceModifications)
        self.Bind(wx.EVT_MENU, self.onToolsSequence, id=ID_sequenceDigest)
        self.Bind(wx.EVT_MENU, self.onToolsSequence, id=ID_sequenceFragment)
        self.Bind(wx.EVT_MENU, self.onToolsSequence, id=ID_sequenceSearch)
        self.Bind(wx.EVT_MENU, self.onSequenceSendToMassCalculator, id=ID_sequenceSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onSequenceSendToEnvelopeFit, id=ID_sequenceSendToEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.onSequenceMatchesCalibrateBy, id=ID_sequenceMatchesCalibrateBy)
        self.Bind(wx.EVT_MENU, self.onSequenceMatchesDelete, id=ID_sequenceMatchesDelete)
        self.Bind(wx.EVT_MENU, self.onSequenceDelete, id=ID_sequenceDelete)
        self.Bind(wx.EVT_MENU, self.onSequenceSort, id=ID_sequenceSort)
        
        self.menubar.Append(sequence, "Sequence")
        
        # tools
        tools = wx.Menu()
        tools.Append(ID_toolsRuler, "Spectrum Ruler"+HK_toolsRuler, "", wx.ITEM_RADIO)
        tools.Append(ID_toolsLabelPeak, "Label Peak"+HK_toolsLabelPeak, "", wx.ITEM_RADIO)
        tools.Append(ID_toolsLabelPoint, "Label Point"+HK_toolsLabelPoint, "", wx.ITEM_RADIO)
        tools.Append(ID_toolsLabelEnvelope, "Label Envelope"+HK_toolsLabelEnvelope, "", wx.ITEM_RADIO)
        tools.Append(ID_toolsDeleteLabel, "Delete Label"+HK_toolsDeleteLabel, "", wx.ITEM_RADIO)
        tools.Append(ID_toolsOffset, "Offset Spectrum", "", wx.ITEM_RADIO)
        tools.AppendSeparator()
        tools.Append(ID_toolsPeriodicTable, "Periodic Table"+HK_toolsPeriodicTable, "")
        tools.Append(ID_toolsMassCalculator, "Mass Calculator"+HK_toolsMassCalculator, "")
        tools.Append(ID_toolsMassToFormula, "Mass to Formula"+HK_toolsMassToFormula, "")
        tools.Append(ID_toolsMassDefectPlot, "Mass Defect Plot"+HK_toolsMassDefectPlot, "")
        tools.AppendSeparator()
        tools.Append(ID_toolsMassFilter, "Mass Filter"+HK_toolsMassFilter, "")
        tools.Append(ID_toolsCompoundsSearch, "Compounds Search"+HK_toolsCompoundsSearch, "")
        tools.Append(ID_toolsPeakDifferences, "Peak Differences"+HK_toolsPeakDifferences, "")
        tools.Append(ID_toolsComparePeaklists, "Compare Peak Lists"+HK_toolsComparePeaklists, "")
        tools.Append(ID_toolsSpectrumGenerator, "Spectrum Generator"+HK_toolsSpectrumGenerator, "")
        tools.AppendSeparator()
        tools.Append(ID_toolsEnvelopeFit, "Envelope Fit"+HK_toolsEnvelopeFit, "")
        tools.AppendSeparator()
        tools.Append(ID_mascotPMF, "Mascot PMF", "")
        tools.Append(ID_mascotMIS, "Mascot MS/MS Search", "")
        tools.Append(ID_mascotSQ, "Mascot Sequence Query", "")
        tools.AppendSeparator()
        tools.Append(ID_toolsProfound, "ProFound Search", "")
        tools.AppendSeparator()
        tools.Append(ID_prospectorMSFit, "Protein Prospector MS-Fit", "")
        tools.Append(ID_prospectorMSTag, "Protein Prospector MS-Tag", "")
        
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsRuler)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsLabelPeak)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsLabelPoint)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsLabelEnvelope)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsDeleteLabel)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrum, id=ID_toolsOffset)
        self.Bind(wx.EVT_MENU, self.onToolsPeriodicTable, id=ID_toolsPeriodicTable)
        self.Bind(wx.EVT_MENU, self.onToolsMassCalculator, id=ID_toolsMassCalculator)
        self.Bind(wx.EVT_MENU, self.onToolsMassToFormula, id=ID_toolsMassToFormula)
        self.Bind(wx.EVT_MENU, self.onToolsMassDefectPlot, id=ID_toolsMassDefectPlot)
        self.Bind(wx.EVT_MENU, self.onToolsMassFilter, id=ID_toolsMassFilter)
        self.Bind(wx.EVT_MENU, self.onToolsCompoundsSearch, id=ID_toolsCompoundsSearch)
        self.Bind(wx.EVT_MENU, self.onToolsPeakDifferences, id=ID_toolsPeakDifferences)
        self.Bind(wx.EVT_MENU, self.onToolsComparePeaklists, id=ID_toolsComparePeaklists)
        self.Bind(wx.EVT_MENU, self.onToolsSpectrumGenerator, id=ID_toolsSpectrumGenerator)
        self.Bind(wx.EVT_MENU, self.onToolsEnvelopeFit, id=ID_toolsEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.onToolsMascot, id=ID_mascotPMF)
        self.Bind(wx.EVT_MENU, self.onToolsMascot, id=ID_mascotMIS)
        self.Bind(wx.EVT_MENU, self.onToolsMascot, id=ID_mascotSQ)
        self.Bind(wx.EVT_MENU, self.onToolsProfound, id=ID_toolsProfound)
        self.Bind(wx.EVT_MENU, self.onToolsProspector, id=ID_prospectorMSFit)
        self.Bind(wx.EVT_MENU, self.onToolsProspector, id=ID_prospectorMSTag)
        
        self.menubar.Append(tools, "Tools")
        
        self.menubar.Check(ID_toolsRuler, True)
        
        # libraries
        libraries = wx.Menu()
        libraries.Append(ID_libraryCompounds, "Compounds...", "")
        libraries.Append(ID_libraryModifications, "Modifications...", "")
        libraries.Append(ID_libraryMonomers, "Monomers...", "")
        libraries.Append(ID_libraryEnzymes, "Enzymes...", "")
        libraries.Append(ID_libraryReferences, "Reference Masses...", "")
        libraries.Append(ID_libraryMascot, "Mascot Servers...", "")
        libraries.AppendSeparator()
        libraries.Append(ID_libraryPresets, "Presets...", "")
        
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryCompounds)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryModifications)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryMonomers)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryEnzymes)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryReferences)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryMascot)
        self.Bind(wx.EVT_MENU, self.onLibraryEdit, id=ID_libraryPresets)
        
        self.menubar.Append(libraries, "Libraries")
        
        # links
        links = wx.Menu()
        
        linksMSTools = wx.Menu()
        linksMSTools.Append(ID_linksExpasy, "ExPASy", "")
        linksMSTools.Append(ID_linksMatrixScience, "Matrix Science", "")
        linksMSTools.Append(ID_linksProspector, "Protein Prospector", "")
        linksMSTools.Append(ID_linksProfound, "ProFound", "")
        linksMSTools.Append(ID_linksBiomedMSTools, "Biomed MS Tools", "")
        links.Append(-1, "MS Tools", linksMSTools)
        
        linksModifications = wx.Menu()
        linksModifications.Append(ID_linksUniMod, "UniMod", "")
        linksModifications.Append(ID_linksDeltaMass, "Delta Mass", "")
        links.Append(-1, "Modifications", linksModifications)
        
        linksSequenceDB = wx.Menu()
        linksSequenceDB.Append(ID_linksUniProt, "UniProt", "")
        linksSequenceDB.Append(ID_linksExpasy, "ExPASy", "")
        linksSequenceDB.Append(ID_linksEMBLEBI, "EMBL EBI", "")
        linksSequenceDB.Append(ID_linksPIR, "PIR", "")
        linksSequenceDB.Append(ID_linksNCBI, "NCBI", "")
        links.Append(-1, "Sequence Databases", linksSequenceDB)
        
        linksSequenceTools = wx.Menu()
        linksSequenceTools.Append(ID_linksBLAST, "BLAST", "")
        linksSequenceTools.Append(ID_linksClustalW, "ClustalW", "")
        linksSequenceTools.Append(ID_linksFASTA, "FASTA", "")
        linksSequenceTools.Append(ID_linksMUSCLE, "MUSCLE", "")
        links.Append(-1, "Sequence Tools", linksSequenceTools)
        
        linksStructures = wx.Menu()
        linksStructures.Append(ID_linksPDB, "RCSB PDB", "")
        links.Append(-1, "Protein Structures", linksStructures)
        
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksExpasy)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksMatrixScience)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksProspector)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksProfound)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksBiomedMSTools)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksUniMod)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksDeltaMass)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksUniProt)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksExpasy)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksEMBLEBI)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksPIR)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksNCBI)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksBLAST)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksClustalW)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksFASTA)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksMUSCLE)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_linksPDB)
        
        self.menubar.Append(links, "Links")
        
        # window
        window = wx.Menu()
        if wx.Platform != '__WXMAC__':
            window.Append(ID_windowMaximize, "Maximize", "")
            window.Append(ID_windowMinimize, "Minimize", "")
            window.AppendSeparator()
            
        window.Append(ID_windowLayout1, "Default"+HK_windowLayout1, "", wx.ITEM_RADIO)
        window.Append(ID_windowLayout2, "Documents Bottom"+HK_windowLayout2, "", wx.ITEM_RADIO)
        window.Append(ID_windowLayout3, "Peaklist Bottom"+HK_windowLayout3, "", wx.ITEM_RADIO)
        window.Append(ID_windowLayout4, "Wide Spectrum"+HK_windowLayout4, "", wx.ITEM_RADIO)
        
        self.Bind(wx.EVT_MENU, self.onWindowMaximize, id=ID_windowMaximize)
        self.Bind(wx.EVT_MENU, self.onWindowIconize, id=ID_windowMinimize)
        self.Bind(wx.EVT_MENU, self.onWindowLayout, id=ID_windowLayout1)
        self.Bind(wx.EVT_MENU, self.onWindowLayout, id=ID_windowLayout2)
        self.Bind(wx.EVT_MENU, self.onWindowLayout, id=ID_windowLayout3)
        self.Bind(wx.EVT_MENU, self.onWindowLayout, id=ID_windowLayout4)
        
        self.menubar.Append(window, "&Window")
        
        # help
        help = wx.Menu()
        help.Append(ID_helpUserGuide, "User's Guide..."+HK_helpUserGuide, "")
        help.AppendSeparator()
        help.Append(ID_helpHomepage, "Homepage...", "")
        help.Append(ID_helpForum, "Support Forum...", "")
        help.Append(ID_helpTwitter, "Twitter Account...", "")
        help.AppendSeparator()
        help.Append(ID_helpCite, "Papers to Cite...", "")
        help.Append(ID_helpDonate, "Make a Donation...", "")
        help.AppendSeparator()
        help.Append(ID_helpUpdate, "Check for Update", "")
        if wx.Platform != '__WXMAC__':
            help.AppendSeparator()
        help.Append(ID_helpAbout, "About mMass", "")
        
        self.Bind(wx.EVT_MENU, self.onHelpUserGuide, id=ID_helpUserGuide)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_helpHomepage)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_helpForum)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_helpTwitter)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_helpCite)
        self.Bind(wx.EVT_MENU, self.onLibraryLink, id=ID_helpDonate)
        self.Bind(wx.EVT_MENU, self.onHelpUpdate, id=ID_helpUpdate)
        self.Bind(wx.EVT_MENU, self.onHelpAbout, id=ID_helpAbout)
        
        self.menubar.Append(help, "&Help")
    # ----
    
    
    def makeToolbar(self):
        """Make main application toolbar."""
        
        # init toolbar
        self.toolbar = self.CreateToolBar(mwx.MAIN_TOOLBAR_STYLE)
        self.toolbar.SetToolBitmapSize(mwx.MAIN_TOOLBAR_TOOLSIZE)
        self.toolbar.SetFont(wx.SMALL_FONT)
        
        # document
        if wx.Platform != '__WXMAC__':
            self.toolbar.AddTool(ID_documentOpen, "Open", images.lib['toolsOpen'], wx.NullBitmap, shortHelp="Open document...", longHelp="Open document")
            self.toolbar.AddTool(ID_documentSave, "Save", images.lib['toolsSave'], wx.NullBitmap, shortHelp="Save document", longHelp="Save current document")
            self.toolbar.AddTool(ID_documentPrintSpectrum, "Print", images.lib['toolsPrint'], wx.NullBitmap, shortHelp="Print spectrum...", longHelp="Print spectrum")
            
            self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentOpen, id=ID_documentOpen)
            self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentSave, id=ID_documentSave)
            self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentPrintSpectrum, id=ID_documentPrintSpectrum)
            
            self.toolbar.AddSeparator()
        
        # tools
        self.toolbar.AddTool(ID_toolsProcessing, "Processing", images.lib['toolsProcessing'], wx.NullBitmap, shortHelp="Data processing...", longHelp="Mass spectrum processing")
        self.toolbar.AddTool(ID_toolsCalibration, "Calibration", images.lib['toolsCalibration'], wx.NullBitmap, shortHelp="Re-calibrate data...", longHelp="Mass spectrum calibration")
        
        if wx.Platform != '__WXMAC__':
             self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_toolsSequence, "Sequence", images.lib['toolsSequence'], wx.NullBitmap, shortHelp="Sequence editor...", longHelp="Sequence editor and tool")
        
        if wx.Platform != '__WXMAC__':
             self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_toolsPeriodicTable, "Elements", images.lib['toolsPeriodicTable'], wx.NullBitmap, shortHelp="Periodic Table...", longHelp="Periodic table of elements")
        self.toolbar.AddTool(ID_toolsMassCalculator, "Masscalc", images.lib['toolsMassCalculator'], wx.NullBitmap, shortHelp="Mass calculator...", longHelp="Calculate ion series and isotopic pattern")
        self.toolbar.AddTool(ID_toolsMassToFormula, "Formulator", images.lib['toolsMassToFormula'], wx.NullBitmap, shortHelp="Mass to formula...", longHelp="Generate molecular formulae for specified mass")
        self.toolbar.AddTool(ID_toolsMassDefectPlot, "Mass Defect", images.lib['toolsMassDefectPlot'], wx.NullBitmap, shortHelp="Mass defect plot...", longHelp="Show various mass defect plots for current peak list")
        
        if wx.Platform != '__WXMAC__':
             self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_toolsMassFilter, "Mass Filter", images.lib['toolsMassFilter'], wx.NullBitmap, shortHelp="Mass filter...", longHelp="Filter spectrum contaminants")
        self.toolbar.AddTool(ID_toolsCompoundsSearch, "Compounds", images.lib['toolsCompoundsSearch'], wx.NullBitmap, shortHelp="Compounds search...", longHelp="Search for compounds")
        self.toolbar.AddTool(ID_toolsPeakDifferences, "Differences", images.lib['toolsPeakDifferences'], wx.NullBitmap, shortHelp="Peak differences...", longHelp="Calculate peak differences")
        self.toolbar.AddTool(ID_toolsComparePeaklists, "Compare", images.lib['toolsComparePeaklists'], wx.NullBitmap, shortHelp="Compare peak lists...", longHelp="Compare multiple peaklists")
        self.toolbar.AddTool(ID_toolsSpectrumGenerator, "Generator", images.lib['toolsSpectrumGenerator'], wx.NullBitmap, shortHelp="Generate mass spectrum...", longHelp="Generate mass spectrum from current peak list")
        self.toolbar.AddTool(ID_toolsEnvelopeFit, "Envelope Fit", images.lib['toolsEnvelopeFit'], wx.NullBitmap, shortHelp="Calculate atom exchange...", longHelp="Calculate atom exchange from peak envelope")
        
        if wx.Platform != '__WXMAC__':
            self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_toolsMascot, "Mascot", images.lib['toolsMascot'], wx.NullBitmap, shortHelp="Mascot search...", longHelp="Send data to Mascot server")
        self.toolbar.AddTool(ID_toolsProfound, "ProFound", images.lib['toolsProfound'], wx.NullBitmap, shortHelp="ProFound search...", longHelp="Send data to ProFound server")
        
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsProcessing, id=ID_toolsProcessing)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsCalibration, id=ID_toolsCalibration)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsSequence, id=ID_toolsSequence)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsPeriodicTable, id=ID_toolsPeriodicTable)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsMassCalculator, id=ID_toolsMassCalculator)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsMassToFormula, id=ID_toolsMassToFormula)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsMassDefectPlot, id=ID_toolsMassDefectPlot)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsMassFilter, id=ID_toolsMassFilter)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsCompoundsSearch, id=ID_toolsCompoundsSearch)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsPeakDifferences, id=ID_toolsPeakDifferences)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsComparePeaklists, id=ID_toolsComparePeaklists)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsSpectrumGenerator, id=ID_toolsSpectrumGenerator)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsEnvelopeFit, id=ID_toolsEnvelopeFit)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsMascot, id=ID_toolsMascot)
        self.toolbar.Bind(wx.EVT_TOOL, self.onToolsProfound, id=ID_toolsProfound)
        
        if wx.Platform != '__WXMAC__':
            self.toolbar.AddSeparator()
        
        self.toolbar.AddTool(ID_toolsDocumentInfo, "Notes", images.lib['toolsDocumentInfo'], wx.NullBitmap, shortHelp="Document information and notes...", longHelp="Show document information and notes")
        self.toolbar.AddTool(ID_toolsDocumentReport, "Report", images.lib['toolsDocumentReport'], wx.NullBitmap, shortHelp="Analysis report", longHelp="Make analysis report for current document")
        self.toolbar.AddTool(ID_toolsDocumentExport, "Export", images.lib['toolsDocumentExport'], wx.NullBitmap, shortHelp="Export data...", longHelp="Export spectrum, peaklist or image")
        
        self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentInfo, id=ID_toolsDocumentInfo)
        self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentReport, id=ID_toolsDocumentReport)
        self.toolbar.Bind(wx.EVT_TOOL, self.onDocumentExport, id=ID_toolsDocumentExport)
    # ----
    
    
    def makeGUI(self):
        """Init all gui elements."""
        
        # make documents panel
        self.documentsPanel = panelDocuments(self, self.documents)
        
        # make spectrum panel
        self.spectrumPanel = panelSpectrum(self, self.documents)
        
        # make peaklist panel
        self.peaklistPanel = panelPeaklist(self)
        
        # init other tools
        self.processingPanel = None
        self.calibrationPanel = None
        self.periodicTablePanel = None
        self.massCalculatorPanel = None
        self.massToFormulaPanel = None
        self.massDefectPlotPanel = None
        self.massFilterPanel = None
        self.compoundsSearchPanel = None
        self.peakDifferencesPanel = None
        self.comparePeaklistsPanel = None
        self.spectrumGeneratorPanel = None
        self.envelopeFitPanel = None
        self.sequencePanel = None
        self.mascotPanel = None
        self.profoundPanel = None
        self.prospectorPanel = None
        self.documentInfoPanel = None
        self.documentExportPanel = None
        
        # manage frames
        self.AUIManager = wx.aui.AuiManager()
        self.AUIManager.SetManagedWindow(self)
        self.AUIManager.SetDockSizeConstraint(0.5, 0.5)
        
        self.AUIManager.AddPane(self.documentsPanel, wx.aui.AuiPaneInfo().Name("documents").
            Left().MinSize((195,100)).Caption("Opened Documents").CaptionVisible(False).
            Gripper(config.main['unlockGUI']).GripperTop(True).
            CloseButton(False).PaneBorder(False))
        
        self.AUIManager.AddPane(self.spectrumPanel, wx.aui.AuiPaneInfo().Name("plot").
            CentrePane().MinSize((300,100)).Caption("Spectrum Viewer").CaptionVisible(False).
            CloseButton(False).PaneBorder(False))
        
        self.AUIManager.AddPane(self.peaklistPanel, wx.aui.AuiPaneInfo().Name("peaklist").
            Right().MinSize((195,100)).Caption("Current Peak List").CaptionVisible(False).
            Gripper(config.main['unlockGUI']).GripperTop(True).
            CloseButton(False).PaneBorder(False))
        
        # show panels
        self.documentsPanel.Show(True)
        self.spectrumPanel.Show(True)
        self.peaklistPanel.Show(True)
        
        # set frame manager properties
        artProvider = self.AUIManager.GetArtProvider()
        #pdb.set_trace()
        artProvider.SetColour(wx.aui.AUI_DOCKART_SASH_COLOUR, self.documentsPanel.GetBackgroundColour())
        artProvider.SetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR, self.documentsPanel.GetBackgroundColour())
        artProvider.SetMetric(wx.aui.AUI_DOCKART_SASH_SIZE, mwx.SASH_SIZE)
        artProvider.SetMetric(wx.aui.AUI_DOCKART_GRIPPER_SIZE, mwx.GRIPPER_SIZE)
        if mwx.SASH_COLOUR:
            self.SetOwnBackgroundColour(mwx.SASH_COLOUR)
            artProvider.SetColour(wx.aui.AUI_DOCKART_SASH_COLOUR, mwx.SASH_COLOUR)
        
        # set last layout
        self.onWindowLayout(layout=config.main['layout'])
    # ----
    
    
    
    # COMMON EVENTS
    
    def onQuit(self, evt):
        """Close all documents and quit application."""
        
        # close all documents
        if not self.onDocumentCloseAll():
            return
        
        # save panels' sizes
        config.main['documentsWidth'], config.main['documentsHeight'] = self.documentsPanel.GetSize()
        config.main['peaklistWidth'], config.main['peaklistHeight'] = self.peaklistPanel.GetSize()
        
        # save config
        config.saveConfig()
        
        # quit application
        evt.Skip()
        self.Destroy()
    # ----
    
    
    def onSize(self, evt):
        """Remember application frame size."""
        
        # get frame size
        config.main['appMaximized'] = int(self.IsMaximized())
        if not self.IsMaximized():
            size = self.GetSize()
            config.main['appWidth'] = size[0]
            config.main['appHeight'] = size[1]
        
        evt.Skip()
    # ----
    
    
    def onError(self, type, value, tb):
        """Catch exception and show error report."""
        
        # get exception
        exception = traceback.format_exception(type, value, tb)
        exception = '\n'.join(exception)
        
        # show error message
        wx.Bell()
        dlg = dlgError(self, exception)
        dlg.ShowModal()
        dlg.Destroy()
    # ----
    
    
    def onPreferences(self, evt):
        """Show mMass preferences."""
        
        dlg = dlgPreferences(self)
        dlg.ShowModal()
        dlg.Destroy()
    # ----
    
    
    def onServerCommand(self, command):
        """Process command from TCP server."""
        
        # strip command
        command = command.strip()
        
        # close app
        if command.lower() in ['exit', 'quit']:
            wx.CallAfter(self.Close)
            return
        
        # open document
        if command and not command in ['mmass.exe', 'mmass.py']:
            wx.CallAfter(self.onDocumentOpen, None, command)
            return
    # ----
    
    
    
    # DOCUMENT
    
    def onDocumentLoaded(self, select=True):
        """Update GUI after document loaded."""
        
        # clear visibility history
        self.documentsSoloCurrent = None
        self.documentsSoloPrevious = {}
        
        # append document
        self.spectrumPanel.appendLastSpectrum()
        self.documentsPanel.appendLastDocument()
        
        # select document
        if select:
            self.documentsPanel.selectDocument(-1)
        
        # update compare panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
        
        # update processing panel
        if self.processingPanel:
            self.processingPanel.updateAvailableDocuments()
        
        # update mass defect plot panel
        if self.massDefectPlotPanel:
            self.massDefectPlotPanel.updateDocuments()
    # ----
    
    
    def onDocumentSelected(self, docIndex):
        """Set current document."""
        
        # get document and application title
        if docIndex != None:
            docData = self.documents[docIndex]
            title = 'mMass - %s' % (docData.title)
            if docData.dirty:
                title += ' *'
        else:
            docData = None
            title = 'mMass'
        
        # update app title
        self.SetTitle(title)
        
        # update panels
        if docIndex != self.currentDocument:
            
            # set current document
            self.currentDocument = docIndex
            self.currentSequence = None
            
            # update spectrum panel
            self.spectrumPanel.selectSpectrum(docIndex, refresh=False)
            
            # update peaklist panel
            self.peaklistPanel.setData(docData)
            
            # update processing panel
            if self.processingPanel:
                self.processingPanel.setData(docData)
            
            # update calibration panel
            if self.calibrationPanel:
                self.calibrationPanel.setData(docData)
            
            # update mass to formula panel
            if self.massToFormulaPanel:
                self.massToFormulaPanel.setData(docData)
            
            # update mass defect plot panel
            if self.massDefectPlotPanel:
                self.massDefectPlotPanel.setData(docData)
            
            # update mass filter panel
            if self.massFilterPanel:
                self.massFilterPanel.setData(docData)
            
            # update compounds panel
            if self.compoundsSearchPanel:
                self.compoundsSearchPanel.setData(docData)
            
            # update differences panel
            if self.peakDifferencesPanel:
                self.peakDifferencesPanel.setData(docData)
            
            # update spectrum generator panel
            if self.spectrumGeneratorPanel:
                self.spectrumGeneratorPanel.setData(docData)
            
            # update envelope fit panel
            if self.envelopeFitPanel:
                self.envelopeFitPanel.setData(docData)
            
            # update sequence panel
            if self.sequencePanel:
                self.sequencePanel.setData(None)
            
            # update mascot panel
            if self.mascotPanel:
                self.mascotPanel.setData(docData)
            
            # update profound panel
            if self.profoundPanel:
                self.profoundPanel.setData(docData)
            
            # update prospector panel
            if self.prospectorPanel:
                self.prospectorPanel.setData(docData)
            
            # update document info panel
            if self.documentInfoPanel:
                self.documentInfoPanel.setData(docData)
            
            # update menubar and toolbar
            self.updateControls()
    # ----
    
    
    def onDocumentChanged(self, items=()):
        """Document content has changed."""
        
        # check selection
        if self.currentDocument is None:
            return
        
        # update spectrum panel
        if 'spectrum' in items:
            self.spectrumPanel.updateSpectrum(self.currentDocument)
        
        # update peaklist panel
        if 'spectrum' in items:
            self.peaklistPanel.updatePeakList()
        
        # update title-dependent panels
        if 'doctitle' in items:
            self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
            
            # update processing panel
            if self.processingPanel:
                self.processingPanel.updateAvailableDocuments()
        
        # update documents panel
        if 'notations' in items:
            self.documentsPanel.updateAnnotations(self.currentDocument)
            for seqIndex in range(len(self.documents[self.currentDocument].sequences)):
                self.documentsPanel.updateSequenceMatches(self.currentDocument, seqIndex)
        if 'annotations' in items:
            self.documentsPanel.updateAnnotations(self.currentDocument, expand=True)
        if 'sequences' in items:
            self.documentsPanel.updateSequences(self.currentDocument)
        if 'seqtitle' in items:
            self.documentsPanel.updateSequenceTitle(self.currentDocument, self.currentSequence)
        if 'matches' in items:
            self.documentsPanel.updateSequenceMatches(self.currentDocument, self.currentSequence, expand=True)
        
        # update notation marks
        if 'notations' in items \
        or 'annotations' in items \
        or 'sequences' in items \
        or 'matches' in items:
            self.updateNotationMarks()
        
        # update data-dependent panels
        if 'spectrum' in items:
            
            docData = self.documents[self.currentDocument]
            
            # update document info panel
            if self.documentInfoPanel:
                self.documentInfoPanel.setData(docData)
            
            # update mascot panel
            if self.mascotPanel:
                self.mascotPanel.setData(docData)
            
            # update profound panel
            if self.profoundPanel:
                self.profoundPanel.setData(docData)
            
            # update prospector panel
            if self.prospectorPanel:
                self.prospectorPanel.setData(docData)
            
            # update differences panel
            if self.peakDifferencesPanel:
                self.peakDifferencesPanel.setData(docData)
            
            # update spectrum generator panel
            if self.spectrumGeneratorPanel:
                self.spectrumGeneratorPanel.setData(docData)
            
            # update envelope fit panel
            if self.envelopeFitPanel:
                self.envelopeFitPanel.setData(docData)
            
            # update mass defect plot panel
            if self.massDefectPlotPanel:
                self.massDefectPlotPanel.setData(docData)
            
            # update sequence panel
            if self.sequencePanel:
                self.sequencePanel.clearMatches()
            
            # update compounds panel
            if self.compoundsSearchPanel:
                self.compoundsSearchPanel.clearMatches()
            
            # update mass filter panel
            if self.massFilterPanel:
                self.massFilterPanel.clearMatches()
        
        # update compare peaklists tool
        if 'spectrum' in items \
        or 'notations' in items \
        or 'annotations' in items \
        or 'sequences' in items \
        or 'matches' in items:
            if self.comparePeaklistsPanel:
                self.comparePeaklistsPanel.setData(self.documents)
        
        # disable undo
        if 'sequence' in items:
            self.documents[self.currentDocument].backup(None)
        
        # set document status
        self.documents[self.currentDocument].dirty = True
        self.documentsPanel.updateDocumentTitle(self.currentDocument)
        
        # update app title
        title = 'mMass - %s *' % (self.documents[self.currentDocument].title)
        self.SetTitle(title)
        
        # update controls
        self.updateControls()
    # ----
    
    
    def onDocumentChangedMulti(self, indexes=[], items=()):
        """Multiple documents content has changed (not all changes are covered!!!)."""
        
        # check selection
        if not indexes:
            return
        
        # set documents dirty
        for docIndex in indexes:
            self.documents[docIndex].dirty = True
            self.documentsPanel.updateDocumentTitle(docIndex)
        
        # update spectrum panel
        if 'spectrum' in items:
            for docIndex in indexes:
                self.spectrumPanel.updateSpectrum(docIndex, refresh=False)
        
        # update documents panel
        if 'notations' in items or 'annotations' in items:
            for docIndex in indexes:
                self.documentsPanel.updateAnnotations(docIndex)
        if 'notations' in items or 'matches' in items:
            for docIndex in indexes:
                for seqIndex in range(len(self.documents[docIndex].sequences)):
                    self.documentsPanel.updateSequenceMatches(docIndex, seqIndex)
        
        # update compare peaklists panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
        
        # update current document
        if self.currentDocument in indexes:
            
            docData = self.documents[self.currentDocument]
            
            # update peaklist panel
            self.peaklistPanel.updatePeakList()
            
            # update document info panel
            if self.documentInfoPanel:
                self.documentInfoPanel.setData(docData)
            
            # update mascot panel
            if self.mascotPanel:
                self.mascotPanel.setData(docData)
            
            # update profound panel
            if self.profoundPanel:
                self.profoundPanel.setData(docData)
            
            # update prospector panel
            if self.prospectorPanel:
                self.prospectorPanel.setData(docData)
            
            # update differences panel
            if self.peakDifferencesPanel:
                self.peakDifferencesPanel.setData(docData)
            
            # update spectrum generator panel
            if self.spectrumGeneratorPanel:
                self.spectrumGeneratorPanel.setData(docData)
            
            # update envelope fit panel
            if self.envelopeFitPanel:
                self.envelopeFitPanel.setData(docData)
            
            # update mass defect plot panel
            if self.massDefectPlotPanel:
                self.massDefectPlotPanel.setData(docData)
            
            # update sequence panel
            if self.sequencePanel:
                self.sequencePanel.clearMatches()
            
            # update compounds panel
            if self.compoundsSearchPanel:
                self.compoundsSearchPanel.clearMatches()
            
            # update mass filter panel
            if self.massFilterPanel:
                self.massFilterPanel.clearMatches()
            
            # update notation marks
            self.updateNotationMarks(refresh=False)
            
            # update app title
            title = 'mMass - %s *' % (self.documents[self.currentDocument].title)
            self.SetTitle(title)
            
            # update controls
            self.updateControls()
        
        # update spectrum
        self.spectrumPanel.refresh()
    # ----
    
    
    def onDocumentNew(self, evt=None, document=None, select=True):
        """Create blank document."""
        
        # make document
        if document is None:
            document = doc.document()
            document.title = 'Blank Document'
        
        # set colour
        document.colour = self.getFreeColour()
        
        # append document
        self.documents.append(document)
        
        # update gui
        self.onDocumentLoaded(select)
    # ----
    
    
    def onDocumentNewFromClipboard(self, evt=None):
        """Make new document from clipboard data."""
        
        # get data from clipboard
        success = False
        data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(data)
            wx.TheClipboard.Close()
        if not success:
            wx.Bell()
            return
        
        # get raw data
        rawData = data.GetText()
        if not rawData:
            wx.Bell()
            return
        
        # parse clipboard data
        while not self.importDocumentFromClipboard(rawData, dataType='profile'):
            dlg = dlgClipboardEditor(self, rawData)
            if dlg.ShowModal() == wx.ID_OK:
                rawData = dlg.data
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
    # ----
    
    
    def onDocumentDuplicate(self, evt=None):
        """Duplicate selected document."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return False
        
        # get selected document
        docData = copy.deepcopy(self.documents[self.currentDocument])
        
        # update document
        docData.format = 'mSD'
        docData.path = ''
        docData.dirty = True
        
        # append new document
        self.onDocumentNew(document=docData)
    # ----
    
    
    def onDocumentOpen(self, evt=None, path=None):
        """Open document."""
        
        # add path to queue
        if path:
            self.tmpDocumentQueue.append(path)
        
        # open dialog if no path specified
        else:
            lastDir = ''
            if os.path.exists(config.main['lastDir']):
                lastDir = config.main['lastDir']
            wildcard =  "All supported formats|fid;*.msd;*.baf;*.yep;*.mzData;*.mzdata*;*.mzXML;*.mzxml;*.mzML;*.mzml;*.xml;*.XML;*.mgf;*.MGF;*.txt;*.xy;*.asc|All files|*.*"
            dlg = wx.FileDialog(self, "Open Document", lastDir, "", wildcard=wildcard, style=wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                dlg.Destroy()
                self.tmpDocumentQueue += list(paths)
            else:
                dlg.Destroy()
                return
        
        # import documents in queue
        self.importDocumentQueue()
    # ----
    
    
    def onDocumentDropped(self, evt=None, paths=None):
        """Open dropped documents."""
        
        # get paths
        if evt != None:
            paths = evt.GetFiles()
        
        # open documents
        if paths:
            self.tmpDocumentQueue += list(paths)
            wx.CallAfter(self.importDocumentQueue)
    # ----
    
    
    def onDocumentRecent(self, evt):
        """Open recent document."""
        
        # get index
        indexes = {
            ID_documentRecent0:0,
            ID_documentRecent1:1,
            ID_documentRecent2:2,
            ID_documentRecent3:3,
            ID_documentRecent4:4,
            ID_documentRecent5:5,
            ID_documentRecent6:6,
            ID_documentRecent7:7,
            ID_documentRecent8:8,
            ID_documentRecent9:9,
        }
        
        # open file
        self.onDocumentOpen(path=config.recent[indexes[evt.GetId()]])
    # ----
    
    
    def onDocumentClearRecent(self, evt):
        """Clear recent items."""
        
        del config.recent[:]
        self.updateRecentFiles()
    # ----
    
    
    def onDocumentClose(self, evt=None, docIndex=None, review=True, selectPrevious=True):
        """Close current document."""
        
        # check document
        if docIndex is None:
            docIndex = self.currentDocument
        if docIndex is None:
            wx.Bell()
            return False
        
        # save unsaved document
        if review and self.documents[docIndex].dirty:
            
            # ensure selected
            if docIndex != self.currentDocument:
                if not self.documents[docIndex].visible:
                    self.onDocumentEnable(docIndex)
                self.documentsPanel.selectDocument(docIndex)
            
            # ask to save
            title = 'Do you want to save the changes you made in\nthe document "%s"?' % self.documents[docIndex].title
            message = "Your changes will be lost if you don't save them."
            buttons = [(ID_dlgDontSave, "Don't Save", 120, False, 40), (ID_dlgCancel, "Cancel", 80, False, 15), (ID_dlgSave, "Save", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            ID = dlg.ShowModal()
            if ID == ID_dlgDontSave:
                pass
            elif ID == ID_dlgSave:
                if not self.onDocumentSave():
                    return False
            else:
                return False
        
        # unblock colour
        colour = self.documents[docIndex].colour
        if colour in self.usedColours:
            del self.usedColours[self.usedColours.index(colour)]
        
        # clear visibility history
        self.documentsSoloCurrent = None
        self.documentsSoloPrevious = {}
        
        # delete document
        self.documentsPanel.selectDocument(None)
        self.documentsPanel.deleteDocument(docIndex)
        self.spectrumPanel.deleteSpectrum(docIndex)
        del self.documents[docIndex]
        
        # select previous visible document
        if selectPrevious:
            while docIndex > 0:
                docIndex -= 1
                if self.documents[docIndex].visible:
                    self.documentsPanel.selectDocument(docIndex)
                    break
        
        # update compare panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
        
        # update processing panel
        if self.processingPanel:
            self.processingPanel.updateAvailableDocuments()
        
        # update mass defect plot panel
        if self.massDefectPlotPanel:
            self.massDefectPlotPanel.updateDocuments()
        
        # update menubar and toolbar
        self.updateControls()
        
        # unchanged or saved document
        return True
    # ----
    
    
    def onDocumentCloseAll(self, evt=None):
        """Close all documents."""
        
        # close panels
        if self.processingPanel:
            self.processingPanel.Close()
        if self.calibrationPanel:
            self.calibrationPanel.Close()
        if self.periodicTablePanel:
            self.periodicTablePanel.Close()
        if self.massCalculatorPanel:
            self.massCalculatorPanel.Close()
        if self.massToFormulaPanel:
            self.massToFormulaPanel.Close()
        if self.massDefectPlotPanel:
            self.massDefectPlotPanel.Close()
        if self.massFilterPanel:
            self.massFilterPanel.Close()
        if self.compoundsSearchPanel:
            self.compoundsSearchPanel.Close()
        if self.peakDifferencesPanel:
            self.peakDifferencesPanel.Close()
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.Close()
        if self.spectrumGeneratorPanel:
            self.spectrumGeneratorPanel.Close()
        if self.envelopeFitPanel:
            self.envelopeFitPanel.Close()
        if self.sequencePanel:
            self.sequencePanel.Close()
        if self.mascotPanel:
            self.mascotPanel.Close()
        if self.profoundPanel:
            self.profoundPanel.Close()
        if self.prospectorPanel:
            self.prospectorPanel.Close()
        if self.documentInfoPanel:
            self.documentInfoPanel.Close()
        if self.documentExportPanel:
            self.documentExportPanel.Close()
        
        # get number of unsaved documents
        count = 0
        for document in self.documents:
            if document.dirty:
                count += 1
        
        # save unsaved documents
        review = True
        if count > 1:
            title = 'You have %d mMass documents with unsaved changes. Do you\nwant to review these changes before quitting?' % count
            message = "If you don't review your documents, all your changes will be lost."
            buttons = [(ID_dlgDiscard, "Discard Changes", 150, False, 40), (ID_dlgCancel, "Cancel", 80, False, 15), (ID_dlgReview, "Review Changes...", 160, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            ID = dlg.ShowModal()
            if ID == ID_dlgDiscard:
                review = False
            elif ID == ID_dlgReview:
                review = True
            else:
                return False
        
        # close documents
        while self.documents:
            docIndex = len(self.documents)-1
            if not self.onDocumentClose(docIndex=docIndex, review=review, selectPrevious=False):
                return False
        
        return True
    # ----
    
    
    def onDocumentSave(self, evt=None, docIndex=None):
        """Save current document."""
        
        # check document
        if docIndex is None:
            docIndex = self.currentDocument
        if docIndex is None:
            wx.Bell()
            return False
        
        # get document
        document = self.documents[docIndex]
        path = document.path
        
        # check doctype and ask to save
        if not path or document.format != 'mSD' or (evt and evt.GetId()==ID_documentSaveAs):
            
            # ensure document is selected
            if docIndex != self.currentDocument:
                if not self.documents[docIndex].visible:
                    self.onDocumentEnable(docIndex)
                self.documentsPanel.selectDocument(docIndex)
            
            # ask for name
            fileName = document.title+'.msd'
            dlg = wx.FileDialog(self, "Save", config.main['lastDir'], fileName, "mMass Spectrum Document|*.msd", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                config.main['lastDir'] = os.path.split(path)[0]
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
        
        # init processing gauge
        gauge = mwx.gaugePanel(self, 'Formating data...')
        gauge.show()
        
        # get document XML
        process = threading.Thread(target=self.runDocumentSave, kwargs={'docIndex':docIndex})
        process.start()
        while process.isAlive():
            gauge.pulse()
        
        # save file
        failed = False
        if self.currentDocumentXML:
            gauge.setLabel('Saving data...')
            try:
                with open(path, 'wb') as f:
                    f.write(self.currentDocumentXML.encode("utf-8"))
            except IOError:
                failed = True
        else:
            failed = True
        
        # close processing gauge
        gauge.close()
        
        # processing failed
        if failed:
            wx.Bell()
            
            # ensure document is selected
            if docIndex != self.currentDocument:
                if not self.documents[docIndex].visible:
                    self.onDocumentEnable(docIndex)
                self.documentsPanel.selectDocument(docIndex)
            
            # show error message
            dlg = mwx.dlgMessage(self, title="Unable to save the document.", message='Please ensure that you have sufficient permissions\nto write into the document folder.')
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # update document meta
        document.format = 'mSD'
        document.path = path
        document.dirty = False
        
        # update document title
        self.documentsPanel.updateDocumentTitle(docIndex)
        
        # update app title
        if docIndex == self.currentDocument:
            title = 'mMass - %s' % (self.documents[docIndex].title)
            self.SetTitle(title)
            self.updateControls()
        
        # update recent files
        self.updateRecentFiles(path)
        
        # document saved
        return True
    # ----
    
    
    def onDocumentSaveAll(self, evt=None):
        """Save all documents."""
        
        # save documents
        for docIndex, document in enumerate(self.documents):
            if document.dirty:
                self.onDocumentSave(docIndex=docIndex)
    # ----
    
    
    def onDocumentPrintSpectrum(self, evt):
        """Print spectrum."""
        
        # get spectrum printout
        printout = self.spectrumPanel.getPrintout(config.main['printQuality'], 'mMass Spectrum')
        
        # set printer defaults
        printData = wx.PrintData()
        printData.SetOrientation(wx.LANDSCAPE)
        printData.SetQuality(wx.PRINT_QUALITY_MEDIUM)
        pageSetup = wx.PageSetupDialogData()
        pageSetup.SetPrintData(printData)
        dlgPrintData = wx.PrintDialogData(pageSetup.GetPrintData())
        dlgPrintData.SetMinPage(1)
        dlgPrintData.SetMaxPage(1)
        printer = wx.Printer(dlgPrintData)
        
        # print
        if printer.Print(self, printout):
            printData = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
            pageSetup.SetPrintData(printData)
        
        # printing failed
        elif printer.GetLastError() == wx.PRINTER_ERROR:
            dlg = mwx.dlgMessage(self, title="Unable to print the spectrum.", message='Unknown error occured while printing.')
            dlg.ShowModal()
            dlg.Destroy()
            return False
    # ----
    
    
    def onDocumentReport(self, evt):
        """Print report."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # make report
        try:
            
            # get tmp folder
            tmpDir = tempfile.gettempdir()
            imagePath = os.path.join(tmpDir, 'mmass_spectrum.png')
            reportPath = os.path.join(tmpDir, 'mmass_report.html')
            
            # make spetrum file
            reportBitmap = self.spectrumPanel.getBitmap(600, 400, None)
            reportImage = reportBitmap.ConvertToImage()
            reportImage.SetOption(wx.IMAGE_OPTION_QUALITY, '100')
            reportImage.SetOption(wx.IMAGE_OPTION_RESOLUTION, '72')
            reportImage.SetOption(wx.IMAGE_OPTION_RESOLUTIONX, '72')
            reportImage.SetOption(wx.IMAGE_OPTION_RESOLUTIONY, '72')
            reportImage.SetOption(wx.IMAGE_OPTION_RESOLUTIONUNIT, '1')
            reportImage.SaveFile(imagePath, wx.BITMAP_TYPE_PNG)
            
            # make report file
            reportHTML = self.documents[self.currentDocument].report(image=imagePath)
            with open(reportPath, 'wb') as f:
                f.write(reportHTML.encode("utf-8"))
            
            # show report
            path = 'file://%s?%s' % (reportPath, time.time())
            webbrowser.open(path, autoraise=1)
            
        except IOError:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to create the report.", message='Unknown error occured while creating the report.')
            dlg.ShowModal()
            dlg.Destroy()
            return
    # ----
    
    
    def onDocumentExport(self, evt=None):
        """Show export panel."""
        
        # destroy panel
        if self.documentExportPanel and evt:
            self.documentExportPanel.Close()
            return
        
        # show panel
        if not self.documentExportPanel:
            self.documentExportPanel = panelDocumentExport(self)
            self.documentExportPanel.Centre()
            self.documentExportPanel.Show(True)
        
        self.documentExportPanel.Raise()
    # ----
    
    
    def onDocumentInfo(self, evt=None):
        """Show document information panel."""
        
        # check document
        if not self.documentInfoPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.documentInfoPanel and evt:
            self.documentInfoPanel.Close()
            return
        
        # show panel
        if not self.documentInfoPanel:
            self.documentInfoPanel = panelDocumentInfo(self)
            self.documentInfoPanel.Centre()
            self.documentInfoPanel.Show(True)
        
        # set current document
        if self.currentDocument != None:
            self.documentInfoPanel.setData(self.documents[self.currentDocument])
            self.documentInfoPanel.Raise()
        else:
            self.documentInfoPanel.setData(None)
            self.documentInfoPanel.Raise()
    # ----
    
    
    def onDocumentSelect(self, evt=None, docIndex=None):
        """Select document."""
        self.documentsPanel.selectDocument(docIndex)
    # ----
    
    
    def onDocumentEnable(self, docIndex):
        """Enable/disable selected document."""
        
        # clear visibility history
        self.documentsSoloCurrent = None
        self.documentsSoloPrevious = {}
        
        # set document visibility
        self.documents[docIndex].visible = not self.documents[docIndex].visible
        
        # update documents panel
        self.documentsPanel.enableDocument(docIndex, self.documents[docIndex].visible)
        
        # update spectrum panel
        self.spectrumPanel.updateSpectrumProperties(docIndex, refresh=(docIndex!=self.currentDocument))
        
        # unselect current document
        if docIndex == self.currentDocument:
            self.documentsPanel.selectDocument(None)
        
        # update compare panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
        
        # update mass defect plot panel
        if self.massDefectPlotPanel:
            self.massDefectPlotPanel.updateDocuments()
    # ----
    
    
    def onDocumentSolo(self, docIndex):
        """Disable all documents except one."""
        
        # remeber current visibility
        if self.documentsSoloCurrent is None:
            self.documentsSoloPrevious = {}
            for x, document in enumerate(self.documents):
                self.documentsSoloPrevious[x] = document.visible
        
        # new solo
        if docIndex != self.documentsSoloCurrent:
            
            # disable all documents
            for x, document in enumerate(self.documents):
                document.visible = False
                self.documentsPanel.enableDocument(x, False)
                self.spectrumPanel.updateSpectrumProperties(x, refresh=False)
            
            # enable the one
            self.documentsSoloCurrent = docIndex
            self.documents[docIndex].visible = True
            self.documentsPanel.enableDocument(docIndex, True)
            self.spectrumPanel.updateSpectrumProperties(docIndex, refresh=True)
            
            # select the one
            self.documentsPanel.selectDocument(docIndex)
        
        # revert to previous visibility
        else:
            
            # apply previous visibility
            for x, document in enumerate(self.documents):
                if x in self.documentsSoloPrevious:
                    document.visible = self.documentsSoloPrevious[x]
                    self.documentsPanel.enableDocument(x, document.visible)
                    self.spectrumPanel.updateSpectrumProperties(x, refresh=False)
            
            # refresh spectrum panel
            self.spectrumPanel.refresh()
            
            # select current document if visible
            if self.documents[docIndex].visible:
                self.documentsPanel.selectDocument(docIndex)
            else:
                self.documentsPanel.selectDocument(None)
            
            # clear visibility history
            self.documentsSoloCurrent = None
            self.documentsSoloPrevious = {}
        
        # update compare panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
    # ----
    
    
    def onDocumentFlip(self, evt):
        """Flip spectrum vertically."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # set document flipping
        self.documents[self.currentDocument].flipped = not self.documents[self.currentDocument].flipped
        
        # update spectrum panel
        self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
    # ----
    
    
    def onDocumentOffset(self, evt):
        """Offset spectrum."""
        
        # set offset for current document
        if evt.GetId() == ID_documentOffset and self.currentDocument != None:
            if config.spectrum['normalize']:
                wx.Bell()
                return
            dlg = dlgSpectrumOffset(self, self.documents[self.currentDocument].offset)
            if dlg.ShowModal() == wx.ID_OK:
                offset = dlg.getData()
                dlg.Destroy()
                self.documents[self.currentDocument].offset = offset
                self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
            else:
                dlg.Destroy()
        
        # clear offset for current document
        elif evt.GetId() == ID_documentClearOffset and self.currentDocument != None:
            self.documents[self.currentDocument].offset = [0,0]
            self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
        
        # clear offset for all documents
        elif evt.GetId() == ID_documentClearOffsets:
            for x, document in enumerate(self.documents):
                document.offset = [0,0]
                self.spectrumPanel.updateSpectrumProperties(x, refresh=False)
            self.spectrumPanel.refresh()
        
        # no document
        else:
            wx.Bell()
            return
    # ----
    
    
    def onDocumentColour(self, evt):
        """Change document colour."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # get current colour
        oldColour = self.documents[self.currentDocument].colour
        currentColour = wx.ColourData()
        currentColour.SetColour(oldColour)
        
        # show dialog and get colour
        dlg = wx.ColourDialog(self, currentColour)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            newColour = list(data.GetColour().Get())
            dlg.Destroy()
        else:
            return
        
        # update used colours
        if oldColour in self.usedColours:
            del self.usedColours[self.usedColours.index(oldColour)]
        self.usedColours.append(newColour)
        
        # set colour to document
        self.documents[self.currentDocument].colour = newColour
        
        # update documents panel
        self.documentsPanel.updateDocumentColour(self.currentDocument)
        
        # update spectrum panel
        self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
        
        # update compare panel
        if self.comparePeaklistsPanel:
            self.comparePeaklistsPanel.setData(self.documents)
        
        # update processing panel
        if self.processingPanel:
            self.processingPanel.updateAvailableDocuments()
        
        # update mass defect plot panel
        if self.massDefectPlotPanel:
            self.massDefectPlotPanel.updateDocuments()
    # ----
    
    
    def onDocumentStyle(self, evt):
        """Change document style."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # set document style
        if evt.GetId() == ID_documentStyleDot:
            self.documents[self.currentDocument].style = wx.DOT
        elif evt.GetId() == ID_documentStyleDash:
            self.documents[self.currentDocument].style = wx.SHORT_DASH
        elif evt.GetId() == ID_documentStyleDotDash:
            self.documents[self.currentDocument].style = wx.DOT_DASH
        else:
            self.documents[self.currentDocument].style = wx.SOLID
        
        # update spectrum panel
        self.spectrumPanel.updateSpectrumProperties(self.currentDocument)
    # ----
    
    
    def onDocumentNotationsDelete(self, evt=None):
        """Delete all annotations and sequence matches."""
        
        # check selection
        if self.currentDocument is None:
            return
        
        # backup annotations and matches
        self.documents[self.currentDocument].backup(('notations'))
        
        # delete annotations
        del self.documents[self.currentDocument].annotations[:]
        
        # delete sequence matches
        for seqIndex in range(len(self.documents[self.currentDocument].sequences)):
            del self.documents[self.currentDocument].sequences[seqIndex].matches[:]
        
        # update GUI
        self.onDocumentChanged(items=('notations'))
    # ----
    
    
    def onDocumentAnnotationsDelete(self, evt=None, annotIndex=None):
        """Delete annotations."""
        
        # check selection
        if self.currentDocument is None:
            return
        
        # delete annotations
        self.documents[self.currentDocument].backup(('annotations'))
        if annotIndex != None:
            del self.documents[self.currentDocument].annotations[annotIndex]
        else:
            del self.documents[self.currentDocument].annotations[:]
        
        # update GUI
        self.onDocumentChanged(items=('annotations'))
    # ----
    
    
    def onDocumentAnnotationsCalibrateBy(self, evt=None):
        """Use annotations for calibration."""
        
        # check selection
        if self.currentDocument is None:
            return
        
        # get annotations
        annotations = []
        for annotation in self.documents[self.currentDocument].annotations:
            if annotation.theoretical != None:
                annotations.append([annotation.label, annotation.theoretical, annotation.mz])
        if not annotations:
            wx.Bell()
            return
        
        # show calibration panel
        self.onToolsCalibration(references=annotations)
    # ----
    
    
    
    # VIEW
    
    def onView(self, evt):
        """Update view parameters in the spectrum."""
        
        # get ID
        ID = evt.GetId()
        
        # set new params
        if ID == ID_viewLegend:
            values = (1,0)
            config.spectrum['showLegend'] = values[bool(config.spectrum['showLegend'])]
            self.menubar.Check(ID_viewLegend, bool(config.spectrum['showLegend']))
        
        elif ID == ID_viewGrid:
            values = (1,0)
            config.spectrum['showGrid'] = values[bool(config.spectrum['showGrid'])]
            self.menubar.Check(ID_viewGrid, bool(config.spectrum['showGrid']))
        
        elif ID == ID_viewMinorTicks:
            values = (1,0)
            config.spectrum['showMinorTicks'] = values[bool(config.spectrum['showMinorTicks'])]
            self.menubar.Check(ID_viewMinorTicks, bool(config.spectrum['showMinorTicks']))
        
        elif ID == ID_viewDataPoints:
            values = (1,0)
            config.spectrum['showDataPoints'] = values[bool(config.spectrum['showDataPoints'])]
            self.menubar.Check(ID_viewDataPoints, bool(config.spectrum['showDataPoints']))
        
        elif ID == ID_viewPosBars:
            values = (1,0)
            config.spectrum['showPosBars'] = values[bool(config.spectrum['showPosBars'])]
            self.menubar.Check(ID_viewPosBars, bool(config.spectrum['showPosBars']))
        
        elif ID == ID_viewGel:
            values = (1,0)
            config.spectrum['showGel'] = values[bool(config.spectrum['showGel'])]
            self.menubar.Check(ID_viewGel, bool(config.spectrum['showGel']))
        
        elif ID == ID_viewGelLegend:
            values = (1,0)
            config.spectrum['showGelLegend'] = values[bool(config.spectrum['showGelLegend'])]
            self.menubar.Check(ID_viewGelLegend, bool(config.spectrum['showGelLegend']))
        
        elif ID == ID_viewTracker:
            values = (1,0)
            config.spectrum['showTracker'] = values[bool(config.spectrum['showTracker'])]
            self.menubar.Check(ID_viewTracker, bool(config.spectrum['showTracker']))
        
        elif ID == ID_viewLabels:
            values = (1,0)
            title = ("Show Labels", "Hide Labels")
            config.spectrum['showLabels'] = values[bool(config.spectrum['showLabels'])]
            self.menubar.SetLabel(ID_viewLabels, title[bool(config.spectrum['showLabels'])]+HK_viewLabels)
        
        elif ID == ID_viewTicks:
            values = (1,0)
            title = ("Show Ticks", "Hide Ticks")
            config.spectrum['showTicks'] = values[bool(config.spectrum['showTicks'])]
            self.menubar.SetLabel(ID_viewTicks, title[bool(config.spectrum['showTicks'])]+HK_viewTicks)
        
        elif ID == ID_viewLabelCharge:
            values = (1,0)
            config.spectrum['labelCharge'] = values[bool(config.spectrum['labelCharge'])]
            self.menubar.Check(ID_viewLabelCharge, bool(config.spectrum['labelCharge']))
        
        elif ID == ID_viewLabelGroup:
            values = (1,0)
            config.spectrum['labelGroup'] = values[bool(config.spectrum['labelGroup'])]
            self.menubar.Check(ID_viewLabelGroup, bool(config.spectrum['labelGroup']))
        
        elif ID == ID_viewLabelBgr:
            values = (1,0)
            config.spectrum['labelBgr'] = values[bool(config.spectrum['labelBgr'])]
            self.menubar.Check(ID_viewLabelBgr, bool(config.spectrum['labelBgr']))
        
        elif ID == ID_viewLabelAngle:
            values = (90,0)
            title = ("Vertical Labels", "Horizontal Labels")
            config.spectrum['labelAngle'] = values[bool(config.spectrum['labelAngle'])]
            self.menubar.SetLabel(ID_viewLabelAngle, title[bool(config.spectrum['labelAngle'])]+HK_viewLabelAngle)
        
        elif ID == ID_viewOverlapLabels:
            values = (1,0)
            config.spectrum['overlapLabels'] = values[bool(config.spectrum['overlapLabels'])]
            self.menubar.Check(ID_viewOverlapLabels, bool(config.spectrum['overlapLabels']))
        
        elif ID == ID_viewCheckLimits:
            values = (1,0)
            config.spectrum['checkLimits'] = values[bool(config.spectrum['checkLimits'])]
            self.menubar.Check(ID_viewCheckLimits, bool(config.spectrum['checkLimits']))
        
        elif ID == ID_viewAllLabels:
            values = (1,0)
            config.spectrum['showAllLabels'] = values[bool(config.spectrum['showAllLabels'])]
            self.menubar.Check(ID_viewAllLabels, bool(config.spectrum['showAllLabels']))
        
        elif ID == ID_viewNotations:
            values = (1,0)
            title = ("Show Notations", "Hide Notations")
            config.spectrum['showNotations'] = values[bool(config.spectrum['showNotations'])]
            self.menubar.SetLabel(ID_viewNotations, title[bool(config.spectrum['showNotations'])])
        
        elif ID == ID_viewNotationMarks:
            values = (1,0)
            config.spectrum['notationMarks'] = values[bool(config.spectrum['notationMarks'])]
            self.menubar.Check(ID_viewNotationMarks, bool(config.spectrum['notationMarks']))
        
        elif ID == ID_viewNotationLabels:
            values = (1,0)
            config.spectrum['notationLabels'] = values[bool(config.spectrum['notationLabels'])]
            self.menubar.Check(ID_viewNotationLabels, bool(config.spectrum['notationLabels']))
        
        elif ID == ID_viewNotationMz:
            values = (1,0)
            config.spectrum['notationMZ'] = values[bool(config.spectrum['notationMZ'])]
            self.menubar.Check(ID_viewNotationMz, bool(config.spectrum['notationMZ']))
        
        elif ID == ID_viewAutoscale:
            values = (1,0)
            config.spectrum['autoscale'] = values[bool(config.spectrum['autoscale'])]
            self.menubar.Check(ID_viewAutoscale, bool(config.spectrum['autoscale']))
        
        elif ID == ID_viewNormalize:
            values = (1,0)
            config.spectrum['normalize'] = values[bool(config.spectrum['normalize'])]
            self.menubar.Check(ID_viewNormalize, bool(config.spectrum['normalize']))
        
        # update spectrum
        self.spectrumPanel.updateCanvasProperties(ID)
        self.spectrumPanel.spectrumCanvas.SetFocus()
        
        # update spectrum generator panel
        if self.spectrumGeneratorPanel:
            self.spectrumGeneratorPanel.updateCanvasProperties()
        
        # update envelope fit panel
        if self.envelopeFitPanel:
            self.envelopeFitPanel.updateCanvasProperties()
    # ----
    
    
    def onViewSpectrumRuler(self, evt):
        """Show / hide cursor info values."""
        
        # get ID
        ID = evt.GetId()
        
        # set items
        items = {
            ID_viewSpectrumRulerMz: 'mz',
            ID_viewSpectrumRulerDist: 'dist',
            ID_viewSpectrumRulerPpm: 'ppm',
            ID_viewSpectrumRulerZ: 'z',
            ID_viewSpectrumRulerCursorMass: 'cmass',
            ID_viewSpectrumRulerParentMass: 'pmass',
            ID_viewSpectrumRulerArea: 'area'
        }
        
        # change config
        item = items[ID]
        if item in config.main['cursorInfo']:
            del config.main['cursorInfo'][config.main['cursorInfo'].index(item)]
        else:
            config.main['cursorInfo'].append(item)
        
        # update menubar
        self.menubar.Check(ID, bool(item in config.main['cursorInfo']))
    # ----
    
    
    def onViewPeaklistColumns(self, evt):
        """Show / hide peaklist columns."""
        
        # get ID
        ID = evt.GetId()
        
        # set items
        items = {
            ID_viewPeaklistColumnMz: 'mz',
            ID_viewPeaklistColumnAi: 'ai',
            ID_viewPeaklistColumnInt: 'int',
            ID_viewPeaklistColumnBase: 'base',
            ID_viewPeaklistColumnRel: 'rel',
            ID_viewPeaklistColumnSn: 'sn',
            ID_viewPeaklistColumnZ: 'z',
            ID_viewPeaklistColumnMass: 'mass',
            ID_viewPeaklistColumnFwhm: 'fwhm',
            ID_viewPeaklistColumnResol: 'resol',
            ID_viewPeaklistColumnGroup: 'group',
        }
        
        # change config
        item = items[ID]
        columns = config.main['peaklistColumns'][:]
        if item in columns:
            del columns[columns.index(item)]
        else:
            columns.append(item)
        
        # ensure at least one item is present and right order
        if len(columns) > 0:
            config.main['peaklistColumns'] = []
            if 'mz' in columns:
                config.main['peaklistColumns'].append('mz')
            if 'ai' in columns:
                config.main['peaklistColumns'].append('ai')
            if 'int' in columns:
                config.main['peaklistColumns'].append('int')
            if 'base' in columns:
                config.main['peaklistColumns'].append('base')
            if 'rel' in columns:
                config.main['peaklistColumns'].append('rel')
            if 'sn' in columns:
                config.main['peaklistColumns'].append('sn')
            if 'z' in columns:
                config.main['peaklistColumns'].append('z')
            if 'mass' in columns:
                config.main['peaklistColumns'].append('mass')
            if 'fwhm' in columns:
                config.main['peaklistColumns'].append('fwhm')
            if 'resol' in columns:
                config.main['peaklistColumns'].append('resol')
            if 'group' in columns:
                config.main['peaklistColumns'].append('group')
        else:
            wx.Bell()
        
        # update menubar
        self.menubar.Check(ID, bool(item in config.main['peaklistColumns']))
        
        # update peaklist
        self.peaklistPanel.updatePeaklistColumns()
    # ----
    
    
    def onViewCanvasProperties(self, evt):
        """Show spectrum canvas properties dialog."""
        self.spectrumPanel.onCanvasProperties()
    # ----
    
    
    def onViewRange(self, evt):
        """Set current ranges for spectrum canvas."""
        
        # get current range
        if not config.internal['canvasXrange']:
            massRange = self.spectrumPanel.getCurrentRange()
            minX = '%.0f' % massRange[0]
            maxX = '%.0f' % massRange[1]
            massRange = (minX, maxX)
        else:
            massRange = config.internal['canvasXrange']
        
        # show range dialog
        dlg = dlgViewRange(self, massRange)
        if dlg.ShowModal() == wx.ID_OK:
            massRange = dlg.data
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # set new range
        self.spectrumPanel.setCanvasRange(xAxis=massRange)
        config.internal['canvasXrange'] = massRange
    # ----
    
    
    
    # MAIN TOOLS
    
    def onToolsUndo(self, evt):
        """Undo last operation."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # undo last operation
        items = self.documents[self.currentDocument].restore()
        if not items:
            wx.Bell()
            return
        
        # update gui
        self.onDocumentChanged(items=items)
    # ----
    
    
    def onToolsSpectrum(self, evt):
        """Toggle spectrum tools."""
        
        # get ID
        ID = evt.GetId()
        
        # set tool in menubar
        if ID == ID_toolsRuler:
            self.menubar.Check(ID_toolsRuler, True)
            tool = 'ruler'
        elif ID == ID_toolsLabelPeak:
            tool = 'labelpeak'
            self.menubar.Check(ID_toolsLabelPeak, True)
        elif ID == ID_toolsLabelPoint:
            tool = 'labelpoint'
            self.menubar.Check(ID_toolsLabelPoint, True)
        elif ID == ID_toolsLabelEnvelope:
            self.menubar.Check(ID_toolsLabelEnvelope, True)
            tool = 'labelenvelope'
        elif ID == ID_toolsDeleteLabel:
            tool = 'deletelabel'
            self.menubar.Check(ID_toolsDeleteLabel, True)
        elif ID == ID_toolsOffset:
            self.menubar.Check(ID_toolsOffset, True)
            tool = 'offset'
        
        # set tool in spectrum
        self.spectrumPanel.setCurrentTool(tool)
        self.spectrumPanel.spectrumCanvas.SetFocus()
    # ----
    
    
    def onToolsProcessing(self, evt=None):
        """Show processing tools panel."""
        
        # check document
        if not self.processingPanel and not self.documents:
            wx.Bell()
            return
        
        # destroy panel
        if self.processingPanel and evt and evt.GetId()==ID_toolsProcessing:
            self.processingPanel.Close()
            return
        
        # init panel
        if not self.processingPanel:
            self.processingPanel = panelProcessing(self)
        
        # show selected tool
        tool = 'peakpicking'
        if evt and evt.GetId() == ID_processingPeakpicking:
            tool = 'peakpicking'
        elif evt and evt.GetId() == ID_processingDeisotoping:
            tool = 'deisotoping'
        elif evt and evt.GetId() == ID_processingDeconvolution:
            tool = 'deconvolution'
        elif evt and evt.GetId() == ID_processingBaseline:
            tool = 'baseline'
        elif evt and evt.GetId() == ID_processingSmoothing:
            tool = 'smoothing'
        elif evt and evt.GetId() == ID_processingCrop:
            tool = 'crop'
        elif evt and evt.GetId() == ID_processingMath:
            tool = 'math'
        elif evt and evt.GetId() == ID_processingBatch:
            tool = 'batch'
        
        self.processingPanel.onToolSelected(tool=tool)
        self.processingPanel.Centre()
        self.processingPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.processingPanel.setData(docData)
        self.processingPanel.Raise()
    # ----
    
    
    def onToolsSequence(self, evt=None):
        """Show sequence tools panel."""
        
        # check document
        if not self.sequencePanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # select first sequence in document or make new
        if not self.sequencePanel and self.currentDocument != None and self.currentSequence is None and evt and evt.GetId()==ID_toolsSequence:
            if self.documents[self.currentDocument].sequences:
                self.documentsPanel.selectSequence(self.currentDocument, 0)
            else:
                self.onSequenceNew()
                return
        
        # disable tools if no sequence selected
        if not self.sequencePanel and self.currentSequence is None and evt and evt.GetId()!=ID_toolsSequence:
            wx.Bell()
            return
        
        # destroy panel
        if self.sequencePanel and evt and evt.GetId()==ID_toolsSequence:
            self.sequencePanel.Close()
            return
        
        # init panel
        if not self.sequencePanel:
            self.sequencePanel = panelSequence(self)
        
        # show selected tool
        tool = 'editor'
        if evt and evt.GetId() == ID_sequenceEditor:
            tool = 'editor'
        elif evt and evt.GetId() == ID_sequenceModifications:
            tool = 'modifications'
        elif evt and evt.GetId() == ID_sequenceDigest:
            tool = 'digest'
        elif evt and evt.GetId() == ID_sequenceFragment:
            tool = 'fragment'
        elif evt and evt.GetId() == ID_sequenceSearch:
            tool = 'search'
        
        self.sequencePanel.onToolSelected(tool=tool)
        self.sequencePanel.Centre()
        self.sequencePanel.Show(True)
        
        # get current document sequence
        seqData = None
        if self.currentDocument != None and self.currentSequence != None:
            seqData = self.documents[self.currentDocument].sequences[self.currentSequence]
        
        # set data
        self.sequencePanel.setData(seqData)
        self.sequencePanel.Raise()
    # ----
    
    
    def onToolsCalibration(self, evt=None, references=None):
        """Show calibration tools panel."""
        
        # check document
        if not self.calibrationPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.calibrationPanel and evt:
            self.calibrationPanel.Close()
            return
        
        # init panel
        if not self.calibrationPanel:
            self.calibrationPanel = panelCalibration(self)
            self.calibrationPanel.Centre()
            self.calibrationPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.calibrationPanel.setData(docData, references)
        self.calibrationPanel.Raise()
    # ----
    
    
    def onToolsPeriodicTable(self, evt=None):
        """Show periodic table panel."""
        
        # destroy panel
        if self.periodicTablePanel and evt:
            self.periodicTablePanel.Close()
            return
        
        # show periodic table
        if not self.periodicTablePanel:
            self.periodicTablePanel = panelPeriodicTable(self)
            self.periodicTablePanel.Centre()
            self.periodicTablePanel.Show(True)
        
        # show panel
        self.periodicTablePanel.Raise()
    # ----
    
    
    def onToolsMassCalculator(self, evt=None, formula=None, charge=None, agentFormula='H', agentCharge=1, fwhm=None):
        """Show mass calculation tool panel."""
        
        # destroy panel
        if self.massCalculatorPanel and evt:
            self.massCalculatorPanel.Close()
            return
        
        # init panel
        if not self.massCalculatorPanel:
            self.massCalculatorPanel = panelMassCalculator(self)
            self.massCalculatorPanel.Centre()
            self.massCalculatorPanel.Show(True)
        
        # set no formula
        if formula is None:
            self.massCalculatorPanel.setData(None)
            self.massCalculatorPanel.Raise()
        
        # set current formula
        else:
            fwhm = None
            intensity = None
            baseline = None
            
            # try to approximate intensity and baseline
            if self.currentDocument != None and charge != None and self.documents[self.currentDocument].spectrum.hasprofile():
                compound = mspy.compound(formula)
                mz = compound.mz(charge=charge, agentFormula=agentFormula, agentCharge=agentCharge)[0]
                peak = mspy.labelpeak(
                    signal = self.documents[self.currentDocument].spectrum.profile,
                    mz = mz,
                    pickingHeight = 0.95
                )
                if peak:
                    intensity = peak.ai
                    baseline = peak.base
                    fwhm = peak.fwhm
            
            # set data
            self.massCalculatorPanel.setData(
                formula = formula,
                charge = charge,
                agentFormula = agentFormula,
                agentCharge = agentCharge,
                fwhm = fwhm,
                intensity = intensity,
                baseline = baseline
            )
            
            # raise panel
            self.massCalculatorPanel.Raise()
    # ----
    
    
    def onToolsMassToFormula(self, evt=None, mass=None, charge=None, tolerance=None, units=None, agentFormula=None):
        """Show mass to formula tool panel."""
        
        # destroy panel
        if self.massToFormulaPanel and evt:
            self.massToFormulaPanel.Close()
            return
        
        # init panel
        if not self.massToFormulaPanel:
            self.massToFormulaPanel = panelMassToFormula(self)
            self.massToFormulaPanel.Centre()
            self.massToFormulaPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.massToFormulaPanel.setData(document=docData, mass=mass, charge=charge, tolerance=tolerance, units=units, agentFormula=agentFormula)
        self.massToFormulaPanel.Raise()
    # ----
    
    
    def onToolsMassDefectPlot(self, evt=None):
        """docstring for onToolsMassDefectPlot"""
        
        # check document
        if not self.massDefectPlotPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.massDefectPlotPanel and evt:
            self.massDefectPlotPanel.Close()
            return
        
        # init panel
        if not self.massDefectPlotPanel:
            self.massDefectPlotPanel = panelMassDefectPlot(self)
            self.massDefectPlotPanel.Centre()
            self.massDefectPlotPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.massDefectPlotPanel.setData(docData)
        self.massDefectPlotPanel.Raise()
    # ----
    
    
    def onToolsMassFilter(self, evt=None):
        """Show mass filter tool panel."""
        
        # check document
        if not self.massFilterPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.massFilterPanel and evt:
            self.massFilterPanel.Close()
            return
        
        # init panel
        if not self.massFilterPanel:
            self.massFilterPanel = panelMassFilter(self)
            self.massFilterPanel.Centre()
            self.massFilterPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.massFilterPanel.setData(docData)
        self.massFilterPanel.Raise()
    # ----
    
    
    def onToolsCompoundsSearch(self, evt=None):
        """Show compounds search tool panel."""
        
        # check document
        if not self.compoundsSearchPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.compoundsSearchPanel and evt:
            self.compoundsSearchPanel.Close()
            return
        
        # init panel
        if not self.compoundsSearchPanel:
            self.compoundsSearchPanel = panelCompoundsSearch(self)
            self.compoundsSearchPanel.Centre()
            self.compoundsSearchPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.compoundsSearchPanel.setData(docData)
        self.compoundsSearchPanel.Raise()
    # ----
    
    
    def onToolsPeakDifferences(self, evt=None):
        """Show differences tool panel."""
        
        # check document
        if not self.peakDifferencesPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.peakDifferencesPanel and evt:
            self.peakDifferencesPanel.Close()
            return
        
        # init panel
        if not self.peakDifferencesPanel:
            self.peakDifferencesPanel = panelPeakDifferences(self)
            self.peakDifferencesPanel.Centre()
            self.peakDifferencesPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set current document
        self.peakDifferencesPanel.setData(docData)
        self.peakDifferencesPanel.Raise()
    # ----
    
    
    def onToolsComparePeaklists(self, evt=None):
        """Show compare peaklists tool panel."""
        
        # check documents
        if not self.comparePeaklistsPanel and not self.documents:
            wx.Bell()
            return
        
        # destroy panel
        if self.comparePeaklistsPanel and evt:
            self.comparePeaklistsPanel.Close()
            return
        
        # init panel
        if not self.comparePeaklistsPanel:
            self.comparePeaklistsPanel = panelComparePeaklists(self)
            self.comparePeaklistsPanel.Centre()
            self.comparePeaklistsPanel.Show(True)
            try: wx.SafeYield()
            except: pass
        
        # set documents
        self.comparePeaklistsPanel.setData(self.documents)
        self.comparePeaklistsPanel.Raise()
    # ----
    
    
    def onToolsSpectrumGenerator(self, evt=None):
        """Show spectrum generator tool panel."""
        
        # check document
        if not self.spectrumGeneratorPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.spectrumGeneratorPanel and evt:
            self.spectrumGeneratorPanel.Close()
            return
        
        # init panel
        if not self.spectrumGeneratorPanel:
            self.spectrumGeneratorPanel = panelSpectrumGenerator(self)
            self.spectrumGeneratorPanel.Centre()
            self.spectrumGeneratorPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.spectrumGeneratorPanel.setData(docData)
        self.spectrumGeneratorPanel.Raise()
    # ----
    
    
    def onToolsEnvelopeFit(self, evt=None, formula=None, sequence=None, charge=None, scale=None):
        """Show envelope fit panel."""
        
        # check document
        if not self.envelopeFitPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.envelopeFitPanel and evt:
            self.envelopeFitPanel.Close()
            return
        
        # init panel
        if not self.envelopeFitPanel:
            self.envelopeFitPanel = panelEnvelopeFit(self)
            self.envelopeFitPanel.Centre()
            self.envelopeFitPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # get data from sequence
        if sequence != None:
            formula = sequence.formula()
            if scale is None and config.envelopeFit['loss'] == 'H' and config.envelopeFit['gain'] == 'H{2}':
                scale = (0, len(sequence) - sequence.count('P') - 1)
        
        # set data
        self.envelopeFitPanel.setData(document=docData, formula=formula, charge=charge, scale=scale)
        self.envelopeFitPanel.Raise()
    # ----
    
    
    def onToolsMascot(self, evt=None):
        """Show Mascot search panel."""
        
        # check document
        if not self.mascotPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.mascotPanel and evt and evt.GetId()==ID_toolsMascot:
            self.mascotPanel.Close()
            return
        
        # init panel
        if not self.mascotPanel:
            self.mascotPanel = panelMascot(self)
        
        # show selected tool
        tool = 'pmf'
        if evt and evt.GetId() == ID_mascotPMF:
            tool = 'pmf'
        elif evt and evt.GetId() == ID_mascotMIS:
            tool = 'mis'
        elif evt and evt.GetId() == ID_mascotSQ:
            tool = 'sq'
        elif self.currentDocument != None and self.documents[self.currentDocument].spectrum.precursorMZ:
            tool = 'mis'
        
        self.mascotPanel.onToolSelected(tool=tool)
        self.mascotPanel.Centre()
        self.mascotPanel.Show(True)
        try: wx.SafeYield()
        except: pass
        self.mascotPanel.updateServerParams()
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.mascotPanel.setData(docData)
        self.mascotPanel.Raise()
    # ----
    
    
    def onToolsProfound(self, evt=None):
        """Show ProFound search panel."""
        
        # check document
        if not self.profoundPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.profoundPanel and evt and evt.GetId()==ID_toolsProfound:
            self.profoundPanel.Close()
            return
        
        # init panel
        if not self.profoundPanel:
            self.profoundPanel = panelProfound(self)
            self.profoundPanel.onToolSelected(tool='pmf')
            self.profoundPanel.Centre()
            self.profoundPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.profoundPanel.setData(docData)
        self.profoundPanel.Raise()
    # ----
    
    
    def onToolsProspector(self, evt=None):
        """Show MS-Fit search panel."""
        
        # check document
        if not self.prospectorPanel and self.currentDocument is None:
            wx.Bell()
            return
        
        # destroy panel
        if self.prospectorPanel and evt and evt.GetId()==ID_toolsProspector:
            self.prospectorPanel.Close()
            return
        
        # init panel
        if not self.prospectorPanel:
            self.prospectorPanel = panelProspector(self)
        
        # show selected tool
        tool = 'msfit'
        if evt and evt.GetId() == ID_prospectorMSFit:
            tool = 'msfit'
        elif evt and evt.GetId() == ID_prospectorMSTag:
            tool = 'mstag'
        elif self.currentDocument != None and self.documents[self.currentDocument].spectrum.precursorMZ:
            tool = 'mstag'
        
        self.prospectorPanel.onToolSelected(tool=tool)
        self.prospectorPanel.Centre()
        self.prospectorPanel.Show(True)
        
        # get current document
        docData = None
        if self.currentDocument != None:
            docData = self.documents[self.currentDocument]
        
        # set data
        self.prospectorPanel.setData(docData)
        self.prospectorPanel.Raise()
    # ----
    
    
    def onToolsSwapData(self, evt=None):
        """Swap peaklist and spectrum data."""
        
        # check document
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # ask to process
        title = 'Do you really want to swap peaklist and spectrum data?'
        message = 'All the annotations and sequence matches will be lost.'
        buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Swap", 80, True, 0)]
        dlg = mwx.dlgMessage(self, title, message, buttons)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        
        # backup data
        self.documents[self.currentDocument].backup(('spectrum', 'notations'))
        
        # swap data
        self.documents[self.currentDocument].spectrum.swap()
        
        # delete annotations
        del self.documents[self.currentDocument].annotations[:]
        
        # delete sequence matches
        for sequence in self.documents[self.currentDocument].sequences:
            del sequence.matches[:]
        
        # update GUI
        self.onDocumentChanged(items=('spectrum', 'notations'))
    # ----
    
    
    
    # SEQUENCE
    
    def onSequenceSelected(self, seqIndex):
        """Set current sequence."""
        
        # get sequence
        if seqIndex != None:
            seqData = self.documents[self.currentDocument].sequences[seqIndex]
        else:
            seqData = None
        
        # update panels
        if seqIndex != self.currentSequence:
            
            # set current sequence
            self.currentSequence = seqIndex
            
            # update sequence panel
            if self.sequencePanel:
                self.sequencePanel.setData(seqData)
            
            # update menubar and toolbar
            self.updateControls()
    # ----
    
    
    def onSequenceNew(self, evt=None, seqData=None):
        """Append new sequence to current document."""
        
        # check selection
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # create new sequence
        if not seqData:
            seqData = mspy.sequence('', title='Untitled Sequence')
            seqData.matches = []
        
        # append sequence
        self.documents[self.currentDocument].sequences.append(seqData)
        
        # update documents panel
        self.documentsPanel.appendLastSequence(self.currentDocument)
        self.documentsPanel.selectSequence(self.currentDocument, -1)
        
        # set document status
        self.onDocumentChanged()
        
        # show sequence panel
        self.onToolsSequence()
    # ----
    
    
    def onSequenceImport(self, evt=None, path=None):
        """Import sequence from file to current document."""
        
        # check selection
        if self.currentDocument is None:
            wx.Bell()
            return
        
        # open dialog if no path specified
        if not path:
            lastDir = ''
            if os.path.exists(config.main['lastSeqDir']):
                lastDir = config.main['lastSeqDir']
            elif os.path.exists(config.main['lastDir']):
                lastDir = config.main['lastDir']
            wildcard =  "All supported formats|*.msd;*.fa;*.fsa;*.faa;*.fasta;|All files|*.*"
            dlg = wx.FileDialog(self, "Import Sequence", lastDir, "", wildcard=wildcard, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
        
        # check path
        if os.path.exists(path):
            config.main['lastSeqDir'] = os.path.split(path)[0]
        else:
            wx.Bell()
            return
        
        # get document type
        docType = self.getDocumentType(path)
        if not docType:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open the document.", message="Document type or structure can't be recognized. Selected format\nis probably unsupported.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # select sequences to open
        sequences = self.askForSequences(path, docType)
        if not sequences:
            return
        
        # append sequences
        for sequence in sequences:
            sequence.matches = []
            self.onSequenceNew(seqData=sequence)
    # ----
    
    
    def onSequenceDelete(self, evt=None):
        """Delete current sequence."""
        
        # check selection
        docIndex = self.currentDocument
        seqIndex = self.currentSequence
        if self.currentDocument is None or self.currentSequence is None:
            return
        
        # update sequence panel
        if self.sequencePanel:
            self.sequencePanel.setData(None)
        
        # update documents panel
        self.documentsPanel.deleteSequence(self.currentDocument, self.currentSequence)
        
        # delete sequence from document
        self.documents[docIndex].backup(('sequences'))
        del self.documents[docIndex].sequences[seqIndex]
        self.currentSequence = None
        
        # set document status
        self.onDocumentChanged()
    # ----
    
    
    def onSequenceMatchesDelete(self, evt=None, matchIndex=None):
        """Delete sequence matches."""
        
        # check selection
        if self.currentDocument is None or self.currentSequence is None:
            return
        
        # delete matches
        self.documents[self.currentDocument].backup(('sequences'))
        if matchIndex != None:
            del self.documents[self.currentDocument].sequences[self.currentSequence].matches[matchIndex]
        else:
            del self.documents[self.currentDocument].sequences[self.currentSequence].matches[:]
        
        # update GUI
        self.onDocumentChanged(items=('matches'))
    # ----
    
    
    def onSequenceMatchesCalibrateBy(self, evt=None):
        """Use sequence matches for calibration."""
        
        # check selection
        if self.currentDocument is None or self.currentSequence is None:
            return
        
        # get matches
        matches = []
        for match in self.documents[self.currentDocument].sequences[self.currentSequence].matches:
            matches.append([match.label, match.theoretical, match.mz])
        if not matches:
            wx.Bell()
            return
        
        # show calibration panel
        self.onToolsCalibration(references=matches)
    # ----
    
    
    def onSequenceSort(self, evt=None):
        """Sort current sequences by title."""
        
        # check selection
        if self.currentDocument is None:
            return
        
        # update document
        self.documents[self.currentDocument].backup(('sequences'))
        self.documents[self.currentDocument].sortSequences()
        
        # update sequence panel
        if self.sequencePanel:
            self.sequencePanel.setData(None)
        
        # update documents panel
        self.currentSequence = None
        
        # set document status
        self.onDocumentChanged(items=('sequences'))
    # ----
    
    
    def onSequenceSendToMassCalculator(self, evt):
        """Show isotopic pattern of current sequence."""
        
        # check selection
        if self.currentDocument is None or self.currentSequence is None:
            wx.Bell()
            return
        
        # get data
        seqData = self.documents[self.currentDocument].sequences[self.currentSequence]
        formula = seqData.formula()
        
        # send data to Mass Calculator
        self.onToolsMassCalculator(formula=formula)
    # ----
    
    
    def onSequenceSendToEnvelopeFit(self, evt):
        """Send current sequence to envelope fit tool."""
        
        # check selection
        if self.currentDocument is None or self.currentSequence is None:
            wx.Bell()
            return
        
        # get data
        seqData = self.documents[self.currentDocument].sequences[self.currentSequence]
        
        # send data to envelope fit
        self.onToolsEnvelopeFit(sequence=seqData)
    # ----
    
    
    
    # LIBRARIES
    
    def onLibraryEdit(self, evt):
        """Edit library."""
        
        # set library to edit
        if evt.GetId() == ID_libraryCompounds:
            library = 'compounds'
            dlg = dlgCompoundsEditor(self)
        
        elif evt.GetId() == ID_libraryModifications:
            library = 'modifications'
            dlg = dlgModificationsEditor(self)
        
        elif evt.GetId() == ID_libraryMonomers:
            library = 'monomers'
            dlg = dlgMonomersEditor(self)
        
        elif evt.GetId() == ID_libraryEnzymes:
            library = 'enzymes'
            dlg = dlgEnzymesEditor(self)
        
        elif evt.GetId() == ID_libraryReferences:
            library = 'references'
            dlg = dlgReferencesEditor(self)
        
        elif evt.GetId() == ID_libraryMascot:
            library = 'mascot'
            dlg = dlgMascotEditor(self)
        
        elif evt.GetId() == ID_libraryPresets:
            library = 'presets'
            dlg = dlgPresetsEditor(self)
        
        # close related panels
        if library == 'compounds' and self.compoundsSearchPanel:
            self.compoundsSearchPanel.Close()
        elif library in ('modifications', 'monomers', 'enzymes') and self.sequencePanel:
            self.sequencePanel.Close()
        elif library == 'references':
            if self.calibrationPanel:
                self.calibrationPanel.Close()
            if self.massFilterPanel:
                self.massFilterPanel.Close()
        elif library == 'mascot' and self.mascotPanel:
            self.mascotPanel.Close()
        
        # show editor
        dlg.ShowModal()
        dlg.Destroy()
        
        # init processing gauge
        gauge = mwx.gaugePanel(self, 'Saving library...')
        gauge.show()
        
        # run process
        process = threading.Thread(target=self.runLibrarySave, kwargs={'library':library})
        process.start()
        while process.isAlive():
            gauge.pulse()
        gauge.close()
        
        # data not saved
        if not self.tmpLibrarySaved:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Library cannot be saved.', message='Please ensure that you have sufficient permissions\nto write into mMass configuration folder.')
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onLibraryLink(self, evt):
        """Open selected webpage."""
        
        # set link
        links = {
            ID_helpHomepage: 'mMassHomepage',
            ID_helpForum: 'mMassForum',
            ID_helpTwitter: 'mMassTwitter',
            ID_helpCite: 'mMassCite',
            ID_helpDonate: 'mMassDonate',
            ID_linksBiomedMSTools: 'biomedmstools',
            ID_linksBLAST: 'blast',
            ID_linksClustalW: 'clustalw',
            ID_linksDeltaMass: 'deltamass',
            ID_linksEMBLEBI: 'emblebi',
            ID_linksExpasy: 'expasy',
            ID_linksFASTA: 'fasta',
            ID_linksMatrixScience: 'matrixscience',
            ID_linksMUSCLE: 'muscle',
            ID_linksNCBI: 'ncbi',
            ID_linksPDB: 'pdb',
            ID_linksPIR: 'pir',
            ID_linksProfound: 'profound',
            ID_linksProspector: 'prospector',
            ID_linksUniMod: 'unimod',
            ID_linksUniProt: 'uniprot',
        }
        link = config.links[links[evt.GetId()]]
        
        # open webpage
        try: webbrowser.open(link, autoraise=1)
        except: pass
    # ----
    
    
    
    # WINDOW
    
    def onWindowMaximize(self, evt):
        """Maximize app."""
        self.Maximize()
    # ----
    
    
    def onWindowIconize(self, evt):
        """Iconize app."""
        self.Iconize()
    # ----
    
    
    def onWindowLayout(self, evt=None, layout=None):
        """Apply selected window layout."""
        
        # documents bottom
        if layout == 'layout2' or (evt and evt.GetId() == ID_windowLayout2):
            config.main['layout'] = 'layout2'
            self.menubar.Check(ID_windowLayout2, True)
            self.AUIManager.GetPane('documents').Show().Bottom().Layer(0).Row(0).Position(0).MinSize((100,195)).BestSize((100,195))
            self.AUIManager.GetPane('peaklist').Show().Right().Layer(0).Row(0).Position(0).MinSize((195,100)).BestSize((195,100))
        
        # peaklist bottom
        elif layout == 'layout3' or (evt and evt.GetId() == ID_windowLayout3):
            config.main['layout'] = 'layout3'
            self.menubar.Check(ID_windowLayout3, True)
            self.AUIManager.GetPane('documents').Show().Left().Layer(0).Row(0).Position(0).MinSize((195,100)).BestSize((195,100))
            self.AUIManager.GetPane('peaklist').Show().Bottom().Layer(0).Row(0).Position(0).MinSize((100,195)).BestSize((100,195))
        
        # documents and peaklist bottom
        elif layout == 'layout4' or (evt and evt.GetId() == ID_windowLayout4):
            config.main['layout'] = 'layout4'
            self.menubar.Check(ID_windowLayout4, True)
            self.AUIManager.GetPane('documents').Show().Bottom().Layer(0).Row(0).Position(0).MinSize((100,195)).BestSize((100,195))
            self.AUIManager.GetPane('peaklist').Show().Bottom().Layer(0).Row(0).Position(1).MinSize((100,195)).BestSize((100,195))
        
        # default
        else:
            config.main['layout'] = 'default'
            self.menubar.Check(ID_windowLayout1, True)
            self.AUIManager.GetPane('documents').Show().Left().Layer(0).Row(0).Position(0).MinSize((195,100)).BestSize((195,100))
            self.AUIManager.GetPane('peaklist').Show().Right().Layer(0).Row(0).Position(0).MinSize((195,100)).BestSize((195,100))
        
        # set last size
        if layout:
            self.AUIManager.GetPane('documents').BestSize((config.main['documentsWidth'], config.main['documentsHeight']))
            self.AUIManager.GetPane('peaklist').BestSize((config.main['peaklistWidth'], config.main['peaklistHeight']))
        
        # apply changes
        self.AUIManager.Update()
    # ----
    
    
    
    # HELP
    
    def onHelpUserGuide(self, evt):
        """Open User's Guide PDF."""
        
        # get path
        if sys.platform == 'darwin':
            path = ''
        else:
            path = os.path.sep
            for folder in os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1]:
                tmp = os.path.join(path, folder)
                if os.path.isdir(tmp):
                    path = tmp
        
        path = os.path.join(path, "User Guide.pdf")
        
        # check path
        if not os.path.exists(path):
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="User's Guide PDF doesn't exists.", message="Please go to the mMass website, download the User's Guide PDF\nand move it into your mMass application folder.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # try to open pdf
        try:
            if wx.Platform == '__WXMSW__':
                os.startfile(path)
            else:
                try: subprocess.Popen(['xdg-open', path])
                except: subprocess.Popen(['open', path])
        except:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open User's Guide.", message="Please make sure that you have any application associated\nwith a PDF format.")
            dlg.ShowModal()
            dlg.Destroy()
            return
    # ----
    
    
    def onHelpUpdate(self, evt=None):
        """Check for available updates."""
        
        # check for available updates
        if not self.getAvailableUpdates():
            wx.Bell()
            title = 'Update Error!'
            message = 'An error occured in retrieving update information.\nPlease try again later.'
            buttons = [(wx.ID_CANCEL, "Cancel Update", -1, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # newer version is available
        if config.main['updatesAvailable'] != config.version or config.nightbuild:
            if config.nightbuild:
                title = 'Different stable version of mMass is available.'
                message = "Version %s is the latest stable version available for download.\nYou are currently using test version %s (%s)." % (config.main['updatesAvailable'], config.version, config.nightbuild)
            else:
                title = 'A newer version of mMass is available from mMass.org'
                message = "Version %s is now available for download.\nYou are currently using version %s." % (config.main['updatesAvailable'], config.version)
            buttons = [(ID_helpWhatsNew, "What's New", -1, False, 15), (wx.ID_CANCEL, "Ask Again Later", -1, False, 15), (ID_helpDownload, "Upgrade Now", -1, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            response = dlg.ShowModal()
            dlg.Destroy()
            if response == ID_helpDownload:
                try: webbrowser.open(config.links['mMassDownload'], autoraise=1)
                except: pass
            elif response == ID_helpWhatsNew:
                try: webbrowser.open(config.links['mMassWhatsNew'], autoraise=1)
                except: pass
        
        # you are up to date
        else:
            title = "You're up to date!"
            message = "mMass %s is currently the newest version available." % config.version
            dlg = mwx.dlgMessage(self, title, message)
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onHelpAbout(self, evt):
        """Show About mMass panel."""
        
        about = panelAbout(self)
        about.Centre()
        about.Show()
        about.SetFocus()
    # ----
    
    
    
    # DOCUMENT IMPORT
    
    def importDocumentQueue(self):
        """Open dropped documents."""
        
        # queue is already running
        if self.processingDocumentQueue:
            return
        
        # process all files in queue
        self.processingDocumentQueue = True
        while self.tmpDocumentQueue:
            self.importDocument(path=self.tmpDocumentQueue[0])
        
        # release processing flag
        self.processingDocumentQueue = False
    # ----
    
    
    def importDocument(self, path):
        """Open document."""
        
        # remove path from queue
        if path in self.tmpDocumentQueue:
            i = self.tmpDocumentQueue.index(path)
            del self.tmpDocumentQueue[i]
        
        # check path
        if os.path.exists(path):
            config.main['lastDir'] = os.path.split(path)[0]
        else:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Document doesn't exists.", message="Specified document path cannot be found or is temporarily\nunavailable.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # get document type
        docType = self.getDocumentType(path)
        if not docType:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open the document.", message="Document type or structure can't be recognized. Selected format\nis probably unsupported.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # import sequences from FASTA
        if docType == 'FASTA':
            self.onSequenceImport(path=path)
            return
        
        # convert Bruker format
        compassUsed = False
        if docType == 'bruker':
            compassUsed = True
            docType = config.main['compassFormat']
            path = self.convertBrukerData(path)
            if not path:
                return
        
        # select scans from multiscan documents
        scans = [None]
        if docType in ('mzXML', 'mzData', 'mzML', 'MGF'):
            scans = self.askForScans(path, docType)
            if not scans:
                return
        
        # open document
        status = True
        for scan in scans:
            before = len(self.documents)
            
            # init processing gauge
            gauge = mwx.gaugePanel(self, 'Reading data...')
            gauge.show()
            
            # load document
            process = threading.Thread(target=self.runDocumentParser, kwargs={'path':path, 'docType':docType, 'scan':scan})
            process.start()
            while process.isAlive():
                gauge.pulse()
            
            # append document
            if before < len(self.documents):
                self.onDocumentLoaded(select=True)
                status *= True
            else:
                status *= False
            
            # close processing gauge
            gauge.close()
        
        # delete compass file
        if compassUsed and config.main['compassDeleteFile']:
            try: os.unlink(path)
            except: pass
        
        # update recent files
        if status and (not compassUsed or not config.main['compassDeleteFile']):
            self.updateRecentFiles(path)
        
        # processing failed
        if not status:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open the document.", message="There were some errors while reading selected document\nor it contains no data.")
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def importDocumentFromClipboard(self, rawData, dataType='profile'):
        """Parse data and make new document."""
        
        before = len(self.documents)
        
        # init processing gauge
        gauge = mwx.gaugePanel(self, 'Reading data...')
        gauge.show()
        
        # load document
        process = threading.Thread(target=self.runDocumentXYParser, kwargs={'rawData':rawData, 'dataType':dataType})
        process.start()
        while process.isAlive():
            gauge.pulse()
        
        # append document
        if before < len(self.documents):
            self.onDocumentLoaded(select=True)
            gauge.close()
            return True
        else:
            gauge.close()
            return False
    # ----
    
    
    def convertBrukerData(self, path):
        """Convert Bruker data."""
        
        self.tmpCompassXport = False
        
        # check platform
        if not wx.Platform == '__WXMSW__':
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to convert data.", message="Unfortunately, it is not possible to use Bruker's CompassXport tool\non this platform.")
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # convert data
        gauge = mwx.gaugePanel(self, 'Converting data...')
        gauge.show()
        process = threading.Thread(target=self.runCompassXport, kwargs={'path':path})
        process.start()
        while process.isAlive():
            gauge.pulse()
        gauge.close()
        
        # unable to convert data
        if not self.tmpCompassXport:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to convert data.", message="Make sure the Bruker's CompassXport tool is installed\non this computer.")
            dlg.ShowModal()
            dlg.Destroy()
            return False
            
        return self.tmpCompassXport
    # ----
    
    
    def runCompassXport(self, path):
        """Convert Bruker data using CompassXport tool."""
        
        self.tmpCompassXport = False
        
        # get data path
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                if 'Analysis.baf' in filenames:
                    path = os.path.join(dirpath, 'Analysis.baf')
                    break
                elif 'analysis.baf' in filenames:
                    path = os.path.join(dirpath, 'analysis.baf')
                    break
                elif 'Analysis.yep' in filenames:
                    path = os.path.join(dirpath, 'Analysis.yep')
                    break
                elif 'analysis.yep' in filenames:
                    path = os.path.join(dirpath, 'analysis.yep')
                    break
                elif 'fid' in filenames:
                    path = os.path.join(dirpath, 'fid')
                    break
                elif 'FID' in filenames:
                    path = os.path.join(dirpath, 'FID')
                    break
        
        # set params
        choices = {'Line': 0, 'Profile': 1}
        raw = choices[config.main['compassMode']]
        choices = {'mzXML': 0, 'mzData': 1, 'mzML': 2}
        mode = choices[config.main['compassFormat']]
        
        # convert data
        try:
            output = os.path.join(os.path.dirname(path), 'Analysis.'+config.main['compassFormat'])
            retcode = subprocess.call(['CompassXport.exe', '-a', path, '-o', output, '-raw', str(raw), '-mode', str(mode)], shell=True)
            if retcode == 0:
                self.tmpCompassXport = output
                return
        except:
            return
    # ----
    
    
    def runDocumentParser(self, path, docType, scan=None):
        """Load spectrum document."""
        
        document = False
        spectrum = False
        
        # get data data
        if docType == 'mSD':
            parser = doc.parseMSD(path)
            document = parser.getDocument()
        elif docType == 'mzData':
            parser = mspy.parseMZDATA(path)
            spectrum = parser.scan(scan)
        elif docType == 'mzXML':
            parser = mspy.parseMZXML(path)
            spectrum = parser.scan(scan)
        elif docType == 'mzML':
            parser = mspy.parseMZML(path)
            spectrum = parser.scan(scan)
        elif docType == 'MGF':
            parser = mspy.parseMGF(path)
            spectrum = parser.scan(scan)
        elif docType == 'XY':
            parser = mspy.parseXY(path)
            spectrum = parser.scan()
        else:
            return
        
        # make document for non-mSD formats
        if spectrum != False:
            
            # init document
            document = doc.document()
            document.format = docType
            document.path = path
            document.spectrum = spectrum
            
            # get info
            info = parser.info()
            if info:
                document.title = info['title']
                document.operator = info['operator']
                document.contact = info['contact']
                document.institution = info['institution']
                document.date = info['date']
                document.instrument = info['instrument']
                document.notes = info['notes']
            
            # set date if empty
            if not document.date and docType != 'mSD':
                document.date = time.ctime(os.path.getctime(path))
            
            # set title if empty
            if not document.title:
                if document.spectrum.title != '':
                    document.title = document.spectrum.title
                else:
                    dirName, fileName = os.path.split(path)
                    baseName, extension = os.path.splitext(fileName)
                    if baseName.lower() == "analysis":
                        document.title = os.path.split(dirName)[1]
                    else:
                        document.title = baseName
            
            # add scan number to title
            if scan:
                document.title += ' [%s]' % scan
            
        # finalize and append document
        if document:
            document.colour = self.getFreeColour()
            document.sortAnnotations()
            document.sortSequenceMatches()
            self.documents.append(document)
            
            # precalculate baseline
            if document.spectrum.hasprofile():
                document.spectrum.baseline(
                    window = (1./config.processing['baseline']['precision']),
                    offset = config.processing['baseline']['offset']
                )
    # ----
    
    
    def runDocumentXYParser(self, rawData, dataType='profile'):
        """Parse XY data and make new document."""
        
        pattern = re.compile('^([-0-9\.eE+]+)[ \t]*(;|,)?[ \t]*([-0-9\.eE+]*)$')
        
        # read lines
        data = []
        for line in rawData.splitlines():
            line = line.strip()
            
            # discard comment lines
            if not line or line[0] == '#' or line[0:3] == 'm/z':
                continue
            
            # check pattern
            parts = pattern.match(line)
            if parts:
                try:
                    mass = float(parts.group(1))
                    intensity = float(parts.group(3))
                except ValueError:
                    return
                data.append([mass, intensity])
            else:
                return
        
        # finalize data
        if dataType == 'peaklist':
            spectrum = mspy.scan(peaklist=data)
        else:
            spectrum = mspy.scan(profile=data)
        
        # add new document
        document = doc.document()
        document.title = 'Clipboard Data'
        document.format = 'mSD'
        document.path = ''
        document.dirty = True
        document.spectrum = spectrum
        document.colour = self.getFreeColour()
        self.documents.append(document)
        
        # precalculate baseline
        document.spectrum.baseline(
            window = (1./config.processing['baseline']['precision']),
            offset = config.processing['baseline']['offset']
        )
    # ----
    
    
    def runDocumentSave(self, docIndex):
        """Save current document."""
        
        # get XML data for selected document
        self.currentDocumentXML = self.documents[docIndex].msd()
    # ----
    
    
    def runLibrarySave(self, library):
        """Save selected library."""
        
        self.tmpLibrarySaved = False
        
        # set process
        if library == 'compounds':
            self.tmpLibrarySaved = libs.saveCompounds()
        elif library == 'modifications':
            self.tmpLibrarySaved = mspy.saveModifications(os.path.join(config.confdir,'modifications.xml'))
        elif library == 'monomers':
            self.tmpLibrarySaved = mspy.saveMonomers(os.path.join(config.confdir,'monomers.xml'))
        elif library == 'enzymes':
            self.tmpLibrarySaved = mspy.saveEnzymes(os.path.join(config.confdir,'enzymes.xml'))
        elif library == 'references':
            self.tmpLibrarySaved = libs.saveReferences()
        elif library == 'mascot':
            self.tmpLibrarySaved = libs.saveMascot()
        elif library == 'presets':
            self.tmpLibrarySaved = libs.savePresets()
    # ----
    
    
    def getDocumentType(self, path):
        """Get document type."""
        
        # get filename and extension
        dirName, fileName = os.path.split(path)
        baseName, extension = os.path.splitext(fileName)
        fileName = fileName.lower()
        baseName = baseName.lower()
        extension = extension.lower()
        
        # get document type by filename or extension
        if extension == '.msd':
            return 'mSD'
        elif fileName == 'fid' or extension in ('.baf', '.yep'):
            return 'bruker'
        elif extension == '.mzdata':
            return 'mzData'
        elif extension == '.mzxml':
            return 'mzXML'
        elif extension == '.mzml':
            return 'mzML'
        elif extension == '.mgf':
            return 'MGF'
        elif extension in ('.xy', '.txt', '.asc'):
            return 'XY'
        elif extension in ('.fa', '.fsa', '.faa', '.fasta'):
            return 'FASTA'
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                names = [i.lower() for i in filenames]
                if 'fid' in names or 'analysis.baf' in names or 'analysis.yep' in names:
                    return 'bruker'
        
        # get document type for xml files
        if extension == '.xml':
            document = open(path, 'r')
            data = document.read(500)
            if '<mzData' in data:
                return 'mzData'
            elif '<mzXML' in data:
                return 'mzXML'
            elif '<mzML' in data:
                return 'mzML'
            document.close()
        
        # unknown document type
        return False
    # ----
    
    
    def getDocumentScanList(self, path, docType):
        """Get scans from document."""
        
        modified = os.path.getmtime(path)
        
        # try to load from buffer
        if path in self.bufferedScanlists and modified == self.bufferedScanlists[path][0]:
            self.tmpScanlist = self.bufferedScanlists[path][1]
            return
        
        # set parser
        if docType == 'mzData':
            parser = mspy.parseMZDATA(path)
        elif docType == 'mzXML':
            parser = mspy.parseMZXML(path)
        elif docType == 'mzML':
            parser = mspy.parseMZML(path)
        elif docType == 'MGF':
            parser = mspy.parseMGF(path)
        else:
            return
        
        # load scans
        self.tmpScanlist = parser.scanlist()
        
        # remember scan list
        if self.tmpScanlist:
            self.bufferedScanlists[path] = (modified, self.tmpScanlist)
    # ----
    
    
    def getDocumentSequences(self, path, docType):
        """Get sequences from document."""
        
        # get sequences
        if docType == 'mSD':
            parser = doc.parseMSD(path)
            self.tmpSequenceList = parser.getSequences()
        elif docType == 'FASTA':
            parser = mspy.parseFASTA(path)
            self.tmpSequenceList = parser.sequences()
        else:
            return
    # ----
    
    
    def askForScans(self, path, docType):
        """Select scans to import."""
        
        self.tmpScanlist = None
        
        # get scan list
        gauge = mwx.gaugePanel(self, 'Gathering scan list...')
        gauge.show()
        process = threading.Thread(target=self.getDocumentScanList, kwargs={'path':path, 'docType':docType})
        process.start()
        while process.isAlive():
            gauge.pulse()
        gauge.close()
        
        # unable to load scan list
        if not self.tmpScanlist:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open the document.", message="Selected document is damaged or contains no data.")
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # select scans to open
        if len(self.tmpScanlist) > 1:
            dlg = dlgSelectScans(self, self.tmpScanlist)
            if dlg.ShowModal() == wx.ID_OK:
                selected = dlg.selected
                dlg.Destroy()
                return selected
            else:
                dlg.Destroy()
                return None
        else:
            return [None]
    # ----
    
    
    def askForSequences(self, path, docType):
        """Select sequences to import."""
        
        self.tmpSequenceList = None
        
        # get scan list
        gauge = mwx.gaugePanel(self, 'Gathering sequences...')
        gauge.show()
        process = threading.Thread(target=self.getDocumentSequences, kwargs={'path':path, 'docType':docType})
        process.start()
        while process.isAlive():
            gauge.pulse()
        gauge.close()
        
        # no sequences found
        if self.tmpSequenceList == []:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="No sequence found.", message="Selected document doesn't contain any valid sequence.")
            dlg.ShowModal()
            dlg.Destroy()
            return None
            
        # unable to load sequences
        elif not self.tmpSequenceList:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unable to open the document.", message="Document type or structure can't be recognized. Selected format\nis probably unsupported.")
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # select sequences to open
        if len(self.tmpSequenceList) > 1:
            dlg = dlgSelectSequences(self, self.tmpSequenceList)
            if dlg.ShowModal() == wx.ID_OK:
                selected = dlg.selected
                dlg.Destroy()
                return selected
            else:
                dlg.Destroy()
                return None
        else:
            return self.tmpSequenceList
    # ----
    
    
    
    # UTILITIES
    
    def updateTmpSpectrum(self, points, flipped=False, refresh=True):
        """Update tmp spectrum in canvas."""
        self.spectrumPanel.updateTmpSpectrum(points, flipped=flipped, refresh=refresh)
    # ----
    
    
    def updateNotationMarks(self, refresh=True):
        """Highlight annotations and sequence matches in canvas."""
        
        # get current selection
        selected = self.documentsPanel.getSelectedItemType()
        
        # hide annotation marks
        if not selected or self.currentDocument is None:
            self.spectrumPanel.updateNotationMarks(None, refresh=refresh)
            return
        
        points = []
        
        # get all
        if selected == 'document':
            document = self.documents[self.currentDocument]
            points += [[a.mz, a.ai, a.label] for a in document.annotations]
            for sequence in document.sequences:
                points += [[m.mz, m.ai, m.label] for m in sequence.matches]
        
        # get annotations
        elif selected in ('annotations', 'annotation'):
            document = self.documents[self.currentDocument]
            points += [[a.mz, a.ai, a.label] for a in document.annotations]
        
        # get sequence matches
        elif selected in ('sequence', 'match') and self.currentSequence != None:
            sequence = self.documents[self.currentDocument].sequences[self.currentSequence]
            points += [[m.mz, m.ai, m.label] for m in sequence.matches]
        
        # sort points
        points.sort()
        
        # update spectrum panel
        self.spectrumPanel.updateNotationMarks(points, refresh=refresh)
    # ----
    
    
    def updateMassPoints(self, points):
        """Highlight specified points in the spectrum."""
        self.spectrumPanel.highlightPoints(points)
    # ----
    
    
    def updateControls(self):
        """Update menubar and toolbar items state."""
        
        # skip for Mac since it doesn't work correctly... why???
        if wx.Platform == '__WXMAC__':
            return
        
        # document
        if self.currentDocument is None:
            enable = False
            document = None
        else:
            enable = True
            document = self.documents[self.currentDocument]
        
        # update menubar
        self.menubar.Enable(ID_documentClose, enable)
        self.menubar.Enable(ID_documentCloseAll, bool(self.documents))
        self.menubar.Enable(ID_documentSave, enable)
        self.menubar.Enable(ID_documentSaveAs, enable)
        self.menubar.Enable(ID_documentSaveAll, bool(self.documents))
        self.menubar.Enable(ID_documentExport, bool(self.documents))
        self.menubar.Enable(ID_documentReport, enable)
        self.menubar.Enable(ID_documentInfo, enable)
        self.menubar.Enable(ID_documentFlip, enable)
        self.menubar.Enable(ID_documentOffset, bool(enable and not config.spectrum['normalize']))
        self.menubar.Enable(ID_processingUndo, bool(enable and document.undo))
        self.menubar.Enable(ID_processingPeakpicking, enable)
        self.menubar.Enable(ID_processingDeisotoping, enable)
        self.menubar.Enable(ID_processingDeconvolution, enable)
        self.menubar.Enable(ID_processingBaseline, enable)
        self.menubar.Enable(ID_processingSmoothing, enable)
        self.menubar.Enable(ID_processingCrop, enable)
        self.menubar.Enable(ID_processingMath, enable)
        self.menubar.Enable(ID_processingBatch, bool(self.documents))
        self.menubar.Enable(ID_toolsSwapData, enable)
        self.menubar.Enable(ID_sequenceNew, enable)
        self.menubar.Enable(ID_sequenceImport, enable)
        self.menubar.Enable(ID_sequenceSort, enable)
        self.menubar.Enable(ID_toolsCalibration, enable)
        self.menubar.Enable(ID_processingDeconvolution, enable)
        self.menubar.Enable(ID_toolsMassFilter, enable)
        self.menubar.Enable(ID_toolsCompoundsSearch, enable)
        self.menubar.Enable(ID_toolsPeakDifferences, enable)
        self.menubar.Enable(ID_toolsComparePeaklists, bool(self.documents))
        self.menubar.Enable(ID_toolsSpectrumGenerator, enable)
        self.menubar.Enable(ID_toolsEnvelopeFit, enable)
        self.menubar.Enable(ID_toolsMassDefectPlot, enable)
        self.menubar.Enable(ID_mascotPMF, enable)
        self.menubar.Enable(ID_mascotSQ, enable)
        self.menubar.Enable(ID_mascotMIS, enable)
        self.menubar.Enable(ID_toolsProfound, enable)
        self.menubar.Enable(ID_prospectorMSFit, enable)
        self.menubar.Enable(ID_prospectorMSTag, enable)
        
        # update toolbar
        if wx.Platform != '__WXMAC__':
            self.toolbar.EnableTool(ID_documentSave, bool(enable and document.dirty))
        self.toolbar.EnableTool(ID_toolsProcessing, bool(self.documents))
        self.toolbar.EnableTool(ID_toolsCalibration, enable)
        self.toolbar.EnableTool(ID_toolsMassFilter, enable)
        self.toolbar.EnableTool(ID_toolsSequence, enable)
        self.toolbar.EnableTool(ID_toolsCompoundsSearch, enable)
        self.toolbar.EnableTool(ID_toolsPeakDifferences, enable)
        self.toolbar.EnableTool(ID_toolsComparePeaklists, bool(self.documents))
        self.toolbar.EnableTool(ID_toolsSpectrumGenerator, enable)
        self.toolbar.EnableTool(ID_toolsEnvelopeFit, enable)
        self.toolbar.EnableTool(ID_toolsMassDefectPlot, enable)
        self.toolbar.EnableTool(ID_toolsMascot, enable)
        self.toolbar.EnableTool(ID_toolsProfound, enable)
        self.toolbar.EnableTool(ID_toolsDocumentExport, bool(self.documents))
        self.toolbar.EnableTool(ID_toolsDocumentInfo, enable)
        self.toolbar.EnableTool(ID_toolsDocumentReport, enable)
        
        # sequence
        if self.currentDocument is None or self.currentSequence is None:
            enable = False
            sequence = None
        else:
            enable = True
            sequence = self.documents[self.currentDocument].sequences[self.currentSequence]
        
        # update menubar
        self.menubar.Enable(ID_sequenceEditor, enable)
        self.menubar.Enable(ID_sequenceModifications, enable)
        self.menubar.Enable(ID_sequenceDigest, enable)
        self.menubar.Enable(ID_sequenceFragment, enable)
        self.menubar.Enable(ID_sequenceSearch, enable)
        self.menubar.Enable(ID_sequenceSendToMassCalculator, enable)
        self.menubar.Enable(ID_sequenceSendToEnvelopeFit, enable)
        self.menubar.Enable(ID_sequenceMatchesCalibrateBy, bool(enable and sequence.matches))
        self.menubar.Enable(ID_sequenceMatchesDelete, bool(enable and sequence.matches))
        self.menubar.Enable(ID_sequenceDelete, enable)
    # ----
    
    
    def updateRecentFiles(self, path=None):
        """Update recent files."""
        
        # update config
        if path:
            if path in config.recent:
                del config.recent[config.recent.index(path)]
            config.recent.insert(0, path)
            while len(config.recent) > 10:
                del config.recent[-1]
        
        # delete old items from menu
        for item in self.menuRecent.GetMenuItems():
            self.menuRecent.Delete(item.GetId())
        
        # add new items to menu
        for i, path in enumerate(config.recent):
            ID = eval('ID_documentRecent'+str(i))
            self.menuRecent.Insert(i, ID, path, "Open Document")
            self.Bind(wx.EVT_MENU, self.onDocumentRecent, id=ID)
            if not os.path.exists(path):
                self.menuRecent.Enable(ID, False)
        
        # append clear
        if config.recent:
            self.menuRecent.AppendSeparator()
        self.menuRecent.Append(ID_documentRecentClear, "Clear Menu", "Clear recent items")
        self.Bind(wx.EVT_MENU, self.onDocumentClearRecent, id=ID_documentRecentClear)
    # ----
    
    
    def getFreeColour(self):
        """Get free colour from config or generate random."""
        
        # get colour from config
        for colour in config.colours:
            if not colour in self.usedColours:
                self.usedColours.append(colour)
                return colour
        
        # generate random colour
        i = 0
        while True:
            i += 1
            colour = [random.randrange(0,255), random.randrange(0,255), random.randrange(0,255)]
            if colour not in self.usedColours or i==10000:
                self.usedColours.append(colour)
                return colour
    # ----
    
    
    def getAvailableUpdates(self):
        """Check for available updates."""
        
        # get latest version available
        socket.setdefaulttimeout(5)
        conn = http.client.HTTPConnection('www.mmass.org')
        try:
            conn.connect()
            url = '/update.php?version=%s&platform=%s' % (config.version, platform.platform())
            conn.request('GET', url)
            response = conn.getresponse()
        except:
            return False
        
        if response.status == 200:
            data = response.read()
            conn.close()
        else:
            conn.close()
            return False
        
        # check version
        if re.match('^([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{1,2})$', data):
            config.main['updatesAvailable'] = data
            config.main['updatesChecked'] = time.strftime("%Y%m%d", time.localtime())
            return True
        else:
            return False
    # ----
    
    
    def getCurrentSpectrumPoints(self, currentView=False):
        """Get spectrum profile from current document."""
        
        # check document
        if self.currentDocument is None:
            return None
        
        # get spectrum
        points = self.documents[self.currentDocument].spectrum.profile
        
        # get current view selection
        if currentView:
            minX, maxX = self.spectrumPanel.getCurrentRange()
            points = mspy.crop(points, minX, maxX)
        
        return points
    # ----
    
    
    def getCurrentPeaklist(self, filters=''):
        """Get peaklist from current document."""
        
        # check document
        if self.currentDocument is None:
            return None
        
        peaklist = []
        blacklist = []
        whitelist = self.documents[self.currentDocument].spectrum.peaklist
        
        # get selection
        if 'S' in filters:
            whitelist = self.peaklistPanel.getSelectedPeaks()
        
        # get annotations
        if 'A' in filters:
            for annotation in self.documents[self.currentDocument].annotations:
                blacklist.append(round(annotation.mz, 6))
        
        # get matches
        if 'M' in filters:
            for sequence in self.documents[self.currentDocument].sequences:
                for match in sequence.matches:
                    blacklist.append(round(match.mz, 6))
        
        # get peaklist
        for peak in whitelist:
            if 'X' in filters and peak.charge is None:
                continue
            elif 'I' in filters and not peak.isotope in (0, None):
                continue
            elif ('A' in filters or 'M' in filters) and round(peak.mz, 6) in blacklist:
                continue
            else:
                peaklist.append(peak)
        
        # finalize peaklist
        peaklist = mspy.peaklist(peaklist)
        
        return peaklist
    # ----
    
    
    def getSpectrumBitmap(self, width, height, printerScale):
        """Get bitmap from current spectrum canvas."""
        return self.spectrumPanel.getBitmap(width, height, printerScale)
    # ----
    
    
    def getUsedMonomers(self):
        """Search all sequences for used monomers."""
        
        # get monomers
        monomers = []
        for document in self.documents:
            for sequence in document.sequences:
                for monomer in sequence:
                    monomers.append(monomer)
        
        return monomers
    # ----
    
    
    def getUsedModifications(self):
        """Search all sequences for used modifications."""
        
        # get modifications
        modifications = []
        for document in self.documents:
            for sequence in document.sequences:
                for mod in sequence.modifications:
                    modifications.append(mod[0])
        
        return modifications
    # ----
    
    
    def checkVersions(self):
        """Check mMass version and available updates."""
        
        # skip testing versions
        if config.nightbuild:
            return
        
        # first run
        if config.main['updatesCurrent'] != config.version:
            config.main['updatesCurrent'] = config.version
            config.main['updatesAvailable'] = ''
            config.main['updatesChecked'] = ''
        
        # updates are available
        elif config.main['updatesEnabled'] and config.main['updatesAvailable'] and config.main['updatesAvailable'] != config.version:
            title = 'A newer version of mMass is available from mMass.org'
            message = "Version %s is now available for download.\nYou are currently using version %s." % (config.main['updatesAvailable'], config.version)
            buttons = [(ID_helpWhatsNew, "What's New", -1, False, 15), (wx.ID_CANCEL, "Ask Again Later", -1, False, 15), (ID_helpDownload, "Upgrade Now", -1, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            response = dlg.ShowModal()
            dlg.Destroy()
            if response == ID_helpDownload:
                try: webbrowser.open(config.links['mMassDownload'], autoraise=1)
                except: pass
            elif response == ID_helpWhatsNew:
                try: webbrowser.open(config.links['mMassWhatsNew'], autoraise=1)
                except: pass
            
        # check for updates
        if config.main['updatesEnabled'] and config.main['updatesChecked'] != time.strftime("%Y%m%d", time.localtime()):
            process = threading.Thread(target=self.getAvailableUpdates)
            process.start()
    # ----
    
    
