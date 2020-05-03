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
import re
import wx

# load modules
import mwx
import config
import mspy


# ENZYMES EDITOR
# --------------

class dlgEnzymesEditor(wx.Dialog):
    """Edit enzymes library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Enzymes Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
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
        self.itemsList = mwx.sortListCtrl(self, -1, size=(741, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "name", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "expression", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(2, "c-term", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(3, "n-term", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(4, "mods before", wx.LIST_FORMAT_CENTER)
        self.itemsList.InsertColumn(5, "mods after", wx.LIST_FORMAT_CENTER)
        
        # set column widths
        for col, width in enumerate((130,130,130,130,100,100)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeItemEditor(self):
        """Make items editor."""
        
        mainSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        itemName_label = wx.StaticText(self, -1, "Name:")
        self.itemName_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemExpression_label = wx.StaticText(self, -1, "Expression:")
        self.itemExpression_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemCTerm_label = wx.StaticText(self, -1, "C-term formula:")
        self.itemCTerm_value = mwx.formulaCtrl(self, -1, "", size=(200, -1))
        
        itemNTerm_label = wx.StaticText(self, -1, "N-term formula:")
        self.itemNTerm_value = mwx.formulaCtrl(self, -1, "", size=(200, -1))
        
        self.itemModsBefore_check = wx.CheckBox(self, -1, "Allow modification before cut")
        
        self.itemModsAfter_check = wx.CheckBox(self, -1, "Allow modification after cut")
        
        # buttons
        add_butt = wx.Button(self, -1, "Add", size=(80,-1))
        add_butt.Bind(wx.EVT_BUTTON, self.onAddItem)
        
        delete_butt = wx.Button(self, -1, "Delete", size=(80,-1))
        delete_butt.Bind(wx.EVT_BUTTON, self.onDeleteItem)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        grid.Add(itemName_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemName_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemExpression_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemExpression_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemCTerm_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemCTerm_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemNTerm_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemNTerm_value, (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(self.itemModsBefore_check, (0,3), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemModsAfter_check, (1,3), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(add_butt, (0,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        name = evt.GetText()
        enzyme = mspy.enzymes[name]
        
        # update item editor
        self.itemName_value.SetValue(name)
        self.itemExpression_value.SetValue(enzyme.expression)
        self.itemCTerm_value.SetValue(enzyme.cTermFormula)
        self.itemNTerm_value.SetValue(enzyme.nTermFormula)
        self.itemModsBefore_check.SetValue(enzyme.modsBefore)
        self.itemModsAfter_check.SetValue(enzyme.modsAfter)
    # ----
    
    
    def onAddItem(self, evt):
        """Add/replace item."""
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check name
        if itemData.name in mspy.enzymes:
            wx.Bell()
            title = 'Enzyme with the same name already exists.\nDo you want to replace it?'
            message = 'Old enzyme definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Replace", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # add/replace item
        mspy.enzymes[itemData.name] = itemData
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # delete?
        title = 'Do you really want to delete selected enzymes?'
        message = 'Enzyme definitions will be lost.'
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
            del mspy.enzymes[name]
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # make map
        for name, enzyme in sorted(mspy.enzymes.items()):
            self.itemsMap.append((
                enzyme.name,
                enzyme.expression,
                enzyme.cTermFormula,
                enzyme.nTermFormula,
                enzyme.modsBefore,
                enzyme.modsAfter,
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
            
            # format data
            modsBefore = 'not allowed'
            if item[4]:
                modsBefore = 'allowed'
            
            modsAfter = 'not allowed'
            if item[5]:
                modsAfter = 'allowed'
            
            # add data
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetStringItem(row, 2, item[2])
            self.itemsList.SetStringItem(row, 3, item[3])
            self.itemsList.SetStringItem(row, 4, modsBefore)
            self.itemsList.SetStringItem(row, 5, modsAfter)
            self.itemsList.SetItemData(row, row)
        
        # sort
        self.itemsList.sort()
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemName_value.SetValue('')
        self.itemExpression_value.SetValue('')
        self.itemCTerm_value.SetValue('')
        self.itemNTerm_value.SetValue('')
        self.itemModsBefore_check.SetValue(False)
        self.itemModsAfter_check.SetValue(False)
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        name = self.itemName_value.GetValue()
        expression = self.itemExpression_value.GetValue()
        cTermFormula = self.itemCTerm_value.GetValue()
        nTermFormula = self.itemNTerm_value.GetValue()
        modsBefore = int(self.itemModsBefore_check.GetValue())
        modsAfter = int(self.itemModsAfter_check.GetValue())
        
        # check values
        if not name or not expression or not cTermFormula or not nTermFormula:
            wx.Bell()
            return False
        
        # make enzyme
        try:
            expr = re.compile(expression)
            enzyme = mspy.enzyme(
                name = name,
                expression = expression,
                cTermFormula = cTermFormula,
                nTermFormula = nTermFormula,
                modsBefore = modsBefore,
                modsAfter = modsAfter
            )
        except:
            wx.Bell()
            return False
        
        return enzyme
    # ----
    
    
