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
import mspy


# MODIFICATIONS EDITOR
# --------------------

class dlgModificationsEditor(wx.Dialog):
    """Edit modifications library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Modifications Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.itemsMap = []
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
        
        # get used modifications
        self.used = parent.getUsedModifications()
        
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
        self.itemsList = mwx.sortListCtrl(self, -1, size=(841, 250), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "name", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "gain", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(2, "loss", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(3, "mo. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(4, "av. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(5, "amino", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(6, "term", wx.LIST_FORMAT_CENTER)
        self.itemsList.InsertColumn(7, "description", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((110,100,60,90,90,100,50,220)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeItemEditor(self):
        """Make items editor."""
        
        mainSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        itemName_label = wx.StaticText(self, -1, "Name:")
        self.itemName_value = wx.TextCtrl(self, -1, "", size=(250, -1))
        
        itemDescription_label = wx.StaticText(self, -1, "Description:")
        self.itemDescription_value = wx.TextCtrl(self, -1, "", size=(250, -1))
        
        itemAminoSpecifity_label = wx.StaticText(self, -1, "Amino specifity:")
        self.itemAminoSpecifity_value = wx.TextCtrl(self, -1, "", size=(250, -1))
        
        itemTermSpecifity_label = wx.StaticText(self, -1, "Terminal specifity:")
        self.itemTermSpecifity_choice = wx.Choice(self, -1, choices=['None','N-terminus','C-terminus'], size=(250, mwx.CHOICE_HEIGHT))
        self.itemTermSpecifity_choice.SetStringSelection('None')
        
        itemGainFormula_label = wx.StaticText(self, -1, "Gain formula:")
        self.itemGainFormula_value = mwx.formulaCtrl(self, -1, "", size=(150, -1))
        self.itemGainFormula_value.Bind(wx.EVT_TEXT, self.onFormulaEdited)
        
        itemLossFormula_label = wx.StaticText(self, -1, "Loss formula:")
        self.itemLossFormula_value = mwx.formulaCtrl(self, -1, "", size=(150, -1))
        self.itemLossFormula_value.Bind(wx.EVT_TEXT, self.onFormulaEdited)
        
        itemMoMass_label = wx.StaticText(self, -1, "Mo. mass:")
        self.itemMoMass_value = wx.TextCtrl(self, -1, "", size=(150, -1))
        itemMoMass_label.Enable(False)
        self.itemMoMass_value.Enable(False)
        
        itemAvMass_label = wx.StaticText(self, -1, "Av. mass:")
        self.itemAvMass_value = wx.TextCtrl(self, -1, "", size=(150, -1))
        itemAvMass_label.Enable(False)
        self.itemAvMass_value.Enable(False)
        
        # buttons
        add_butt = wx.Button(self, -1, "Add", size=(80,-1))
        add_butt.Bind(wx.EVT_BUTTON, self.onAddItem)
        
        delete_butt = wx.Button(self, -1, "Delete", size=(80,-1))
        delete_butt.Bind(wx.EVT_BUTTON, self.onDeleteItem)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        grid.Add(itemName_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemName_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemDescription_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemDescription_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemAminoSpecifity_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemAminoSpecifity_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemTermSpecifity_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemTermSpecifity_choice, (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemGainFormula_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemGainFormula_value, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemLossFormula_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemLossFormula_value, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemMoMass_label, (2,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemMoMass_value, (2,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemAvMass_label, (3,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemAvMass_value, (3,4), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(add_butt, (0,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        name = evt.GetText()
        mod = mspy.modifications[name]
        
        # update item editor
        self.itemName_value.SetValue(name)
        self.itemDescription_value.SetValue(mod.description)
        self.itemAminoSpecifity_value.SetValue(mod.aminoSpecifity)
        self.itemGainFormula_value.SetValue(mod.gainFormula)
        self.itemLossFormula_value.SetValue(mod.lossFormula)
        
        if mod.termSpecifity == 'C':
            self.itemTermSpecifity_choice.SetStringSelection('C-terminus')
        elif mod.termSpecifity == 'N':
            self.itemTermSpecifity_choice.SetStringSelection('N-terminus')
        else:
            self.itemTermSpecifity_choice.SetStringSelection('None')
    # ----
    
    
    def onAddItem(self, evt):
        """Add/replace item."""
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check name
        if itemData.name in mspy.modifications:
            wx.Bell()
            title = 'Modification with the same name already exists.\nDo you want to replace it?'
            message = 'Old modification definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Replace", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # add/replace item
        mspy.modifications[itemData.name] = itemData
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # delete?
        title = 'Do you really want to delete selected modifications?'
        message = 'Modification definitions will be lost.'
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
                del mspy.modifications[name]
            else:
                wx.Bell()
                dlg = mwx.dlgMessage(self, title='Modification "'+name+'" is currently applied\nand cannot be removed.', message='Remove the modification from all of your documents first.')
                dlg.ShowModal()
                dlg.Destroy()
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onFormulaEdited(self, evt):
        """Update formula mass while editing."""
        evt.Skip()
        wx.CallAfter(self.updateFormulaMass)
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # make map
        for name, mod in sorted(mspy.modifications.items()):
            self.itemsMap.append((
                mod.name,
                mod.gainFormula,
                mod.lossFormula,
                mod.mass[0],
                mod.mass[1],
                mod.aminoSpecifity,
                mod.termSpecifity,
                mod.description,
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
            moMass = digits % (item[3])
            avMass = digits % (item[4])
            
            # add data
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetStringItem(row, 2, item[2])
            self.itemsList.SetStringItem(row, 3, str(moMass))
            self.itemsList.SetStringItem(row, 4, str(avMass))
            self.itemsList.SetStringItem(row, 5, item[5])
            self.itemsList.SetStringItem(row, 6, item[6])
            self.itemsList.SetStringItem(row, 7, item[7])
            self.itemsList.SetItemData(row, row)
        
        # sort
        self.itemsList.sort()
    # ----
    
    
    def updateFormulaMass(self):
        """Update formula mass."""
        
        # get formula
        gain = self.itemGainFormula_value.GetValue()
        loss = self.itemLossFormula_value.GetValue()
        
        # show formula masses
        try:
            gain = mspy.compound(gain)
            loss = mspy.compound(loss)
            gainMass = gain.mass()
            lossMass = loss.mass()
            self.itemMoMass_value.SetValue(str(gainMass[0] - lossMass[0]))
            self.itemAvMass_value.SetValue(str(gainMass[1] - lossMass[1]))
        except:
            wx.Bell()
            self.itemMoMass_value.SetValue('')
            self.itemAvMass_value.SetValue('')
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemName_value.SetValue('')
        self.itemDescription_value.SetValue('')
        self.itemAminoSpecifity_value.SetValue('')
        self.itemGainFormula_value.SetValue('')
        self.itemLossFormula_value.SetValue('')
        self.itemMoMass_value.SetValue('')
        self.itemAvMass_value.SetValue('')
        self.itemTermSpecifity_choice.SetStringSelection('None')
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        name = self.itemName_value.GetValue()
        description = self.itemDescription_value.GetValue()
        aminoSpecifity = self.itemAminoSpecifity_value.GetValue()
        termSpecifity = self.itemTermSpecifity_choice.GetStringSelection()
        gainFormula = self.itemGainFormula_value.GetValue()
        lossFormula = self.itemLossFormula_value.GetValue()
        
        # term specifity
        if termSpecifity == 'None':
            termSpecifity = ''
        elif termSpecifity == 'N-terminus':
            termSpecifity = 'N'
        elif termSpecifity == 'C-terminus':
            termSpecifity = 'C'
        
        # check values
        if not name or (not gainFormula and not lossFormula):
            wx.Bell()
            return False
        
        # make compound
        try:
            modification = mspy.modification(
                    name = name,
                    gainFormula = gainFormula,
                    lossFormula = lossFormula,
                    aminoSpecifity = aminoSpecifity,
                    termSpecifity = termSpecifity,
                    description = description
                )
        except:
            wx.Bell()
            return False
        
        return modification
    # ----
    
    

