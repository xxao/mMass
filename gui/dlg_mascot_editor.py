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
import libs
import mspy


# MASCOT SERVERS EDITOR
# ---------------------

class dlgMascotEditor(wx.Dialog):
    """Edit mascot servers library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Mascot Servers Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.itemsMap = []
        
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
        self.itemsList = mwx.sortListCtrl(self, -1, size=(711, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "title", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "host", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(2, "path", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((220,250,220)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeItemEditor(self):
        """Make items editor."""
        
        mainSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        itemName_label = wx.StaticText(self, -1, "Title:")
        self.itemName_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemHost_label = wx.StaticText(self, -1, "Host name:")
        self.itemHost_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemPath_label = wx.StaticText(self, -1, "Mascot path:")
        self.itemPath_value = wx.TextCtrl(self, -1, "/", size=(200, -1))
        
        itemSearch_label = wx.StaticText(self, -1, "Search:")
        self.itemSearch_value = wx.TextCtrl(self, -1, "cgi/nph-mascot.exe", size=(170, -1))
        
        itemResults_label = wx.StaticText(self, -1, "Results:")
        self.itemResults_value = wx.TextCtrl(self, -1, "cgi/master_results.pl", size=(170, -1))
        
        itemExport_label = wx.StaticText(self, -1, "Export:")
        self.itemExport_value = wx.TextCtrl(self, -1, "cgi/export_dat_2.pl", size=(170, -1))
        
        itemParams_label = wx.StaticText(self, -1, "Params:")
        self.itemParams_value = wx.TextCtrl(self, -1, "cgi/get_params.pl", size=(170, -1))
        
        # buttons
        add_butt = wx.Button(self, -1, "Add", size=(80,-1))
        add_butt.Bind(wx.EVT_BUTTON, self.onAddItem)
        
        delete_butt = wx.Button(self, -1, "Delete", size=(80,-1))
        delete_butt.Bind(wx.EVT_BUTTON, self.onDeleteItem)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        grid.Add(itemName_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemName_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemHost_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemHost_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemPath_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemPath_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemSearch_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemSearch_value, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemResults_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemResults_value, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemExport_label, (2,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemExport_value, (2,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemParams_label, (3,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemParams_value, (3,4), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(add_butt, (0,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        name = evt.GetText()
        server = libs.mascot[name]
        
        # update item editor
        self.itemName_value.SetValue(name)
        self.itemHost_value.SetValue(server['host'])
        self.itemPath_value.SetValue(server['path'])
        self.itemSearch_value.SetValue(server['search'])
        self.itemResults_value.SetValue(server['results'])
        self.itemExport_value.SetValue(server['export'])
        self.itemParams_value.SetValue(server['params'])
    # ----
    
    
    def onAddItem(self, evt):
        """Add/replace item."""
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check name
        name = self.itemName_value.GetValue()
        if name in libs.mascot:
            wx.Bell()
            title = 'Server with the same name already exists.\nDo you want to replace it?'
            message = 'Old server definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Replace", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # add/replace item
        libs.mascot[name] = itemData
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # delete?
        title = 'Do you really want to delete selected servers?'
        message = 'Server definitions will be lost.'
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
            del libs.mascot[name]
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # make map
        for server in sorted(libs.mascot.keys()):
            self.itemsMap.append((
                server,
                libs.mascot[server]['host'],
                libs.mascot[server]['path'],
            ))
    # ----
    
    
    def updateItemsList(self):
        """Update items list."""
        
        # clear previous data and set new
        self.updateItemsMap()
        self.itemsList.DeleteAllItems()
        self.itemsList.setDataMap(self.itemsMap)
        
        # check data
        if not self.itemsMap:
            return
        
        # add new data
        for row, item in enumerate(self.itemsMap):
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetStringItem(row, 2, item[2])
            self.itemsList.SetItemData(row, row)
        
        # sort
        self.itemsList.sort()
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemName_value.SetValue('')
        self.itemHost_value.SetValue('')
        self.itemPath_value.SetValue('/')
        self.itemSearch_value.SetValue('cgi/nph-mascot.exe')
        self.itemResults_value.SetValue('cgi/master_results.pl')
        self.itemExport_value.SetValue('cgi/export_dat_2.pl')
        self.itemParams_value.SetValue('cgi/get_params.pl')
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        name = self.itemName_value.GetValue()
        host = self.itemHost_value.GetValue()
        path = self.itemPath_value.GetValue()
        search = self.itemSearch_value.GetValue()
        results = self.itemResults_value.GetValue()
        export = self.itemExport_value.GetValue()
        params = self.itemParams_value.GetValue()
        
        # check values
        if not name or not host or not path or not search or not results or not export or not params:
            wx.Bell()
            return False
        
        # make compound
        server = {
            'host': host,
            'path': path,
            'search': search,
            'results': results,
            'export': export,
            'params': params,
        }
        
        return server
    # ----
    
    
