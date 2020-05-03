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


# MONOMERS EDITOR
# ---------------

class dlgMonomersEditor(wx.Dialog):
    """Edit monomers library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Monomers Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.itemsMap = []
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
        
        # get regular amino acids
        self._aminoacids = []
        for abbr in mspy.monomers:
            if mspy.monomers[abbr].category == '_InternalAA':
                self._aminoacids.append(abbr)
        
        # get used monomers
        self.used = parent.getUsedMonomers()
        
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
        self.itemsList = mwx.sortListCtrl(self, -1, size=(871, 250), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "abbr.", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "name", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(2, "category", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(3, "formula", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(4, "mo. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(5, "av. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(6, "losses", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((110,180,90,110,90,90,180)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeItemEditor(self):
        """Make items editor."""
        
        mainSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        itemSearch_label = wx.StaticText(self, -1, "Search:")
        self.itemSearch_value = wx.TextCtrl(self, -1, "", size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.itemSearch_value.Bind(wx.EVT_TEXT, self.onSearch)
        
        itemAbbr_label = wx.StaticText(self, -1, "Abbr.:")
        self.itemAbbr_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemName_label = wx.StaticText(self, -1, "Name:")
        self.itemName_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemCategory_label = wx.StaticText(self, -1, "Category:")
        self.itemCategory_value = wx.TextCtrl(self, -1, "", size=(200, -1))
        
        itemFormula_label = wx.StaticText(self, -1, "Formula:")
        self.itemFormula_value = mwx.formulaCtrl(self, -1, "", size=(150, -1))
        self.itemFormula_value.Bind(wx.EVT_TEXT, self.onFormulaEdited)
        
        itemMoMass_label = wx.StaticText(self, -1, "Mo. mass:")
        self.itemMoMass_value = wx.TextCtrl(self, -1, "", size=(150, -1))
        itemMoMass_label.Enable(False)
        self.itemMoMass_value.Enable(False)
        
        itemAvMass_label = wx.StaticText(self, -1, "Av. mass:")
        self.itemAvMass_value = wx.TextCtrl(self, -1, "", size=(150, -1))
        itemAvMass_label.Enable(False)
        self.itemAvMass_value.Enable(False)
        
        itemLossMoMass_label = wx.StaticText(self, -1, "Mo. loss mass:")
        self.itemLossMoMass_value = wx.TextCtrl(self, -1, "", size=(150, -1))
        itemLossMoMass_label.Enable(False)
        self.itemLossMoMass_value.Enable(False)
        
        itemLosses_label = wx.StaticText(self, -1, "Losses:")
        self.itemLosses_values = []
        for x in range(4):
            item = mwx.formulaCtrl(self, -1, "", size=(100, -1))
            item.Bind(wx.EVT_TEXT, self.onLossFormula)
            item.Bind(wx.EVT_SET_FOCUS, self.onLossFormula)
            item.Bind(wx.EVT_KILL_FOCUS, self.onLossFormula)
            self.itemLosses_values.append(item)
        
        # buttons
        add_butt = wx.Button(self, -1, "Add", size=(80,-1))
        add_butt.Bind(wx.EVT_BUTTON, self.onAddItem)
        
        delete_butt = wx.Button(self, -1, "Delete", size=(80,-1))
        delete_butt.Bind(wx.EVT_BUTTON, self.onDeleteItem)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        grid.Add(itemSearch_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemSearch_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemAbbr_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemAbbr_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemName_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemName_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemCategory_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemCategory_value, (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemFormula_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemFormula_value, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemMoMass_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemMoMass_value, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemAvMass_label, (2,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemAvMass_value, (2,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemLossMoMass_label, (3,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLossMoMass_value, (3,4), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemLosses_label, (0,6), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLosses_values[0], (0,7), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLosses_values[1], (1,7), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLosses_values[2], (2,7), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLosses_values[3], (3,7), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(add_butt, (0,10), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,10), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        abbr = evt.GetText()
        monomer = mspy.monomers[abbr]
        
        # update item editor
        self.itemAbbr_value.SetValue(abbr)
        self.itemName_value.SetValue(monomer.name)
        self.itemCategory_value.SetValue(monomer.category)
        self.itemFormula_value.SetValue(monomer.formula)
        
        for x in range(4):
            self.itemLosses_values[x].SetValue('')
            if x < len(monomer.losses):
                self.itemLosses_values[x].SetValue(monomer.losses[x])
    # ----
    
    
    def onAddItem(self, evt):
        """Add/replace item."""
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check regular amino acids
        if itemData.abbr in self._aminoacids:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Specified abbreviation is reserved!', message='Specified abbreviation is already used for regular amino acids\nwhich cannot be modified.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # check name
        if itemData.abbr in mspy.monomers:
            wx.Bell()
            title = 'Monomer with the same abbreviation already exists.\nDo you want to replace it?'
            message = 'Old monomer definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Replace", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # add/replace item
        mspy.monomers[itemData.abbr] = itemData
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # delete?
        title = 'Do you really want to delete selected monomers?'
        message = 'Monomer definitions will be lost.'
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
            if not name in self.used:
                del mspy.monomers[name]
            else:
                wx.Bell()
                dlg = mwx.dlgMessage(self, title='Monomer "'+name+'" is currently used\nand cannot be removed.', message='Remove the monomer from all of your documents first.')
                dlg.ShowModal()
                dlg.Destroy()
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onSearch(self, evt):
        """Search monomers library."""
        
        # clear editor
        self.clearEditor()
        
        # update list
        self.updateItemsList()
    # ----
    
    
    def onFormulaEdited(self, evt):
        """Update formula mass while editing."""
        evt.Skip()
        wx.CallAfter(self.updateFormulaMass)
    # ----
    
    
    def onLossFormula(self, evt):
        """Update loss formula mass while editing."""
        evt.Skip()
        wx.CallAfter(self.updateLossFormulaMass)
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # get search
        search = self.itemSearch_value.GetValue().lower().split()
        
        # make map
        for abbr, monomer in sorted(mspy.monomers.items()):
            
            # skip regular amino acids
            if monomer.category == '_InternalAA':
                continue
            
            # skip by search filter
            if search and not (
                    all(map(lambda x: x in monomer.abbr.lower(), search)) or
                    all(map(lambda x: x in monomer.name.lower(), search))
                ):
                continue
            
            # append monomer
            self.itemsMap.append((
                abbr,
                monomer.name,
                monomer.category,
                monomer.formula,
                monomer.mass[0],
                monomer.mass[1],
                ', '.join(monomer.losses),
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
        digits = '%0.' + `config.main['mzDigits']` + 'f'
        for row, item in enumerate(self.itemsMap):
            
            # format data
            moMass = digits % (item[4])
            avMass = digits % (item[5])
            
            # add data
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetStringItem(row, 2, item[2])
            self.itemsList.SetStringItem(row, 3, item[3])
            self.itemsList.SetStringItem(row, 4, str(moMass))
            self.itemsList.SetStringItem(row, 5, str(avMass))
            self.itemsList.SetStringItem(row, 6, item[6])
            self.itemsList.SetItemData(row, row)
        
        # sort
        self.itemsList.sort()
    # ----
    
    
    def updateFormulaMass(self):
        """Update formula mass."""
        
        # get formula
        formula = self.itemFormula_value.GetValue()
        
        # show formula masses
        try:
            formula = mspy.compound(formula)
            mass = formula.mass()
            self.itemMoMass_value.SetValue(str(mass[0]))
            self.itemAvMass_value.SetValue(str(mass[1]))
        except:
            self.itemMoMass_value.SetValue('')
            self.itemAvMass_value.SetValue('')
    # ----
    
    
    def updateLossFormulaMass(self):
        """Update loss formula mass."""
        
        # erase old value
        self.itemLossMoMass_value.SetValue('')
        
        # get current item
        focus = self.FindFocus()
        for x in range(4):
            item = self.itemLosses_values[x]
            
            # found focused item
            if item is focus:
                try:
                    formula = item.GetValue()
                    formula = mspy.compound(formula)
                    mass = formula.mass()
                    self.itemLossMoMass_value.SetValue(str(mass[0]))
                except:
                    pass
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemAbbr_value.SetValue('')
        self.itemName_value.SetValue('')
        self.itemCategory_value.SetValue('')
        self.itemFormula_value.SetValue('')
        self.itemMoMass_value.SetValue('')
        self.itemAvMass_value.SetValue('')
        
        for x in range(4):
            self.itemLosses_values[x].SetValue('')
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        abbr = self.itemAbbr_value.GetValue()
        name = self.itemName_value.GetValue()
        category = self.itemCategory_value.GetValue()
        formula = self.itemFormula_value.GetValue()
        
        losses = []
        for item in self.itemLosses_values:
            if item.GetValue():
                losses.append(item.GetValue())
        
        # check values
        if not abbr or not formula or not re.match('^[A-Za-z0-9\-_]*$', abbr):
            wx.Bell()
            return False
        
        # make monomer
        try:
            monomer = mspy.monomer(
                abbr = abbr,
                name = name,
                formula = formula,
                losses = losses,
                category = category
            )
        except:
            wx.Bell()
            return False
        
        return monomer
    # ----
    
    

