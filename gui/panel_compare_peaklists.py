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
import wx.grid

# load modules
import mwx
import images
import config
import mspy


# FLOATING PANEL WITH COMPARE PEAKLISTS TOOL
# ------------------------------------------

class panelComparePeaklists(wx.MiniFrame):
    """Compare peaklists tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Compare Peak Lists', size=(500, 400), style=wx.DEFAULT_FRAME_STYLE)
        
        self.parent = parent
        
        self.processing = None
        
        self.currentDocuments = []
        self.currentPeaklist = []
        self.currentMatches = []
        
        self._maxSize = 0
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panel
        mainPanel = self.makeMainPanel()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(mainPanel, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide gauge
        self.mainSizer.Hide(2)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbarNoBorder'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make elements
        compare_label = wx.StaticText(panel, -1, "Compare:")
        compare_label.SetFont(wx.SMALL_FONT)
        
        choices = ['Peak Lists', 'Notations (measured)', 'Notations (theoretical)']
        self.compare_choice = wx.Choice(panel, -1, choices=choices, size=(180, mwx.SMALL_CHOICE_HEIGHT))
        self.compare_choice.Bind(wx.EVT_CHOICE, self.onUpdatePeaklist)
        self.compare_choice.Select(0)
        if config.comparePeaklists['compare'] == 'measured':
            self.compare_choice.Select(1)
        elif config.comparePeaklists['compare'] == 'theoretical':
            self.compare_choice.Select(2)
        
        tolerance_label = wx.StaticText(panel, -1, "Tolerance:")
        tolerance_label.SetFont(wx.SMALL_FONT)
        
        self.tolerance_value = wx.TextCtrl(panel, -1, str(config.comparePeaklists['tolerance']), size=(60, -1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        self.tolerance_value.Bind(wx.EVT_TEXT_ENTER, self.onCompare)
        
        self.unitsDa_radio = wx.RadioButton(panel, -1, "Da", style=wx.RB_GROUP)
        self.unitsDa_radio.SetFont(wx.SMALL_FONT)
        self.unitsDa_radio.SetValue(True)
        
        self.unitsPpm_radio = wx.RadioButton(panel, -1, "ppm")
        self.unitsPpm_radio.SetFont(wx.SMALL_FONT)
        self.unitsPpm_radio.SetValue((config.comparePeaklists['units'] == 'ppm'))
        
        self.ignoreCharge_check = wx.CheckBox(panel, -1, "Ignore charge")
        self.ignoreCharge_check.SetFont(wx.SMALL_FONT)
        self.ignoreCharge_check.SetValue(config.comparePeaklists['ignoreCharge'])
        
        self.ratioCheck_check = wx.CheckBox(panel, -1, "Int. ratio:")
        self.ratioCheck_check.SetFont(wx.SMALL_FONT)
        self.ratioCheck_check.SetValue(config.comparePeaklists['ratioCheck'])
        self.ratioCheck_check.Bind(wx.EVT_CHECKBOX, self.onRatioCheckChanged)
        
        self.ratioDirection_choice = wx.Choice(panel, -1, choices=['Above', 'Below'], size=(80, mwx.SMALL_CHOICE_HEIGHT))
        self.ratioDirection_choice.Select(0)
        if config.comparePeaklists['ratioDirection'] == -1:
            self.ratioDirection_choice.Select(1)
        
        self.ratioThreshold_value = wx.TextCtrl(panel, -1, str(config.comparePeaklists['ratioThreshold']), size=(50, -1), validator=mwx.validator('floatPos'))
        
        self.compare_butt = wx.Button(panel, -1, "Compare", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.compare_butt.Bind(wx.EVT_BUTTON, self.onCompare)
        
        self.onRatioCheckChanged()
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(compare_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.compare_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(tolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.tolerance_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(self.unitsDa_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.unitsPpm_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.ignoreCharge_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.ratioCheck_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ratioDirection_choice, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.ratioThreshold_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.compare_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeMainPanel(self):
        """Make main panel."""
        
        panel = wx.Panel(self, -1)
        
        # make grids
        self.makeDocumentsGrid(panel)
        self.makePeaklistGrid(panel)
        self.makeMatchesGrid(panel)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.documentsGrid, 1, wx.EXPAND)
        mainSizer.AddSpacer(mwx.SASH_SIZE)
        mainSizer.Add(self.peaklistGrid, 0, wx.EXPAND)
        mainSizer.AddSpacer(mwx.SASH_SIZE)
        mainSizer.Add(self.matchesGrid, 0, wx.EXPAND)
        
        # fit layout
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeDocumentsGrid(self, panel):
        """Make documents grid."""
        
        # make table
        self.documentsGrid = wx.grid.Grid(panel, -1, size=(550, 500), style=mwx.GRID_STYLE)
        self.documentsGrid.CreateGrid(0, 0)
        self.documentsGrid.DisableDragColSize()
        self.documentsGrid.DisableDragRowSize()
        self.documentsGrid.SetColLabelSize(19)
        self.documentsGrid.SetRowLabelSize(0)
        self.documentsGrid.SetDefaultRowSize(19)
        self.documentsGrid.AutoSizeColumns(True)
        self.documentsGrid.SetLabelFont(wx.SMALL_FONT)
        self.documentsGrid.SetDefaultCellFont(wx.SMALL_FONT)
        self.documentsGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_TOP)
        self.documentsGrid.SetDefaultCellBackgroundColour(wx.WHITE)
        
        self.documentsGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onDocumentsCellSelected)
        self.documentsGrid.Bind(wx.EVT_KEY_DOWN, self.onDocumentsKey)
    # ----
    
    
    def makePeaklistGrid(self, panel):
        """Make total peaklist grid."""
        
        # make table
        self.peaklistGrid = wx.grid.Grid(panel, -1, size=(225, 400), style=mwx.GRID_STYLE)
        self.peaklistGrid.CreateGrid(0, 0)
        self.peaklistGrid.DisableDragColSize()
        self.peaklistGrid.DisableDragRowSize()
        self.peaklistGrid.SetColLabelSize(19)
        self.peaklistGrid.SetRowLabelSize(0)
        self.peaklistGrid.SetDefaultRowSize(19)
        self.peaklistGrid.AutoSizeColumns(True)
        self.peaklistGrid.SetLabelFont(wx.SMALL_FONT)
        self.peaklistGrid.SetDefaultCellFont(wx.SMALL_FONT)
        self.peaklistGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_TOP)
        self.peaklistGrid.SetDefaultCellBackgroundColour(wx.WHITE)
        
        self.peaklistGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onPeaklistCellSelected)
        self.peaklistGrid.Bind(wx.EVT_KEY_DOWN, self.onPeaklistKey)
    # ----
    
    
    def makeMatchesGrid(self, panel):
        """Make matches grid."""
        
        # make table
        self.matchesGrid = wx.grid.Grid(panel, -1, size=(225, 400), style=mwx.GRID_STYLE)
        self.matchesGrid.CreateGrid(0, 0)
        self.matchesGrid.DisableDragColSize()
        self.matchesGrid.DisableDragRowSize()
        self.matchesGrid.SetColLabelSize(19)
        self.matchesGrid.SetRowLabelSize(0)
        self.matchesGrid.SetDefaultRowSize(19)
        self.matchesGrid.AutoSizeColumns(True)
        self.matchesGrid.SetLabelFont(wx.SMALL_FONT)
        self.matchesGrid.SetDefaultCellFont(wx.SMALL_FONT)
        self.matchesGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_TOP)
        self.matchesGrid.SetDefaultCellBackgroundColour(wx.WHITE)
        
        self.matchesGrid.Bind(wx.EVT_KEY_DOWN, self.onMatchesKey)
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
            self.mainSizer.Show(2)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(2)
            self.processing = None
            mspy.start()
        
        # fit layout
        self.documentsGrid.SetMinSize(self.documentsGrid.GetSize())
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
        self.documentsGrid.SetMinSize((-1,-1))
    # ----
    
    
    def onStop(self, evt):
        """Cancel current processing."""
        
        if self.processing and self.processing.isAlive():
            mspy.stop()
        else:
            wx.Bell()
    # ----
    
    
    def onRatioCheckChanged(self, evt=None):
        """Disable ratio chacking options."""
        
        enabled = self.ratioCheck_check.IsChecked()
        self.ratioDirection_choice.Enable(enabled)
        self.ratioThreshold_value.Enable(enabled)
    # ----
    
    
    def onDocumentsCellSelected(self, evt):
        """Show more info for selected cell."""
        
        evt.Skip()
        
        # check documents
        if not self.currentDocuments:
            return
        
        # get slection
        col = evt.GetCol()
        row = evt.GetRow()
        
        # get peak index
        docIndex = int(col) / int((len(self.currentDocuments)+1))
        pkIndex = None
        count = -1
        for i, item in enumerate(self.currentPeaklist):
            if item[1] == docIndex:
                count += 1
            if count == row:
                pkIndex = i
                break
        
        # check peak index
        if pkIndex == None:
            self.currentMatches = []
            self.updateMatchesGrid()
            return
        
        # highlight mass in plot
        self.parent.updateMassPoints([self.currentPeaklist[pkIndex][0]])
        
        # compare selected mass
        self.compareSelected(pkIndex)
        self.updateMatchesGrid()
    # ----
    
    
    def onPeaklistCellSelected(self, evt):
        """Show more info for selected cell."""
        
        evt.Skip()
        
        # check documents
        if not self.currentDocuments:
            return
        
        # get slection
        row = evt.GetRow()
        
        # get peak index
        pkIndex = row
        
        # highlight mass in plot
        self.parent.updateMassPoints([self.currentPeaklist[pkIndex][0]])
        
        # compare selected mass
        self.compareSelected(pkIndex)
        self.updateMatchesGrid()
    # ----
    
    
    def onDocumentsKey(self, evt):
        """Key pressed."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.copyDocuments()
        
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onPeaklistKey(self, evt):
        """Key pressed."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.copyPeaklist()
        
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onMatchesKey(self, evt):
        """Key pressed."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.copyMatches()
        
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onCompare(self, evt):
        """Compare data."""
        
        # check processing
        if self.processing:
            return
        
        # check documents
        if not self.currentDocuments:
            wx.Bell()
            return
        
        # get params
        if not self.getParams():
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.compare_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runCompare)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        self.updateDocumentsGrid(recreate=False)
        self.updatePeaklistGrid(recreate=False)
        self.updateMatchesGrid()
        
        # hide processing gauge
        self.onProcessing(False)
        self.compare_butt.Enable(True)
    # ----
    
    
    def onUpdatePeaklist(self, evt=None):
        """Get relevant peaks lists."""
        
        # check processing
        if self.processing:
            return
        
        # get peak list type
        value = self.compare_choice.GetStringSelection()
        if value == 'Notations (measured)':
            config.comparePeaklists['compare'] = 'measured'
        elif value == 'Notations (theoretical)':
            config.comparePeaklists['compare'] = 'theoretical'
        else:
            config.comparePeaklists['compare'] = 'peaklists'
        
        # check documents
        if not self.currentDocuments:
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.compare_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runGetPeaklists)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        self.updateDocumentsGrid()
        self.updatePeaklistGrid()
        self.updateMatchesGrid()
        
        # hide processing gauge
        self.onProcessing(False)
        self.compare_butt.Enable(True)
    # ----
    
    
    def setData(self, documents):
        """Set data."""
        
        self.currentDocuments = []
        self.currentPeaklist = []
        self.currentMatches = []
        
        # get visible documents only
        for document in documents:
            if document.visible:
                self.currentDocuments.append(document)
        
        # update peak lists
        self.onUpdatePeaklist()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            config.comparePeaklists['tolerance'] = float(self.tolerance_value.GetValue())
            
            config.comparePeaklists['units'] = 'ppm'
            if self.unitsDa_radio.GetValue():
                config.comparePeaklists['units'] = 'Da'
            
            config.comparePeaklists['ignoreCharge'] = 0
            if self.ignoreCharge_check.GetValue():
                config.comparePeaklists['ignoreCharge'] = 1
            
            config.comparePeaklists['ratioCheck'] = 0
            if self.ratioCheck_check.GetValue():
                config.comparePeaklists['ratioCheck'] = 1
                
            config.comparePeaklists['ratioDirection'] = -1
            if self.ratioDirection_choice.GetStringSelection() == 'Above':
                config.comparePeaklists['ratioDirection'] = 1
            
            if self.ratioCheck_check.GetValue():
                config.comparePeaklists['ratioThreshold'] = float(self.ratioThreshold_value.GetValue())
            
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateDocumentsGrid(self, recreate=True):
        """Update current documents grid."""
        
        # make new grid
        if recreate or not self.currentPeaklist:
            
            # erase grid
            if self.documentsGrid.GetNumberCols():
                self.documentsGrid.DeleteCols(0, self.documentsGrid.GetNumberCols())
            if self.documentsGrid.GetNumberRows():
                self.documentsGrid.DeleteRows(0, self.documentsGrid.GetNumberRows())
            
            # check peaklist
            if not self.currentPeaklist:
                return
            
            # make new grid
            count = len(self.currentDocuments)
            self.documentsGrid.AppendCols(count**2+count)
            self.documentsGrid.AppendRows(self._maxSize)
            
            cellAttr = wx.grid.GridCellAttr()
            cellAttr.SetReadOnly(True)
            for x in range(count**2+count):
                self.documentsGrid.SetColAttr(x, cellAttr)
                if x % (count+1):
                    self.documentsGrid.SetColLabelValue(x, '*')
                    self.documentsGrid.SetColSize(x, 20)
                else:
                    self.documentsGrid.SetColLabelValue(x, 'm/z')
        
        # set formats
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        defaultColour = self.documentsGrid.GetDefaultCellBackgroundColour()
        
        # add data
        rows = [0]*len(self.currentDocuments)
        count = len(self.currentDocuments)
        for i, item in enumerate(self.currentPeaklist):
            
            # get item column and row
            col = item[1]*(count+1)
            row = rows[item[1]]
            rows[item[1]] += 1
            
            # add mz
            mz = mzFormat % item[0]
            self.documentsGrid.SetCellValue(row, col, mz)
            
            # add matches
            for x in range(count):
                if item[-1][x]:
                    self.documentsGrid.SetCellBackgroundColour(row, col+x+1, self.currentDocuments[x].colour)
                else:
                    self.documentsGrid.SetCellBackgroundColour(row, col+x+1, defaultColour)
                
                if x == item[1]:
                    self.documentsGrid.SetCellValue(row, col+x+1, '*')
                    self.documentsGrid.SetCellAlignment(row, col+x+1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        
        self.documentsGrid.AutoSizeColumns(True)
    # ----
    
    
    def updatePeaklistGrid(self, recreate=True):
        """Update current total peaklist grid."""
        
        # make new grid
        if recreate or not self.currentPeaklist:
            
            # erase grid
            if self.peaklistGrid.GetNumberCols():
                self.peaklistGrid.DeleteCols(0, self.peaklistGrid.GetNumberCols())
            if self.peaklistGrid.GetNumberRows():
                self.peaklistGrid.DeleteRows(0, self.peaklistGrid.GetNumberRows())
            
            # check peaklist
            if not self.currentPeaklist:
                return
            
            # make new grid
            count = len(self.currentDocuments)
            self.peaklistGrid.AppendCols(count+1)
            self.peaklistGrid.AppendRows(len(self.currentPeaklist))
            self.peaklistGrid.SetColLabelValue(0, 'm/z')
            cellAttr = wx.grid.GridCellAttr()
            cellAttr.SetReadOnly(True)
            for x in range(count+1):
                self.peaklistGrid.SetColAttr(x, cellAttr)
            for x in range(1, count+1):
                self.peaklistGrid.SetColLabelValue(x, '*')
                self.peaklistGrid.SetColSize(x, 20)
        
        # set formats
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        defaultColour = self.peaklistGrid.GetDefaultCellBackgroundColour()
        
        # add data
        count = len(self.currentDocuments)
        for i, item in enumerate(self.currentPeaklist):
            
            # add mz
            mz = mzFormat % item[0]
            self.peaklistGrid.SetCellValue(i, 0, mz)
            
            # add matches
            for x in range(count):
                if item[-1][x]:
                    self.peaklistGrid.SetCellBackgroundColour(i, x+1, self.currentDocuments[x].colour)
                else:
                    self.peaklistGrid.SetCellBackgroundColour(i, x+1, defaultColour)
                
                if x == item[1]:
                    self.peaklistGrid.SetCellValue(i, x+1, '*')
                    self.peaklistGrid.SetCellAlignment(i, x+1, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        
        self.peaklistGrid.AutoSizeColumns(True)
    # ----
    
    
    def updateMatchesGrid(self):
        """Update current matches."""
        
        # erase grid
        if self.matchesGrid.GetNumberCols():
            self.matchesGrid.DeleteCols(0, self.matchesGrid.GetNumberCols())
        if self.matchesGrid.GetNumberRows():
            self.matchesGrid.DeleteRows(0, self.matchesGrid.GetNumberRows())
        
        # check matches
        if not self.currentMatches:
            return
        
        # make grid
        self.matchesGrid.AppendCols(5)
        self.matchesGrid.AppendRows(len(self.currentMatches))
        self.matchesGrid.SetColLabelValue(0, '*')
        self.matchesGrid.SetColLabelValue(1, 'm/z')
        self.matchesGrid.SetColLabelValue(2, 'error')
        self.matchesGrid.SetColLabelValue(3, 'a/b')
        self.matchesGrid.SetColLabelValue(4, 'b/a')
        cellAttr = wx.grid.GridCellAttr()
        cellAttr.SetReadOnly(True)
        for x in range(5):
            self.matchesGrid.SetColAttr(x, cellAttr)
        self.matchesGrid.SetColSize(0, 20)
        
        # set formats
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.comparePeaklists['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        
        # add data
        for i, match in enumerate(self.currentMatches):
            mz = mzFormat % match[1]
            error = errFormat % match[2]
            ratio1 = '%0.2f' % match[3]
            ratio2 = '%0.2f' % match[4]
            
            self.matchesGrid.SetCellValue(i, 1, mz)
            self.matchesGrid.SetCellValue(i, 2, error)
            self.matchesGrid.SetCellValue(i, 3, ratio1)
            self.matchesGrid.SetCellValue(i, 4, ratio2)
            self.matchesGrid.SetCellBackgroundColour(i, 0, self.currentDocuments[match[0]].colour)
            if match[5] == True:
                self.matchesGrid.SetCellAlignment(i, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                self.matchesGrid.SetCellValue(i, 0, '*')
        
        self.matchesGrid.AutoSizeColumns(True)
    # ----
    
    
    def runGetPeaklists(self):
        """Filter peaklists according to specified type."""
        
        # empty current data
        self.currentPeaklist = []
        self.currentMatches = []
        self._maxSize = 0
        
        # run task
        try:
            
            # get peaklist
            count = len(self.currentDocuments)
            for x, document in enumerate(self.currentDocuments):
                size = 0
                
                # use measured notations
                if config.comparePeaklists['compare'] == 'measured':
                    items = []
                    for item in document.annotations:
                        items.append(item)
                    for sequence in document.sequences:
                        for item in sequence.matches:
                            items.append(item)
                    for item in items:
                        # [mz, docIndex, z, intensity, [matches]]
                        self.currentPeaklist.append( [ round(item.mz,6), x, item.charge, item.ai-item.base, count*[False] ] )
                        self.currentPeaklist[-1][-1][x] = True
                        size += 1
                
                # use theoretical notations
                elif config.comparePeaklists['compare'] == 'theoretical':
                    items = []
                    for item in document.annotations:
                        if item.theoretical != None:
                            items.append(item)
                    for sequence in document.sequences:
                        for item in sequence.matches:
                            if item.theoretical != None:
                                items.append(item)
                    for item in items:
                        self.currentPeaklist.append( [ round(item.theoretical,6), x, item.charge, item.ai-item.base, count*[False] ] )
                        self.currentPeaklist[-1][-1][x] = True
                        size += 1
                
                # use peaklists
                else:
                    for item in document.spectrum.peaklist:
                        self.currentPeaklist.append( [ round(item.mz,6), x, item.charge, item.ai-item.base, count*[False] ] )
                        self.currentPeaklist[-1][-1][x] = True
                        size += 1
                
                # remember max peaklist size
                self._maxSize = max(size, self._maxSize)
            
            # sort peaklist by mz
            self.currentPeaklist.sort()
        
        # task canceled
        except mspy.ForceQuit:
            self.currentPeaklist = []
            self._maxSize = 0
            return
    # ----
    
    
    def runCompare(self):
        """Compare all peaklists."""
        
        self.currentMatches = []
        
        # run task
        try:
            
            # erase previous matches
            count = len(self.currentDocuments)
            for i, item in enumerate(self.currentPeaklist):
                item[-1] = count*[False]
                item[-1][item[1]] = True
            
            # compare peaklists
            count = len(self.currentPeaklist)
            for i in range(count):
                for j in range(i, count):
                    p1 = self.currentPeaklist[i]
                    p2 = self.currentPeaklist[j]
                    matched = False
                    
                    # check charge
                    if not config.comparePeaklists['ignoreCharge'] and (p1[2] != p2[2]) and (p1[2] != None and p2[2] != None):
                        continue
                    
                    # check error
                    error = mspy.delta(p1[0], p2[0], config.comparePeaklists['units'])
                    if abs(error) <= config.comparePeaklists['tolerance']:
                        matched = True
                    elif error < 0:
                        break
                    
                    # check ratio
                    if matched and config.comparePeaklists['ratioCheck'] and p1[3] and p2[3]:
                        
                        ratio = p1[3]/p2[3]
                        if config.comparePeaklists['ratioThreshold'] > 1 and ratio < 1 \
                        or config.comparePeaklists['ratioThreshold'] < 1 and ratio > 1:
                            ratio = 1./ratio
                        
                        if (config.comparePeaklists['ratioDirection'] == 1 and ratio < config.comparePeaklists['ratioThreshold']) \
                        or (config.comparePeaklists['ratioDirection'] == -1 and ratio > config.comparePeaklists['ratioThreshold']):
                            matched = False
                    
                    # save matched
                    if matched:
                        p1[-1][p2[1]] = True
                        p2[-1][p1[1]] = True
        
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def compareSelected(self, pkIndex):
        """Compare selected mass only."""
        
        self.currentMatches = []
        
        # get current peak
        p1 = self.currentPeaklist[pkIndex]
        
        # compare mass
        for p2 in self.currentPeaklist:
            
            # check charge
            if not config.comparePeaklists['ignoreCharge'] and (p1[2] != p2[2]) and (p1[2] != None and p2[2] != None):
                continue
            
            # check error
            error = mspy.delta(p1[0], p2[0], config.comparePeaklists['units'])
            if abs(error) <= config.comparePeaklists['tolerance']:
                ratio1 = p1[3]/p2[3]
                ratio2 = 1/ratio1
                self.currentMatches.append([p2[1], p2[0], error, ratio1, ratio2, p1[1]==p2[1]])
            elif error < 0:
                break
        
        # sort matches by document
        self.currentMatches.sort()
    # ----
    
    
    def copyDocuments(self):
        """Copy documents table into clipboard."""
        
        # get default bgr colour
        defaultColour = self.documentsGrid.GetDefaultCellBackgroundColour()
        
        # get data
        buff = ''
        for row in range(self.documentsGrid.GetNumberRows()):
            line = ''
            for col in range(self.documentsGrid.GetNumberCols()):
                value = self.documentsGrid.GetCellValue(row, col)
                if value == '' and defaultColour != self.documentsGrid.GetCellBackgroundColour(row, col):
                    value = "x"
                line += value + '\t'
            buff += '%s\n' % (line.rstrip())
        
        # make text object for data
        obj = wx.TextDataObject()
        obj.SetText(buff.rstrip())
        
        # paste to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
    # ----
    
    
    def copyPeaklist(self):
        """Copy total peaklist table into clipboard."""
        
        # get default bgr colour
        defaultColour = self.peaklistGrid.GetDefaultCellBackgroundColour()
        
        # get data
        buff = ''
        for row in range(self.peaklistGrid.GetNumberRows()):
            line = ''
            for col in range(self.peaklistGrid.GetNumberCols()):
                value = self.peaklistGrid.GetCellValue(row, col)
                if value == '' and defaultColour != self.peaklistGrid.GetCellBackgroundColour(row, col):
                    value = "x"
                line += value + '\t'
            buff += '%s\n' % (line.rstrip())
        
        # make text object for data
        obj = wx.TextDataObject()
        obj.SetText(buff.rstrip())
        
        # paste to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
    # ----
    
    
    def copyMatches(self):
        """Copy matches table into clipboard."""
        
        # get data
        buff = ''
        for row in range(self.matchesGrid.GetNumberRows()):
            line = ''
            for col in range(1, self.matchesGrid.GetNumberCols()):
                line += self.matchesGrid.GetCellValue(row, col) + '\t'
            buff += '%s\n' % (line.rstrip())
        
        # make text object for data
        obj = wx.TextDataObject()
        obj.SetText(buff.rstrip())
        
        # paste to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
    # ----
    
    

