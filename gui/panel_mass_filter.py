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

from gui.panel_match import panelMatch


# FLOATING PANEL WITH MASS FILTER TOOL
# -------------------------------------

class panelMassFilter(wx.MiniFrame):
    """Mass filter tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Mass Filter', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.matchPanel = None
        
        self.currentDocument = None
        self.currentReferences = None
        
        self._referencesFilter = 0
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        self.makeReferencesList()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.referencesList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbarNoBorder'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        references_label = wx.StaticText(panel, -1, "References:")
        references_label.SetFont(wx.SMALL_FONT)
        
        choices = libs.references.keys()
        choices.sort()
        choices.insert(0,'Reference lists')
        self.references_choice = wx.Choice(panel, -1, choices=choices, size=(200, mwx.SMALL_CHOICE_HEIGHT))
        self.references_choice.Select(0)
        self.references_choice.Bind(wx.EVT_CHOICE, self.onReferencesSelected)
        
        # make buttons
        self.match_butt = wx.Button(panel, -1, "Match", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.match_butt.Bind(wx.EVT_BUTTON, self.onMatch)
        
        self.annotate_butt = wx.Button(panel, -1, "Annotate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.annotate_butt.Bind(wx.EVT_BUTTON, self.onAnnotate)
        
        self.remove_butt = wx.Button(panel, -1, "Remove", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.remove_butt.Bind(wx.EVT_BUTTON, self.onRemove)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(references_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.references_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.match_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.annotate_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.remove_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeReferencesList(self):
        """Make references list."""
        
        # init list
        self.referencesList = mwx.sortListCtrl(self, -1, size=(581, 250), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.referencesList.SetFont(wx.SMALL_FONT)
        self.referencesList.setSecondarySortColumn(2)
        self.referencesList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.referencesList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.referencesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        if wx.Platform == '__WXMAC__':
            self.referencesList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.referencesList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.referencesList.InsertColumn(0, "reference", wx.LIST_FORMAT_LEFT)
        self.referencesList.InsertColumn(1, "m/z", wx.LIST_FORMAT_RIGHT)
        self.referencesList.InsertColumn(2, "error", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((380,90,90)):
            self.referencesList.SetColumnWidth(col, width)
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # close match panel
        if self.matchPanel:
            self.matchPanel.Close()
        
        # close self
        self.Destroy()
    # ----
    
    
    def onItemSelected(self, evt):
        """Show selected mass in spectrum canvas."""
        
        # get mass
        mz = self.currentReferences[evt.GetData()][1]
        
        # show mass
        self.parent.updateMassPoints([mz])
    # ----
    
    
    def onItemActivated(self, evt):
        """Discard selected item."""
        
        # get item
        index = evt.GetData()
        row = evt.GetIndex()
        
        # update item
        self.currentReferences[index][3] = not self.currentReferences[index][3]
        
        # update GUI
        self.updateReferencesList()
        
        # scroll to see selected reference
        self.referencesList.EnsureVisible(row)
    # ----
    
    
    def onListRMU(self, evt):
        """Show filter pop-up menu on lists."""
        
        # popup menu
        menu = wx.Menu()
        menu.Append(ID_listViewAll, "Show All", "", wx.ITEM_RADIO)
        menu.Append(ID_listViewMatched, "Show Matched Only", "", wx.ITEM_RADIO)
        menu.Append(ID_listViewUnmatched, "Show Unmatched Only", "", wx.ITEM_RADIO)
        
        # check item
        if self._referencesFilter == 1:
            menu.Check(ID_listViewMatched, True)
        elif self._referencesFilter == -1:
            menu.Check(ID_listViewUnmatched, True)
        else:
            menu.Check(ID_listViewAll, True)
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewAll)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewMatched)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewUnmatched)
        
        # show menu
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onListFilter(self, evt):
        """Apply selected view filter on current list."""
        
        # set filter
        if evt.GetId() == ID_listViewMatched:
            self._referencesFilter = 1
        elif evt.GetId() == ID_listViewUnmatched:
            self._referencesFilter = -1
        else:
            self._referencesFilter = 0
        
        # update list
        self.updateReferencesList()
    # ----
    
    
    def onReferencesSelected(self, evt):
        """Update references list."""
        
        # clear previous data
        self.currentReferences = None
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.clear()
        
        # get references
        group = self.references_choice.GetStringSelection()
        if group and group in libs.references:
            self.currentReferences = []
            for item in libs.references[group]:
                self.currentReferences.append([item[0], item[1], None, True, []])
                # 0 title, 1 theoretical, 2 error, 3 use, 4 matches
        
        # update references list
        self._referencesFilter = 0
        self.updateReferencesList(scroll=True)
        
        # send data to match panel
        if self.matchPanel:
            self.matchPanel.setData(self.currentReferences)
    # ----
    
    
    def onMatch(self, evt=None):
        """Match data to current peaklist."""
        
        # init match panel
        match = True
        if not self.matchPanel:
            match = False
            self.matchPanel = panelMatch(self, self.parent, 'massfilter')
            self.matchPanel.Centre()
            self.matchPanel.Show(True)
        
        # set data
        self.matchPanel.setData(self.currentReferences)
        
        # raise panel
        if evt:
            self.matchPanel.Raise()
        
        # match data
        if match and evt:
            self.matchPanel.onMatch()
    # ----
    
    
    def onAnnotate(self, evt):
        """Annotate matched peaks."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # check references
        if not self.currentReferences:
            wx.Bell()
            return
        
        # get annotations
        annotations = []
        for item in self.currentReferences:
            if item[3]:
                for annotation in item[-1]:
                    annotation.label = item[0]
                    annotations.append(annotation)
        
        # store annotation
        if annotations:
            self.currentDocument.backup(('annotations'))
            self.currentDocument.annotations += annotations
            self.currentDocument.sortAnnotations()
            self.parent.onDocumentChanged(items=('annotations'))
    # ----
    
    
    def onRemove(self, evt=None):
        """Remove matched masses from current peaklist."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # check references
        if not self.currentReferences:
            wx.Bell()
            return
        
        # get peak indexes
        indexes = []
        for item in self.currentReferences:
            if item[3]:
                for annotation in item[-1]:
                    if not annotation.peakIndex in indexes:
                        indexes.append(annotation.peakIndex)
        
        # delete peaks
        if indexes:
            self.currentDocument.backup(('spectrum'))
            self.currentDocument.spectrum.peaklist.delete(indexes)
            self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set new document
        self.currentDocument = document
        
        # clear previous matches
        self.clearMatches()
    # ----
    
    
    def updateReferencesList(self, scroll=False):
        """Update references list."""
        
        # clear previous data and set new
        self.referencesList.DeleteAllItems()
        self.referencesList.setDataMap(self.currentReferences)
        
        # check data
        if not self.currentReferences:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.match['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        fontMatched = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        fontSkipped = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.NORMAL)
        
        row = -1
        for index, item in enumerate(self.currentReferences):
            
            # filter data
            if self._referencesFilter == 1 and item[2] == None:
                continue
            elif self._referencesFilter == -1 and item[2] != None:
                continue
            
            # format data
            theoretical = mzFormat % (item[1])
            
            error = ''
            if item[2] != None:
                error = errFormat % (item[2])
            
            # add data
            row += 1
            self.referencesList.InsertStringItem(row, '')
            self.referencesList.SetStringItem(row, 0, item[0])
            self.referencesList.SetStringItem(row, 1, theoretical)
            self.referencesList.SetStringItem(row, 2, error)
            self.referencesList.SetItemData(row, index)
            
            # mark matched
            if item[2] != None:
                self.referencesList.SetItemTextColour(row, (0,200,0))
                self.referencesList.SetItemFont(row, fontMatched)
            
            # mark skipped
            if not item[3]:
                self.referencesList.SetItemTextColour(row, (150,150,150))
                self.referencesList.SetItemFont(row, fontSkipped)
        
        # sort data
        self.referencesList.sort()
        
        # scroll top
        if scroll:
            self.referencesList.EnsureVisible(0)
    # ----
    
    
    def updateMatches(self, resultList=None):
        """Update references list."""
        
        # update references list
        self.updateReferencesList()
    # ----
    
    
    def clearMatches(self):
        """Clear matched data."""
        
        # update references list
        if self.currentReferences != None:
            for item in self.currentReferences:
                item[2] = None
                item[-1] = []
            self.updateReferencesList()
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.setData(self.currentReferences)
    # ----
    
    
    def calibrateByMatches(self, references):
        """Use matches for calibration."""
        self.parent.onToolsCalibration(references=references)
    # ----
    
    
