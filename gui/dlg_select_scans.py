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
import datetime
import wx

# load modules
from . import mwx
from . import config
import mspy


# SCAN SELECTION DIALOG
# ---------------------

class dlgSelectScans(wx.Dialog):
    """Select scans from multiscan files."""
    
    def __init__(self, parent, scans):
        wx.Dialog.__init__(self, parent, -1, "Select Scan", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.RESIZE_BORDER)
        
        self.scans = scans
        self.selected = None
        self.showChromCanvas = False
        
        self.usedColours = []
        
        # make GUI
        sizer = self.makeGUI()
        
        # show data
        self.updateScanList()
        self.updateChromPlot()
        
        # show / hide chromatograms
        if not self.showChromCanvas:
            sizer.Hide(1)
            sizer.Hide(2)
            self.scanList.SetInitialSize((656, 250))
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make GUI elements
        self.makeScanList()
        self.makeChromPlot()
        buttons = self.makeButtons()
        
        # pack element
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.scanList, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
        sizer.AddSpacer(3)
        sizer.Add(self.chromCanvas, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
        sizer.Add(buttons, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return sizer
    # ----
    
    
    def makeButtons(self):
        """Make buttons."""
        
        # make items
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        open_butt = wx.Button(self, wx.ID_OK, "Open Selected")
        open_butt.Bind(wx.EVT_BUTTON, self.onOpen)
        
        # pack items
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        sizer.Add(open_butt, 0)
        
        return sizer
    # ----
    
    
    def makeScanList(self):
        """Make list for scans."""
        
        # init list
        self.scanList = mwx.sortListCtrl(self, -1, size=(656, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.scanList.SetFont(wx.SMALL_FONT)
        self.scanList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.scanList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.scanList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        
        # make columns
        self.scanList.InsertColumn(0, "id", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(1, "retention", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(2, "ms", wx.LIST_FORMAT_CENTER)
        self.scanList.InsertColumn(3, "precursor", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(4, "z", wx.LIST_FORMAT_CENTER)
        self.scanList.InsertColumn(5, "mz range", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(6, "ion current", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(7, "points", wx.LIST_FORMAT_RIGHT)
        self.scanList.InsertColumn(8, "data type", wx.LIST_FORMAT_CENTER)
        
        # set column widths
        for col, width in enumerate((45,110,40,85,40,85,90,60,80)):
            self.scanList.SetColumnWidth(col, width)
    # ----
    
    
    def makeChromPlot(self):
        """Make plot canvas and set defalt parameters."""
        
        # init canvas
        self.chromCanvas = mspy.plot.canvas(self, size=(-1, 200), style=mwx.PLOTCANVAS_STYLE_DIALOG)
        
        # set default params
        self.chromCanvas.setProperties(xLabel='retention time in min.')
        self.chromCanvas.setProperties(yLabel='normalized ion current')
        self.chromCanvas.setProperties(showGrid=True)
        self.chromCanvas.setProperties(showMinorTicks=config.spectrum['showMinorTicks'])
        self.chromCanvas.setProperties(showLegend=True)
        self.chromCanvas.setProperties(showXPosBar=True)
        self.chromCanvas.setProperties(showYPosBar=True)
        self.chromCanvas.setProperties(posBarSize=6)
        self.chromCanvas.setProperties(showGel=False)
        self.chromCanvas.setProperties(checkLimits=True)
        self.chromCanvas.setProperties(autoScaleY=True)
        self.chromCanvas.setProperties(zoomAxis='x')
        self.chromCanvas.setProperties(xPosDigits=2)
        self.chromCanvas.setProperties(yPosDigits=2)
        self.chromCanvas.setProperties(reverseScrolling=config.main['reverseScrolling'])
        self.chromCanvas.setProperties(reverseDrawing=True)
        self.chromCanvas.setLMBFunction('xDistance')
        self.chromCanvas.setMFunction('cross')
        
        axisFont = wx.Font(config.spectrum['axisFontSize'], wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0)
        self.chromCanvas.setProperties(axisFont=axisFont)
        
        self.chromCanvas.Bind(wx.EVT_LEFT_UP, self.onCanvasLMU)
        
        self.chromCanvas.draw(mspy.plot.container([]))
    # ----
    
    
    def updateScanList(self):
        """Set data to scan list."""
        
        # set data map
        self.scanMap = []
        for scanID, scan in sorted(self.scans.items()):
            self.scanMap.append((
                scan['scanNumber'],
                scan['retentionTime'],
                scan['msLevel'],
                scan['precursorMZ'],
                scan['precursorCharge'],
                (scan['lowMZ'], scan['highMZ']),
                scan['totIonCurrent'],
                scan['pointsCount'],
                scan['spectrumType'],
            ))
        self.scanList.setDataMap(self.scanMap)
        
        # add data
        row = 0
        for scanID, scan in sorted(self.scans.items()):
            
            retentionTime = ''
            if scan['retentionTime'] != None:
                try: retentionTime = '%.2f (%s)' % (scan['retentionTime']/60, str(datetime.timedelta(seconds=round(scan['retentionTime']))))
                except: pass
            
            msLevel = ''
            if scan['msLevel'] != None:
                msLevel = str(scan['msLevel'])
            
            precursorMZ = ''
            if scan['precursorMZ'] != None:
                try: precursorMZ = '%.4f' % (scan['precursorMZ'])
                except: pass
            
            precursorCharge = ''
            if scan['precursorCharge'] != None:
                if scan['polarity']:
                    precursorCharge = str(scan['precursorCharge'] * scan['polarity'])
                else:
                    precursorCharge = str(scan['precursorCharge'])
            
            mzRange = ''
            if scan['lowMZ'] != None and scan['highMZ'] != None:
                try: mzRange = '%d-%d' % (scan['lowMZ'], scan['highMZ'])
                except: pass
            
            totIonCurrent = ''
            if scan['totIonCurrent'] != None:
                try: totIonCurrent = '%.0f' % (scan['totIonCurrent'])
                except: pass
            
            pointsCount = ''
            if scan['pointsCount'] != None:
                try: pointsCount = str(scan['pointsCount'])
                except: pass
            
            self.scanList.InsertItem(row, str(scan['scanNumber']))
            self.scanList.SetItem(row, 1, retentionTime)
            self.scanList.SetItem(row, 2, msLevel)
            self.scanList.SetItem(row, 3, precursorMZ)
            self.scanList.SetItem(row, 4, precursorCharge)
            self.scanList.SetItem(row, 5, mzRange)
            self.scanList.SetItem(row, 6, totIonCurrent)
            self.scanList.SetItem(row, 7, pointsCount)
            self.scanList.SetItem(row, 8, scan['spectrumType'])
            self.scanList.SetItemData(row, row)
            row += 1
        
        # sort data
        self.scanList.sort()
    # ----
    
    
    def updateChromPlot(self):
        """Update chromatograms."""
        
        container = mspy.plot.container([])
        
        # get data
        ticData = []
        bpcData = []
        for scanID, scan in sorted(self.scans.items()):
            if scan['msLevel'] != 1 or scan['retentionTime'] is None:
                continue
            if scan['totIonCurrent'] != None:
                ticData.append((scan['retentionTime']/60, scan['totIonCurrent']))
            if scan['basePeakIntensity'] != None:
                bpcData.append((scan['retentionTime']/60, scan['basePeakIntensity']))
        
        # make objects
        if len(ticData) > 10:
            ticData.sort()
            obj = mspy.plot.points(ticData, lineColour=(16,71,185), legend="TIC (MS)", showLines=True, showPoints=False, exactFit=True, normalized=True)
            container.append(obj)
            self.showChromCanvas = True
        
        if len(bpcData) > 10:
            ticData.sort()
            obj = mspy.plot.points(bpcData, lineColour=(50,140,0), legend="BPC (MS)", showLines=True, showPoints=False, exactFit=True, normalized=True)
            container.append(obj)
            self.showChromCanvas = True
        
        # draw container
        self.chromCanvas.draw(container)
    # ----
    
    
    def onItemSelected(self, evt):
        """Show selected scans in chromatogram."""
        
        # check chromatogram
        if not self.showChromCanvas:
            return
        
        # get selected retentions
        points = []
        for scanID in self.getSelecedScans():
            retention = self.scans[scanID]['retentionTime']
            if retention != None:
                points.append(retention/60)
        
        # highlight retentions
        if points:
            self.chromCanvas.highlightXPoints(points)
    # ----
    
    
    def onItemActivated(self, evt):
        """Open selected scans."""
        
        self.selected = self.getSelecedScans()
        self.EndModal(wx.ID_OK)
    # ----
    
    
    def onCanvasLMU(self, evt):
        """Show nearest scan."""
        
        # check chromatogram
        if not self.showChromCanvas:
            return
        
        # get cursor positions
        position = self.chromCanvas.getCursorPosition()
        self.chromCanvas.onLMU(evt)
        if not position:
            return
        
        # show nearest scan
        diff = None
        nearest = None
        retention = position[0]*60
        for scanID, scan in sorted(self.scans.items()):
            if scan['retentionTime'] != None and diff is None:
                diff = abs(scan['retentionTime'] - retention)
                nearest = scanID
            elif scan['retentionTime'] != None:
                current = abs(scan['retentionTime'] - retention)
                if current < diff:
                    diff = current
                    nearest = scanID
        
        # show scan in the list
        if nearest != None:
            i = -1
            while True:
                i = self.scanList.GetNextItem(i, wx.LIST_NEXT_ALL)
                if i == -1:
                    break
                else:
                    item = self.scanList.GetItem(i,0)
                    if int(item.GetText()) == nearest:
                        self.scanList.EnsureVisible(i)
                        break
    # ----
    
    
    def onOpen(self, evt):
        """Check selected scan."""
        
        # get selection
        self.selected = self.getSelecedScans()
        if self.selected:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
    
    def getSelecedScans(self):
        """Get scan numbers for selected scans."""
        
        # get selected items
        selected = []
        i = -1
        while True:
            i = self.scanList.GetNextItem(i, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if i == -1:
                break
            else:
                selected.append(i)
        selected.sort()
        
        # get scans
        scans = []
        for x in selected:
            item = self.scanList.GetItem(x,0)
            scans.append(int(item.GetText()))
        
        return scans
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
    
    
