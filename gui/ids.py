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

# common
ID_quit = wx.ID_EXIT
ID_about = wx.ID_ABOUT
ID_preferences = wx.ID_PREFERENCES

HK_quit = '\tCtrl+Q'
HK_preferences = ''
if wx.Platform == '__WXMAC__':
    HK_preferences = '\tCtrl+,'

# file
ID_documentNew = wx.NewId()
ID_documentNewFromClipboard = wx.NewId()
ID_documentDuplicate = wx.NewId()
ID_documentOpen = wx.NewId()
ID_documentRecent = wx.NewId()
ID_documentClose = wx.NewId()
ID_documentCloseAll = wx.NewId()
ID_documentSave = wx.NewId()
ID_documentSaveAs = wx.NewId()
ID_documentSaveAll = wx.NewId()
ID_documentExport = wx.NewId()
ID_documentInfo = wx.NewId()
ID_documentPrintSpectrum = wx.NewId()
ID_documentReport = wx.NewId()
ID_documentFlip = wx.NewId()
ID_documentOffset = wx.NewId()
ID_documentClearOffset = wx.NewId()
ID_documentClearOffsets = wx.NewId()
ID_documentColour = wx.NewId()
ID_documentStyle = wx.NewId()
ID_documentStyleSolid = wx.NewId()
ID_documentStyleDot = wx.NewId()
ID_documentStyleDash = wx.NewId()
ID_documentStyleDotDash = wx.NewId()
ID_documentAnnotationEdit = wx.NewId()
ID_documentAnnotationDelete = wx.NewId()
ID_documentAnnotationSendToMassCalculator = wx.NewId()
ID_documentAnnotationSendToMassToFormula = wx.NewId()
ID_documentAnnotationSendToEnvelopeFit = wx.NewId()
ID_documentAnnotationsDelete = wx.NewId()
ID_documentAnnotationsCalibrateBy = wx.NewId()
ID_documentNotationsDelete = wx.NewId()

ID_documentRecent0 = wx.NewId()
ID_documentRecent1 = wx.NewId()
ID_documentRecent2 = wx.NewId()
ID_documentRecent3 = wx.NewId()
ID_documentRecent4 = wx.NewId()
ID_documentRecent5 = wx.NewId()
ID_documentRecent6 = wx.NewId()
ID_documentRecent7 = wx.NewId()
ID_documentRecent8 = wx.NewId()
ID_documentRecent9 = wx.NewId()
ID_documentRecentClear = wx.NewId()

HK_documentNew = '\tCtrl+N'
HK_documentNewFromClipboard = '\tShift+Ctrl+N'
HK_documentOpen = '\tCtrl+O'
HK_documentClose = '\tCtrl+W'
HK_documentCloseAll = '\tShift+Ctrl+W'
HK_documentSave = '\tCtrl+S'
HK_documentSaveAs = '\tShift+Ctrl+S'
HK_documentSaveAll = '\tAlt+Ctrl+S'
HK_documentExport = '\tCtrl+E'
HK_documentInfo = '\tCtrl+I'
HK_documentPrintSpectrum = '\tCtrl+P'
HK_documentReport = '\tShift+Ctrl+R'
HK_documentFlip = '\tAlt+Ctrl+F'

# view
ID_viewGrid = wx.NewId()
ID_viewMinorTicks = wx.NewId()
ID_viewLegend = wx.NewId()
ID_viewPosBars = wx.NewId()
ID_viewGel = wx.NewId()
ID_viewGelLegend = wx.NewId()
ID_viewTracker = wx.NewId()
ID_viewDataPoints = wx.NewId()
ID_viewLabels = wx.NewId()
ID_viewTicks = wx.NewId()
ID_viewLabelCharge = wx.NewId()
ID_viewLabelGroup = wx.NewId()
ID_viewLabelBgr = wx.NewId()
ID_viewLabelAngle = wx.NewId()
ID_viewAllLabels = wx.NewId()
ID_viewOverlapLabels = wx.NewId()
ID_viewCheckLimits = wx.NewId()
ID_viewNotations = wx.NewId()
ID_viewNotationMarks = wx.NewId()
ID_viewNotationLabels = wx.NewId()
ID_viewNotationMz = wx.NewId()
ID_viewAutoscale = wx.NewId()
ID_viewNormalize = wx.NewId()
ID_viewRange = wx.NewId()
ID_viewCanvasProperties = wx.NewId()

ID_viewSpectrumRulerMz = wx.NewId()
ID_viewSpectrumRulerDist = wx.NewId()
ID_viewSpectrumRulerPpm = wx.NewId()
ID_viewSpectrumRulerZ = wx.NewId()
ID_viewSpectrumRulerCursorMass = wx.NewId()
ID_viewSpectrumRulerParentMass = wx.NewId()
ID_viewSpectrumRulerArea = wx.NewId()

ID_viewPeaklistColumnMz = wx.NewId()
ID_viewPeaklistColumnAi = wx.NewId()
ID_viewPeaklistColumnInt = wx.NewId()
ID_viewPeaklistColumnBase = wx.NewId()
ID_viewPeaklistColumnRel = wx.NewId()
ID_viewPeaklistColumnSn = wx.NewId()
ID_viewPeaklistColumnZ = wx.NewId()
ID_viewPeaklistColumnMass = wx.NewId()
ID_viewPeaklistColumnFwhm = wx.NewId()
ID_viewPeaklistColumnResol = wx.NewId()
ID_viewPeaklistColumnGroup = wx.NewId()

HK_viewPosBars = '\tAlt+Ctrl+P'
HK_viewGel = '\tAlt+Ctrl+G'
HK_viewLabels = '\tAlt+Ctrl+L'
HK_viewTicks = '\tAlt+Ctrl+T'
HK_viewLabelAngle = '\tAlt+Ctrl+H'
HK_viewAllLabels = '\tAlt+Ctrl+Shift+L'
HK_viewOverlapLabels = '\tAlt+Ctrl+O'
HK_viewAutoscale = '\tAlt+Ctrl+A'
HK_viewNormalize = '\tAlt+Ctrl+N'
HK_viewRange = '\tAlt+Ctrl+R'
HK_viewCanvasProperties = '\tCtrl+J'

# processing
ID_processingUndo = wx.NewId()
ID_processingPeakpicking = wx.NewId()
ID_processingDeisotoping = wx.NewId()
ID_processingDeconvolution = wx.NewId()
ID_processingBaseline = wx.NewId()
ID_processingSmoothing = wx.NewId()
ID_processingCrop = wx.NewId()
ID_processingMath = wx.NewId()
ID_processingBatch = wx.NewId()
ID_toolsSwapData = wx.NewId()

HK_processingUndo = '\tCtrl+Z'
HK_processingPeakpicking = '\tCtrl+F'
HK_processingDeisotoping = '\tCtrl+D'
HK_processingDeconvolution = ''
HK_processingSmoothing = '\tCtrl+G'
HK_processingBaseline = '\tCtrl+B'

# sequence
ID_sequenceNew = wx.NewId()
ID_sequenceImport = wx.NewId()
ID_sequenceEditor = wx.NewId()
ID_sequenceModifications = wx.NewId()
ID_sequenceDigest = wx.NewId()
ID_sequenceFragment = wx.NewId()
ID_sequenceSearch = wx.NewId()
ID_sequenceSendToMassCalculator = wx.NewId()
ID_sequenceSendToEnvelopeFit = wx.NewId()
ID_sequenceDelete = wx.NewId()
ID_sequenceSort = wx.NewId()
ID_sequenceMatchEdit = wx.NewId()
ID_sequenceMatchDelete = wx.NewId()
ID_sequenceMatchSendToMassCalculator = wx.NewId()
ID_sequenceMatchSendToEnvelopeFit = wx.NewId()
ID_sequenceMatchesDelete = wx.NewId()
ID_sequenceMatchesCalibrateBy = wx.NewId()

# tools
ID_toolsProcessing = wx.NewId()
ID_toolsCalibration = wx.NewId()
ID_toolsSequence = wx.NewId()
ID_toolsRuler = wx.NewId()
ID_toolsLabelPeak = wx.NewId()
ID_toolsLabelPoint = wx.NewId()
ID_toolsLabelEnvelope = wx.NewId()
ID_toolsDeleteLabel = wx.NewId()
ID_toolsOffset = wx.NewId()
ID_toolsPeriodicTable = wx.NewId()
ID_toolsMassCalculator = wx.NewId()
ID_toolsMassToFormula = wx.NewId()
ID_toolsMassDefectPlot = wx.NewId()
ID_toolsMassFilter = wx.NewId()
ID_toolsCompoundsSearch = wx.NewId()
ID_toolsPeakDifferences = wx.NewId()
ID_toolsComparePeaklists = wx.NewId()
ID_toolsSpectrumGenerator = wx.NewId()
ID_toolsEnvelopeFit = wx.NewId()
ID_toolsMascot = wx.NewId()
ID_toolsProfound = wx.NewId()
ID_toolsProspector = wx.NewId()
ID_toolsDocumentInfo = wx.NewId()
ID_toolsDocumentReport = wx.NewId()
ID_toolsDocumentExport = wx.NewId()

HK_toolsCalibration = '\tCtrl+R'
HK_toolsRuler = '\tShift+Ctrl+H'
HK_toolsLabelPeak = '\tShift+Ctrl+P'
HK_toolsLabelPoint = '\tShift+Ctrl+I'
HK_toolsLabelEnvelope = '\tShift+Ctrl+E'
HK_toolsDeleteLabel = '\tShift+Ctrl+X'
HK_toolsPeriodicTable = '\tShift+Ctrl+T'
HK_toolsMassCalculator = '\tShift+Ctrl+M'
HK_toolsMassToFormula = '\tShift+Ctrl+B'
HK_toolsMassDefectPlot = '\tShift+Ctrl+O'
HK_toolsMassFilter = '\tShift+Ctrl+F'
HK_toolsCompoundsSearch = '\tShift+Ctrl+U'
HK_toolsPeakDifferences = '\tShift+Ctrl+D'
HK_toolsComparePeaklists = '\tShift+Ctrl+C'
HK_toolsSpectrumGenerator = '\tShift+Ctrl+G'
HK_toolsEnvelopeFit = '\tShift+Ctrl+V'

# library
ID_libraryCompounds = wx.NewId()
ID_libraryModifications = wx.NewId()
ID_libraryMonomers = wx.NewId()
ID_libraryEnzymes = wx.NewId()
ID_libraryReferences = wx.NewId()
ID_libraryMascot = wx.NewId()
ID_libraryPresets = wx.NewId()

# links
ID_linksBiomedMSTools = wx.NewId()
ID_linksBLAST = wx.NewId()
ID_linksClustalW = wx.NewId()
ID_linksDeltaMass = wx.NewId()
ID_linksEMBLEBI = wx.NewId()
ID_linksExpasy = wx.NewId()
ID_linksFASTA = wx.NewId()
ID_linksMatrixScience = wx.NewId()
ID_linksMUSCLE = wx.NewId()
ID_linksNCBI = wx.NewId()
ID_linksPDB = wx.NewId()
ID_linksPIR = wx.NewId()
ID_linksProfound = wx.NewId()
ID_linksProspector = wx.NewId()
ID_linksUniMod = wx.NewId()
ID_linksUniProt = wx.NewId()

# window
ID_windowMaximize = wx.NewId()
ID_windowMinimize = wx.NewId()
ID_windowLayout1 = wx.NewId()
ID_windowLayout2 = wx.NewId()
ID_windowLayout3 = wx.NewId()
ID_windowLayout4 = wx.NewId()

HK_windowLayout1 = '\tF5'
HK_windowLayout2 = '\tF6'
HK_windowLayout3 = '\tF7'
HK_windowLayout4 = '\tF8'

# help
ID_helpAbout = wx.ID_ABOUT
ID_helpHomepage = wx.NewId()
ID_helpForum = wx.NewId()
ID_helpTwitter = wx.NewId()
ID_helpCite = wx.NewId()
ID_helpDonate = wx.NewId()
ID_helpUpdate = wx.NewId()
ID_helpUserGuide = wx.NewId()
ID_helpDownload = wx.NewId()
ID_helpWhatsNew = wx.NewId()

HK_helpUserGuide = '\tF1'

# peaklist panel
ID_peaklistAnnotate = wx.NewId()
ID_peaklistSendToMassToFormula = wx.NewId()

# match panel
ID_matchErrors = wx.NewId()
ID_matchSummary = wx.NewId()

# calibration panel
ID_calibrationReferences = wx.NewId()
ID_calibrationErrors = wx.NewId()

# mass calculator panel
ID_massCalculatorSummary = wx.NewId()
ID_massCalculatorIonSeries = wx.NewId()
ID_massCalculatorPattern = wx.NewId()
ID_massCalculatorCollapse = wx.NewId()

# mass to formula panel
ID_massToFormulaSearchPubChem = wx.NewId()
ID_massToFormulaSearchChemSpider = wx.NewId()
ID_massToFormulaSearchMETLIN = wx.NewId()
ID_massToFormulaSearchHMDB = wx.NewId()
ID_massToFormulaSearchLipidMaps = wx.NewId()

# coumpounds search panel
ID_compoundsSearchCompounds = wx.NewId()
ID_compoundsSearchFormula = wx.NewId()

# mascot panel
ID_mascotPMF = wx.NewId()
ID_mascotMIS = wx.NewId()
ID_mascotSQ = wx.NewId()
ID_mascotQuery = wx.NewId()

# profound panel
ID_profoundPMF = wx.NewId()
ID_profoundQuery = wx.NewId()

# prospector panel
ID_prospectorMSFit = wx.NewId()
ID_prospectorMSTag = wx.NewId()
ID_prospectorQuery = wx.NewId()

# info panel
ID_documentInfoSummary = wx.NewId()
ID_documentInfoSpectrum = wx.NewId()
ID_documentInfoNotes = wx.NewId()

# export panel
ID_documentExportImage = wx.NewId()
ID_documentExportPeaklist = wx.NewId()
ID_documentExportSpectrum = wx.NewId()

# dialog buttons
ID_dlgDontSave = wx.NewId()
ID_dlgSave = wx.NewId()
ID_dlgCancel = wx.NewId()
ID_dlgDiscard = wx.NewId()
ID_dlgReview = wx.NewId()
ID_dlgReplace = wx.NewId()
ID_dlgReplaceAll = wx.NewId()
ID_dlgSkip = wx.NewId()
ID_dlgAppend = wx.NewId()

# list pop-up menu
ID_listViewAll = wx.NewId()
ID_listViewMatched = wx.NewId()
ID_listViewUnmatched = wx.NewId()
ID_listCopy = wx.NewId()
ID_listCopySequence = wx.NewId()
ID_listCopyFormula = wx.NewId()
ID_listSendToMassCalculator = wx.NewId()
ID_listSendToEnvelopeFit = wx.NewId()
