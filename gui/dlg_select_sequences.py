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
import mwx
import config


# SEQUENCE SELECTION DIALOG
# -------------------------

class dlgSelectSequences(wx.Dialog):
    """Select sequences from multisequence files"""
    
    def __init__(self, parent, sequences):
        wx.Dialog.__init__(self, parent, -1, "Select Sequence", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.RESIZE_BORDER)
        
        self.sequences = sequences
        self.sequencesMap = []
        self.selected = None
        
        # make GUI
        sizer = self.makeGUI()
        
        # show data
        self.updateSequenceList()
        
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
        self.makeSequenceList()
        buttons = self.makeButtons()
        
        # pack element
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sequenceList, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
        sizer.Add(buttons, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return sizer
    # ----
    
    
    def makeButtons(self):
        """Make buttons."""
        
        # make items
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        import_butt = wx.Button(self, wx.ID_OK, "Import")
        import_butt.Bind(wx.EVT_BUTTON, self.onImport)
        
        # pack items
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        sizer.Add(import_butt, 0)
        
        return sizer
    # ----
    
    
    def makeSequenceList(self):
        """Make list for sequences."""
        
        # init list
        self.sequenceList = mwx.sortListCtrl(self, -1, size=(626, 250), style=mwx.LISTCTRL_STYLE_MULTI)
        self.sequenceList.SetFont(wx.SMALL_FONT)
        self.sequenceList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.sequenceList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        
        # make columns
        self.sequenceList.InsertColumn(0, "#", wx.LIST_FORMAT_RIGHT)
        self.sequenceList.InsertColumn(1, "accession", wx.LIST_FORMAT_LEFT)
        self.sequenceList.InsertColumn(2, "title", wx.LIST_FORMAT_LEFT)
        self.sequenceList.InsertColumn(3, "length", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((30,120,385,70)):
            self.sequenceList.SetColumnWidth(col, width)
    # ----
    
    
    def updateSequenceList(self):
        """Set data to sequence list."""
        
        # set data map
        self.sequencesMap = []
        for x, sequence in enumerate(self.sequences):
            self.sequencesMap.append((x, sequence.accession, sequence.title, len(sequence)))
        self.sequenceList.setDataMap(self.sequencesMap)
        
        # add data
        for row, item in enumerate(self.sequencesMap):
            
            accession = ''
            if item[1]:
                accession = str(item[1])
            
            self.sequenceList.InsertStringItem(row, str(item[0]+1))
            self.sequenceList.SetStringItem(row, 1, accession)
            self.sequenceList.SetStringItem(row, 2, item[2])
            self.sequenceList.SetStringItem(row, 3, str(item[3]))
            self.sequenceList.SetItemData(row, row)
        
        # sort data
        self.sequenceList.sort()
    # ----
    
    
    def onItemActivated(self, evt):
        """Import selected sequence."""
        
        self.selected = self.getSelecedSequences()
        self.EndModal(wx.ID_OK)
    # ----
    
    
    def onImport(self, evt):
        """Check selected sequences."""
        
        # get selection
        self.selected = self.getSelecedSequences()
        if self.selected:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
    
    def getSelecedSequences(self):
        """Get selected sequences."""
        
        # get selected sequences
        sequences = []
        for item in self.sequenceList.getSelected():
            sequence = self.sequences[self.sequenceList.GetItemData(item)]
            sequences.append(sequence)
        
        return sequences
    # ----
    
    
