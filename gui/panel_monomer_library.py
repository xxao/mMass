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

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy


# FLOATING PANEL WITH MONOMER LIBRARY
# -----------------------------------

class panelMonomerLibrary(wx.MiniFrame):
    """Monomer library."""
    
    def __init__(self, parent, filterIn=[], filterOut=[], DnD=True):
        wx.MiniFrame.__init__(self, parent, -1, 'Monomer Library', size=(250, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.filterIn = filterIn
        self.filterOut = filterOut
        self.DnD = DnD
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # update list
        self.updateMonomerList()
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make list
        self.makeMonomerList()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.monomerList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
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
        if wx.Platform == '__WXMAC__':
            self.search_value = wx.SearchCtrl(panel, -1, size=(150, mwx.SMALL_SEARCH_HEIGHT), style=wx.TE_PROCESS_ENTER)
            self.search_value.ShowCancelButton(True)
            self.search_value.SetDescriptiveText('Search')
            self.search_value.Bind(wx.EVT_TEXT, self.onSearch)
            self.search_value.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, lambda evt: self.search_value.SetValue(''))
        else:
            self.search_value = wx.TextCtrl(panel, -1, size=(150, mwx.SMALL_SEARCH_HEIGHT), style=wx.TE_PROCESS_ENTER)
            self.search_value.Bind(wx.EVT_TEXT, self.onSearch)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.search_value, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeMonomerList(self):
        """Make references list."""
        
        # init list
        self.monomerList = mwx.sortListCtrl(self, -1, size=(231, 300), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.monomerList.SetFont(wx.SMALL_FONT)
        self.monomerList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.monomerList.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onBeginDrag)
        
        # make columns
        self.monomerList.InsertColumn(0, "abbr", wx.LIST_FORMAT_LEFT)
        self.monomerList.InsertColumn(1, "name", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((100,110)):
            self.monomerList.SetColumnWidth(col, width)
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        self.Destroy()
    # ----
    
    
    def onSearch(self, evt):
        """Search monomer library."""
        self.updateMonomerList()
    # ----
    
    
    def onBeginDrag(self, evt):
        """Start item drag."""
        
        # check if enabled
        if not self.DnD:
            evt.Veto()
            return
        
        # get item
        index = self.monomerList.getSelected()
        if not index:
            return
        
        # get monomer abbr
        abbr = self.monomerMap[index[0]][0]
        
        # create data object with text
        dataObject = wx.PyTextDataObject()
        dataObject.SetText(abbr)
        
        # create drop source
        dropSource = wx.DropSource(self)
        dropSource.SetData(dataObject)
        dropSource.DoDragDrop(flags=wx.Drag_CopyOnly)
    # ----
    
    
    def setFilter(self, filterIn=[], filterOut=[]):
        """Set current group filter."""
        
        # set filters
        self.filterIn = filterIn
        self.filterOut = filterOut
        
        # update list
        self.updateMonomerList()
    # ----
    
    
    def enableDnD(self, enable):
        """Enable / disable drag and drop."""
        self.DnD = enable
    # ----
    
    
    def updateMonomerMap(self):
        """Update items map."""
        
        self.monomerMap = []
        
        # get search
        search = self.search_value.GetValue().lower().split()
        
        # make map
        for abbr, monomer in sorted(mspy.monomers.items()):
            
            # check filters
            if self.filterIn and not monomer.category in self.filterIn:
                continue
            elif self.filterOut and monomer.category in self.filterOut:
                continue
            
            # check search
            if search and not (
                    all(map(lambda x: x in monomer.abbr.lower(), search)) or
                    all(map(lambda x: x in monomer.name.lower(), search))
                ):
                continue
            
            # append item
            self.monomerMap.append((abbr, monomer.name))
    # ----
    
    
    def updateMonomerList(self):
        """Update items list."""
        
        # clear previous data and set new
        self.updateMonomerMap()
        self.monomerList.DeleteAllItems()
        self.monomerList.setDataMap(self.monomerMap)
        
        # check data
        if not self.monomerMap:
            return
        
        # add new data
        for row, item in enumerate(self.monomerMap):
            self.monomerList.InsertStringItem(row, item[0])
            self.monomerList.SetStringItem(row, 1, item[1])
            self.monomerList.SetItemData(row, row)
        
        # sort
        self.monomerList.sort()
    # ----
    
