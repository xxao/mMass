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
import threading
import wx
import httplib
import socket
import webbrowser
import tempfile
import os.path

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy
import doc


# FLOATING PANEL WITH MASCOT SEARCH
# ---------------------------------

class panelMascot(wx.MiniFrame):
    """Mascot search tool."""
    
    def __init__(self, parent, tool=config.mascot['common']['searchType']):
        wx.MiniFrame.__init__(self, parent, -1, 'Mascot Tools', size=(300, -1), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.processing = None
        
        self.currentTool = tool
        self.currentDocument = None
        self.currentConnection = False
        self.currentParams = None
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # select tool
        self.onToolSelected(tool=self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        pmf = self.makePMFPanel()
        mis = self.makeMISPanel()
        sq = self.makeSQPanel()
        query = self.makeQueryPanel()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(pmf, 1, wx.EXPAND, 0)
        self.mainSizer.Add(mis, 1, wx.EXPAND, 0)
        self.mainSizer.Add(sq, 1, wx.EXPAND, 0)
        self.mainSizer.Add(query, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        self.mainSizer.Hide(5)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        self.pmf_butt = wx.BitmapButton(panel, ID_mascotPMF, images.lib['mascotPMFOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.pmf_butt.SetToolTip(wx.ToolTip("Peptide mass fingerprint"))
        self.pmf_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.mis_butt = wx.BitmapButton(panel, ID_mascotMIS, images.lib['mascotMISOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.mis_butt.SetToolTip(wx.ToolTip("MS/MS ion search"))
        self.mis_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.sq_butt = wx.BitmapButton(panel, ID_mascotSQ, images.lib['mascotSQOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.sq_butt.SetToolTip(wx.ToolTip("Sequence query"))
        self.sq_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.query_butt = wx.BitmapButton(panel, ID_mascotQuery, images.lib['mascotQueryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.query_butt.SetToolTip(wx.ToolTip("Query / Peak list"))
        self.query_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        server_label = wx.StaticText(panel, -1, "Server:")
        choices=libs.mascot.keys()
        choices.insert(0, 'Select Server')
        self.server_choice = wx.Choice(panel, -1, choices=choices, size=(220, mwx.SMALL_CHOICE_HEIGHT))
        if config.mascot['common']['server'] in libs.mascot:
            self.server_choice.SetStringSelection(config.mascot['common']['server'])
        else:
            self.server_choice.Select(0)
        self.server_choice.Bind(wx.EVT_CHOICE, self.onServerSelected)
        
        self.search_butt = wx.Button(panel, -1, "Search", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.search_butt.Bind(wx.EVT_BUTTON, self.onSearch)
        self.search_butt.Enable(False)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.pmf_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.mis_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.sq_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.query_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(20)
        sizer.Add(server_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.server_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.search_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makePMFPanel(self):
        """Make controls for search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramPMFSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramPMFTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        paramPMFUserName_label = wx.StaticText(panel, -1, "Name:")
        self.paramPMFUserName_value = wx.TextCtrl(panel, -1, config.mascot['common']['userName'], size=(150, -1))
        
        paramPMFUserEmail_label = wx.StaticText(panel, -1, " E-mail:")
        self.paramPMFUserEmail_value = wx.TextCtrl(panel, -1, config.mascot['common']['userEmail'], size=(150, -1))
        
        # make sequence elements
        paramPMFTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramPMFTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramPMFDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramPMFDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramPMFEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramPMFEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramPMFMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramPMFMiscleavages_choice = wx.Choice(panel, -1, choices=['0','1','2','3','4','5','6','7','8','9'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramPMFMiscleavages_choice.SetStringSelection(str(config.mascot['pmf']['miscleavages']))
        
        # make modifications elements
        self.paramPMFFixedMods_label = wx.StaticText(panel, -1, "Fixed modifications:")
        self.paramPMFFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramPMFFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramPMFFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramPMFVariableMods_label = wx.StaticText(panel, -1, "Variable modifications:")
        self.paramPMFVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramPMFVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramPMFVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramPMFHiddenMods_check = wx.CheckBox(panel, -1, "Show hidden modifications")
        self.paramPMFHiddenMods_check.SetValue(config.mascot['pmf']['hiddenMods'])
        self.paramPMFHiddenMods_check.Bind(wx.EVT_CHECKBOX, self.onHiddenModifications)
        
        # make masses elements
        paramPMFProteinMass_label = wx.StaticText(panel, -1, "Protein mass:")
        self.paramPMFProteinMass_value = wx.TextCtrl(panel, -1, "", size=(60, -1), validator=mwx.validator('floatPos'))
        paramPMFProteinMassUnits_label = wx.StaticText(panel, -1, "kDa")
        
        paramPMFPeptideTol_label = wx.StaticText(panel, -1, "Peptide tolerance:")
        self.paramPMFPeptideTol_value = wx.TextCtrl(panel, -1, str(config.mascot['pmf']['peptideTol']), size=(60, -1), validator=mwx.validator('floatPos'))
        self.paramPMFPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','mmu','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramPMFPeptideTolUnits_choice.SetStringSelection(config.mascot['pmf']['peptideTolUnits'])
        
        paramPMFMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramPMFMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramPMFMassType_choice.SetStringSelection(config.mascot['pmf']['massType'])
        
        paramPMFCharge_label = wx.StaticText(panel, -1, "Charge:")
        self.paramPMFCharge_choice = wx.Choice(panel, -1, choices=['1+','Mr','1-'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramPMFCharge_choice.SetStringSelection(config.mascot['pmf']['charge'])
        
        # make other elements
        self.paramPMFDecoy_check = wx.CheckBox(panel, -1, "Decoy")
        self.paramPMFDecoy_check.SetValue(config.mascot['pmf']['decoy'])
        
        paramPMFReport_label = wx.StaticText(panel, -1, "Report:")
        self.paramPMFReport_choice = wx.Choice(panel, -1, choices=['AUTO','5','10','20','30','50'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramPMFReport_choice.SetStringSelection(config.mascot['pmf']['report'])
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramPMFSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramPMFTitle_value, (0,1), (1,3), flag=wx.EXPAND)
        infoGrid.Add(paramPMFUserName_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramPMFUserName_value, (1,1), flag=wx.EXPAND)
        infoGrid.Add(paramPMFUserEmail_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramPMFUserEmail_value, (1,3), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        infoGrid.AddGrowableCol(3)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramPMFTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramPMFTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramPMFDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramPMFDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramPMFEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramPMFEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramPMFMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramPMFMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramPMFFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramPMFVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramPMFFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramPMFVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.Add(self.paramPMFHiddenMods_check, (2,0), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramPMFProteinMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPMFProteinMass_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramPMFProteinMassUnits_label, (0,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramPMFPeptideTol_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPMFPeptideTol_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPMFPeptideTolUnits_choice, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramPMFMassType_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPMFMassType_choice, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramPMFCharge_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPMFCharge_choice, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(2)
        
        othersGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        othersGrid.Add(self.paramPMFDecoy_check, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(paramPMFReport_label, (0,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(self.paramPMFReport_choice, (0,3), flag=wx.ALIGN_CENTER_VERTICAL)
        othersGrid.AddGrowableCol(2)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(infoGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(sequenceGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(modsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(massesGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(othersGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeMISPanel(self):
        """Make controls for search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramMISSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramMISTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        paramMISUserName_label = wx.StaticText(panel, -1, "Name:")
        self.paramMISUserName_value = wx.TextCtrl(panel, -1, config.mascot['common']['userName'], size=(150, -1))
        
        paramMISUserEmail_label = wx.StaticText(panel, -1, " E-mail:")
        self.paramMISUserEmail_value = wx.TextCtrl(panel, -1, config.mascot['common']['userEmail'], size=(150, -1))
        
        # make sequence elements
        paramMISTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramMISTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramMISDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramMISDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramMISEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramMISEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramMISMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramMISMiscleavages_choice = wx.Choice(panel, -1, choices=['0','1','2','3','4','5','6','7','8','9'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramMISMiscleavages_choice.SetStringSelection(str(config.mascot['mis']['miscleavages']))
        
        # make modifications elements
        self.paramMISFixedMods_label = wx.StaticText(panel, -1, "Fixed modifications:")
        self.paramMISFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMISFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMISFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramMISVariableMods_label = wx.StaticText(panel, -1, "Variable modifications:")
        self.paramMISVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMISVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMISVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramMISHiddenMods_check = wx.CheckBox(panel, -1, "Show hidden modifications")
        self.paramMISHiddenMods_check.SetValue(config.mascot['mis']['hiddenMods'])
        self.paramMISHiddenMods_check.Bind(wx.EVT_CHECKBOX, self.onHiddenModifications)
        
        # make masses elements
        paramMISPrecursorMass_label = wx.StaticText(panel, -1, "Precursor m/z:")
        self.paramMISPeptideMass_value = wx.TextCtrl(panel, -1, "", size=(145, -1), validator=mwx.validator('floatPos'))
        
        paramMISPeptideTol_label = wx.StaticText(panel, -1, "Precursor tolerance:")
        self.paramMISPeptideTol_value = wx.TextCtrl(panel, -1, str(config.mascot['mis']['peptideTol']), size=(60, -1), validator=mwx.validator('floatPos'))
        self.paramMISPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','mmu','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMISPeptideTolUnits_choice.SetStringSelection(config.mascot['mis']['peptideTolUnits'])
        
        paramMISMSMSTol_label = wx.StaticText(panel, -1, "MS/MS tolerance:")
        self.paramMISMSMSTol_value = wx.TextCtrl(panel, -1, str(config.mascot['mis']['msmsTol']), size=(60, -1), validator=mwx.validator('floatPos'))
        self.paramMISMSMSTolUnits_choice = wx.Choice(panel, -1, choices=['Da','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMISMSMSTolUnits_choice.SetStringSelection(config.mascot['mis']['msmsTolUnits'])
        
        paramMISMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramMISMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramMISMassType_choice.SetStringSelection(config.mascot['mis']['massType'])
        
        paramMISCharge_label = wx.StaticText(panel, -1, "Charge:")
        self.paramMISCharge_choice = wx.Choice(panel, -1, choices=['8-','7-','6-','5-','4-','3-','2- and 3-','2-','1-, 2- and 3-','1-','Mr','1+','1+, 2+ and 3+','2+','2+ and 3+','3+','4+','5+','6+','7+','8+'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramMISCharge_choice.SetStringSelection(config.mascot['mis']['charge'])
        
        paramMISInstrument_label = wx.StaticText(panel, -1, "Instrument:")
        self.paramMISInstrument_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramMISQuantitation_label = wx.StaticText(panel, -1, "Quantitation:")
        self.paramMISQuantitation_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        # make other elements
        self.paramMISDecoy_check = wx.CheckBox(panel, -1, "Decoy")
        self.paramMISDecoy_check.SetValue(config.mascot['mis']['decoy'])
        
        self.paramMISErrorTolerant_check = wx.CheckBox(panel, -1, "Error tolerant")
        self.paramMISErrorTolerant_check.SetValue(config.mascot['mis']['errorTolerant'])
        
        paramMISReport_label = wx.StaticText(panel, -1, "Report:")
        self.paramMISReport_choice = wx.Choice(panel, -1, choices=['AUTO','5','10','20','30','50'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMISReport_choice.SetStringSelection(str(config.mascot['mis']['report']))
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramMISSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramMISTitle_value, (0,1), (1,3), flag=wx.EXPAND)
        infoGrid.Add(paramMISUserName_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramMISUserName_value, (1,1), flag=wx.EXPAND)
        infoGrid.Add(paramMISUserEmail_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramMISUserEmail_value, (1,3), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        infoGrid.AddGrowableCol(3)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramMISTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMISTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramMISDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMISDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramMISEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMISEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramMISMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMISMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramMISFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMISVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMISFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramMISVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.Add(self.paramMISHiddenMods_check, (2,0), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramMISPrecursorMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISPeptideMass_value, (0,1), (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISPeptideTol_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISPeptideTol_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISPeptideTolUnits_choice, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISMSMSTol_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISMSMSTol_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISMSMSTolUnits_choice, (2,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISMassType_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISMassType_choice, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISCharge_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISCharge_choice, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISInstrument_label, (2,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISInstrument_choice, (2,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMISQuantitation_label, (3,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMISQuantitation_choice, (3,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(2)
        
        othersGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        othersGrid.Add(self.paramMISDecoy_check, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(self.paramMISErrorTolerant_check, (0,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(paramMISReport_label, (0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(self.paramMISReport_choice, (0,5), flag=wx.ALIGN_CENTER_VERTICAL)
        othersGrid.AddGrowableCol(4)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(infoGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(sequenceGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(modsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(massesGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(othersGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSQPanel(self):
        """Make controls for search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramSQSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramSQTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        paramSQUserName_label = wx.StaticText(panel, -1, "Name:")
        self.paramSQUserName_value = wx.TextCtrl(panel, -1, config.mascot['common']['userName'], size=(150, -1))
        
        paramSQUserEmail_label = wx.StaticText(panel, -1, " E-mail:")
        self.paramSQUserEmail_value = wx.TextCtrl(panel, -1, config.mascot['common']['userEmail'], size=(150, -1))
        
        # make sequence elements
        paramSQTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramSQTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramSQDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramSQDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramSQEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramSQEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramSQMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramSQMiscleavages_choice = wx.Choice(panel, -1, choices=['0','1','2','3','4','5','6','7','8','9'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramSQMiscleavages_choice.SetStringSelection(str(config.mascot['sq']['miscleavages']))
        
        # make modifications elements
        self.paramSQFixedMods_label = wx.StaticText(panel, -1, "Fixed modifications:")
        self.paramSQFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramSQFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramSQFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramSQVariableMods_label = wx.StaticText(panel, -1, "Variable modifications:")
        self.paramSQVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramSQVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramSQVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramSQHiddenMods_check = wx.CheckBox(panel, -1, "Show hidden modifications")
        self.paramSQHiddenMods_check.SetValue(config.mascot['sq']['hiddenMods'])
        self.paramSQHiddenMods_check.Bind(wx.EVT_CHECKBOX, self.onHiddenModifications)
        
        # make masses elements
        paramSQPeptideTol_label = wx.StaticText(panel, -1, "Peptide tolerance:")
        self.paramSQPeptideTol_value = wx.TextCtrl(panel, -1, str(config.mascot['sq']['peptideTol']), size=(60, -1), validator=mwx.validator('floatPos'))
        self.paramSQPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','mmu','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramSQPeptideTolUnits_choice.SetStringSelection(config.mascot['sq']['peptideTolUnits'])
        
        paramSQMSMSTol_label = wx.StaticText(panel, -1, "MS/MS tolerance:")
        self.paramSQMSMSTol_value = wx.TextCtrl(panel, -1, str(config.mascot['sq']['msmsTol']), size=(60, -1), validator=mwx.validator('floatPos'))
        self.paramSQMSMSTolUnits_choice = wx.Choice(panel, -1, choices=['Da','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramSQMSMSTolUnits_choice.SetStringSelection(config.mascot['sq']['msmsTolUnits'])
        
        paramSQMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramSQMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramSQMassType_choice.SetStringSelection(config.mascot['sq']['massType'])
        
        paramSQCharge_label = wx.StaticText(panel, -1, "Charge:")
        self.paramSQCharge_choice = wx.Choice(panel, -1, choices=['8-','7-','6-','5-','4-','3-','2- and 3-','2-','1-, 2- and 3-','1-','Mr','1+','1+, 2+ and 3+','2+','2+ and 3+','3+','4+','5+','6+','7+','8+'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramSQCharge_choice.SetStringSelection(config.mascot['sq']['charge'])
        
        paramSQInstrument_label = wx.StaticText(panel, -1, "Instrument:")
        self.paramSQInstrument_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramSQQuantitation_label = wx.StaticText(panel, -1, "Quantitation:")
        self.paramSQQuantitation_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        # make other elements
        self.paramSQDecoy_check = wx.CheckBox(panel, -1, "Decoy")
        self.paramSQDecoy_check.SetValue(config.mascot['sq']['decoy'])
        
        paramSQReport_label = wx.StaticText(panel, -1, "Report:")
        self.paramSQReport_choice = wx.Choice(panel, -1, choices=['AUTO','5','10','20','30','50'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramSQReport_choice.SetStringSelection(config.mascot['sq']['report'])
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramSQSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramSQTitle_value, (0,1), (1,3), flag=wx.EXPAND)
        infoGrid.Add(paramSQUserName_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramSQUserName_value, (1,1), flag=wx.EXPAND)
        infoGrid.Add(paramSQUserEmail_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramSQUserEmail_value, (1,3), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        infoGrid.AddGrowableCol(3)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramSQTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramSQTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramSQDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramSQDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramSQEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramSQEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramSQMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramSQMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramSQFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramSQVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramSQFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramSQVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.Add(self.paramSQHiddenMods_check, (2,0), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramSQPeptideTol_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQPeptideTol_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQPeptideTolUnits_choice, (0,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramSQMSMSTol_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQMSMSTol_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQMSMSTolUnits_choice, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramSQMassType_label, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQMassType_choice, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramSQCharge_label, (1,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQCharge_choice, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramSQInstrument_label, (2,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQInstrument_choice, (2,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramSQQuantitation_label, (3,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramSQQuantitation_choice, (3,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(2)
        
        othersGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        othersGrid.Add(self.paramSQDecoy_check, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(paramSQReport_label, (0,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        othersGrid.Add(self.paramSQReport_choice, (0,3), flag=wx.ALIGN_CENTER_VERTICAL)
        othersGrid.AddGrowableCol(2)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(infoGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(sequenceGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(modsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(massesGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(othersGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeQueryPanel(self):
        """Make controls for query."""
        
        # init panels
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        pklPanel = wx.Panel(self, -1)
        
        # make elements
        filter_label = wx.StaticText(ctrlPanel, -1, "Remove:")
        filter_label.SetFont(wx.SMALL_FONT)
        
        self.filterAnnotations_check = wx.CheckBox(ctrlPanel, -1, "Annotated")
        self.filterAnnotations_check.SetFont(wx.SMALL_FONT)
        self.filterAnnotations_check.SetValue(config.mascot['common']['filterAnnotations'])
        self.filterAnnotations_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterMatches_check = wx.CheckBox(ctrlPanel, -1, "Matched")
        self.filterMatches_check.SetFont(wx.SMALL_FONT)
        self.filterMatches_check.SetValue(config.mascot['common']['filterMatches'])
        self.filterMatches_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnselected_check = wx.CheckBox(ctrlPanel, -1, "Unselected")
        self.filterUnselected_check.SetFont(wx.SMALL_FONT)
        self.filterUnselected_check.SetValue(config.mascot['common']['filterUnselected'])
        self.filterUnselected_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterIsotopes_check = wx.CheckBox(ctrlPanel, -1, "Isotopes")
        self.filterIsotopes_check.SetFont(wx.SMALL_FONT)
        self.filterIsotopes_check.SetValue(config.mascot['common']['filterIsotopes'])
        self.filterIsotopes_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnknown_check = wx.CheckBox(ctrlPanel, -1, "Unknown")
        self.filterUnknown_check.SetFont(wx.SMALL_FONT)
        self.filterUnknown_check.SetValue(config.mascot['common']['filterUnknown'])
        self.filterUnknown_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.paramQuery_value = wx.TextCtrl(pklPanel, -1, "", size=(300, 300), style=wx.TE_MULTILINE)
        self.paramQuery_value.SetFont(wx.SMALL_FONT)
        
        # pack elements
        ctrlSizer = wx.BoxSizer(wx.HORIZONTAL)
        ctrlSizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        ctrlSizer.Add(filter_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        ctrlSizer.Add(self.filterAnnotations_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        ctrlSizer.Add(self.filterMatches_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        ctrlSizer.Add(self.filterUnselected_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        ctrlSizer.Add(self.filterIsotopes_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        ctrlSizer.Add(self.filterUnknown_check, 0, wx.ALIGN_CENTER_VERTICAL)
        ctrlSizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        ctrlSizer.Fit(ctrlPanel)
        ctrlPanel.SetSizer(ctrlSizer)
        
        pklSizer = wx.BoxSizer(wx.VERTICAL)
        if wx.Platform == '__WXMAC__': pklSizer.AddSpacer(mwx.PANEL_SPACE_MAIN)
        pklSizer.Add(self.paramQuery_value, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        pklSizer.Fit(pklPanel)
        pklPanel.SetSizer(pklSizer)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND|wx.ALIGN_CENTER)
        mainSizer.Add(pklPanel, 1, wx.EXPAND|wx.ALIGN_CENTER)
        
        return mainSizer
    # ----
    
    
    def makeGaugePanel(self):
        """Make processing gauge."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.gauge = mwx.gauge(panel, -1)
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.gauge, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.GAUGE_SPACE)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # delete temporary file
        try:
            path = os.path.join(tempfile.gettempdir(), 'mmass_mascot_search.html')
            os.unlink(path)
        except:
            pass
        
        self.Destroy()
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(5)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(5)
            self.processing = None
        
        # fit layout
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # get the tool
        if evt != None:
            tool = 'pmf'
            if evt and evt.GetId() == ID_mascotPMF:
                tool = 'pmf'
            elif evt and evt.GetId() == ID_mascotMIS:
                tool = 'mis'
            elif evt and evt.GetId() == ID_mascotSQ:
                tool = 'sq'
            elif evt and evt.GetId() == ID_mascotQuery:
                tool = 'query'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        
        # set icons off
        self.pmf_butt.SetBitmapLabel(images.lib['mascotPMFOff'])
        self.mis_butt.SetBitmapLabel(images.lib['mascotMISOff'])
        self.sq_butt.SetBitmapLabel(images.lib['mascotSQOff'])
        self.query_butt.SetBitmapLabel(images.lib['mascotQueryOff'])
        
        # set panel
        if tool == 'pmf':
            config.mascot['common']['searchType'] = 'pmf'
            self.SetTitle("Mascot - Peptide Mass Fingerprint")
            self.mainSizer.Show(1)
            self.pmf_butt.SetBitmapLabel(images.lib['mascotPMFOn'])
            self.server_choice.Enable(True)
        
        elif tool == 'mis':
            config.mascot['common']['searchType'] = 'mis'
            self.SetTitle("Mascot - MS/MS Ion Search")
            self.mainSizer.Show(2)
            self.mis_butt.SetBitmapLabel(images.lib['mascotMISOn'])
            self.server_choice.Enable(True)
        
        elif tool == 'sq':
            config.mascot['common']['searchType'] = 'sq'
            self.SetTitle("Mascot - Sequence Query")
            self.mainSizer.Show(3)
            self.sq_butt.SetBitmapLabel(images.lib['mascotSQOn'])
            self.server_choice.Enable(True)
        
        elif tool == 'query':
            self.SetTitle("Mascot - Query / Peak List")
            self.mainSizer.Show(4)
            self.query_butt.SetBitmapLabel(images.lib['mascotQueryOn'])
            self.server_choice.Enable(False)
        
        # enable search button
        if self.currentConnection and tool in ('pmf', 'sq', 'mis'):
            self.search_butt.Enable(True)
        else:
            self.search_butt.Enable(False)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onServerSelected(self, evt=None):
        """Get parameters from the server and update form."""
        self.updateServerParams()
    # ----
    
    
    def onModificationSelected(self, evt=None):
        """Count and show number of selected modifications."""
        
        if (self.paramPMFFixedMods_label and self.paramPMFVariableMods_label):
            label = 'Fixed modifications: (%d)' % len(self.paramPMFFixedMods_listbox.GetSelections())
            self.paramPMFFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramPMFVariableMods_listbox.GetSelections())
            self.paramPMFVariableMods_label.SetLabel(label)
        
        if (self.paramMISFixedMods_label and self.paramMISVariableMods_label):
            label = 'Fixed modifications: (%d)' % len(self.paramMISFixedMods_listbox.GetSelections())
            self.paramMISFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramMISVariableMods_listbox.GetSelections())
            self.paramMISVariableMods_label.SetLabel(label)
        
        if (self.paramSQFixedMods_label and self.paramSQVariableMods_label):
            label = 'Fixed modifications: (%d)' % len(self.paramSQFixedMods_listbox.GetSelections())
            self.paramSQFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramSQVariableMods_listbox.GetSelections())
            self.paramSQVariableMods_label.SetLabel(label)
    # ----
    
    
    def onHiddenModifications(self, evt=None):
        """Enable / disable hidden modifications."""
        
        # get value
        config.mascot['pmf']['hiddenMods'] = int(self.paramPMFHiddenMods_check.GetValue())
        config.mascot['mis']['hiddenMods'] = int(self.paramMISHiddenMods_check.GetValue())
        config.mascot['sq']['hiddenMods'] = int(self.paramSQHiddenMods_check.GetValue())
        
        # update modifications list
        if self.currentParams:
            self.updateModification(tool=self.currentTool)
    # ----
    
    
    def onGetPeaklist(self, evt=None):
        """Get current peaklist according to specified filter."""
        
        # get filters
        filters = ''
        if self.filterAnnotations_check.GetValue():
            filters += 'A'
        if self.filterMatches_check.GetValue():
            filters += 'M'
        if self.filterUnselected_check.GetValue():
            filters += 'S'
        if self.filterIsotopes_check.GetValue():
            filters += 'I'
        if self.filterUnknown_check.GetValue():
            filters += 'X'
        
        # get peaklist
        peaklist = self.parent.getCurrentPeaklist(filters)
        
        # check data
        if not peaklist:
            self.paramQuery_value.SetValue('')
            if evt:
                wx.Bell()
            return
        
        # make new query
        query = ''
        for peak in peaklist:
            query += '%f\t%f\n' % (peak.mz, peak.intensity)
        
        # set data
        self.paramQuery_value.SetValue(query)
    # ----
    
    
    def onSearch(self, evt):
        """Make query and send data to Mascot."""
        
        # get params
        if not self.getParams():
            return
        
        # check params
        if not self.checkParams():
            return
        
        # make temporary search file
        htmlData = self.makeSearchHTML()
        try:
            path = os.path.join(tempfile.gettempdir(), 'mmass_mascot_search.html')
            htmlFile = file(path, 'w')
            htmlFile.write(htmlData.encode("utf-8"))
            htmlFile.close()
            webbrowser.open('file://'+path, autoraise=1)
        except:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Unable to send data to Mascot server.', message='Unknown error occured while creating the search page.')
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set current document
        self.currentDocument = document
        
        # check document
        if not document:
            self.paramPMFTitle_value.SetValue('')
            self.paramMISTitle_value.SetValue('')
            self.paramSQTitle_value.SetValue('')
            self.paramQuery_value.SetValue('')
            return
        
        # change search title
        self.paramPMFTitle_value.SetValue(document.title)
        self.paramMISTitle_value.SetValue(document.title)
        self.paramSQTitle_value.SetValue(document.title)
        
        # change precursor mass
        if document.spectrum.precursorMZ:
            self.paramMISPeptideMass_value.SetValue(str(document.spectrum.precursorMZ))
        else:
            self.paramMISPeptideMass_value.SetValue('')
        
        # get peaklist
        self.onGetPeaklist()
    # ----
    
    
    def getServerParams(self):
        """Get form params from the selected server."""
        
        # server
        name = config.mascot['common']['server']
        server = libs.mascot[name]
        
        # get data from the server
        socket.setdefaulttimeout(5)
        try:
            conn = httplib.HTTPConnection(server['host'])
            conn.connect()
            conn.request('GET', server['path'] + server['params'])
            response = conn.getresponse()
        except:
            self.currentParams = None
            return False
        
        if response.status == 200:
            data = response.read()
            conn.close()
        else:
            conn.close()
            self.currentParams = None
            return
        
        # parse parameter file
        self.currentParams = {
            'DB':[],
            'TAXONOMY':['All entries'],
            'CLE':[],
            'MODS':[],
            'HIDDEN_MODS':[],
            'INSTRUMENT':['Default'],
            'QUANTITATION':['None'],
        }
        pattSection = re.compile('^\[([a-zA-Z_]*)\]$')
        for line in data.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # section header
            if pattSection.match(line):
                section = line[1:-1]
                self.currentParams[section]=[]
            else:
                self.currentParams[section].append(line)
    # ----
    
    
    def getParams(self):
        """Get dialog params."""
        
        try:
            
            # PMF params
            if config.mascot['common']['searchType'] == 'pmf':
                
                config.mascot['common']['title'] = self.paramPMFTitle_value.GetValue()
                config.mascot['common']['userName'] = self.paramPMFUserName_value.GetValue()
                config.mascot['common']['userEmail'] = self.paramPMFUserEmail_value.GetValue()
                config.mascot['pmf']['database'] = self.paramPMFDatabase_choice.GetStringSelection()
                config.mascot['pmf']['taxonomy'] = self.paramPMFTaxonomy_choice.GetStringSelection()
                config.mascot['pmf']['enzyme'] = self.paramPMFEnzyme_choice.GetStringSelection()
                config.mascot['pmf']['miscleavages'] = self.paramPMFMiscleavages_choice.GetStringSelection()
                config.mascot['pmf']['proteinMass'] = self.paramPMFProteinMass_value.GetValue()
                config.mascot['pmf']['peptideTol'] = self.paramPMFPeptideTol_value.GetValue()
                config.mascot['pmf']['peptideTolUnits'] = self.paramPMFPeptideTolUnits_choice.GetStringSelection()
                config.mascot['pmf']['massType'] = self.paramPMFMassType_choice.GetStringSelection()
                config.mascot['pmf']['charge'] = self.paramPMFCharge_choice.GetStringSelection()
                config.mascot['pmf']['decoy'] = int(self.paramPMFDecoy_check.GetValue())
                config.mascot['pmf']['report'] = self.paramPMFReport_choice.GetStringSelection()
                
                fixedMods = self.paramPMFFixedMods_listbox.GetStrings()
                variableMods = self.paramPMFVariableMods_listbox.GetStrings()
                config.mascot['pmf']['fixedMods'] = []
                config.mascot['pmf']['variableMods'] = []
                for item in self.paramPMFFixedMods_listbox.GetSelections():
                    config.mascot['pmf']['fixedMods'].append(fixedMods[item])
                for item in self.paramPMFVariableMods_listbox.GetSelections():
                    config.mascot['pmf']['variableMods'].append(variableMods[item])
                
                if config.mascot['pmf']['proteinMass']:
                    config.mascot['pmf']['proteinMass'] = float(config.mascot['pmf']['proteinMass'])
                
                if config.mascot['pmf']['peptideTol']:
                    config.mascot['pmf']['peptideTol'] = float(config.mascot['pmf']['peptideTol'])
            
            # MIS params
            elif config.mascot['common']['searchType'] == 'mis':
                
                config.mascot['common']['title'] = self.paramMISTitle_value.GetValue()
                config.mascot['common']['userName'] = self.paramMISUserName_value.GetValue()
                config.mascot['common']['userEmail'] = self.paramMISUserEmail_value.GetValue()
                config.mascot['mis']['database'] = self.paramMISDatabase_choice.GetStringSelection()
                config.mascot['mis']['taxonomy'] = self.paramMISTaxonomy_choice.GetStringSelection()
                config.mascot['mis']['enzyme'] = self.paramMISEnzyme_choice.GetStringSelection()
                config.mascot['mis']['miscleavages'] = self.paramMISMiscleavages_choice.GetStringSelection()
                config.mascot['mis']['peptideMass'] = self.paramMISPeptideMass_value.GetValue()
                config.mascot['mis']['peptideTol'] = self.paramMISPeptideTol_value.GetValue()
                config.mascot['mis']['peptideTolUnits'] = self.paramMISPeptideTolUnits_choice.GetStringSelection()
                config.mascot['mis']['msmsTol'] = self.paramMISMSMSTol_value.GetValue()
                config.mascot['mis']['msmsTolUnits'] = self.paramMISMSMSTolUnits_choice.GetStringSelection()
                config.mascot['mis']['massType'] = self.paramMISMassType_choice.GetStringSelection()
                config.mascot['mis']['charge'] = self.paramMISCharge_choice.GetStringSelection()
                config.mascot['mis']['instrument'] = self.paramMISInstrument_choice.GetStringSelection()
                config.mascot['mis']['quantitation'] = self.paramMISQuantitation_choice.GetStringSelection()
                config.mascot['mis']['errorTolerant'] = int(self.paramMISErrorTolerant_check.GetValue())
                config.mascot['mis']['decoy'] = int(self.paramMISDecoy_check.GetValue())
                config.mascot['mis']['report'] = self.paramMISReport_choice.GetStringSelection()
                
                fixedMods = self.paramMISFixedMods_listbox.GetStrings()
                variableMods = self.paramMISVariableMods_listbox.GetStrings()
                config.mascot['mis']['fixedMods'] = []
                config.mascot['mis']['variableMods'] = []
                for item in self.paramMISFixedMods_listbox.GetSelections():
                    config.mascot['mis']['fixedMods'].append(fixedMods[item])
                for item in self.paramMISVariableMods_listbox.GetSelections():
                    config.mascot['mis']['variableMods'].append(variableMods[item])
                
                if config.mascot['mis']['peptideMass']:
                    config.mascot['mis']['peptideMass'] = float(config.mascot['mis']['peptideMass'])
                
                if config.mascot['mis']['peptideTol']:
                    config.mascot['mis']['peptideTol'] = float(config.mascot['mis']['peptideTol'])
                
                if config.mascot['mis']['msmsTol']:
                    config.mascot['mis']['msmsTol'] = float(config.mascot['mis']['msmsTol'])
            
            # SQ params
            elif config.mascot['common']['searchType'] == 'sq':
                
                config.mascot['common']['title'] = self.paramSQTitle_value.GetValue()
                config.mascot['common']['userName'] = self.paramSQUserName_value.GetValue()
                config.mascot['common']['userEmail'] = self.paramSQUserEmail_value.GetValue()
                config.mascot['sq']['database'] = self.paramSQDatabase_choice.GetStringSelection()
                config.mascot['sq']['taxonomy'] = self.paramSQTaxonomy_choice.GetStringSelection()
                config.mascot['sq']['enzyme'] = self.paramSQEnzyme_choice.GetStringSelection()
                config.mascot['sq']['miscleavages'] = self.paramSQMiscleavages_choice.GetStringSelection()
                config.mascot['sq']['peptideTol'] = self.paramSQPeptideTol_value.GetValue()
                config.mascot['sq']['peptideTolUnits'] = self.paramSQPeptideTolUnits_choice.GetStringSelection()
                config.mascot['sq']['msmsTol'] = self.paramSQMSMSTol_value.GetValue()
                config.mascot['sq']['msmsTolUnits'] = self.paramSQMSMSTolUnits_choice.GetStringSelection()
                config.mascot['sq']['massType'] = self.paramSQMassType_choice.GetStringSelection()
                config.mascot['sq']['charge'] = self.paramSQCharge_choice.GetStringSelection()
                config.mascot['sq']['instrument'] = self.paramSQInstrument_choice.GetStringSelection()
                config.mascot['sq']['quantitation'] = self.paramSQQuantitation_choice.GetStringSelection()
                config.mascot['sq']['decoy'] = int(self.paramSQDecoy_check.GetValue())
                config.mascot['sq']['report'] = self.paramSQReport_choice.GetStringSelection()
                
                fixedMods = self.paramSQFixedMods_listbox.GetStrings()
                variableMods = self.paramSQVariableMods_listbox.GetStrings()
                config.mascot['sq']['fixedMods'] = []
                config.mascot['sq']['variableMods'] = []
                for item in self.paramSQFixedMods_listbox.GetSelections():
                    config.mascot['sq']['fixedMods'].append(fixedMods[item])
                for item in self.paramSQVariableMods_listbox.GetSelections():
                    config.mascot['sq']['variableMods'].append(variableMods[item])
                
                if config.mascot['sq']['peptideTol']:
                    config.mascot['sq']['peptideTol'] = float(config.mascot['sq']['peptideTol'])
                
                if config.mascot['sq']['msmsTol']:
                    config.mascot['sq']['msmsTol'] = float(config.mascot['sq']['msmsTol'])
                
            return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def checkParams(self):
        """Check search parameters."""
        
        errors = ''
        form = config.mascot['common']['searchType']
        
        # check user name and e-mail
        if not config.mascot['common']['userName']:
            errors += '- Your name must be specified.\n'
        if not config.mascot['common']['userEmail']:
            errors += '- Your e-mail must be specified.\n'
        
        # check taxonomy and database
        if not config.mascot[form]['taxonomy']:
            errors += '- Taxonomy must be selected.\n'
        if not config.mascot[form]['database']:
            errors += '- Database must be selected.\n'
        if not config.mascot[form]['enzyme']:
            errors += '- Enzyme must be selected.\n'
        
        # check protein mass
        if config.mascot['common']['searchType'] == 'pmf':
            if config.mascot['pmf']['proteinMass']:
                if config.mascot['pmf']['proteinMass'] < 0:
                    errors += '- Protein mass cannot be negative.\n'
                elif config.mascot['pmf']['proteinMass'] > 1000:
                    errors += '- Upper limit on protein mass cannot exceed 1000 kDa.\n'
        
        # check precursor mass
        if config.mascot['common']['searchType'] == 'mis':
            if config.mascot['mis']['peptideMass']:
                if config.mascot['mis']['peptideMass'] < 100:
                    errors += '- Precursor mass must be at least 100 Da.\n'
                elif config.mascot['mis']['peptideMass'] > 16000:
                    errors += '- Precursor mass must be less than 16 000 Da.\n'
            else:
                errors += '- Precursor mass must be specified.\n'
        
        # check peptide tolerance
        if config.mascot[form]['peptideTol']:
            if config.mascot[form]['peptideTol'] < 0:
                errors += '- Peptide tolerance cannot be negative.\n'
            elif config.mascot[form]['peptideTol'] > 10 and config.mascot[form]['peptideTolUnits'] == 'Da':
                errors += '- Peptide tolerance must be less than 10 Da.\n'
            elif config.mascot[form]['peptideTol'] > 10000 and config.mascot[form]['peptideTolUnits'] == 'mmu':
                errors += '- Peptide tolerance must be less than 10 000 mmu.\n'
            elif config.mascot[form]['peptideTol'] > 10000 and config.mascot[form]['peptideTolUnits'] == 'ppm':
                errors += '- Peptide tolerance must be less than 10 000 ppm.\n'
            elif config.mascot[form]['peptideTol'] > 1 and config.mascot[form]['peptideTolUnits'] == '%':
                errors += '- Peptide tolerance must be less than 1%.\n'
        else:
            errors += '- Peptide tolerance must be specified.\n'
        
        # check MSMS tolerance
        if config.mascot['common']['searchType'] in ('mis', 'sq'):
            if config.mascot[form]['msmsTol']:
                if config.mascot[form]['msmsTol'] < 0:
                    errors += '- MS/MS tolerance cannot be negative.\n'
                elif config.mascot[form]['msmsTol'] > 10 and config.mascot[form]['msmsTolUnits'] == 'Da':
                    errors += '- MS/MS tolerance must be less than 10 Da.\n'
                elif config.mascot[form]['msmsTol'] > 10000 and config.mascot[form]['msmsTolUnits'] == 'mmu':
                    errors += '- MS/MS tolerance must be less than 10 000 mmu.\n'
                elif config.mascot[form]['msmsTol'] > 10000 and config.mascot[form]['msmsTolUnits'] == 'ppm':
                    errors += '- MS/MS tolerance must be less than 10 000 ppm.\n'
                elif config.mascot[form]['msmsTol'] > 1 and config.mascot[form]['msmsTolUnits'] == '%':
                    errors += '- MS/MS tolerance must be less than 1%.\n'
            else:
                errors += '- MS/MS tolerance must be specified.\n'
        
        # check error tolerant
        if config.mascot['common']['searchType'] == 'mis':
            if config.mascot['mis']['decoy'] and config.mascot['mis']['errorTolerant']:
                errors += '- Cannot select both Error tolerant and Decoy checkboxes.\n'
            if config.mascot['mis']['errorTolerant'] and config.mascot['mis']['quantitation'] != 'None':
                errors += '- Cannot combine Error tolerant with Quantitation.\n'
            if config.mascot['mis']['errorTolerant'] and config.mascot['mis']['enzyme'] == 'None':
                errors += '- Can only combine Error tolerant with a fully-specific enzyme.\n'
        
        # check query
        if not self.paramQuery_value.GetValue():
            errors += '- Query is empty.\n'
        
        # show warning if errors
        if errors:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="You have the following errors in the search form.", message=errors)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        else:
            return True
    # ----
    
    
    def updateServerParams(self):
        """Get parameters from the server and update form."""
        
        # check processing
        if self.processing:
            return
        
        # get server params
        name = self.server_choice.GetStringSelection()
        if name in libs.mascot:
            config.mascot['common']['server'] = name
        else:
            wx.Bell()
            self.currentConnection = False
            self.search_butt.Enable(False)
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.search_butt.Enable(False)
        
        # get params from server
        self.processing = threading.Thread(target=self.getServerParams)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # hide processing gauge
        self.onProcessing(False)
        
        # update form fields
        if self.currentParams:
            self.updateForm()
            self.currentConnection = True
            self.search_butt.Enable(True)
        else:
            self.currentConnection = False
            self.search_butt.Enable(False)
            wx.Bell()
            title = 'Connection failed.'
            message = 'Selected Mascot server is not responding. Check your internet\nconnection or the server settings.'
            buttons = [(wx.ID_CANCEL, "Close", -1, False, 15), (wx.ID_OK, "Retry", -1, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
                self.updateServerParams()
            else:
                dlg.Destroy()
    # ----
    
    
    def updateForm(self):
        """Get params from selected server and update items."""
        
        # update databases
        self.paramPMFDatabase_choice.Clear()
        self.paramMISDatabase_choice.Clear()
        self.paramSQDatabase_choice.Clear()
        
        for item in self.currentParams['DB']:
            self.paramPMFDatabase_choice.Append(item)
            self.paramMISDatabase_choice.Append(item)
            self.paramSQDatabase_choice.Append(item)
            
        if config.mascot['pmf']['database'] in self.currentParams['DB']:
            self.paramPMFDatabase_choice.Select(self.currentParams['DB'].index(config.mascot['pmf']['database']))
        if config.mascot['mis']['database'] in self.currentParams['DB']:
            self.paramMISDatabase_choice.Select(self.currentParams['DB'].index(config.mascot['mis']['database']))
        if config.mascot['sq']['database'] in self.currentParams['DB']:
            self.paramSQDatabase_choice.Select(self.currentParams['DB'].index(config.mascot['sq']['database']))
        
        # update taxonomy
        self.paramPMFTaxonomy_choice.Clear()
        self.paramMISTaxonomy_choice.Clear()
        self.paramSQTaxonomy_choice.Clear()
        
        for item in self.currentParams['TAXONOMY']:
            self.paramPMFTaxonomy_choice.Append(item)
            self.paramMISTaxonomy_choice.Append(item)
            self.paramSQTaxonomy_choice.Append(item)
            
        if config.mascot['pmf']['taxonomy'] in self.currentParams['TAXONOMY']:
            self.paramPMFTaxonomy_choice.Select(self.currentParams['TAXONOMY'].index(config.mascot['pmf']['taxonomy']))
        if config.mascot['mis']['taxonomy'] in self.currentParams['TAXONOMY']:
            self.paramMISTaxonomy_choice.Select(self.currentParams['TAXONOMY'].index(config.mascot['mis']['taxonomy']))
        if config.mascot['sq']['taxonomy'] in self.currentParams['TAXONOMY']:
            self.paramSQTaxonomy_choice.Select(self.currentParams['TAXONOMY'].index(config.mascot['sq']['taxonomy']))
        
        # update enzymes
        self.paramPMFEnzyme_choice.Clear()
        self.paramMISEnzyme_choice.Clear()
        self.paramSQEnzyme_choice.Clear()
        
        for item in self.currentParams['CLE']:
            self.paramPMFEnzyme_choice.Append(item)
            self.paramMISEnzyme_choice.Append(item)
            self.paramSQEnzyme_choice.Append(item)
            
        if config.mascot['pmf']['enzyme'] in self.currentParams['CLE']:
            self.paramPMFEnzyme_choice.Select(self.currentParams['CLE'].index(config.mascot['pmf']['enzyme']))
        if config.mascot['pmf']['enzyme'] in self.currentParams['CLE']:
            self.paramSQEnzyme_choice.Select(self.currentParams['CLE'].index(config.mascot['pmf']['enzyme']))
        if config.mascot['pmf']['enzyme'] in self.currentParams['CLE']:
            self.paramMISEnzyme_choice.Select(self.currentParams['CLE'].index(config.mascot['pmf']['enzyme']))
        
        # update instrument
        self.paramMISInstrument_choice.Clear()
        self.paramSQInstrument_choice.Clear()
        
        for item in self.currentParams['INSTRUMENT']:
            self.paramMISInstrument_choice.Append(item)
            self.paramSQInstrument_choice.Append(item)
            
        if config.mascot['mis']['instrument'] in self.currentParams['INSTRUMENT']:
            self.paramMISInstrument_choice.Select(self.currentParams['INSTRUMENT'].index(config.mascot['mis']['instrument']))
        if config.mascot['sq']['instrument'] in self.currentParams['INSTRUMENT']:
            self.paramSQInstrument_choice.Select(self.currentParams['INSTRUMENT'].index(config.mascot['sq']['instrument']))
        
        # update quantifications
        self.paramMISQuantitation_choice.Clear()
        self.paramSQQuantitation_choice.Clear()
        
        for item in self.currentParams['QUANTITATION']:
            self.paramMISQuantitation_choice.Append(item)
            self.paramSQQuantitation_choice.Append(item)
            
        if config.mascot['mis']['quantitation'] in self.currentParams['QUANTITATION']:
            self.paramMISQuantitation_choice.Select(self.currentParams['QUANTITATION'].index(config.mascot['mis']['quantitation']))
        if config.mascot['sq']['quantitation'] in self.currentParams['QUANTITATION']:
            self.paramSQQuantitation_choice.Select(self.currentParams['QUANTITATION'].index(config.mascot['sq']['quantitation']))
        
        # update modifications
        self.updateModification()
    # ----
    
    
    def updateModification(self, tool=None):
        """Update modifications items."""
        
        # update PMF
        if not tool or tool=='pmf':
            self.paramPMFFixedMods_listbox.Clear()
            self.paramPMFVariableMods_listbox.Clear()
            
            modifications = self.currentParams['MODS'][:]
            if config.mascot['pmf']['hiddenMods']:
                modifications += self.currentParams['HIDDEN_MODS'][:]
                modifications.sort()
            
            for item in modifications:
                self.paramPMFFixedMods_listbox.Append(item)
                self.paramPMFVariableMods_listbox.Append(item)
            
            for item in config.mascot['pmf']['fixedMods']:
                if item in modifications:
                    self.paramPMFFixedMods_listbox.Select(modifications.index(item))
            for item in config.mascot['pmf']['variableMods']:
                if item in modifications:
                    self.paramPMFVariableMods_listbox.Select(modifications.index(item))
        
        # update MIS
        if not tool or tool=='mis':
            self.paramMISVariableMods_listbox.Clear()
            self.paramMISFixedMods_listbox.Clear()
            
            modifications = self.currentParams['MODS'][:]
            if config.mascot['mis']['hiddenMods']:
                modifications += self.currentParams['HIDDEN_MODS'][:]
                modifications.sort()
            
            for item in modifications:
                self.paramMISFixedMods_listbox.Append(item)
                self.paramMISVariableMods_listbox.Append(item)
            
            for item in config.mascot['mis']['fixedMods']:
                if item in modifications:
                    self.paramMISFixedMods_listbox.Select(modifications.index(item))
            for item in config.mascot['mis']['variableMods']:
                if item in modifications:
                    self.paramMISVariableMods_listbox.Select(modifications.index(item))
        
        # update SQ
        if not tool or tool=='sq':
            self.paramSQVariableMods_listbox.Clear()
            self.paramSQFixedMods_listbox.Clear()
            
            modifications = self.currentParams['MODS'][:]
            if config.mascot['sq']['hiddenMods']:
                modifications += self.currentParams['HIDDEN_MODS'][:]
                modifications.sort()
            
            for item in modifications:
                self.paramSQFixedMods_listbox.Append(item)
                self.paramSQVariableMods_listbox.Append(item)
            
            for item in config.mascot['sq']['fixedMods']:
                if item in modifications:
                    self.paramSQFixedMods_listbox.Select(modifications.index(item))
            for item in config.mascot['sq']['variableMods']:
                if item in modifications:
                    self.paramSQVariableMods_listbox.Select(modifications.index(item))
        
        # update modifications count
        self.onModificationSelected()
    # ----
    
    
    def makeMGFQuery(self):
        """Make Mascot query."""
        
        form = config.mascot['common']['searchType']
        
        # common params
        query = ''
        query += 'SEARCH=%s\n' % (form.upper())
        query += 'FORMVER=1.01\n'
        query += 'REPTYPE=Peptide\n'
        query += 'REPORT=%s\n' % (config.mascot[form]['report'])
        query += 'PEAK=AUTO\n'
        query += 'FORMAT=Mascot generic\n'
        
        # title and user
        query += 'COM=%s\n' % (config.mascot['common']['title'])
        query += 'USERNAME=%s\n' % (config.mascot['common']['userName'])
        query += 'USEREMAIL=%s\n' % (config.mascot['common']['userEmail'])
        
        # taxonomy
        query += 'DB=%s\n' % (config.mascot[form]['database'])
        query += 'TAXONOMY=%s\n' % (config.mascot[form]['taxonomy'])
        query += 'CLE=%s\n' % (config.mascot[form]['enzyme'])
        query += 'PFA=%s\n' % (config.mascot[form]['miscleavages'])
        query += 'DECOY=%s\n' % (config.mascot[form]['decoy'])
        
        # fixed modifications
        query += 'MODS='
        for mod in config.mascot[form]['fixedMods']:
            query += '%s,' % (mod)
        query += '\n'
        
        # variable modifications
        query += 'IT_MODS='
        for mod in config.mascot[form]['variableMods']:
            query += '%s,' % (mod)
        query += '\n'
        
        # PMF params
        if config.mascot['common']['searchType'] == 'pmf':
            query += 'SEG=%s\n' % (config.mascot['pmf']['proteinMass'])
            query += 'TOL=%s\n' % (config.mascot['pmf']['peptideTol'])
            query += 'TOLU=%s\n' % (config.mascot['pmf']['peptideTolUnits'])
            query += 'MASS=%s\n' % (config.mascot['pmf']['massType'])
            query += 'CHARGE=%s\n' % (config.mascot['pmf']['charge'])
            
            # add peaklist
            query += self.paramQuery_value.GetValue()
        
        # MIS params
        elif config.mascot['common']['searchType'] == 'mis':
            query += 'PRECURSOR=%s\n' % (config.mascot['mis']['peptideMass'])
            query += 'TOL=%s\n' % (config.mascot['mis']['peptideTol'])
            query += 'TOLU=%s\n' % (config.mascot['mis']['peptideTolUnits'])
            query += 'ITOL=%s\n' % (config.mascot['mis']['msmsTol'])
            query += 'ITOLU=%s\n' % (config.mascot['mis']['msmsTolUnits'])
            query += 'MASS=%s\n' % (config.mascot['mis']['massType'])
            query += 'CHARGE=%s\n' % (config.mascot['mis']['charge'])
            query += 'INSTRUMENT=%s\n' % (config.mascot['mis']['instrument'])
            query += 'QUANTITATION=%s\n' % (config.mascot['mis']['quantitation'])
            query += 'ERRORTOLERANT=%s\n' % (config.mascot['mis']['errorTolerant'])
            
            # add peaklist
            query += 'BEGIN IONS\n'
            query += 'PEPMASS=%s\n' % (config.mascot['mis']['peptideMass'])
            query += self.paramQuery_value.GetValue()
            query += '\nEND IONS\n'
        
        # SQ params
        elif config.mascot['common']['searchType'] == 'sq':
            query += 'TOL=%s\n' % (config.mascot['sq']['peptideTol'])
            query += 'TOLU=%s\n' % (config.mascot['sq']['peptideTolUnits'])
            query += 'ITOL=%s\n' % (config.mascot['sq']['msmsTol'])
            query += 'ITOLU=%s\n' % (config.mascot['sq']['msmsTolUnits'])
            query += 'MASS=%s\n' % (config.mascot['sq']['massType'])
            query += 'CHARGE=%s\n' % (config.mascot['sq']['charge'])
            query += 'INSTRUMENT=%s\n' % (config.mascot['sq']['instrument'])
            query += 'QUANTITATION=%s\n' % (config.mascot['sq']['quantitation'])
            
            # add peaklist
            query += self.paramQuery_value.GetValue()
        
        return query
    # ----
    
    
    def makeSearchHTML(self):
        """Format data to mascot html."""
        
        # make query
        query = self.makeMGFQuery()
        
        # make search path
        name = config.mascot['common']['server']
        script = libs.mascot[name]['protocol']+'://'+libs.mascot[name]['host']+libs.mascot[name]['path']+libs.mascot[name]['search']+'?1'
        
        # make html page
        buff = '<?xml version="1.0" encoding="utf-8"?>\n'
        buff += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        buff += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        buff += '<head>\n'
        buff += '  <title>mMass - Mascot Search</title>\n'
        buff += '  <style type="text/css">\n'
        buff += '    <!--\n'
        buff += '      body{margin: auto; font-size: .8em; font-family: Arial, Verdana, Geneva, Helvetica, sans-serif; text-align: center; text-shadow: 1px 1px 1px #fff; color: #000; background-color: #f5f4f2;}\n'
        buff += '      h1{margin: 0; padding: .7em; font-size: 1.4em; font-weight: bold; text-align: center; color: #999; border-bottom: 1px solid #ddd; }\n'
        buff += '      #data{display:none;}\n'
        buff += '      #info{ width: 350px; margin: auto; margin-top: 5em; background-color: #edece9; border-radius: 7px; border: 2px solid #fff; box-shadow: 0 0 5px rgba(0,0,0,.5);}\n'
        buff += '      #sending{font-weight: bold}\n'
        buff += '      #wait{font-weight: bold; display: none;}\n'
        buff += '      #note{font-size: .85em;}\n'
        buff += '      #button{padding: .5em 1em;}\n'
        buff += '    -->\n'
        buff += '  </style>\n'
        buff += '  <script type="text/javascript">\n'
        buff += '     function runsearch() {\n'
        buff += '       document.getElementById(\'note\').style.display = \'none\';\n'
        buff += '       document.getElementById(\'button\').style.display = \'none\';\n'
        buff += '       document.getElementById(\'wait\').style.display = \'block\';\n'
        buff += '       document.forms[0].submit();\n'
        buff += '       return true;\n'
        buff += '     }\n'
        buff += '  </script>\n'
        buff += '</head>\n\n'
        
        buff += '<body onload="runsearch()">\n'
        buff += '  <form action="%s" id="mainSearch" enctype="multipart/form-data" method="post">\n' % (script)
        buff += '    <div style="display:none;">\n\n'
        buff += '      <textarea name="QUE" rows="6" cols="30">\n%s\n</textarea>\n\n' % (query)
        buff += '    </div>\n\n'
        
        buff += '    <div id="info">\n'
        buff += '      <h1>mMass - Mascot Search</h1>\n'
        buff += '      <p id="sending">Sending data to %s &hellip;</p>\n' % (name)
        buff += '      <p id="wait">Please wait &hellip;</p>\n'
        buff += '      <p id="note">Press the <strong>Search</strong> button if data was not sent automatically.</p>\n'
        buff += '      <p id="button"><input type="submit" value="Search" /></p>\n'
        buff += '    </div>\n\n'
        
        buff += '  </form>\n'
        buff += '</body>\n'
        buff += '</html>\n'
        
        return buff
    # ----
    
    

