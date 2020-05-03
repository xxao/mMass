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


# FLOATING PANEL WITH PEAK DIFFERENCES TOOL
# -----------------------------------------

class panelPeakDifferences(wx.MiniFrame):
    """Peak differences tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Peak Differences', size=(500, 400), style=wx.DEFAULT_FRAME_STYLE)
        
        self.parent = parent
        
        self.processing = None
        
        self.currentDocument = None
        self.currentDifference = None
        self.currentDifferences = None
        self.currentMatches = None
        
        # init amino acids and dipeptides
        self.initAminoacids()
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
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
        
        # make match fields
        difference_label = wx.StaticText(panel, -1, "Difference:")
        difference_label.SetFont(wx.SMALL_FONT)
        
        self.difference_value = wx.TextCtrl(panel, -1, '', size=(100, -1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        self.difference_value.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        
        self.aminoacids_check = wx.CheckBox(panel, -1, "Amino acids")
        self.aminoacids_check.SetFont(wx.SMALL_FONT)
        self.aminoacids_check.SetValue(config.peakDifferences['aminoacids'])
        
        self.dipeptides_check = wx.CheckBox(panel, -1, "Dipeptides")
        self.dipeptides_check.SetFont(wx.SMALL_FONT)
        self.dipeptides_check.SetValue(config.peakDifferences['dipeptides'])
        
        massType_label = wx.StaticText(panel, -1, "Mass:")
        massType_label.SetFont(wx.SMALL_FONT)
        
        self.massTypeMo_radio = wx.RadioButton(panel, -1, "Mo", style=wx.RB_GROUP)
        self.massTypeMo_radio.SetFont(wx.SMALL_FONT)
        self.massTypeMo_radio.SetValue(True)
        
        self.massTypeAv_radio = wx.RadioButton(panel, -1, "Av")
        self.massTypeAv_radio.SetFont(wx.SMALL_FONT)
        self.massTypeAv_radio.SetValue(config.peakDifferences['massType'])
        
        tolerance_label = wx.StaticText(panel, -1, "Tolerance:")
        tolerance_label.SetFont(wx.SMALL_FONT)
        
        self.tolerance_value = wx.TextCtrl(panel, -1, str(config.peakDifferences['tolerance']), size=(50, -1), validator=mwx.validator('floatPos'))
        
        toleranceUnits_label = wx.StaticText(panel, -1, "m/z")
        toleranceUnits_label.SetFont(wx.SMALL_FONT)
        
        self.consolidate_check = wx.CheckBox(panel, -1, "Hide umatched")
        self.consolidate_check.SetFont(wx.SMALL_FONT)
        self.consolidate_check.SetValue(config.peakDifferences['consolidate'])
        
        self.search_butt = wx.Button(panel, -1, "Search", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.search_butt.Bind(wx.EVT_BUTTON, self.onSearch)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(difference_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.difference_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.aminoacids_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.dipeptides_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(massType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.massTypeMo_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.massTypeAv_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(tolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.tolerance_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(toleranceUnits_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.consolidate_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.search_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeMainPanel(self):
        """Make differences panel."""
        
        panel = wx.Panel(self, -1)
        
        # make table
        self.makeDifferencesGrid(panel)
        self.makeMatchesGrid(panel)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.differencesGrid, 1, wx.EXPAND)
        mainSizer.AddSpacer(mwx.SASH_SIZE)
        mainSizer.Add(self.matchesGrid, 0, wx.EXPAND)
        
        # fit layout
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeDifferencesGrid(self, panel):
        """Make differences grid."""
        
        # make table
        self.differencesGrid = wx.grid.Grid(panel, -1, size=(700, 500), style=mwx.GRID_STYLE)
        self.differencesGrid.CreateGrid(0, 0)
        self.differencesGrid.DisableDragColSize()
        self.differencesGrid.DisableDragRowSize()
        self.differencesGrid.SetColLabelSize(19)
        self.differencesGrid.SetDefaultRowSize(19)
        self.differencesGrid.SetLabelFont(wx.SMALL_FONT)
        self.differencesGrid.SetDefaultCellFont(wx.SMALL_FONT)
        self.differencesGrid.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_TOP)
        self.differencesGrid.SetDefaultCellBackgroundColour(wx.WHITE)
        
        self.differencesGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onCellSelected)
        self.differencesGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.onCellActivated)
    # ----
    
    
    def makeMatchesGrid(self, panel):
        """Make matches grid."""
        
        # make table
        self.matchesGrid = wx.grid.Grid(panel, -1, size=(200, 400), style=mwx.GRID_STYLE)
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
        self.differencesGrid.SetMinSize(self.differencesGrid.GetSize())
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
        self.differencesGrid.SetMinSize((-1,-1))
    # ----
    
    
    def onStop(self, evt):
        """Cancel current processing."""
        
        if self.processing and self.processing.isAlive():
            mspy.stop()
        else:
            wx.Bell()
    # ----
    
    
    def onCellSelected(self, evt):
        """Grid cell selected."""
        
        evt.Skip()
        
        # get cell
        col = evt.GetCol()
        row = evt.GetRow()
        
        # highlight selected cell
        self.differencesGrid.SelectBlock(row, col, row, col)
        
        # get peaks and diff
        mz1 = self.currentDifferences[col][0][0]
        mz2 = self.currentDifferences[row][0][0]
        diff = abs(mz1 - mz2)
        
        # highlight masses in plot
        self.parent.updateMassPoints([mz1,mz2])
        
        # search diff
        self.searchSelected(diff)
        self.updateMatchesGrid()
    # ----
    
    
    def onCellActivated(self, evt):
        """Grid cell activated."""
        
        evt.Skip()
        
        # get cell
        col = evt.GetCol()
        row = evt.GetRow()
        
        # highlight selected cell
        self.differencesGrid.SelectBlock(row, col, row, col)
        
        # get peaks and diff
        mz1 = self.currentDifferences[col][0][0]
        mz2 = self.currentDifferences[row][0][0]
        diff = abs(mz1 - mz2)
        
        # highlight masses in plot
        self.parent.updateMassPoints([mz1,mz2])
        
        # send difference into mass to formula tool
        self.parent.onToolsMassToFormula(
            mass = diff,
            charge = 0,
            tolerance = config.peakDifferences['tolerance'],
            units = 'Da',
            agentFormula = ''
        )
    # ----
    
    
    def onSearch(self, evt):
        """Generate differences and search for specified mass(es)."""
        
        # check processing
        if self.processing:
            return
        
        # clear previous
        self.currentDifferences = None
        self.currentMatches = None
        
        # check document
        if not self.currentDocument:
            wx.Bell()
            return
        
        # get params
        if not self.getParams():
            wx.Bell()
            self.updateDifferencesGrid()
            self.updateMatchesGrid()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.search_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runSearch)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        self.updateDifferencesGrid()
        self.updateMatchesGrid()
        
        # hide processing gauge
        self.onProcessing(False)
        self.search_butt.Enable(True)
    # ----
    
    
    def setData(self, document):
        """Set data."""
        
        # set new document
        self.currentDocument = document
        self.currentDifferences = None
        self.currentMatches = None
        
        # update gui
        self.updateDifferencesGrid()
        self.updateMatchesGrid()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            if self.difference_value.GetValue():
                self.currentDifference = float(self.difference_value.GetValue())
            else:
                self.currentDifference = None
            
            config.peakDifferences['aminoacids'] = int(self.aminoacids_check.GetValue())
            config.peakDifferences['dipeptides'] = int(self.dipeptides_check.GetValue())
            config.peakDifferences['tolerance'] = float(self.tolerance_value.GetValue())
            config.peakDifferences['massType'] = int(self.massTypeAv_radio.GetValue())
            config.peakDifferences['consolidate'] = int(self.consolidate_check.GetValue())
            
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateDifferencesGrid(self):
        """Update grid values."""
        
        # erase grid
        if self.differencesGrid.GetNumberRows():
            self.differencesGrid.DeleteCols(0, self.differencesGrid.GetNumberCols())
            self.differencesGrid.DeleteRows(0, self.differencesGrid.GetNumberRows())
        
        # check differences
        if not self.currentDifferences:
            return
        
        # get grid size
        size = len(self.currentDifferences)
        
        # create new cells
        self.differencesGrid.AppendCols(size)
        self.differencesGrid.AppendRows(size)
        
        # create labels
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        cellAttr = wx.grid.GridCellAttr()
        cellAttr.SetReadOnly(True)
        for x in range(size):
            label = mzFormat % self.currentDifferences[x][0][0]
            self.differencesGrid.SetColLabelValue(x, label)
            self.differencesGrid.SetRowLabelValue(x, label)
            self.differencesGrid.SetColAttr(x, cellAttr)
        
        # paste data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        for x in range(size):
            for y in range(size):
                
                # get difference indexes
                if y == x:
                    self.differencesGrid.SetCellValue(x, y, '---')
                    continue
                elif y < x:
                    i = x
                    j = (y + 1)
                elif y > x:
                    i = y
                    j = (x + 1)
                
                # set value
                diff = mzFormat % self.currentDifferences[i][j][0]
                self.differencesGrid.SetCellValue(x, y, diff)
                
                # highlight matches
                if self.currentDifferences[i][j][1] == False:
                    continue
                elif self.currentDifferences[i][j][1] == 'value':
                    self.differencesGrid.SetCellBackgroundColour(x, y, (100,255,100))
                elif self.currentDifferences[i][j][1] == 'amino':
                    self.differencesGrid.SetCellBackgroundColour(x, y, (0,200,255))
                elif self.currentDifferences[i][j][1] == 'dipep':
                    self.differencesGrid.SetCellBackgroundColour(x, y, (100,255,255))
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
        self.matchesGrid.AppendCols(2)
        self.matchesGrid.AppendRows(len(self.currentMatches))
        self.matchesGrid.SetColLabelValue(0, 'match')
        self.matchesGrid.SetColLabelValue(1, 'error')
        
        cellAttr = wx.grid.GridCellAttr()
        cellAttr.SetAlignment(wx.ALIGN_TOP, wx.ALIGN_LEFT)
        cellAttr.SetReadOnly(True)
        self.matchesGrid.SetColAttr(0, cellAttr)
        
        cellAttr = wx.grid.GridCellAttr()
        cellAttr.SetAlignment(wx.ALIGN_TOP, wx.ALIGN_RIGHT)
        cellAttr.SetReadOnly(True)
        self.matchesGrid.SetColAttr(1, cellAttr)
        
        # set format
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        
        # add data
        for i, match in enumerate(self.currentMatches):
            error = errFormat % match[1]
            self.matchesGrid.SetCellValue(i, 0, match[0])
            self.matchesGrid.SetCellValue(i, 1, error)
        
        self.matchesGrid.AutoSizeColumns(True)
    # ----
    
    
    def searchSelected(self, diff):
        """Search difference for specified value, aminoacids or dipeptides."""
        
        self.currentMatches = []
        
        # search for value
        if self.currentDifference:
            error = diff - self.currentDifference
            if abs(error) <= config.peakDifferences['tolerance']:
                self.currentMatches.append([str(self.currentDifference), error])
        
        # search for aminoacids
        if config.peakDifferences['aminoacids']:
            for aa in self._aaMasses:
                error = diff - self._aaMasses[aa][config.peakDifferences['massType']]
                if abs(error) <= config.peakDifferences['tolerance']:
                    self.currentMatches.append([aa, error])
        
        # search for dipeptides
        if config.peakDifferences['dipeptides']:
            for dip in self._dipMasses:
                error = diff - self._dipMasses[dip][config.peakDifferences['massType']]
                if abs(error) <= config.peakDifferences['tolerance']:
                    self.currentMatches.append([dip, error])
    # ----
    
    
    def runSearch(self):
        """Calculate differences for current peaklist and search for matches."""
        
        # run task
        try:
            
            # get peaklist
            peaklist = self.currentDocument.spectrum.peaklist
            if not peaklist:
                return False
            
            # init limits
            diffMin = 0.0
            diffMax = 0.0
            if self.currentDifference:
                diffMin = self.currentDifference - config.peakDifferences['tolerance']
                diffMax = self.currentDifference + config.peakDifferences['tolerance']
            aaMin = self._aaLimits[0] - config.peakDifferences['tolerance']
            aaMax = self._aaLimits[1] + config.peakDifferences['tolerance']
            dipMin = self._dipLimits[0] - config.peakDifferences['tolerance']
            dipMax = self._dipLimits[1] + config.peakDifferences['tolerance']
            
            # calc differences
            self.currentDifferences = []
            for x in range(len(peaklist)):
                rowBuff = [(peaklist[x].mz, x)]
                for y in range(x+1):
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    diff = peaklist[x].mz - peaklist[y].mz
                    match = False
                    
                    # match specified value
                    if self.currentDifference != None and (diffMin <= diff <= diffMax):
                        match = 'value'
                    
                    # match amino acids
                    if not match and config.peakDifferences['aminoacids'] and (aaMin <= diff <= aaMax):
                        for aa in self._aaMasses:
                            error = diff - self._aaMasses[aa][config.peakDifferences['massType']]
                            if abs(error) <= config.peakDifferences['tolerance']:
                                match = 'amino'
                                break
                    
                    # match dipeptides
                    if not match and config.peakDifferences['dipeptides'] and (dipMin <= diff <= dipMax):
                        for dip in self._dipMasses:
                            error = diff - self._dipMasses[dip][config.peakDifferences['massType']]
                            if abs(error) <= config.peakDifferences['tolerance']:
                                match = 'dipep'
                                break
                    
                    # append difference
                    rowBuff.append((diff, match))
                
                # append row
                self.currentDifferences.append(rowBuff)
            
            # consolidate table - remove unmatched peaks
            if config.peakDifferences['consolidate']:
                self.consolidateTable()
        
        # task canceled
        except mspy.ForceQuit:
            self.currentDifferences = []
            return
    # ----
    
    
    def initAminoacids(self):
        """Calculate amino acids / dipeptides masses and ranges."""
        
        self._aaLimits = [0.0, 1000.0]
        self._dipLimits = [0.0, 1000.0]
        self._aaMasses = {}
        self._dipMasses = {}
        
        # get amino acids
        aminoacids = []
        for abbr in mspy.monomers:
            if mspy.monomers[abbr].category == '_InternalAA':
                aminoacids.append(abbr)
                self._aaMasses[abbr] = mspy.monomers[abbr].mass
        
        # approximate mass limits
        masses = []
        for aa in aminoacids:
            masses.append(mspy.monomers[aa].mass[1])
        self._aaLimits = [min(masses)-1, max(masses)+1]
        self._dipLimits = [2*self._aaLimits[0]-1, 2*self._aaLimits[1]+1]
        
        # generate dipeptides
        for x in range(len(aminoacids)):
            for y in range(x, len(aminoacids)):
                
                aX = aminoacids[x]
                aY = aminoacids[y]
                
                massX = mspy.monomers[aX].mass
                massY = mspy.monomers[aY].mass
                mass = (massX[0] + massY[0], massX[1] + massY[1])
                
                if aX != aY:
                    label = '%s%s/%s%s' % (aX,aY,aY,aX)
                else:
                    label = aX+aY
                
                self._dipMasses[label] = mass
    # ----
    
    
    def consolidateTable(self):
        """Remove unmatched peaks."""
        
        # find matches
        indexes = []
        for i, row in enumerate(self.currentDifferences):
            for j, item in enumerate(row[1:]):
                if item[1] != False: 
                    if not i in indexes:
                        indexes.append(i)
                    if not j in indexes:
                        indexes.append(j)
        
        # sort indexes
        indexes.sort()
        
        # consolidate table
        buff = []
        for i in indexes[:]:
            row = self.currentDifferences[i]
            rowBuff = [row[0]]
            for j, item in enumerate(row[1:]):
                if j in indexes:
                    rowBuff.append(item)
            buff.append(rowBuff)
            
        self.currentDifferences = buff
    # ----
    

