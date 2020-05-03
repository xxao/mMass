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
from wx.tools import img2py

import ids


# IMAGES
# ------

lib = {}

def loadImages():
    """Load images from lib."""
    
    # load image library
    if wx.Platform == '__WXMAC__':
        import images_lib_mac as images_lib
    elif wx.Platform == '__WXMSW__':
        import images_lib_msw as images_lib
    else:
        import images_lib_gtk as images_lib
    
    # common
    lib['icon16'] = images_lib.getIcon16Icon()
    lib['icon32'] = images_lib.getIcon32Icon()
    lib['icon48'] = images_lib.getIcon48Icon()
    lib['icon128'] = images_lib.getIcon128Icon()
    lib['icon256'] = images_lib.getIcon256Icon()
    lib['icon512'] = images_lib.getIcon512Icon()
    
    lib['iconAbout'] = images_lib.getIconAboutBitmap()
    lib['iconError'] = images_lib.getIconErrorBitmap()
    lib['iconDlg'] = images_lib.getIconDlgBitmap()
    
    # singles
    lib['stopper'] = images_lib.getStopperBitmap()
    
    # cursors
    cursors = images_lib.getCursorsBitmap()
    image = cursors.GetSubBitmap(wx.Rect(0, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrow'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(16, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrowMeasure'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(32, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrowPeak'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(48, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrowPoint'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(64, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrowDelete'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(80, 0, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 0)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 0)
    lib['cursorsArrowOffset'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(0, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCross'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(16, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCrossMeasure'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(32, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCrossPeak'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(48, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCrossPoint'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(64, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCrossDelete'] = wx.CursorFromImage(image)
    image = cursors.GetSubBitmap(wx.Rect(80, 16, 16, 16)).ConvertToImage()
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 7)
    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 7)
    lib['cursorsCrossOffset'] = wx.CursorFromImage(image)
    
    # arrows
    arrows = images_lib.getArrowsBitmap()
    lib['arrowsUp'] = arrows.GetSubBitmap(wx.Rect(0, 0, 11, 11))
    lib['arrowsRight'] = arrows.GetSubBitmap(wx.Rect(11, 0, 11, 11))
    lib['arrowsDown'] = arrows.GetSubBitmap(wx.Rect(22, 0, 11, 11))
    lib['arrowsLeft'] = arrows.GetSubBitmap(wx.Rect(33, 0, 11, 11))
    
    # backgrounds
    lib['bgrToolbar'] = images_lib.getBgrToolbarBitmap()
    lib['bgrToolbarNoBorder'] = images_lib.getBgrToolbarNoBorderBitmap()
    lib['bgrControlbar'] = images_lib.getBgrControlbarBitmap()
    lib['bgrControlbarBorder'] = images_lib.getBgrControlbarBorderBitmap()
    lib['bgrControlbarDouble'] = images_lib.getBgrControlbarDoubleBitmap()
    lib['bgrBottombar'] = images_lib.getBgrBottombarBitmap()
    lib['bgrPeakEditor'] = images_lib.getBgrPeakEditorBitmap()
    
    # bullets
    bulletsOn = images_lib.getBulletsOnBitmap()
    bulletsOff = images_lib.getBulletsOffBitmap()
    lib['bulletsDocument'] = bulletsOn.GetSubBitmap(wx.Rect(0, 0, 13, 12))
    lib['bulletsAnnotationsOn'] = bulletsOn.GetSubBitmap(wx.Rect(13, 0, 13, 12))
    lib['bulletsAnnotationsOff'] = bulletsOff.GetSubBitmap(wx.Rect(13, 0, 13, 12))
    lib['bulletsSequenceOn'] = bulletsOn.GetSubBitmap(wx.Rect(26, 0, 13, 12))
    lib['bulletsSequenceOff'] = bulletsOff.GetSubBitmap(wx.Rect(26, 0, 13, 12))
    lib['bulletsNotationOn'] = bulletsOn.GetSubBitmap(wx.Rect(39, 0, 13, 12))
    lib['bulletsNotationOff'] = bulletsOff.GetSubBitmap(wx.Rect(39, 0, 13, 12))
    
    # tools
    if wx.Platform == '__WXMAC__':
        tools = images_lib.getToolsBitmap()
        lib['toolsProcessing'] = tools.GetSubBitmap(wx.Rect(0, 5, 32, 23))
        lib['toolsCalibration'] = tools.GetSubBitmap(wx.Rect(32, 5, 32, 23))
        lib['toolsSequence'] = tools.GetSubBitmap(wx.Rect(64, 5, 32, 23))
        lib['toolsMassCalculator'] = tools.GetSubBitmap(wx.Rect(96, 5, 32, 23))
        lib['toolsCompoundsSearch'] = tools.GetSubBitmap(wx.Rect(128, 5, 32, 23))
        lib['toolsPeakDifferences'] = tools.GetSubBitmap(wx.Rect(160, 5, 32, 23))
        lib['toolsComparePeaklists'] = tools.GetSubBitmap(wx.Rect(192, 5, 32, 23))
        lib['toolsMascot'] = tools.GetSubBitmap(wx.Rect(224, 5, 32, 23))
        lib['toolsProfound'] = tools.GetSubBitmap(wx.Rect(256, 5, 32, 23))
        lib['toolsDocumentInfo'] = tools.GetSubBitmap(wx.Rect(288, 5, 32, 23))
        lib['toolsDocumentReport'] = tools.GetSubBitmap(wx.Rect(320, 5, 32, 23))
        lib['toolsDocumentExport'] = tools.GetSubBitmap(wx.Rect(352, 5, 32, 23))
        lib['toolsMassFilter'] = tools.GetSubBitmap(wx.Rect(384, 5, 32, 23))
        lib['toolsSpectrumGenerator'] = tools.GetSubBitmap(wx.Rect(416, 5, 32, 23))
        lib['toolsEnvelopeFit'] = tools.GetSubBitmap(wx.Rect(448, 5, 32, 23))
        lib['toolsMassToFormula'] = tools.GetSubBitmap(wx.Rect(480, 5, 32, 23))
        lib['toolsPeriodicTable'] = tools.GetSubBitmap(wx.Rect(512, 5, 32, 23))
        lib['toolsMassDefectPlot'] = tools.GetSubBitmap(wx.Rect(544, 5, 32, 23))
        
        lib['toolsPresets'] = tools.GetSubBitmap(wx.Rect(0, 37, 32, 22))
        lib['toolsLibrary'] = tools.GetSubBitmap(wx.Rect(32, 37, 32, 22))
    else:
        tools = images_lib.getToolsBitmap()
        lib['toolsOpen'] = tools.GetSubBitmap(wx.Rect(0, 0, 22, 22))
        lib['toolsSave'] = tools.GetSubBitmap(wx.Rect(22, 0, 22, 22))
        lib['toolsPrint'] = tools.GetSubBitmap(wx.Rect(44, 0, 22, 22))
        lib['toolsProcessing'] = tools.GetSubBitmap(wx.Rect(66, 0, 22, 22))
        lib['toolsCalibration'] = tools.GetSubBitmap(wx.Rect(88, 0, 22, 22))
        lib['toolsSequence'] = tools.GetSubBitmap(wx.Rect(110, 0, 22, 22))
        lib['toolsMassCalculator'] = tools.GetSubBitmap(wx.Rect(132, 0, 22, 22))
        lib['toolsCompoundsSearch'] = tools.GetSubBitmap(wx.Rect(154, 0, 22, 22))
        lib['toolsPeakDifferences'] = tools.GetSubBitmap(wx.Rect(176, 0, 22, 22))
        lib['toolsComparePeaklists'] = tools.GetSubBitmap(wx.Rect(198, 0, 22, 22))
        lib['toolsMascot'] = tools.GetSubBitmap(wx.Rect(220, 0, 22, 22))
        lib['toolsProfound'] = tools.GetSubBitmap(wx.Rect(242, 0, 22, 22))
        lib['toolsDocumentInfo'] = tools.GetSubBitmap(wx.Rect(264, 0, 22, 22))
        lib['toolsDocumentReport'] = tools.GetSubBitmap(wx.Rect(286, 0, 22, 22))
        lib['toolsDocumentExport'] = tools.GetSubBitmap(wx.Rect(308, 0, 22, 22))
        lib['toolsPresets'] = tools.GetSubBitmap(wx.Rect(330, 0, 22, 22))
        lib['toolsMassFilter'] = tools.GetSubBitmap(wx.Rect(352, 0, 22, 22))
        lib['toolsSpectrumGenerator'] = tools.GetSubBitmap(wx.Rect(374, 0, 22, 22))
        lib['toolsEnvelopeFit'] = tools.GetSubBitmap(wx.Rect(396, 0, 22, 22))
        lib['toolsLibrary'] = tools.GetSubBitmap(wx.Rect(418, 0, 22, 22))
        lib['toolsMassToFormula'] = tools.GetSubBitmap(wx.Rect(440, 0, 22, 22))
        lib['toolsPeriodicTable'] = tools.GetSubBitmap(wx.Rect(462, 0, 22, 22))
        lib['toolsMassDefectPlot'] = tools.GetSubBitmap(wx.Rect(484, 0, 22, 22))
    
    # bottombars
    bottombarsOn = images_lib.getBottombarsOnBitmap()
    bottombarsOff = images_lib.getBottombarsOffBitmap()
    
    lib['documentsAdd'] = bottombarsOff.GetSubBitmap(wx.Rect(0, 0, 29, 22))
    lib['documentsDelete'] = bottombarsOff.GetSubBitmap(wx.Rect(29, 0, 29, 22))
    
    lib['peaklistAdd'] = bottombarsOff.GetSubBitmap(wx.Rect(0, 22, 29, 22))
    lib['peaklistDelete'] = bottombarsOff.GetSubBitmap(wx.Rect(29, 22, 29, 22))
    lib['peaklistAnnotate'] = bottombarsOff.GetSubBitmap(wx.Rect(58, 22, 29, 22))
    lib['peaklistEditorOn'] = bottombarsOn.GetSubBitmap(wx.Rect(87, 22, 29, 22))
    lib['peaklistEditorOff'] = bottombarsOff.GetSubBitmap(wx.Rect(87, 22, 29, 22))
    
    lib['spectrumLabelsOn'] = bottombarsOn.GetSubBitmap(wx.Rect(0, 44, 29, 22))
    lib['spectrumLabelsOff'] = bottombarsOff.GetSubBitmap(wx.Rect(0, 44, 29, 22))
    lib['spectrumTicksOn'] = bottombarsOn.GetSubBitmap(wx.Rect(29, 44, 29, 22))
    lib['spectrumTicksOff'] = bottombarsOff.GetSubBitmap(wx.Rect(29, 44, 29, 22))
    lib['spectrumNotationsOn'] = bottombarsOn.GetSubBitmap(wx.Rect(58, 44, 29, 22))
    lib['spectrumNotationsOff'] = bottombarsOff.GetSubBitmap(wx.Rect(58, 44, 29, 22))
    lib['spectrumLabelAngleOn'] = bottombarsOn.GetSubBitmap(wx.Rect(87, 44, 29, 22))
    lib['spectrumLabelAngleOff'] = bottombarsOff.GetSubBitmap(wx.Rect(87, 44, 29, 22))
    lib['spectrumPosBarsOn'] = bottombarsOn.GetSubBitmap(wx.Rect(116, 44, 29, 22))
    lib['spectrumPosBarsOff'] = bottombarsOff.GetSubBitmap(wx.Rect(116, 44, 29, 22))
    lib['spectrumGelOn'] = bottombarsOn.GetSubBitmap(wx.Rect(145, 44, 29, 22))
    lib['spectrumGelOff'] = bottombarsOff.GetSubBitmap(wx.Rect(145, 44, 29, 22))
    lib['spectrumTrackerOn'] = bottombarsOn.GetSubBitmap(wx.Rect(174, 44, 29, 22))
    lib['spectrumTrackerOff'] = bottombarsOff.GetSubBitmap(wx.Rect(174, 44, 29, 22))
    lib['spectrumAutoscaleOn'] = bottombarsOn.GetSubBitmap(wx.Rect(203, 44, 29, 22))
    lib['spectrumAutoscaleOff'] = bottombarsOff.GetSubBitmap(wx.Rect(203, 44, 29, 22))
    lib['spectrumNormalizeOn'] = bottombarsOn.GetSubBitmap(wx.Rect(232, 44, 29, 22))
    lib['spectrumNormalizeOff'] = bottombarsOff.GetSubBitmap(wx.Rect(232, 44, 29, 22))
    
    lib['spectrumRulerOn'] = bottombarsOn.GetSubBitmap(wx.Rect(0, 66, 29, 22))
    lib['spectrumRulerOff'] = bottombarsOff.GetSubBitmap(wx.Rect(0, 66, 29, 22))
    lib['spectrumLabelPeakOn'] = bottombarsOn.GetSubBitmap(wx.Rect(29, 66, 29, 22))
    lib['spectrumLabelPeakOff'] = bottombarsOff.GetSubBitmap(wx.Rect(29, 66, 29, 22))
    lib['spectrumLabelPointOn'] = bottombarsOn.GetSubBitmap(wx.Rect(58, 66, 29, 22))
    lib['spectrumLabelPointOff'] = bottombarsOff.GetSubBitmap(wx.Rect(58, 66, 29, 22))
    lib['spectrumLabelEnvelopeOn'] = bottombarsOn.GetSubBitmap(wx.Rect(87, 66, 29, 22))
    lib['spectrumLabelEnvelopeOff'] = bottombarsOff.GetSubBitmap(wx.Rect(87, 66, 29, 22))
    lib['spectrumDeleteLabelOn'] = bottombarsOn.GetSubBitmap(wx.Rect(116, 66, 29, 22))
    lib['spectrumDeleteLabelOff'] = bottombarsOff.GetSubBitmap(wx.Rect(116, 66, 29, 22))
    lib['spectrumOffsetOn'] = bottombarsOn.GetSubBitmap(wx.Rect(145, 66, 29, 22))
    lib['spectrumOffsetOff'] = bottombarsOff.GetSubBitmap(wx.Rect(145, 66, 29, 22))
    
    # toolbars
    toolbarsOn = images_lib.getToolbarsOnBitmap()
    toolbarsOff = images_lib.getToolbarsOffBitmap()
    
    lib['compoundsSearchCompoundsOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 0, 29, 22))
    lib['compoundsSearchCompoundsOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 0, 29, 22))
    lib['compoundsSearchFormulaOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 0, 29, 22))
    lib['compoundsSearchFormulaOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 0, 29, 22))
    
    lib['calibrationReferencesOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 22, 29, 22))
    lib['calibrationReferencesOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 22, 29, 22))
    lib['calibrationErrorsOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 22, 29, 22))
    lib['calibrationErrorsOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 22, 29, 22))
    
    lib['documentExportImageOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 44, 29, 22))
    lib['documentExportImageOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 44, 29, 22))
    lib['documentExportPeaklistOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 44, 29, 22))
    lib['documentExportPeaklistOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 44, 29, 22))
    lib['documentExportSpectrumOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 44, 29, 22))
    lib['documentExportSpectrumOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 44, 29, 22))
    
    lib['documentInfoSummaryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 66, 29, 22))
    lib['documentInfoSummaryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 66, 29, 22))
    lib['documentInfoSpectrumOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 66, 29, 22))
    lib['documentInfoSpectrumOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 66, 29, 22))
    lib['documentInfoNotesOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 66, 29, 22))
    lib['documentInfoNotesOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 66, 29, 22))
    
    lib['mascotPMFOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 88, 29, 22))
    lib['mascotPMFOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 88, 29, 22))
    lib['mascotMISOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 88, 29, 22))
    lib['mascotMISOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 88, 29, 22))
    lib['mascotSQOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 88, 29, 22))
    lib['mascotSQOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 88, 29, 22))
    lib['mascotQueryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(87, 88, 29, 22))
    lib['mascotQueryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(87, 88, 29, 22))
    
    lib['massCalculatorSummaryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 110, 29, 22))
    lib['massCalculatorSummaryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 110, 29, 22))
    lib['massCalculatorIonSeriesOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 110, 29, 22))
    lib['massCalculatorIonSeriesOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 110, 29, 22))
    lib['massCalculatorPatternOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 110, 29, 22))
    lib['massCalculatorPatternOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 110, 29, 22))
    
    lib['processingMathOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 132, 29, 22))
    lib['processingMathOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 132, 29, 22))
    lib['processingCropOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 132, 29, 22))
    lib['processingCropOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 132, 29, 22))
    lib['processingBaselineOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 132, 29, 22))
    lib['processingBaselineOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 132, 29, 22))
    lib['processingSmoothingOn'] = toolbarsOn.GetSubBitmap(wx.Rect(87, 132, 29, 22))
    lib['processingSmoothingOff'] = toolbarsOff.GetSubBitmap(wx.Rect(87, 132, 29, 22))
    lib['processingPeakpickingOn'] = toolbarsOn.GetSubBitmap(wx.Rect(116, 132, 29, 22))
    lib['processingPeakpickingOff'] = toolbarsOff.GetSubBitmap(wx.Rect(116, 132, 29, 22))
    lib['processingDeisotopingOn'] = toolbarsOn.GetSubBitmap(wx.Rect(145, 132, 29, 22))
    lib['processingDeisotopingOff'] = toolbarsOff.GetSubBitmap(wx.Rect(145, 132, 29, 22))
    lib['processingDeconvolutionOn'] = toolbarsOn.GetSubBitmap(wx.Rect(174, 132, 29, 22))
    lib['processingDeconvolutionOff'] = toolbarsOff.GetSubBitmap(wx.Rect(174, 132, 29, 22))
    lib['processingBatchOn'] = toolbarsOn.GetSubBitmap(wx.Rect(203, 132, 29, 22))
    lib['processingBatchOff'] = toolbarsOff.GetSubBitmap(wx.Rect(203, 132, 29, 22))
    
    lib['sequenceEditorOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 154, 29, 22))
    lib['sequenceEditorOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 154, 29, 22))
    lib['sequenceModificationsOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 154, 29, 22))
    lib['sequenceModificationsOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 154, 29, 22))
    lib['sequenceDigestOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 154, 29, 22))
    lib['sequenceDigestOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 154, 29, 22))
    lib['sequenceFragmentOn'] = toolbarsOn.GetSubBitmap(wx.Rect(87, 154, 29, 22))
    lib['sequenceFragmentOff'] = toolbarsOff.GetSubBitmap(wx.Rect(87, 154, 29, 22))
    lib['sequenceSearchOn'] = toolbarsOn.GetSubBitmap(wx.Rect(116, 154, 29, 22))
    lib['sequenceSearchOff'] = toolbarsOff.GetSubBitmap(wx.Rect(116, 154, 29, 22))
    
    lib['profoundPMFOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 176, 29, 22))
    lib['profoundPMFOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 176, 29, 22))
    lib['profoundQueryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 176, 29, 22))
    lib['profoundQueryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 176, 29, 22))
    
    lib['prospectorMSFitOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 176, 29, 22))
    lib['prospectorMSFitOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 176, 29, 22))
    lib['prospectorMSTagOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 88, 29, 22))
    lib['prospectorMSTagOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 88, 29, 22))
    lib['prospectorQueryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(58, 176, 29, 22))
    lib['prospectorQueryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(58, 176, 29, 22))
    
    lib['matchErrorsOn'] = toolbarsOn.GetSubBitmap(wx.Rect(0, 198, 29, 22))
    lib['matchErrorsOff'] = toolbarsOff.GetSubBitmap(wx.Rect(0, 198, 29, 22))
    lib['matchSummaryOn'] = toolbarsOn.GetSubBitmap(wx.Rect(29, 198, 29, 22))
    lib['matchSummaryOff'] = toolbarsOff.GetSubBitmap(wx.Rect(29, 198, 29, 22))
    
    # periodic table
    ptableOn = images_lib.getPtableOnBitmap()
    ptableOff = images_lib.getPtableOffBitmap()
    ptableSel = images_lib.getPtableSelBitmap()
    
    lib['periodicTableConnection'] = ptableOn.GetSubBitmap(wx.Rect(48, 183, 24, 72))
    
    lib['periodicTableHOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 0, 25, 27))
    lib['periodicTableHeOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 0, 25, 27))
    lib['periodicTableLiOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 26, 25, 27))
    lib['periodicTableBeOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 26, 25, 27))
    lib['periodicTableBOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 26, 25, 27))
    lib['periodicTableCOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 26, 25, 27))
    lib['periodicTableNOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 26, 25, 27))
    lib['periodicTableOOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 26, 25, 27))
    lib['periodicTableFOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 26, 25, 27))
    lib['periodicTableNeOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 26, 25, 27))
    lib['periodicTableNaOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 52, 25, 27))
    lib['periodicTableMgOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 52, 25, 27))
    lib['periodicTableAlOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 52, 25, 27))
    lib['periodicTableSiOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 52, 25, 27))
    lib['periodicTablePOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 52, 25, 27))
    lib['periodicTableSOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 52, 25, 27))
    lib['periodicTableClOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 52, 25, 27))
    lib['periodicTableArOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 52, 25, 27))
    lib['periodicTableKOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 78, 25, 27))
    lib['periodicTableCaOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 78, 25, 27))
    lib['periodicTableScOn'] = ptableOn.GetSubBitmap(wx.Rect(48, 78, 25, 27))
    lib['periodicTableTiOn'] = ptableOn.GetSubBitmap(wx.Rect(72, 78, 25, 27))
    lib['periodicTableVOn'] = ptableOn.GetSubBitmap(wx.Rect(96, 78, 25, 27))
    lib['periodicTableCrOn'] = ptableOn.GetSubBitmap(wx.Rect(120, 78, 25, 27))
    lib['periodicTableMnOn'] = ptableOn.GetSubBitmap(wx.Rect(144, 78, 25, 27))
    lib['periodicTableFeOn'] = ptableOn.GetSubBitmap(wx.Rect(168, 78, 25, 27))
    lib['periodicTableCoOn'] = ptableOn.GetSubBitmap(wx.Rect(192, 78, 25, 27))
    lib['periodicTableNiOn'] = ptableOn.GetSubBitmap(wx.Rect(216, 78, 25, 27))
    lib['periodicTableCuOn'] = ptableOn.GetSubBitmap(wx.Rect(240, 78, 25, 27))
    lib['periodicTableZnOn'] = ptableOn.GetSubBitmap(wx.Rect(264, 78, 25, 27))
    lib['periodicTableGaOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 78, 25, 27))
    lib['periodicTableGeOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 78, 25, 27))
    lib['periodicTableAsOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 78, 25, 27))
    lib['periodicTableSeOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 78, 25, 27))
    lib['periodicTableBrOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 78, 25, 27))
    lib['periodicTableKrOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 78, 25, 27))
    lib['periodicTableRbOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 104, 25, 27))
    lib['periodicTableSrOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 104, 25, 27))
    lib['periodicTableYOn'] = ptableOn.GetSubBitmap(wx.Rect(48, 104, 25, 27))
    lib['periodicTableZrOn'] = ptableOn.GetSubBitmap(wx.Rect(72, 104, 25, 27))
    lib['periodicTableNbOn'] = ptableOn.GetSubBitmap(wx.Rect(96, 104, 25, 27))
    lib['periodicTableMoOn'] = ptableOn.GetSubBitmap(wx.Rect(120, 104, 25, 27))
    lib['periodicTableTcOn'] = ptableOn.GetSubBitmap(wx.Rect(144, 104, 25, 27))
    lib['periodicTableRuOn'] = ptableOn.GetSubBitmap(wx.Rect(168, 104, 25, 27))
    lib['periodicTableRhOn'] = ptableOn.GetSubBitmap(wx.Rect(192, 104, 25, 27))
    lib['periodicTablePdOn'] = ptableOn.GetSubBitmap(wx.Rect(216, 104, 25, 27))
    lib['periodicTableAgOn'] = ptableOn.GetSubBitmap(wx.Rect(240, 104, 25, 27))
    lib['periodicTableCdOn'] = ptableOn.GetSubBitmap(wx.Rect(264, 104, 25, 27))
    lib['periodicTableInOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 104, 25, 27))
    lib['periodicTableSnOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 104, 25, 27))
    lib['periodicTableSbOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 104, 25, 27))
    lib['periodicTableTeOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 104, 25, 27))
    lib['periodicTableIOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 104, 25, 27))
    lib['periodicTableXeOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 104, 25, 27))
    lib['periodicTableCsOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 130, 25, 27))
    lib['periodicTableBaOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 130, 25, 27))
    lib['periodicTableLaOn'] = ptableOn.GetSubBitmap(wx.Rect(48, 130, 25, 27))
    lib['periodicTableHfOn'] = ptableOn.GetSubBitmap(wx.Rect(72, 130, 25, 27))
    lib['periodicTableTaOn'] = ptableOn.GetSubBitmap(wx.Rect(96, 130, 25, 27))
    lib['periodicTableWOn'] = ptableOn.GetSubBitmap(wx.Rect(120, 130, 25, 27))
    lib['periodicTableReOn'] = ptableOn.GetSubBitmap(wx.Rect(144, 130, 25, 27))
    lib['periodicTableOsOn'] = ptableOn.GetSubBitmap(wx.Rect(168, 130, 25, 27))
    lib['periodicTableIrOn'] = ptableOn.GetSubBitmap(wx.Rect(192, 130, 25, 27))
    lib['periodicTablePtOn'] = ptableOn.GetSubBitmap(wx.Rect(216, 130, 25, 27))
    lib['periodicTableAuOn'] = ptableOn.GetSubBitmap(wx.Rect(240, 130, 25, 27))
    lib['periodicTableHgOn'] = ptableOn.GetSubBitmap(wx.Rect(264, 130, 25, 27))
    lib['periodicTableTlOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 130, 25, 27))
    lib['periodicTablePbOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 130, 25, 27))
    lib['periodicTableBiOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 130, 25, 27))
    lib['periodicTablePoOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 130, 25, 27))
    lib['periodicTableAtOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 130, 25, 27))
    lib['periodicTableRnOn'] = ptableOn.GetSubBitmap(wx.Rect(408, 130, 25, 27))
    lib['periodicTableFrOn'] = ptableOn.GetSubBitmap(wx.Rect(0, 156, 25, 27))
    lib['periodicTableRaOn'] = ptableOn.GetSubBitmap(wx.Rect(24, 156, 25, 27))
    lib['periodicTableAcOn'] = ptableOn.GetSubBitmap(wx.Rect(48, 156, 25, 27))
    lib['periodicTableCeOn'] = ptableOn.GetSubBitmap(wx.Rect(72, 202, 25, 27))
    lib['periodicTablePrOn'] = ptableOn.GetSubBitmap(wx.Rect(96, 202, 25, 27))
    lib['periodicTableNdOn'] = ptableOn.GetSubBitmap(wx.Rect(120, 202, 25, 27))
    lib['periodicTablePmOn'] = ptableOn.GetSubBitmap(wx.Rect(144, 202, 25, 27))
    lib['periodicTableSmOn'] = ptableOn.GetSubBitmap(wx.Rect(168, 202, 25, 27))
    lib['periodicTableEuOn'] = ptableOn.GetSubBitmap(wx.Rect(192, 202, 25, 27))
    lib['periodicTableGdOn'] = ptableOn.GetSubBitmap(wx.Rect(216, 202, 25, 27))
    lib['periodicTableTbOn'] = ptableOn.GetSubBitmap(wx.Rect(240, 202, 25, 27))
    lib['periodicTableDyOn'] = ptableOn.GetSubBitmap(wx.Rect(264, 202, 25, 27))
    lib['periodicTableHoOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 202, 25, 27))
    lib['periodicTableErOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 202, 25, 27))
    lib['periodicTableTmOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 202, 25, 27))
    lib['periodicTableYbOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 202, 25, 27))
    lib['periodicTableLuOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 202, 25, 27))
    lib['periodicTableThOn'] = ptableOn.GetSubBitmap(wx.Rect(72, 228, 25, 27))
    lib['periodicTablePaOn'] = ptableOn.GetSubBitmap(wx.Rect(96, 228, 25, 27))
    lib['periodicTableUOn'] = ptableOn.GetSubBitmap(wx.Rect(120, 228, 25, 27))
    lib['periodicTableNpOn'] = ptableOn.GetSubBitmap(wx.Rect(144, 228, 25, 27))
    lib['periodicTablePuOn'] = ptableOn.GetSubBitmap(wx.Rect(168, 228, 25, 27))
    lib['periodicTableAmOn'] = ptableOn.GetSubBitmap(wx.Rect(192, 228, 25, 27))
    lib['periodicTableCmOn'] = ptableOn.GetSubBitmap(wx.Rect(216, 228, 25, 27))
    lib['periodicTableBkOn'] = ptableOn.GetSubBitmap(wx.Rect(240, 228, 25, 27))
    lib['periodicTableCfOn'] = ptableOn.GetSubBitmap(wx.Rect(264, 228, 25, 27))
    lib['periodicTableEsOn'] = ptableOn.GetSubBitmap(wx.Rect(288, 228, 25, 27))
    lib['periodicTableFmOn'] = ptableOn.GetSubBitmap(wx.Rect(312, 228, 25, 27))
    lib['periodicTableMdOn'] = ptableOn.GetSubBitmap(wx.Rect(336, 228, 25, 27))
    lib['periodicTableNoOn'] = ptableOn.GetSubBitmap(wx.Rect(360, 228, 25, 27))
    lib['periodicTableLrOn'] = ptableOn.GetSubBitmap(wx.Rect(384, 228, 25, 27))
    
    lib['periodicTableHOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 0, 25, 27))
    lib['periodicTableHeOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 0, 25, 27))
    lib['periodicTableLiOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 26, 25, 27))
    lib['periodicTableBeOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 26, 25, 27))
    lib['periodicTableBOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 26, 25, 27))
    lib['periodicTableCOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 26, 25, 27))
    lib['periodicTableNOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 26, 25, 27))
    lib['periodicTableOOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 26, 25, 27))
    lib['periodicTableFOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 26, 25, 27))
    lib['periodicTableNeOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 26, 25, 27))
    lib['periodicTableNaOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 52, 25, 27))
    lib['periodicTableMgOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 52, 25, 27))
    lib['periodicTableAlOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 52, 25, 27))
    lib['periodicTableSiOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 52, 25, 27))
    lib['periodicTablePOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 52, 25, 27))
    lib['periodicTableSOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 52, 25, 27))
    lib['periodicTableClOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 52, 25, 27))
    lib['periodicTableArOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 52, 25, 27))
    lib['periodicTableKOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 78, 25, 27))
    lib['periodicTableCaOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 78, 25, 27))
    lib['periodicTableScOff'] = ptableOff.GetSubBitmap(wx.Rect(48, 78, 25, 27))
    lib['periodicTableTiOff'] = ptableOff.GetSubBitmap(wx.Rect(72, 78, 25, 27))
    lib['periodicTableVOff'] = ptableOff.GetSubBitmap(wx.Rect(96, 78, 25, 27))
    lib['periodicTableCrOff'] = ptableOff.GetSubBitmap(wx.Rect(120, 78, 25, 27))
    lib['periodicTableMnOff'] = ptableOff.GetSubBitmap(wx.Rect(144, 78, 25, 27))
    lib['periodicTableFeOff'] = ptableOff.GetSubBitmap(wx.Rect(168, 78, 25, 27))
    lib['periodicTableCoOff'] = ptableOff.GetSubBitmap(wx.Rect(192, 78, 25, 27))
    lib['periodicTableNiOff'] = ptableOff.GetSubBitmap(wx.Rect(216, 78, 25, 27))
    lib['periodicTableCuOff'] = ptableOff.GetSubBitmap(wx.Rect(240, 78, 25, 27))
    lib['periodicTableZnOff'] = ptableOff.GetSubBitmap(wx.Rect(264, 78, 25, 27))
    lib['periodicTableGaOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 78, 25, 27))
    lib['periodicTableGeOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 78, 25, 27))
    lib['periodicTableAsOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 78, 25, 27))
    lib['periodicTableSeOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 78, 25, 27))
    lib['periodicTableBrOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 78, 25, 27))
    lib['periodicTableKrOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 78, 25, 27))
    lib['periodicTableRbOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 104, 25, 27))
    lib['periodicTableSrOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 104, 25, 27))
    lib['periodicTableYOff'] = ptableOff.GetSubBitmap(wx.Rect(48, 104, 25, 27))
    lib['periodicTableZrOff'] = ptableOff.GetSubBitmap(wx.Rect(72, 104, 25, 27))
    lib['periodicTableNbOff'] = ptableOff.GetSubBitmap(wx.Rect(96, 104, 25, 27))
    lib['periodicTableMoOff'] = ptableOff.GetSubBitmap(wx.Rect(120, 104, 25, 27))
    lib['periodicTableTcOff'] = ptableOff.GetSubBitmap(wx.Rect(144, 104, 25, 27))
    lib['periodicTableRuOff'] = ptableOff.GetSubBitmap(wx.Rect(168, 104, 25, 27))
    lib['periodicTableRhOff'] = ptableOff.GetSubBitmap(wx.Rect(192, 104, 25, 27))
    lib['periodicTablePdOff'] = ptableOff.GetSubBitmap(wx.Rect(216, 104, 25, 27))
    lib['periodicTableAgOff'] = ptableOff.GetSubBitmap(wx.Rect(240, 104, 25, 27))
    lib['periodicTableCdOff'] = ptableOff.GetSubBitmap(wx.Rect(264, 104, 25, 27))
    lib['periodicTableInOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 104, 25, 27))
    lib['periodicTableSnOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 104, 25, 27))
    lib['periodicTableSbOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 104, 25, 27))
    lib['periodicTableTeOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 104, 25, 27))
    lib['periodicTableIOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 104, 25, 27))
    lib['periodicTableXeOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 104, 25, 27))
    lib['periodicTableCsOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 130, 25, 27))
    lib['periodicTableBaOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 130, 25, 27))
    lib['periodicTableLaOff'] = ptableOff.GetSubBitmap(wx.Rect(48, 130, 25, 27))
    lib['periodicTableHfOff'] = ptableOff.GetSubBitmap(wx.Rect(72, 130, 25, 27))
    lib['periodicTableTaOff'] = ptableOff.GetSubBitmap(wx.Rect(96, 130, 25, 27))
    lib['periodicTableWOff'] = ptableOff.GetSubBitmap(wx.Rect(120, 130, 25, 27))
    lib['periodicTableReOff'] = ptableOff.GetSubBitmap(wx.Rect(144, 130, 25, 27))
    lib['periodicTableOsOff'] = ptableOff.GetSubBitmap(wx.Rect(168, 130, 25, 27))
    lib['periodicTableIrOff'] = ptableOff.GetSubBitmap(wx.Rect(192, 130, 25, 27))
    lib['periodicTablePtOff'] = ptableOff.GetSubBitmap(wx.Rect(216, 130, 25, 27))
    lib['periodicTableAuOff'] = ptableOff.GetSubBitmap(wx.Rect(240, 130, 25, 27))
    lib['periodicTableHgOff'] = ptableOff.GetSubBitmap(wx.Rect(264, 130, 25, 27))
    lib['periodicTableTlOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 130, 25, 27))
    lib['periodicTablePbOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 130, 25, 27))
    lib['periodicTableBiOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 130, 25, 27))
    lib['periodicTablePoOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 130, 25, 27))
    lib['periodicTableAtOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 130, 25, 27))
    lib['periodicTableRnOff'] = ptableOff.GetSubBitmap(wx.Rect(408, 130, 25, 27))
    lib['periodicTableFrOff'] = ptableOff.GetSubBitmap(wx.Rect(0, 156, 25, 27))
    lib['periodicTableRaOff'] = ptableOff.GetSubBitmap(wx.Rect(24, 156, 25, 27))
    lib['periodicTableAcOff'] = ptableOff.GetSubBitmap(wx.Rect(48, 156, 25, 27))
    lib['periodicTableCeOff'] = ptableOff.GetSubBitmap(wx.Rect(72, 202, 25, 27))
    lib['periodicTablePrOff'] = ptableOff.GetSubBitmap(wx.Rect(96, 202, 25, 27))
    lib['periodicTableNdOff'] = ptableOff.GetSubBitmap(wx.Rect(120, 202, 25, 27))
    lib['periodicTablePmOff'] = ptableOff.GetSubBitmap(wx.Rect(144, 202, 25, 27))
    lib['periodicTableSmOff'] = ptableOff.GetSubBitmap(wx.Rect(168, 202, 25, 27))
    lib['periodicTableEuOff'] = ptableOff.GetSubBitmap(wx.Rect(192, 202, 25, 27))
    lib['periodicTableGdOff'] = ptableOff.GetSubBitmap(wx.Rect(216, 202, 25, 27))
    lib['periodicTableTbOff'] = ptableOff.GetSubBitmap(wx.Rect(240, 202, 25, 27))
    lib['periodicTableDyOff'] = ptableOff.GetSubBitmap(wx.Rect(264, 202, 25, 27))
    lib['periodicTableHoOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 202, 25, 27))
    lib['periodicTableErOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 202, 25, 27))
    lib['periodicTableTmOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 202, 25, 27))
    lib['periodicTableYbOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 202, 25, 27))
    lib['periodicTableLuOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 202, 25, 27))
    lib['periodicTableThOff'] = ptableOff.GetSubBitmap(wx.Rect(72, 228, 25, 27))
    lib['periodicTablePaOff'] = ptableOff.GetSubBitmap(wx.Rect(96, 228, 25, 27))
    lib['periodicTableUOff'] = ptableOff.GetSubBitmap(wx.Rect(120, 228, 25, 27))
    lib['periodicTableNpOff'] = ptableOff.GetSubBitmap(wx.Rect(144, 228, 25, 27))
    lib['periodicTablePuOff'] = ptableOff.GetSubBitmap(wx.Rect(168, 228, 25, 27))
    lib['periodicTableAmOff'] = ptableOff.GetSubBitmap(wx.Rect(192, 228, 25, 27))
    lib['periodicTableCmOff'] = ptableOff.GetSubBitmap(wx.Rect(216, 228, 25, 27))
    lib['periodicTableBkOff'] = ptableOff.GetSubBitmap(wx.Rect(240, 228, 25, 27))
    lib['periodicTableCfOff'] = ptableOff.GetSubBitmap(wx.Rect(264, 228, 25, 27))
    lib['periodicTableEsOff'] = ptableOff.GetSubBitmap(wx.Rect(288, 228, 25, 27))
    lib['periodicTableFmOff'] = ptableOff.GetSubBitmap(wx.Rect(312, 228, 25, 27))
    lib['periodicTableMdOff'] = ptableOff.GetSubBitmap(wx.Rect(336, 228, 25, 27))
    lib['periodicTableNoOff'] = ptableOff.GetSubBitmap(wx.Rect(360, 228, 25, 27))
    lib['periodicTableLrOff'] = ptableOff.GetSubBitmap(wx.Rect(384, 228, 25, 27))
    
    lib['periodicTableHSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 0, 25, 27))
    lib['periodicTableHeSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 0, 25, 27))
    lib['periodicTableLiSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 26, 25, 27))
    lib['periodicTableBeSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 26, 25, 27))
    lib['periodicTableBSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 26, 25, 27))
    lib['periodicTableCSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 26, 25, 27))
    lib['periodicTableNSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 26, 25, 27))
    lib['periodicTableOSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 26, 25, 27))
    lib['periodicTableFSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 26, 25, 27))
    lib['periodicTableNeSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 26, 25, 27))
    lib['periodicTableNaSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 52, 25, 27))
    lib['periodicTableMgSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 52, 25, 27))
    lib['periodicTableAlSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 52, 25, 27))
    lib['periodicTableSiSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 52, 25, 27))
    lib['periodicTablePSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 52, 25, 27))
    lib['periodicTableSSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 52, 25, 27))
    lib['periodicTableClSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 52, 25, 27))
    lib['periodicTableArSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 52, 25, 27))
    lib['periodicTableKSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 78, 25, 27))
    lib['periodicTableCaSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 78, 25, 27))
    lib['periodicTableScSel'] = ptableSel.GetSubBitmap(wx.Rect(48, 78, 25, 27))
    lib['periodicTableTiSel'] = ptableSel.GetSubBitmap(wx.Rect(72, 78, 25, 27))
    lib['periodicTableVSel'] = ptableSel.GetSubBitmap(wx.Rect(96, 78, 25, 27))
    lib['periodicTableCrSel'] = ptableSel.GetSubBitmap(wx.Rect(120, 78, 25, 27))
    lib['periodicTableMnSel'] = ptableSel.GetSubBitmap(wx.Rect(144, 78, 25, 27))
    lib['periodicTableFeSel'] = ptableSel.GetSubBitmap(wx.Rect(168, 78, 25, 27))
    lib['periodicTableCoSel'] = ptableSel.GetSubBitmap(wx.Rect(192, 78, 25, 27))
    lib['periodicTableNiSel'] = ptableSel.GetSubBitmap(wx.Rect(216, 78, 25, 27))
    lib['periodicTableCuSel'] = ptableSel.GetSubBitmap(wx.Rect(240, 78, 25, 27))
    lib['periodicTableZnSel'] = ptableSel.GetSubBitmap(wx.Rect(264, 78, 25, 27))
    lib['periodicTableGaSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 78, 25, 27))
    lib['periodicTableGeSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 78, 25, 27))
    lib['periodicTableAsSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 78, 25, 27))
    lib['periodicTableSeSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 78, 25, 27))
    lib['periodicTableBrSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 78, 25, 27))
    lib['periodicTableKrSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 78, 25, 27))
    lib['periodicTableRbSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 104, 25, 27))
    lib['periodicTableSrSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 104, 25, 27))
    lib['periodicTableYSel'] = ptableSel.GetSubBitmap(wx.Rect(48, 104, 25, 27))
    lib['periodicTableZrSel'] = ptableSel.GetSubBitmap(wx.Rect(72, 104, 25, 27))
    lib['periodicTableNbSel'] = ptableSel.GetSubBitmap(wx.Rect(96, 104, 25, 27))
    lib['periodicTableMoSel'] = ptableSel.GetSubBitmap(wx.Rect(120, 104, 25, 27))
    lib['periodicTableTcSel'] = ptableSel.GetSubBitmap(wx.Rect(144, 104, 25, 27))
    lib['periodicTableRuSel'] = ptableSel.GetSubBitmap(wx.Rect(168, 104, 25, 27))
    lib['periodicTableRhSel'] = ptableSel.GetSubBitmap(wx.Rect(192, 104, 25, 27))
    lib['periodicTablePdSel'] = ptableSel.GetSubBitmap(wx.Rect(216, 104, 25, 27))
    lib['periodicTableAgSel'] = ptableSel.GetSubBitmap(wx.Rect(240, 104, 25, 27))
    lib['periodicTableCdSel'] = ptableSel.GetSubBitmap(wx.Rect(264, 104, 25, 27))
    lib['periodicTableInSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 104, 25, 27))
    lib['periodicTableSnSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 104, 25, 27))
    lib['periodicTableSbSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 104, 25, 27))
    lib['periodicTableTeSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 104, 25, 27))
    lib['periodicTableISel'] = ptableSel.GetSubBitmap(wx.Rect(384, 104, 25, 27))
    lib['periodicTableXeSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 104, 25, 27))
    lib['periodicTableCsSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 130, 25, 27))
    lib['periodicTableBaSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 130, 25, 27))
    lib['periodicTableLaSel'] = ptableSel.GetSubBitmap(wx.Rect(48, 130, 25, 27))
    lib['periodicTableHfSel'] = ptableSel.GetSubBitmap(wx.Rect(72, 130, 25, 27))
    lib['periodicTableTaSel'] = ptableSel.GetSubBitmap(wx.Rect(96, 130, 25, 27))
    lib['periodicTableWSel'] = ptableSel.GetSubBitmap(wx.Rect(120, 130, 25, 27))
    lib['periodicTableReSel'] = ptableSel.GetSubBitmap(wx.Rect(144, 130, 25, 27))
    lib['periodicTableOsSel'] = ptableSel.GetSubBitmap(wx.Rect(168, 130, 25, 27))
    lib['periodicTableIrSel'] = ptableSel.GetSubBitmap(wx.Rect(192, 130, 25, 27))
    lib['periodicTablePtSel'] = ptableSel.GetSubBitmap(wx.Rect(216, 130, 25, 27))
    lib['periodicTableAuSel'] = ptableSel.GetSubBitmap(wx.Rect(240, 130, 25, 27))
    lib['periodicTableHgSel'] = ptableSel.GetSubBitmap(wx.Rect(264, 130, 25, 27))
    lib['periodicTableTlSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 130, 25, 27))
    lib['periodicTablePbSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 130, 25, 27))
    lib['periodicTableBiSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 130, 25, 27))
    lib['periodicTablePoSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 130, 25, 27))
    lib['periodicTableAtSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 130, 25, 27))
    lib['periodicTableRnSel'] = ptableSel.GetSubBitmap(wx.Rect(408, 130, 25, 27))
    lib['periodicTableFrSel'] = ptableSel.GetSubBitmap(wx.Rect(0, 156, 25, 27))
    lib['periodicTableRaSel'] = ptableSel.GetSubBitmap(wx.Rect(24, 156, 25, 27))
    lib['periodicTableAcSel'] = ptableSel.GetSubBitmap(wx.Rect(48, 156, 25, 27))
    lib['periodicTableCeSel'] = ptableSel.GetSubBitmap(wx.Rect(72, 202, 25, 27))
    lib['periodicTablePrSel'] = ptableSel.GetSubBitmap(wx.Rect(96, 202, 25, 27))
    lib['periodicTableNdSel'] = ptableSel.GetSubBitmap(wx.Rect(120, 202, 25, 27))
    lib['periodicTablePmSel'] = ptableSel.GetSubBitmap(wx.Rect(144, 202, 25, 27))
    lib['periodicTableSmSel'] = ptableSel.GetSubBitmap(wx.Rect(168, 202, 25, 27))
    lib['periodicTableEuSel'] = ptableSel.GetSubBitmap(wx.Rect(192, 202, 25, 27))
    lib['periodicTableGdSel'] = ptableSel.GetSubBitmap(wx.Rect(216, 202, 25, 27))
    lib['periodicTableTbSel'] = ptableSel.GetSubBitmap(wx.Rect(240, 202, 25, 27))
    lib['periodicTableDySel'] = ptableSel.GetSubBitmap(wx.Rect(264, 202, 25, 27))
    lib['periodicTableHoSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 202, 25, 27))
    lib['periodicTableErSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 202, 25, 27))
    lib['periodicTableTmSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 202, 25, 27))
    lib['periodicTableYbSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 202, 25, 27))
    lib['periodicTableLuSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 202, 25, 27))
    lib['periodicTableThSel'] = ptableSel.GetSubBitmap(wx.Rect(72, 228, 25, 27))
    lib['periodicTablePaSel'] = ptableSel.GetSubBitmap(wx.Rect(96, 228, 25, 27))
    lib['periodicTableUSel'] = ptableSel.GetSubBitmap(wx.Rect(120, 228, 25, 27))
    lib['periodicTableNpSel'] = ptableSel.GetSubBitmap(wx.Rect(144, 228, 25, 27))
    lib['periodicTablePuSel'] = ptableSel.GetSubBitmap(wx.Rect(168, 228, 25, 27))
    lib['periodicTableAmSel'] = ptableSel.GetSubBitmap(wx.Rect(192, 228, 25, 27))
    lib['periodicTableCmSel'] = ptableSel.GetSubBitmap(wx.Rect(216, 228, 25, 27))
    lib['periodicTableBkSel'] = ptableSel.GetSubBitmap(wx.Rect(240, 228, 25, 27))
    lib['periodicTableCfSel'] = ptableSel.GetSubBitmap(wx.Rect(264, 228, 25, 27))
    lib['periodicTableEsSel'] = ptableSel.GetSubBitmap(wx.Rect(288, 228, 25, 27))
    lib['periodicTableFmSel'] = ptableSel.GetSubBitmap(wx.Rect(312, 228, 25, 27))
    lib['periodicTableMdSel'] = ptableSel.GetSubBitmap(wx.Rect(336, 228, 25, 27))
    lib['periodicTableNoSel'] = ptableSel.GetSubBitmap(wx.Rect(360, 228, 25, 27))
    lib['periodicTableLrSel'] = ptableSel.GetSubBitmap(wx.Rect(384, 228, 25, 27))
# ----


def convertImages():
    """Convert an image to PNG format and embed it in a Python file. """
    
    # get libs to import images
    try:
        from wx.lib.embeddedimage import PyEmbeddedImage
        imp = '#load libs\nfrom wx.lib.embeddedimage import PyEmbeddedImage\n\n\n'
    except:
        imp = '#load libs\nimport cStringIO\nfrom wx import ImageFromStream, BitmapFromImage\n\n\n'
    
    # convert images
    for platform in ('mac', 'msw', 'gtk'):
        
        # create file
        imageFile = file('images_lib_'+platform+'.py', 'w')
        imageFile.write(imp)
        imageFile.close()
        
        # make commands
        commands = [
            "-f -a -u -i -n Icon16 images/"+platform+"/icon_16.png images_lib_"+platform+".py",
            "-f -a -u -i -n Icon32 images/"+platform+"/icon_32.png images_lib_"+platform+".py",
            "-f -a -u -i -n Icon48 images/"+platform+"/icon_48.png images_lib_"+platform+".py",
            "-f -a -u -i -n Icon128 images/"+platform+"/icon_128.png images_lib_"+platform+".py",
            "-f -a -u -i -n Icon256 images/"+platform+"/icon_256.png images_lib_"+platform+".py",
            "-f -a -u -i -n Icon512 images/"+platform+"/icon_512.png images_lib_"+platform+".py",
            
            "-f -a -u -n IconAbout images/"+platform+"/icon_about.png images_lib_"+platform+".py",
            "-f -a -u -n IconError images/"+platform+"/icon_error.png images_lib_"+platform+".py",
            "-f -a -u -n IconDlg images/"+platform+"/icon_dlg.png images_lib_"+platform+".py",
            
            "-f -a -u -n Stopper images/"+platform+"/stopper.png images_lib_"+platform+".py",
            "-f -a -u -n Cursors images/"+platform+"/cursors.png images_lib_"+platform+".py",
            "-f -a -u -n Arrows images/"+platform+"/arrows.png images_lib_"+platform+".py",
            
            "-f -a -u -n BgrToolbar images/"+platform+"/bgr_toolbar.png images_lib_"+platform+".py",
            "-f -a -u -n BgrToolbarNoBorder images/"+platform+"/bgr_toolbar_noborder.png images_lib_"+platform+".py",
            "-f -a -u -n BgrControlbar images/"+platform+"/bgr_controlbar.png images_lib_"+platform+".py",
            "-f -a -u -n BgrControlbarBorder images/"+platform+"/bgr_controlbar_border.png images_lib_"+platform+".py",
            "-f -a -u -n BgrControlbarDouble images/"+platform+"/bgr_controlbar_double.png images_lib_"+platform+".py",
            "-f -a -u -n BgrBottombar images/"+platform+"/bgr_bottombar.png images_lib_"+platform+".py",
            "-f -a -u -n BgrPeakEditor images/"+platform+"/bgr_peakeditor.png images_lib_"+platform+".py",
            
            "-f -a -u -n BulletsOn images/"+platform+"/bullets_on.png images_lib_"+platform+".py",
            "-f -a -u -n BulletsOff images/"+platform+"/bullets_off.png images_lib_"+platform+".py",
            
            "-f -a -u -n Tools images/"+platform+"/tools.png images_lib_"+platform+".py",
            
            "-f -a -u -n BottombarsOn images/"+platform+"/bottombars_on.png images_lib_"+platform+".py",
            "-f -a -u -n BottombarsOff images/"+platform+"/bottombars_off.png images_lib_"+platform+".py",
            "-f -a -u -n ToolbarsOn images/"+platform+"/toolbars_on.png images_lib_"+platform+".py",
            "-f -a -u -n ToolbarsOff images/"+platform+"/toolbars_off.png images_lib_"+platform+".py",
            
            "-f -a -u -n PtableOn images/"+platform+"/periodic_table_on.png images_lib_"+platform+".py",
            "-f -a -u -n PtableOff images/"+platform+"/periodic_table_off.png images_lib_"+platform+".py",
            "-f -a -u -n PtableSel images/"+platform+"/periodic_table_sel.png images_lib_"+platform+".py",
        ]
        
        # convert images
        for command in commands:
            img2py.main(command.split())
# ----


if __name__ == "__main__":
    convertImages()