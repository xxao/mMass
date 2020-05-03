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
import xml.dom.minidom

# load modules
from ids import *
import mwx
import config
import libs
import mspy


# COMPOUNDS EDITOR
# ----------------

class dlgCompoundsEditor(wx.Dialog):
    """Edit compounds library."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Compounds Library", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.group = None
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
        self.updateGroups()
        self.groupName_choice.Select(0)
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make GUI elements
        groups = self.makeGroupEditor()
        self.makeItemsList()
        editor = self.makeItemEditor()
        
        # pack elements
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(groups, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        sizer.Add(self.itemsList, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
        sizer.Add(editor, 0, wx.EXPAND|wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return sizer
    # ----
    
    
    def makeGroupEditor(self):
        """Make group editor."""
        
        # make elements
        self.groupName_choice = wx.Choice(self, -1, size=(-1, mwx.CHOICE_HEIGHT))
        self.groupName_choice.Bind(wx.EVT_CHOICE, self.onGroupSelected)
        
        groupImport_butt = wx.Button(self, -1, "Import")
        groupImport_butt.Bind(wx.EVT_BUTTON, self.onImport)
        
        groupNew_butt = wx.Button(self, -1, "New")
        groupNew_butt.Bind(wx.EVT_BUTTON, self.onAddGroup)
        
        groupRename_butt = wx.Button(self, -1, "Rename")
        groupRename_butt.Bind(wx.EVT_BUTTON, self.onRenameGroup)
        
        groupDelete_butt = wx.Button(self, -1, "Delete")
        groupDelete_butt.Bind(wx.EVT_BUTTON, self.onDeleteGroup)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.groupName_choice, 1, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 30)
        sizer.Add(groupImport_butt, 0, wx.RIGHT, 15)
        sizer.Add(groupNew_butt, 0, wx.RIGHT, 15)
        sizer.Add(groupRename_butt, 0, wx.RIGHT, 15)
        sizer.Add(groupDelete_butt, 0)
        
        return sizer
    # ----
    
    
    def makeItemsList(self):
        """Make list for items."""
        
        # init list
        self.itemsList = mwx.sortListCtrl(self, -1, size=(771, 250), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        
        # make columns
        self.itemsList.InsertColumn(0, "name", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "formula", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(2, "mo. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(3, "av. mass", wx.LIST_FORMAT_RIGHT)
        self.itemsList.InsertColumn(4, "description", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((200,120,90,90,250)):
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
        
        itemFormula_label = wx.StaticText(self, -1, "Formula:")
        self.itemFormula_value = mwx.formulaCtrl(self, -1, "", size=(250, -1))
        self.itemFormula_value.Bind(wx.EVT_TEXT, self.onFormulaEdited)
        
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
        grid.Add(itemFormula_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemFormula_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(itemMoMass_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemMoMass_value, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(itemAvMass_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.itemAvMass_value, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        
        grid.Add(add_butt, (0,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(delete_butt, (1,7), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        return mainSizer
    # ----
    
    
    def onGroupSelected(self, evt=None):
        """Update items for selected group."""
        
        # get selected group
        group = self.groupName_choice.GetStringSelection()
        if group in libs.compounds:
            self.group = group
        else:
            self.group = None
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onItemSelected(self, evt):
        """Update item editor with selected item."""
        
        # get selected item
        name = evt.GetText()
        compound = libs.compounds[self.group][name]
        
        # update item editor
        self.itemName_value.SetValue(name)
        self.itemDescription_value.SetValue(compound.description)
        self.itemFormula_value.SetValue(compound.expression)
    # ----
    
    
    def onImport(self, evt):
        """Import items from xml library."""
        
        # show open file dialog
        wildcard =  "Library files|*.xml;*.XML"
        dlg = wx.FileDialog(self, "Import Library", wildcard=wildcard, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # read data
        importedItems = self.readLibraryXML(path)
        if importedItems == False:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Unrecognized library format.", message="Specified file is not a valid compounds library.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        elif importedItems == {}:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="No data to import.", message="Specified library contains no data.")
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # select groups to import
        dlg = dlgSelectItemsToImport(self, importedItems)
        if dlg.ShowModal() == wx.ID_OK:
            selected = dlg.selected
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # check same items
        selectAfter = 'Compounds lists'
        replaceAll = False
        for item in selected:
            if replaceAll or not item in libs.compounds:
                libs.compounds[item] = importedItems[item]
                selectAfter = item
            else:
                title = 'Group entitled "%s"\nis already in you library. Do you want to replace it?' % item
                message = "All compounds within this group will be lost."
                buttons = [(ID_dlgReplaceAll, "Replace All", 120, False, 40), (ID_dlgSkip, "Skip", 80, False, 15), (ID_dlgReplace, "Replace", 80, True, 0)]
                dlg = mwx.dlgMessage(self, title, message, buttons)
                ID = dlg.ShowModal()
                if ID == ID_dlgSkip:
                    continue
                elif ID == ID_dlgReplaceAll:
                    replaceAll = True
                    libs.compounds[item] = importedItems[item]
                    selectAfter = item
                elif ID == ID_dlgReplace:
                    libs.compounds[item] = importedItems[item]
                    selectAfter = item
        
        # update gui
        self.updateGroups()
        self.groupName_choice.SetStringSelection(selectAfter)
        self.onGroupSelected()
    # ----
    
    
    def onAddGroup(self, evt):
        """Add new group."""
        
        # get group name
        dlg = dlgGroupName(self)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # check group name
        if name in libs.compounds:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Group with the same name already exists.', message='Type a different name.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # add group
        libs.compounds[name] = {}
        
        # update gui
        self.updateGroups()
        self.groupName_choice.SetStringSelection(name)
        self.onGroupSelected()
    # ----
    
    
    def onRenameGroup(self, evt):
        """Rename selected group."""
        
        # check group
        if not self.group:
            wx.Bell()
            return
        
        # get group name
        dlg = dlgGroupName(self, self.group)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # check group name
        if name == self.group:
            return
        if name in libs.compounds:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Group with the same name already exists.', message='Type a different name.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # rename group
        data = copy.deepcopy(libs.compounds[self.group])
        libs.compounds[name] = data
        del libs.compounds[self.group]
        
        # update gui
        self.updateGroups()
        self.groupName_choice.SetStringSelection(name)
        self.onGroupSelected()
    # ----
    
    
    def onDeleteGroup(self, evt):
        """Delete selected group."""
        
        # check group
        if not self.group:
            wx.Bell()
            return
        
        # delete selected group
        title = 'Do you really want to delete selected group?'
        message = 'All compounds within the group will be lost.'
        buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Delete", 80, True, 0)]
        dlg = mwx.dlgMessage(self, title, message, buttons)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        
        # remove group
        del libs.compounds[self.group]
        
        # update gui
        self.updateGroups()
        self.groupName_choice.Select(0)
        self.onGroupSelected()
    # ----
    
    
    def onAddItem(self, evt):
        """Add/replace item."""
        
        # check group
        if not self.group:
            wx.Bell()
            return
        
        # get item data
        itemData = self.getItemData()
        if not itemData:
            return
        
        # check name
        if itemData.name in libs.compounds[self.group]:
            wx.Bell()
            title = 'Compound with the same name already exists.\nDo you want to replace it?'
            message = 'Old compound definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Replace", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
        
        # add/replace item
        libs.compounds[self.group][itemData.name] = itemData
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onDeleteItem(self, evt):
        """Remove selected items."""
        
        # check group
        if not self.group:
            wx.Bell()
            return
        
        # delete?
        title = 'Do you really want to delete selected compounds?'
        message = 'Compound definitions will be lost.'
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
            del libs.compounds[self.group][name]
        
        # update gui
        self.updateItemsList()
        self.clearEditor()
    # ----
    
    
    def onFormulaEdited(self, evt):
        """Update formula mass while editing."""
        evt.Skip()
        wx.CallAfter(self.updateFormulaMass)
    # ----
    
    
    def updateGroups(self):
        """Update groups combo."""
        
        # clear groups
        self.groupName_choice.Clear()
        
        # get names
        choices = sorted(libs.compounds.keys())
        choices.insert(0, 'Compounds lists')
        
        # add names
        for choice in choices:
            self.groupName_choice.Append(choice)
    # ----
    
    
    def updateItemsMap(self):
        """Update items map."""
        
        self.itemsMap = []
        
        # check group
        if not self.group:
            return
        
        # make map
        for name, compound in sorted(libs.compounds[self.group].items()):
            mass = compound.mass()
            self.itemsMap.append((
                name,
                compound.expression,
                mass[0],
                mass[1],
                compound.description,
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
            moMass = digits % (item[2])
            avMass = digits % (item[3])
            
            # add data
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, item[1])
            self.itemsList.SetStringItem(row, 2, str(moMass))
            self.itemsList.SetStringItem(row, 3, str(avMass))
            self.itemsList.SetStringItem(row, 4, item[4])
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
            wx.Bell()
            self.itemMoMass_value.SetValue('')
            self.itemAvMass_value.SetValue('')
    # ----
    
    
    def clearEditor(self):
        """Clear item editor."""
        
        # update editor
        self.itemName_value.SetValue('')
        self.itemDescription_value.SetValue('')
        self.itemFormula_value.SetValue('')
    # ----
    
    
    def getItemData(self):
        """Get formated item data."""
        
        # get data
        name = self.itemName_value.GetValue()
        description = self.itemDescription_value.GetValue()
        formula = self.itemFormula_value.GetValue()
        
        # check values
        if not name or not formula:
            wx.Bell()
            return False
        
        # make compound
        try:
            compound = mspy.compound(formula)
            compound.name = name
            compound.description = description
        except:
            wx.Bell()
            return False
        
        return compound
    # ----
    
    
    def readLibraryXML(self, path):
        """Read xml library."""
        
        compounds = {}
        
        # parse XML file
        try:
            document = xml.dom.minidom.parse(path)
        except:
            return False
        
        if not document.getElementsByTagName('mMassCompounds'):
            return False
        
        # read data
        groupTags = document.getElementsByTagName('group')
        if groupTags:
            for groupTag in groupTags:
                groupName = groupTag.getAttribute('name')
                compounds[groupName] = {}
                compoundTags = groupTag.getElementsByTagName('compound')
                if compoundTags:
                    for compoundTag in compoundTags:
                        try:
                            name = compoundTag.getAttribute('name')
                            compound = mspy.compound(compoundTag.getAttribute('formula'))
                            compound.description = self._getNodeText(compoundTag)
                            compounds[groupName][name] = compound
                        except:
                            pass
        
        return compounds
    # ----
    
    
    def _getNodeText(self, node):
        """Get text from node list."""
        
        buff = ''
        for node in node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                buff += node.data
        
        return buff
    # ----
    


class dlgGroupName(wx.Dialog):
    """Set group name."""
    
    def __init__(self, parent, name=''):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, "Group Name", style=wx.DEFAULT_DIALOG_STYLE)
        
        self.name = name
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.HORIZONTAL)
        
        # make elements
        self.name_value = wx.TextCtrl(self, -1, self.name, size=(300,-1), style=wx.TE_PROCESS_ENTER)
        self.name_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, "OK")
        ok_butt.Bind(wx.EVT_BUTTON, self.onOK)
        
        # pack elements
        staticSizer.Add(self.name_value, 0, wx.ALL, 10)
        
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttons.Add(ok_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.CENTER|wx.TOP|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttons, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onOK(self, evt):
        """Get name."""
        
        self.name = self.name_value.GetValue()
        if self.name:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    


class dlgSelectItemsToImport(wx.Dialog):
    """Select items to import."""
    
    def __init__(self, parent, items):
        wx.Dialog.__init__(self, parent, -1, "Select Items to Import", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.RESIZE_BORDER)
        
        self.items = items
        self.itemsMap = []
        self.selected = None
        
        # make GUI
        sizer = self.makeGUI()
        
        # show data
        self.updateItemsList()
        
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
        self.makeItemsList()
        buttons = self.makeButtons()
        
        # pack element
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.itemsList, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, mwx.LISTCTRL_SPACE)
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
    
    
    def makeItemsList(self):
        """Make list for items."""
        
        # init list
        self.itemsList = mwx.sortListCtrl(self, -1, size=(461, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.itemsList.SetFont(wx.SMALL_FONT)
        self.itemsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.itemsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        
        # make columns
        self.itemsList.InsertColumn(0, "group title", wx.LIST_FORMAT_LEFT)
        self.itemsList.InsertColumn(1, "compounds", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((350,90)):
            self.itemsList.SetColumnWidth(col, width)
    # ----
    
    
    def updateItemsList(self):
        """Set data to items list."""
        
        # set data map
        self.itemsMap = []
        for x, item in enumerate(self.items):
            self.itemsMap.append((item, len(self.items[item])))
        self.itemsList.setDataMap(self.itemsMap)
        
        # add data
        for row, item in enumerate(self.itemsMap):
            self.itemsList.InsertStringItem(row, item[0])
            self.itemsList.SetStringItem(row, 1, str(item[1]))
            self.itemsList.SetItemData(row, row)
        
        # sort data
        self.itemsList.sort()
    # ----
    
    
    def onItemActivated(self, evt):
        """Import selected item."""
        
        self.selected = self.getSelecedItems()
        self.EndModal(wx.ID_OK)
    # ----
    
    
    def onImport(self, evt):
        """Check selected items and quit."""
        
        # get selection
        self.selected = self.getSelecedItems()
        if self.selected:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
    
    def getSelecedItems(self):
        """Get selected items."""
        
        # get selected items
        keys = []
        for item in self.itemsList.getSelected():
            index = self.itemsList.GetItemData(item)
            name = self.itemsMap[index][0]
            keys.append(name)
        
        return keys
    # ----
    

