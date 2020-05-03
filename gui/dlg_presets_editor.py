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
import copy

# load modules
import mwx
import config
import libs
import mspy


# PRESETS EDITOR
# --------------

class dlgPresetsEditor(wx.Dialog):
    """Edit presets library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Presets Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.itemsMap = []
        self.selectedItem = None
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
        
        # show data
        self.updateItemsList()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make GUI elements
        self.makeItemsList()
        editor = self.makeItemEditor()
        
        # pack elements
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.itemsList, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
        sizer.Add(editor, 0, wx.EXPAND|wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return sizer
    # ----
    
    
    def makeItemsList(self):
        """Make list for items."""
        
        # init list
        self.itemsList = mwx.sortListCtrl(self, -1, size=(501, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "name", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "category", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((330,150)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeItemEditor(self):
        """Make items editor."""
        
        mainSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        itemName_label = wx.StaticText(self, -1, "Name:")
        self.itemName_value = wx.TextCtrl(self, -1, "", size=(250, -1))
        
        itemCategory_label = wx.StaticText(self, -1, "Category:")
        self.itemCategory_value = wx.TextCtrl(self, -1, "", size=(250, -1))
        self.itemCategory_value.Enable(False)
        
        # buttons
        rename_butt = wx.Button(self, -1, "Rename", size=(80,-1))
        rename_butt.Bind(wx.EVT_BUTTON, self.onRenameItem)
        
        delete_butt = wx.Button(self, -1, "Delete", size=(80,-1))
        delete_butt.Bind(wx.EVT_BUTTON, self.onDeleteItem)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        grid.Add(itemName_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemName_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemCategory_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemCategory_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(rename_butt, (0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        index = evt.GetData()
        name = self.itemsMap[index][0]
        category = self.itemsMap[index][1]
        self.selectedItem = index
        
        # update item editor
        self.itemName_value.SetValue(name)
        self.itemCategory_value.SetValue(category)
    # ----
    
    
    def onRenameItem(self, evt):
        """Rename item."""
        
        # check selection
        if self.selectedItem == None:
            wx.Bell()
            return
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check name
        if itemData[0] in libs.presets[itemData[1]]:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Presets with the same name already exists.', message='Type a different name.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # rename item
        oldName = self.itemsMap[self.selectedItem][0]
        data = copy.deepcopy(libs.presets[itemData[1]][oldName])
        libs.presets[itemData[1]][itemData[0]] = data
        del libs.presets[itemData[1]][oldName]
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # delete?
        title = 'Do you really want to delete selected presets?'
        message = 'Presets definitions will be lost.'
        buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Delete", 80, True, 0)]
        dlg = mwx.dlgMessage(self, title, message, buttons)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        
        # delete items
        for i in self.itemsList.getSelected():
            index = self.itemsList.GetItemData(i)
            name = self.itemsMap[index][0]
            category = self.itemsMap[index][1]
            del libs.presets[category][name]
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # make map
        for category in libs.presets.keys():
            for name, presets in sorted(libs.presets[category].items()):
                self.itemsMap.append((name, category))
    # ----
    
    
    def updateItemsList(self):
        """Update items list."""
        
        # clear previous data and set new
        self.updateItemsMap()
        self.itemsList.DeleteAllItems()
        self.itemsList.setDataMap(self.itemsMap)
        self.selectedItem = None
        
        # check data
        if not self.itemsMap:
            return
        
        # add new data
        for row, item in enumerate(self.itemsMap):
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetItemData(row, row)
        
        # sort
        self.itemsList.sort()
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemName_value.SetValue('')
        self.itemCategory_value.SetValue('')
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        name = self.itemName_value.GetValue()
        category = self.itemCategory_value.GetValue()
        
        # check values
        if not name or not category:
            wx.Bell()
            return False
        
        return (name, category)
    # ----
    
    

