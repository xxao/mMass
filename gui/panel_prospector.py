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
import webbrowser
import tempfile
import os.path

# load modules
from ids import *
import mwx
import images
import config
import mspy
import doc


# FLOATING PANEL WITH PROSPECTOR SEARCH TOOLS
# -------------------------------------------

class panelProspector(wx.MiniFrame):
    """ProteinProspector search tools."""
    
    def __init__(self, parent, tool=config.prospector['common']['searchType']):
        wx.MiniFrame.__init__(self, parent, -1, 'Protein Prospector', size=(300, -1), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.currentTool = tool
        self.currentDocument = None
        self.currentParams = None
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # select tool
        self.onToolSelected(tool=self.currentTool)
        
        # update form params
        self.updateForm()
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        msFit = self.makeMSFitPanel()
        msTag = self.makeMSTagPanel()
        query = self.makeQueryPanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(msFit, 1, wx.EXPAND, 0)
        self.mainSizer.Add(msTag, 1, wx.EXPAND, 0)
        self.mainSizer.Add(query, 1, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        self.msFit_butt = wx.BitmapButton(panel, ID_prospectorMSFit, images.lib['prospectorMSFitOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.msFit_butt.SetToolTip(wx.ToolTip("MS-Fit Tool"))
        self.msFit_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.msTag_butt = wx.BitmapButton(panel, ID_prospectorMSTag, images.lib['prospectorMSTagOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.msTag_butt.SetToolTip(wx.ToolTip("MS-Tag Tool"))
        self.msTag_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.query_butt = wx.BitmapButton(panel, ID_prospectorQuery, images.lib['prospectorQueryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.query_butt.SetToolTip(wx.ToolTip("Peak list"))
        self.query_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.search_butt = wx.Button(panel, -1, "Search", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.search_butt.Bind(wx.EVT_BUTTON, self.onSearch)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.msFit_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.msTag_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.query_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
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
    
    
    def makeMSFitPanel(self):
        """Make controls for MS-Fit search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramMSFitSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramMSFitTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        # make sequence elements
        paramMSFitTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramMSFitTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramMSFitDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramMSFitDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramMSFitEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramMSFitEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramMSFitMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramMSFitMiscleavages_choice = wx.Choice(panel, -1, choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramMSFitMiscleavages_choice.SetStringSelection(str(config.prospector['msfit']['miscleavages']))
        
        # make modifications elements
        self.paramMSFitFixedMods_label = wx.StaticText(panel, -1, "Fixed modifications:")
        self.paramMSFitFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMSFitFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMSFitFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramMSFitVariableMods_label = wx.StaticText(panel, -1, "Variable modifications:")
        self.paramMSFitVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMSFitVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMSFitVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        # make masses elements
        paramMSFitProteinMass_label = wx.StaticText(panel, -1, "Protein mass:")
        self.paramMSFitProteinMassLow_value = wx.TextCtrl(panel, -1, "0", size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramMSFitProteinMassHigh_value = wx.TextCtrl(panel, -1, "300", size=(50, -1), validator=mwx.validator('floatPos'))
        paramMSFitProteinMass_dash = wx.StaticText(panel, -1, "-")
        paramMSFitProteinMassUnits_label = wx.StaticText(panel, -1, "kDa")
        
        paramProteinPI_label = wx.StaticText(panel, -1, "Protein pI:")
        self.paramMSFitProteinPILow_value = wx.TextCtrl(panel, -1, "0", size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramMSFitProteinPIHigh_value = wx.TextCtrl(panel, -1, "14", size=(50, -1), validator=mwx.validator('floatPos'))
        paramMSFitProteinPI_dash = wx.StaticText(panel, -1, "-")
        
        paramMSFitPeptideTol_label = wx.StaticText(panel, -1, "Peptide tolerance:")
        self.paramMSFitPeptideTol_value = wx.TextCtrl(panel, -1, str(config.prospector['msfit']['peptideTol']), size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramMSFitPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMSFitPeptideTolUnits_choice.SetStringSelection(config.prospector['msfit']['peptideTolUnits'])
        
        paramMSFitMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramMSFitMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramMSFitMassType_choice.SetStringSelection(config.prospector['msfit']['massType'])
        
        paramMSFitInstrument_label = wx.StaticText(panel, -1, "Instrument:")
        self.paramMSFitInstrument_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        # results elements
        paramMSFitMinMatches_label = wx.StaticText(panel, -1, "Min. matches required:")
        self.paramMSFitMinMatches_choice = wx.Choice(panel, -1, choices=['1','2','3','4','5','6','7','8','9','10'], size=(60, mwx.CHOICE_HEIGHT))
        self.paramMSFitMinMatches_choice.SetStringSelection(str(config.prospector['msfit']['minMatches']))
        
        paramMSFitMaxMods_label = wx.StaticText(panel, -1, "Max. mods:")
        self.paramMSFitMaxMods_choice = wx.Choice(panel, -1, choices=['1','2','3','4'], size=(60, mwx.CHOICE_HEIGHT))
        self.paramMSFitMaxMods_choice.SetStringSelection(str(config.prospector['msfit']['maxMods']))
        
        paramMSFitReport_label = wx.StaticText(panel, -1, "Report:")
        self.paramMSFitReport_choice = wx.Choice(panel, -1, choices=['5','10','20','30','50'], size=(60, mwx.CHOICE_HEIGHT))
        self.paramMSFitReport_choice.SetStringSelection(str(config.prospector['msfit']['report']))
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramMSFitSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramMSFitTitle_value, (0,1), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramMSFitTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSFitTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSFitDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSFitDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSFitEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSFitEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSFitMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSFitMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramMSFitFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMSFitVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMSFitFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramMSFitVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramMSFitProteinMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitProteinMassLow_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSFitProteinMass_dash, (0,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitProteinMassHigh_value, (0,3), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSFitProteinMassUnits_label, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramProteinPI_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitProteinPILow_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSFitProteinPI_dash, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitProteinPIHigh_value, (1,3), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSFitPeptideTol_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitPeptideTol_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitPeptideTolUnits_choice, (2,3), (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        
        massesGrid.Add(paramMSFitMassType_label, (0,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitMassType_choice, (0,6), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSFitInstrument_label, (1,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSFitInstrument_choice, (1,6), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(4)
        
        resultsGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        resultsGrid.Add(paramMSFitMaxMods_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramMSFitMaxMods_choice, (0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(paramMSFitMinMatches_label, (0,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramMSFitMinMatches_choice, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(paramMSFitReport_label, (0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramMSFitReport_choice, (0,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.AddGrowableCol(2)
        resultsGrid.AddGrowableCol(4)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(infoGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(sequenceGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(modsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(massesGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(resultsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeMSTagPanel(self):
        """Make controls for MS-Tag search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramMSTagSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramMSTagTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        # make sequence elements
        paramMSTagTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramMSTagTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramMSTagDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramMSTagDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramMSTagEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramMSTagEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramMSTagMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramMSTagMiscleavages_choice = wx.Choice(panel, -1, choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramMSTagMiscleavages_choice.SetStringSelection(str(config.prospector['mstag']['miscleavages']))
        
        # make modifications elements
        self.paramMSTagFixedMods_label = wx.StaticText(panel, -1, "Fixed modifications:")
        self.paramMSTagFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMSTagFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMSTagFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramMSTagVariableMods_label = wx.StaticText(panel, -1, "Variable modifications:")
        self.paramMSTagVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramMSTagVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramMSTagVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        # make masses elements
        paramMSTagPeptideMass_label = wx.StaticText(panel, -1, "Precursor m/z:")
        self.paramMSTagPeptideMass_value = wx.TextCtrl(panel, -1, "", size=(145, -1), validator=mwx.validator('float'))
        
        paramMSTagPeptideCharge_label = wx.StaticText(panel, -1, "Precursor charge:")
        self.paramMSTagPeptideCharge_choice = wx.Choice(panel, -1, choices=['Automatic', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], size=(145, mwx.CHOICE_HEIGHT))
        self.paramMSTagPeptideCharge_choice.SetStringSelection(str(config.prospector['mstag']['peptideCharge']))
        
        paramMSTagPeptideTol_label = wx.StaticText(panel, -1, "Precursor tolerance:")
        self.paramMSTagPeptideTol_value = wx.TextCtrl(panel, -1, str(config.prospector['mstag']['peptideTol']), size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramMSTagPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMSTagPeptideTolUnits_choice.SetStringSelection(config.prospector['mstag']['peptideTolUnits'])
        
        paramMSTagMSMSTol_label = wx.StaticText(panel, -1, "MS/MS tolerance:")
        self.paramMSTagMSMSTol_value = wx.TextCtrl(panel, -1, str(config.prospector['mstag']['msmsTol']), size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramMSTagMSMSTolUnits_choice = wx.Choice(panel, -1, choices=['Da','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramMSTagMSMSTolUnits_choice.SetStringSelection(config.prospector['mstag']['msmsTolUnits'])
        
        paramMSTagMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramMSTagMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramMSTagMassType_choice.SetStringSelection(config.prospector['mstag']['massType'])
        
        paramMSTagInstrument_label = wx.StaticText(panel, -1, "Instrument:")
        self.paramMSTagInstrument_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        # results elements
        paramMSTagMaxMods_label = wx.StaticText(panel, -1, "Max. mods:")
        self.paramMSTagMaxMods_choice = wx.Choice(panel, -1, choices=['1','2','3','4'], size=(60, mwx.CHOICE_HEIGHT))
        self.paramMSTagMaxMods_choice.SetStringSelection(str(config.prospector['mstag']['maxMods']))
        
        paramMSTagReport_label = wx.StaticText(panel, -1, "Report:")
        self.paramMSTagReport_choice = wx.Choice(panel, -1, choices=['5','10','20','30','50'], size=(60, mwx.CHOICE_HEIGHT))
        self.paramMSTagReport_choice.SetStringSelection(str(config.prospector['mstag']['report']))
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramMSTagSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramMSTagTitle_value, (0,1), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramMSTagTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSTagTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSTagDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSTagDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSTagEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSTagEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramMSTagMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMSTagMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramMSTagFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMSTagVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramMSTagFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramMSTagVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramMSTagPeptideMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagPeptideMass_value, (0,1), (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSTagPeptideCharge_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagPeptideCharge_choice, (1,1), (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSTagPeptideTol_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagPeptideTol_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        massesGrid.Add(self.paramMSTagPeptideTolUnits_choice, (2,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        massesGrid.Add(paramMSTagMSMSTol_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagMSMSTol_value, (3,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        massesGrid.Add(self.paramMSTagMSMSTolUnits_choice, (3,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        
        massesGrid.Add(paramMSTagMassType_label, (0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagMassType_choice, (0,5), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMSTagInstrument_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMSTagInstrument_choice, (1,5), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(1)
        massesGrid.AddGrowableCol(3)
        
        resultsGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        resultsGrid.Add(paramMSTagMaxMods_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramMSTagMaxMods_choice, (0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(paramMSTagReport_label, (0,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramMSTagReport_choice, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.AddGrowableCol(2)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(infoGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(sequenceGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(modsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(massesGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(resultsGrid, 0, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
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
        self.filterAnnotations_check.SetValue(config.prospector['common']['filterAnnotations'])
        self.filterAnnotations_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterMatches_check = wx.CheckBox(ctrlPanel, -1, "Matched")
        self.filterMatches_check.SetFont(wx.SMALL_FONT)
        self.filterMatches_check.SetValue(config.prospector['common']['filterMatches'])
        self.filterMatches_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnselected_check = wx.CheckBox(ctrlPanel, -1, "Unselected")
        self.filterUnselected_check.SetFont(wx.SMALL_FONT)
        self.filterUnselected_check.SetValue(config.prospector['common']['filterUnselected'])
        self.filterUnselected_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterIsotopes_check = wx.CheckBox(ctrlPanel, -1, "Isotopes")
        self.filterIsotopes_check.SetFont(wx.SMALL_FONT)
        self.filterIsotopes_check.SetValue(config.prospector['common']['filterIsotopes'])
        self.filterIsotopes_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnknown_check = wx.CheckBox(ctrlPanel, -1, "Unknown")
        self.filterUnknown_check.SetFont(wx.SMALL_FONT)
        self.filterUnknown_check.SetValue(config.prospector['common']['filterUnknown'])
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
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # delete temporary file
        try:
            path = os.path.join(tempfile.gettempdir(), 'mmass_prospector_search.html')
            os.unlink(path)
        except:
            pass
        
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'msfit'
            if evt and evt.GetId() == ID_prospectorMSFit:
                tool = 'msfit'
            elif evt and evt.GetId() == ID_prospectorMSTag:
                tool = 'mstag'
            elif evt and evt.GetId() == ID_prospectorQuery:
                tool = 'query'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # set icons off
        self.msFit_butt.SetBitmapLabel(images.lib['prospectorMSFitOff'])
        self.msTag_butt.SetBitmapLabel(images.lib['prospectorMSTagOff'])
        self.query_butt.SetBitmapLabel(images.lib['prospectorQueryOff'])
        
        # set panel
        if tool == 'msfit':
            config.prospector['common']['searchType'] = 'msfit'
            self.SetTitle("Protein Prospector - MS-Fit")
            self.mainSizer.Show(1)
            self.msFit_butt.SetBitmapLabel(images.lib['prospectorMSFitOn'])
        
        elif tool == 'mstag':
            config.prospector['common']['searchType'] = 'mstag'
            self.SetTitle("Protein Prospector - MS-Tag")
            self.mainSizer.Show(2)
            self.msTag_butt.SetBitmapLabel(images.lib['prospectorMSTagOn'])
        
        elif tool == 'query':
            self.SetTitle("Protein Prospector - Peak List")
            self.mainSizer.Show(3)
            self.query_butt.SetBitmapLabel(images.lib['prospectorQueryOn'])
        
        # enable search button
        if tool in ('msfit', 'mstag'):
            self.search_butt.Enable(True)
        else:
            self.search_butt.Enable(False)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onModificationSelected(self, evt=None):
        """Count and show number of selected modifications."""
        
        if (self.paramMSFitFixedMods_label and self.paramMSFitVariableMods_label):
            label = 'Fixed modifications: (%d)' % len(self.paramMSFitFixedMods_listbox.GetSelections())
            self.paramMSFitFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramMSFitVariableMods_listbox.GetSelections())
            self.paramMSFitVariableMods_label.SetLabel(label)
        
        if (self.paramMSTagFixedMods_label and self.paramMSTagVariableMods_label):
            label = 'Fixed modifications: (%d)' % len(self.paramMSTagFixedMods_listbox.GetSelections())
            self.paramMSTagFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramMSTagVariableMods_listbox.GetSelections())
            self.paramMSTagVariableMods_label.SetLabel(label)
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
        """Make query and send data to ProFound."""
        
        # get params
        if not self.getParams():
            return
        
        # check params
        if not self.checkParams():
            return
        
        # make temporary search file
        htmlData = self.makeSearchHTML()
        try:
            path = os.path.join(tempfile.gettempdir(), 'mmass_prospector_search.html')
            htmlFile = file(path, 'w')
            htmlFile.write(htmlData.encode("utf-8"))
            htmlFile.close()
            webbrowser.open('file://'+path, autoraise=1)
        except:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Unable to send data to ProFound server.', message='Unknown error occured while creating the search page.')
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set current document
        self.currentDocument = document
        
        # check document
        if not document:
            self.paramMSFitTitle_value.SetValue('')
            self.paramMSTagTitle_value.SetValue('')
            self.paramQuery_value.SetValue('')
            return
        
        # change search title
        self.paramMSFitTitle_value.SetValue(document.title)
        self.paramMSTagTitle_value.SetValue(document.title)
        
        # change precursor mass
        if document.spectrum.precursorMZ:
            self.paramMSTagPeptideMass_value.SetValue(str(document.spectrum.precursorMZ))
        else:
            self.paramMSTagPeptideMass_value.SetValue('')
        
        # get peaklist
        self.onGetPeaklist()
    # ----
    
    
    def getParams(self):
        """Get dialog params."""
        
        try:
            
            # MS-Fit params
            if config.prospector['common']['searchType'] == 'msfit':
                
                config.prospector['msfit']['title'] = self.paramMSFitTitle_value.GetValue()
                config.prospector['msfit']['database'] = self.paramMSFitDatabase_choice.GetStringSelection()
                config.prospector['msfit']['taxonomy'] = self.paramMSFitTaxonomy_choice.GetStringSelection()
                config.prospector['msfit']['enzyme'] = self.paramMSFitEnzyme_choice.GetStringSelection()
                config.prospector['msfit']['miscleavages'] = self.paramMSFitMiscleavages_choice.GetStringSelection()
                config.prospector['msfit']['proteinMassLow'] = self.paramMSFitProteinMassLow_value.GetValue()
                config.prospector['msfit']['proteinMassHigh'] = self.paramMSFitProteinMassHigh_value.GetValue()
                config.prospector['msfit']['proteinPILow'] = self.paramMSFitProteinPILow_value.GetValue()
                config.prospector['msfit']['proteinPIHigh'] = self.paramMSFitProteinPIHigh_value.GetValue()
                config.prospector['msfit']['peptideTol'] = self.paramMSFitPeptideTol_value.GetValue()
                config.prospector['msfit']['peptideTolUnits'] = self.paramMSFitPeptideTolUnits_choice.GetStringSelection()
                config.prospector['msfit']['massType'] = self.paramMSFitMassType_choice.GetStringSelection()
                config.prospector['msfit']['instrument'] = self.paramMSFitInstrument_choice.GetStringSelection()
                config.prospector['msfit']['minMatches'] = self.paramMSFitMinMatches_choice.GetStringSelection()
                config.prospector['msfit']['maxMods'] = self.paramMSFitMaxMods_choice.GetStringSelection()
                config.prospector['msfit']['report'] = self.paramMSFitReport_choice.GetStringSelection()
                
                config.prospector['msfit']['fixedMods'] = []
                fixedMods = self.paramMSFitFixedMods_listbox.GetStrings()
                for item in self.paramMSFitFixedMods_listbox.GetSelections():
                    config.prospector['msfit']['fixedMods'].append(fixedMods[item])
                
                config.prospector['msfit']['variableMods'] = []
                variableMods = self.paramMSFitVariableMods_listbox.GetStrings()
                for item in self.paramMSFitVariableMods_listbox.GetSelections():
                    config.prospector['msfit']['variableMods'].append(variableMods[item])
                
                if config.prospector['msfit']['proteinMassLow']:
                    config.prospector['msfit']['proteinMassLow'] = float(config.prospector['msfit']['proteinMassLow'])
                
                if config.prospector['msfit']['proteinMassHigh']:
                    config.prospector['msfit']['proteinMassHigh'] = float(config.prospector['msfit']['proteinMassHigh'])
                
                if config.prospector['msfit']['proteinPILow']:
                    config.prospector['msfit']['proteinPILow'] = float(config.prospector['msfit']['proteinPILow'])
                
                if config.prospector['msfit']['proteinPIHigh']:
                    config.prospector['msfit']['proteinPIHigh'] = float(config.prospector['msfit']['proteinPIHigh'])
                
                if config.prospector['msfit']['peptideTol']:
                    config.prospector['msfit']['peptideTol'] = float(config.prospector['msfit']['peptideTol'])
                
                return True
            
            # MS-Tag params
            if config.prospector['common']['searchType'] == 'mstag':
                
                config.prospector['mstag']['title'] = self.paramMSTagTitle_value.GetValue()
                config.prospector['mstag']['database'] = self.paramMSTagDatabase_choice.GetStringSelection()
                config.prospector['mstag']['taxonomy'] = self.paramMSTagTaxonomy_choice.GetStringSelection()
                config.prospector['mstag']['enzyme'] = self.paramMSTagEnzyme_choice.GetStringSelection()
                config.prospector['mstag']['miscleavages'] = self.paramMSTagMiscleavages_choice.GetStringSelection()
                config.prospector['mstag']['peptideMass'] = self.paramMSTagPeptideMass_value.GetValue()
                config.prospector['mstag']['peptideTol'] = self.paramMSTagPeptideTol_value.GetValue()
                config.prospector['mstag']['peptideTolUnits'] = self.paramMSTagPeptideTolUnits_choice.GetStringSelection()
                config.prospector['mstag']['msmsTol'] = self.paramMSTagMSMSTol_value.GetValue()
                config.prospector['mstag']['msmsTolUnits'] = self.paramMSTagMSMSTolUnits_choice.GetStringSelection()
                config.prospector['mstag']['massType'] = self.paramMSTagMassType_choice.GetStringSelection()
                config.prospector['mstag']['peptideCharge'] = self.paramMSTagPeptideCharge_choice.GetStringSelection()
                config.prospector['mstag']['instrument'] = self.paramMSTagInstrument_choice.GetStringSelection()
                config.prospector['mstag']['maxMods'] = self.paramMSTagMaxMods_choice.GetStringSelection()
                config.prospector['mstag']['report'] = self.paramMSTagReport_choice.GetStringSelection()
                
                config.prospector['mstag']['fixedMods'] = []
                fixedMods = self.paramMSTagFixedMods_listbox.GetStrings()
                for item in self.paramMSTagFixedMods_listbox.GetSelections():
                    config.prospector['mstag']['fixedMods'].append(fixedMods[item])
                
                config.prospector['mstag']['variableMods'] = []
                variableMods = self.paramMSTagVariableMods_listbox.GetStrings()
                for item in self.paramMSTagVariableMods_listbox.GetSelections():
                    config.prospector['mstag']['variableMods'].append(variableMods[item])
                
                if config.prospector['mstag']['peptideMass']:
                    config.prospector['mstag']['peptideMass'] = float(config.prospector['mstag']['peptideMass'])
                
                if config.prospector['mstag']['peptideTol']:
                    config.prospector['mstag']['peptideTol'] = float(config.prospector['mstag']['peptideTol'])
                
                if config.prospector['mstag']['msmsTol']:
                    config.prospector['mstag']['msmsTol'] = float(config.prospector['mstag']['msmsTol'])
                
                return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def checkParams(self):
        """Check search parameters."""
        
        errors = ''
        form = config.prospector['common']['searchType']
        
        # check taxonomy and database
        if not config.prospector[form]['taxonomy']:
            errors += '- Taxonomy must be selected.\n'
        if not config.prospector[form]['database']:
            errors += '- Database must be selected.\n'
        if not config.prospector[form]['enzyme']:
            errors += '- Enzyme must be selected.\n'
        if not config.prospector[form]['instrument']:
            errors += '- Instrument must be selected.\n'
        
        # check variable modifications
        if len(config.prospector[form]['variableMods']) > 4:
            errors += '- Up to 4 variable modifications can be selected.\n'
        
        # check precursor and MS/MS
        if config.prospector['common']['searchType'] == 'msfit':
            if not config.prospector['msfit']['peptideTol']:
                errors += '- Peptide tolerance must be specified.\n'
        
        # check precursor and MS/MS
        if config.prospector['common']['searchType'] == 'mstag':
            if not config.prospector['mstag']['peptideMass']:
                errors += '- Precursor mass must be specified.\n'
            if not config.prospector['mstag']['peptideTol']:
                errors += '- Precursor mass tolerance must be specified.\n'
            if not config.prospector['mstag']['msmsTol']:
                errors += '- MS/MS tolerance must be specified.\n'
        
        # check query
        if not self.paramQuery_value.GetValue():
            errors += '- Peak list is empty.\n'
        
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
    
    
    def updateForm(self):
        """Update items."""
        
        # default server params
        self.currentParams = {
            'databases':[
                'NCBInr',
                'SwissProt',
                'UniProtKB',
            ],
            'taxonomy':[
                'All',
                'HUMAN MOUSE',
                'HUMAN RODENT',
                'MODEL PLANTS',
                'RODENT',
                'ROACH LOCUST BEETLE',
                'MICROORGANISMS',
                'ARABIDOPSIS',
                'ARABIDOPSIS THALIANA',
                'ARCHAEOGLOBUS FULGIDUS',
                'BACILLUS SUBTILIS',
                'BACULOVIRIDAE',
                'BORRELIA BURGDORFERI',
                'BOS TAURUS',
                'BOTHROPS INSULARIS',
                'BRASSICA',
                'BRUGIA MALAYI',
                'CAENORHABDITIS ELEGANS',
                'CANDIDA',
                'CANIS FAMILIARIS',
                'CAPRA HIRCUS',
                'CERCOPITHECUS AETHIOPS',
                'CHLAMYDIA TRACHOMATIS',
                'CHLAMYDOPHILA PNEUMONIAE',
                'DANIO RERIO',
                'DICTYOSTELIUM DISCOIDEUM',
                'DROSOPHILA MELANOGASTER',
                'EQUUS CABALLUS',
                'ESCHERICHIA COLI',
                'FELIS CATUS',
                'FRANCISELLA TULARENSIS',
                'GALLUS GALLUS',
                'GLYCINE MAX',
                'GREEN PLANTS',
                'GORILLA GORILLA',
                'HAEMOPHILUS',
                'HAEMOPHILUS INFLUENZAE',
                'HELICOBACTER PYLORI',
                'HOMO SAPIENS',
                'HORDEUM',
                'HUMAN ADENOVIRUS 5',
                'MACACA',
                'MAMMALS',
                'METHANOCOCCUS JANNASCHII',
                'MUS MUSCULUS',
                'MYCOBACTERIUM',
                'MYCOPLASMA',
                'NATRIALBA MAGADII',
                'NEISSERIA',
                'ORYCTOLAGUS CUNICULUS',
                'ORYZA',
                'ORYZA SATIVA',
                'OVIS ARIES',
                'PAN TROGLODYTES',
                'PSEUDOMONAS AERUGINOSA',
                'RATTUS NORVEGICUS',
                'SACCHAROMYCES',
                'SACCHAROMYCES CEREVISIAE',
                'SALMONELLA',
                'SCHIZOSACCHAROMYCES POMBE',
                'SECALE',
                'SHEWANELLA ONEIDENSIS',
                'SUS SCROFA',
                'SYNECHOCYSTIS',
                'TOXOPLASMA GONDII',
                'TREPONEMA PALLIDUM',
                'TRITICUM',
                'TRYPANOSOMA',
                'UNKNOWN',
                'UNREADABLE',
                'XENOPUS LAEVIS',
                'ZEA',
            ],
            'enzymes':[
                'Trypsin',
                'TrypsinPro',
                'SlymotrypsinFYWKR',
                'Chymotrypsin',
                'Chymotrypsin FYW',
                'ChymotrypsinFWYMEDLN',
                'V8 DE',
                'V8 E',
                'Lys-C',
                'Lys-C-Pro',
                'Lys-N',
                'Arg-C',
                'Asp-N',
                'Asp-C',
                'DE-N',
                'CNBr',
                'Pepsin(porcine gastric)',
                'Glu-C',
                'Tyr-C',
                'Thermolysin',
                'Elastase',
                'Full Protein',
                'Pro-C',
                'Pro-N',
                'Proteinase K',
                'Rhizopuspepsin',
                'Cys-N',
                'KR-N',
                'CNBr/Trypsin',
                'CNBr/V8 DE',
                'CNBr/V8 E',
                'CNBr/Lys-C',
                'CNBr/Asp-N',
                'CNBr/Asp-C',
                'CNBr/Arg-C',
                'CNBr/V8 E',
                'CNBr/Trypsin/V8 DE',
                'CNBr/Trypsin/V8 E',
                'CNBr/Arg-C/V8 E',
                'CNBr/Lys-C/V8 E',
                'Trypsin/Asp-N',
                'Trypsin/DE-N',
                'Trypsin/V8 DE',
                'Trypsin/V8 E',
                'Trypsin/Glu-C',
                'Chymotrypsin/Arg-C',
                'Lys-C/Trypsin',
                'Lys-C/V8 DE',
                'Lys-C/V8 E',
                'Lys-C/Asp-N',
                'Lys-C/DE-N',
                'Lys-C/Glu-C',
                'V8 DE/Chymotrypsin',
                'Arg-C/V8 E',
                'Glu-C/Asp-N',
                'DE-N/Cys-N',
                'Asp-N/Asp-C',
                'Asp-C/Cys-N',
                'Lys-C/Lys-N',
                'Trypsin/KR-N',
            ],
            'fixedMods':[
                'Acetohydrazide (C-term)',
                'Acetohydrazide (DE)',
                'Acetyl (K)',
                'Acetyl (N-term)',
                'Acetyl:2H(3) (K)',
                'Acetyl:2H(3) (N-term)',
                'Acetyl:2H(3)+Methyl (K)',
                'ADP-Ribosyl (CEKNSR)',
                'ADP-Ribosyl (E)',
                'ADP-Ribosyl (K)',
                'ADP-Ribosyl (R)',
                'Amidated (C-term)',
                'Amidated+iTRAQ8plex (C-term)',
                'Amino (Y)',
                'Ammonia-loss (K)',
                'Ammonia-loss (R)',
                'AMTzGalNAcGlcNAc (N)',
                'AMTzGalNAcGlcNAc (ST)',
                'APTA (C)',
                'Asn-&gt;Succinimide (N)',
                'Biotin (N-term)',
                'Carbamidomethyl (C)',
                'Carbamidomethyl (N-term)',
                'Carbamyl (K)',
                'Carbamyl (N-term)',
                'Carboxy (E)',
                'Carboxy (W)',
                'Carboxymethyl (C)',
                'Cation:Na (C-term)',
                'Cation:Na (DE)',
                'Cyano (C)',
                'Cys-&gt;Dha (C)',
                'Deamidated (N)',
                'Deamidated (Q)',
                'Dehydrated (C-term)',
                'Dehydrated (D)',
                'Dehydrated (ST)',
                'Dehydro (C)',
                'Delta:2H(6)C(3) (K)',
                'Delta:2H(6)C(3) (N-term)',
                'Delta:H(2)C(2) (N-term)',
                'Delta:H(2)C(3) (K)',
                'Delta:H(4)C(3)O(1) (C)',
                'Delta:H(4)C(3)O(1) (CHK)',
                'Delta:H(4)C(6) (K)',
                'Delta:H(6)C(3) (K)',
                'Delta:H(6)C(3) (N-term)',
                'Delta:H(6)C(6)O(1) (K)',
                'Delta:H(8)C(6)O(2) (K)',
                'Dethiomethyl (M)',
                'Didehydro (C)',
                'Dimethyl (N-term)',
                'Dioxidation (C)',
                'Dioxidation (M)',
                'Dioxidation (W)',
                'DTT_C (C)',
                'DTT_C:2H(6) (C)',
                'DTT_ST (ST)',
                'DTT_ST:2H(6) (ST)',
                'Ethanolyl (C)',
                'Formyl (K)',
                'Formyl (N-term)',
                'Formyl (ST)',
                'GirardT (N)',
                'GlyGly (C)',
                'GlyGly (N-term)',
                'GlyTyr (N-term)',
                'Guanidinyl (K)',
                'HexNAc (N)',
                'HexNAc (ST)',
                'HexNAc (Y)',
                'HexNAcHex (ST)',
                'HexNAcHexSA (ST)',
                'HexNAcHexSA2 (ST)',
                'HexNAcHexSAOx (ST)',
                'HexNACHExSAOxSAOx (ST)',
                'HexNACHexSASAOx (ST)',
                'HexNAcSA (ST)',
                'HexNAcSAOx (ST)',
                'Hydroxymethyl (CRWHKNQY)',
                'ICAT-C (C)',
                'ICAT-C:13C(9) (C)',
                'ICAT-D (C)',
                'ICAT-D:2H(8) (C)',
                'IDEnT (C)',
                'iTRAQ4plex (K)',
                'iTRAQ4plex (N-term)',
                'iTRAQ4plex (Y)',
                'iTRAQ8plex (K)',
                'iTRAQ8plex (N-term)',
                'iTRAQ8plex (Y)',
                'Label:13C(6) (K)',
                'Label:13C(6) (L)',
                'Label:13C(6) (R)',
                'Label:13C(6)15N(1) (L)',
                'Label:13C(6)15N(2) (K)',
                'Label:13C(6)15N(2)+Carbamyl (K)',
                'Label:13C(6)15N(4) (R)',
                'Label:15N(1) (A)',
                'Label:15N(1) (C)',
                'Label:15N(1) (D)',
                'Label:15N(1) (E)',
                'Label:15N(1) (F)',
                'Label:15N(1) (G)',
                'Label:15N(1) (I)',
                'Label:15N(1) (L)',
                'Label:15N(1) (M)',
                'Label:15N(1) (P)',
                'Label:15N(1) (S)',
                'Label:15N(1) (T)',
                'Label:15N(1) (V)',
                'Label:15N(1) (Y)',
                'Label:15N(1)+Carbamidomethyl (C)',
                'Label:15N(1)+Deamidated (N)',
                'Label:15N(1)+Oxidation (M)',
                'Label:15N(2) (K)',
                'Label:15N(2) (N)',
                'Label:15N(2) (Q)',
                'Label:15N(2) (W)',
                'Label:15N(3) (H)',
                'Label:15N(4) (R)',
                'Label:18O(1) (C-term)',
                'Label:18O(2) (C-term)',
                'Label:2H(3) (L)',
                'Methyl (C-term)',
                'Methyl (DE)',
                'Methyl (E)',
                'Methyl (H)',
                'Methyl (K)',
                'Methyl (R)',
                'Methyl:13C(1)2H(3) (C-term)',
                'Methyl:13C(1)2H(3) (DE)',
                'Methylthiol (C)',
                'Nethylmaleimide (C)',
                'Nethylmaleimide+water (C)',
                'NIPCAM (C)',
                'Nitro (Y)',
                'Nitrosyl (C)',
                'Oxidation (M)',
                'Oxidation (P)',
                'Oxidation (PWY)',
                'Oxidation (W)',
                'Oxidation (Y)',
                'PEO-Iodoacetyl-LC-Biotin (C)',
                'Phospho (ST)',
                'Phospho (STY)',
                'Phospho (Y)',
                'PhosphoHexNAc (ST)',
                'Piperidine (K)',
                'Piperidine (N-term)',
                'Propionamide (C)',
                'Pyridylethyl (C)',
                'Quinone (W)',
                'SerTyr (N-term)',
                'SerTyr+iTRAQ (N-term)',
                'SerTyrLys(OAc) (N-term)',
                'SerTyrLys(OAcs) (N-term)',
                'Sulfide (C)',
                'Sulfo (Y)',
                'Thiophospho (ST)',
                'TMT (K)',
                'TMT (N-term)',
                'TMT (Y)',
                'TMT2plex (K)',
                'TMT2plex (N-term)',
                'TMT2plex (Y)',
                'TMT6plex (K)',
                'TMT6plex (N-term)',
                'TMT6plex (Y)',
                'Trioxidation (C)',
                'Trp-&gt;Hydroxykynurenin (W)',
                'Trp-&gt;Kynurenin (W)',
                'Xlink:BSSA1 (N-term)',
                'Xlink:BSSA2 (N-term)',
                'Xlink:DSS1 (N-term)',
                'Xlink:DSS1:2H(12) (N-term)',
                'Xlink:DSS1:2H(4) (N-term)',
                'Xlink:DSS2 (N-term)',
                'Xlink:DSS2:2H(12) (N-term)',
                'Xlink:DSS2:2H(4) (N-term)',
                'Xlink:FCXL1-1 (N-term)',
                'Xlink:FCXL1-2 (N-term)',
            ],
            'variableMods':[
                'Acetohydrazide (C-term)',
                'Acetohydrazide (DE)',
                'Acetyl (K)',
                'Acetyl (N-term)',
                'Acetyl:2H(3) (K)',
                'Acetyl:2H(3) (N-term)',
                'Acetyl:2H(3)+Methyl (K)',
                'ADP-Ribosyl (CEKNSR)',
                'ADP-Ribosyl (E)',
                'ADP-Ribosyl (K)',
                'ADP-Ribosyl (R)',
                'Amidated (C-term)',
                'Amidated+iTRAQ8plex (C-term)',
                'Amino (Y)',
                'Ammonia-loss (K)',
                'Ammonia-loss (R)',
                'AMTzGalNAcGlcNAc (N)',
                'AMTzGalNAcGlcNAc (ST)',
                'APTA (C)',
                'Asn-&gt;Succinimide (N)',
                'Biotin (N-term)',
                'Carbamidomethyl (C)',
                'Carbamidomethyl (N-term)',
                'Carbamyl (K)',
                'Carbamyl (N-term)',
                'Carboxy (E)',
                'Carboxy (W)',
                'Carboxymethyl (C)',
                'Cation:Na (C-term)',
                'Cation:Na (DE)',
                'Cyano (C)',
                'Cys-&gt;Dha (C)',
                'Deamidated (N)',
                'Deamidated (Q)',
                'Dehydrated (C-term)',
                'Dehydrated (D)',
                'Dehydrated (ST)',
                'Dehydro (C)',
                'Delta:2H(6)C(3) (K)',
                'Delta:2H(6)C(3) (N-term)',
                'Delta:H(2)C(2) (N-term)',
                'Delta:H(2)C(3) (K)',
                'Delta:H(4)C(3)O(1) (C)',
                'Delta:H(4)C(3)O(1) (CHK)',
                'Delta:H(4)C(6) (K)',
                'Delta:H(6)C(3) (K)',
                'Delta:H(6)C(3) (N-term)',
                'Delta:H(6)C(6)O(1) (K)',
                'Delta:H(8)C(6)O(2) (K)',
                'Dethiomethyl (M)',
                'Didehydro (C)',
                'Dimethyl (N-term)',
                'Dioxidation (C)',
                'Dioxidation (M)',
                'Dioxidation (W)',
                'DTT_C (C)',
                'DTT_C:2H(6) (C)',
                'DTT_ST (ST)',
                'DTT_ST:2H(6) (ST)',
                'Ethanolyl (C)',
                'Formyl (K)',
                'Formyl (N-term)',
                'Formyl (ST)',
                'GirardT (N)',
                'GlyGly (C)',
                'GlyGly (N-term)',
                'GlyTyr (N-term)',
                'Guanidinyl (K)',
                'HexNAc (N)',
                'HexNAc (ST)',
                'HexNAc (Y)',
                'HexNAcHex (ST)',
                'HexNAcHexSA (ST)',
                'HexNAcHexSA2 (ST)',
                'HexNAcHexSAOx (ST)',
                'HexNACHExSAOxSAOx (ST)',
                'HexNACHexSASAOx (ST)',
                'HexNAcSA (ST)',
                'HexNAcSAOx (ST)',
                'Hydroxymethyl (CRWHKNQY)',
                'ICAT-C (C)',
                'ICAT-C:13C(9) (C)',
                'ICAT-D (C)',
                'ICAT-D:2H(8) (C)',
                'IDEnT (C)',
                'iTRAQ4plex (K)',
                'iTRAQ4plex (N-term)',
                'iTRAQ4plex (Y)',
                'iTRAQ8plex (K)',
                'iTRAQ8plex (N-term)',
                'iTRAQ8plex (Y)',
                'Label:13C(6) (K)',
                'Label:13C(6) (L)',
                'Label:13C(6) (R)',
                'Label:13C(6)15N(1) (L)',
                'Label:13C(6)15N(2) (K)',
                'Label:13C(6)15N(2)+Carbamyl (K)',
                'Label:13C(6)15N(4) (R)',
                'Label:15N(1) (A)',
                'Label:15N(1) (C)',
                'Label:15N(1) (D)',
                'Label:15N(1) (E)',
                'Label:15N(1) (F)',
                'Label:15N(1) (G)',
                'Label:15N(1) (I)',
                'Label:15N(1) (L)',
                'Label:15N(1) (M)',
                'Label:15N(1) (P)',
                'Label:15N(1) (S)',
                'Label:15N(1) (T)',
                'Label:15N(1) (V)',
                'Label:15N(1) (Y)',
                'Label:15N(1)+Carbamidomethyl (C)',
                'Label:15N(1)+Deamidated (N)',
                'Label:15N(1)+Oxidation (M)',
                'Label:15N(2) (K)',
                'Label:15N(2) (N)',
                'Label:15N(2) (Q)',
                'Label:15N(2) (W)',
                'Label:15N(3) (H)',
                'Label:15N(4) (R)',
                'Label:18O(1) (C-term)',
                'Label:18O(2) (C-term)',
                'Label:2H(3) (L)',
                'Methyl (C-term)',
                'Methyl (DE)',
                'Methyl (E)',
                'Methyl (H)',
                'Methyl (K)',
                'Methyl (R)',
                'Methyl:13C(1)2H(3) (C-term)',
                'Methyl:13C(1)2H(3) (DE)',
                'Methylthiol (C)',
                'Nethylmaleimide (C)',
                'Nethylmaleimide+water (C)',
                'NIPCAM (C)',
                'Nitro (Y)',
                'Nitrosyl (C)',
                'Oxidation (M)',
                'Oxidation (P)',
                'Oxidation (PWY)',
                'Oxidation (W)',
                'Oxidation (Y)',
                'PEO-Iodoacetyl-LC-Biotin (C)',
                'Phospho (ST)',
                'Phospho (STY)',
                'Phospho (Y)',
                'PhosphoHexNAc (ST)',
                'Piperidine (K)',
                'Piperidine (N-term)',
                'Propionamide (C)',
                'Pyridylethyl (C)',
                'Quinone (W)',
                'SerTyr (N-term)',
                'SerTyr+iTRAQ (N-term)',
                'SerTyrLys(OAc) (N-term)',
                'SerTyrLys(OAcs) (N-term)',
                'Sulfide (C)',
                'Sulfo (Y)',
                'Thiophospho (ST)',
                'TMT (K)',
                'TMT (N-term)',
                'TMT (Y)',
                'TMT2plex (K)',
                'TMT2plex (N-term)',
                'TMT2plex (Y)',
                'TMT6plex (K)',
                'TMT6plex (N-term)',
                'TMT6plex (Y)',
                'Trioxidation (C)',
                'Trp-&gt;Hydroxykynurenin (W)',
                'Trp-&gt;Kynurenin (W)',
                'Xlink:BSSA1 (N-term)',
                'Xlink:BSSA2 (N-term)',
                'Xlink:DSS1 (N-term)',
                'Xlink:DSS1:2H(12) (N-term)',
                'Xlink:DSS1:2H(4) (N-term)',
                'Xlink:DSS2 (N-term)',
                'Xlink:DSS2:2H(12) (N-term)',
                'Xlink:DSS2:2H(4) (N-term)',
                'Xlink:FCXL1-1 (N-term)',
                'Xlink:FCXL1-2 (N-term)',
            ],
            'instruments':[
                'ESI-Q-TOF',
                'ESI-Q-high-res',
                'ESI-ION-TRAP-low-res',
                'ESI-FT-ICR-CID',
                'ESI-FT-ICR-ECD',
                'ESI-ETD-low-res',
                'MALDI-Q-TOF',
                'MALDI-TOFTOF',
            ],
        }
        
        # update databases
        self.paramMSFitDatabase_choice.Clear()
        self.paramMSTagDatabase_choice.Clear()
        
        for item in self.currentParams['databases']:
            self.paramMSFitDatabase_choice.Append(item)
            self.paramMSTagDatabase_choice.Append(item)
        
        if config.prospector['msfit']['database'] in self.currentParams['databases']:
            self.paramMSFitDatabase_choice.Select(self.currentParams['databases'].index(config.prospector['msfit']['database']))
        if config.prospector['mstag']['database'] in self.currentParams['databases']:
            self.paramMSTagDatabase_choice.Select(self.currentParams['databases'].index(config.prospector['mstag']['database']))
        
        # update taxonomy
        self.paramMSFitTaxonomy_choice.Clear()
        self.paramMSTagTaxonomy_choice.Clear()
        
        for item in self.currentParams['taxonomy']:
            self.paramMSFitTaxonomy_choice.Append(item)
            self.paramMSTagTaxonomy_choice.Append(item)
        
        if config.prospector['msfit']['taxonomy'] in self.currentParams['taxonomy']:
            self.paramMSFitTaxonomy_choice.Select(self.currentParams['taxonomy'].index(config.prospector['msfit']['taxonomy']))
        if config.prospector['mstag']['taxonomy'] in self.currentParams['taxonomy']:
            self.paramMSTagTaxonomy_choice.Select(self.currentParams['taxonomy'].index(config.prospector['mstag']['taxonomy']))
        
        # update enzymes
        self.paramMSFitEnzyme_choice.Clear()
        self.paramMSTagEnzyme_choice.Clear()
        
        for item in self.currentParams['enzymes']:
            self.paramMSFitEnzyme_choice.Append(item)
            self.paramMSTagEnzyme_choice.Append(item)
        
        if config.prospector['msfit']['enzyme'] in self.currentParams['enzymes']:
            self.paramMSFitEnzyme_choice.Select(self.currentParams['enzymes'].index(config.prospector['msfit']['enzyme']))
        if config.prospector['mstag']['enzyme'] in self.currentParams['enzymes']:
            self.paramMSTagEnzyme_choice.Select(self.currentParams['enzymes'].index(config.prospector['mstag']['enzyme']))
        
        # update fixed modifications
        self.paramMSFitFixedMods_listbox.Clear()
        self.paramMSTagFixedMods_listbox.Clear()
        
        for item in self.currentParams['fixedMods']:
            self.paramMSFitFixedMods_listbox.Append(item)
            self.paramMSTagFixedMods_listbox.Append(item)
        
        for item in config.prospector['msfit']['fixedMods']:
            if item in self.currentParams['fixedMods']:
                self.paramMSFitFixedMods_listbox.Select(self.currentParams['fixedMods'].index(item))
        for item in config.prospector['mstag']['fixedMods']:
            if item in self.currentParams['fixedMods']:
                self.paramMSTagFixedMods_listbox.Select(self.currentParams['fixedMods'].index(item))
        
        # update variable modifications
        self.paramMSFitVariableMods_listbox.Clear()
        self.paramMSTagVariableMods_listbox.Clear()
        
        for item in self.currentParams['variableMods']:
            self.paramMSFitVariableMods_listbox.Append(item)
            self.paramMSTagVariableMods_listbox.Append(item)
        
        for item in config.prospector['msfit']['variableMods']:
            if item in self.currentParams['variableMods']:
                self.paramMSFitVariableMods_listbox.Select(self.currentParams['variableMods'].index(item))
        for item in config.prospector['mstag']['variableMods']:
            if item in self.currentParams['variableMods']:
                self.paramMSTagVariableMods_listbox.Select(self.currentParams['variableMods'].index(item))
        
        # update instruments
        self.paramMSFitInstrument_choice.Clear()
        self.paramMSTagInstrument_choice.Clear()
        
        for item in self.currentParams['instruments']:
            self.paramMSFitInstrument_choice.Append(item)
            self.paramMSTagInstrument_choice.Append(item)
        
        if config.prospector['msfit']['instrument'] in self.currentParams['instruments']:
            self.paramMSFitInstrument_choice.Select(self.currentParams['instruments'].index(config.prospector['msfit']['instrument']))
        if config.prospector['mstag']['instrument'] in self.currentParams['instruments']:
            self.paramMSTagInstrument_choice.Select(self.currentParams['instruments'].index(config.prospector['mstag']['instrument']))
        
        # update modifications count
        self.onModificationSelected()
    # ----
    
    
    def makeSearchHTML(self):
        """Format data to profound html."""
        
        form = config.prospector['common']['searchType']
        
        # make html page
        buff = '<?xml version="1.0" encoding="utf-8"?>\n'
        buff += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        buff += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        buff += '<head>\n'
        buff += '  <title>mMass - Protein Prospector Search</title>\n'
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
        buff += '<body>\n'
        buff += '  <form action="%s" id="mainSearch" method="post">\n' % (config.prospector['common']['script'])
        buff += '    <div style="display:none;">\n\n'
        
        # common parameters
        buff += '      <input type="text" name="version" value="5.5.0" />\n'
        buff += '      <input type="text" name="input_program_name" value="msfit" />\n'
        buff += '      <input type="text" name="input_filename" value="lastres" />\n'
        buff += '      <input type="text" name="results_to_file" value="0" />\n'
        buff += '      <input type="text" name="results_from_file" value="0" />\n'
        buff += '      <input type="text" name="output_type" value="HTML" />\n'
        buff += '      <input type="text" name="output_filename" value="lastres" />\n'
        buff += '      <input type="text" name="dna_frame_translation" value="3" />\n'
        buff += '      <input type="text" name="species_remove" value="" />\n'
        buff += '      <input type="text" name="species_names" value="" />\n'
        buff += '      <input type="text" name="accession_nums" value="" />\n'
        buff += '      <input type="text" name="names" value="" />\n'
        buff += '      <input type="text" name="add_accession_numbers" value="" />\n'
        buff += '      <input type="text" name="data_source" value="Data Paste Area" />\n'
        buff += '      <input type="text" name="data_format" value="PP M/Z Intensity Charge" />\n'
        buff += '      <input type="text" name="ms_mass_exclusion" value="0" />\n'
        buff += '      <input type="text" name="ms_matrix_exclusion" value="0" />\n'
        buff += '      <input type="text" name="ms_peak_exclusion" value="0" />\n'
        buff += '      <input type="text" name="msms_deisotope" value="0" />\n'
        buff += '      <input type="text" name="msms_join_peaks" value="0" />\n'
        buff += '      <input type="text" name="msms_mass_exclusion" value="0" />\n'
        buff += '      <input type="text" name="msms_matrix_exclusion" value="0" />\n'
        buff += '      <input type="text" name="msms_peak_exclusion" value="0" />\n'
        
        buff += '      <input type="text" name="database" value="%s" />\n' % (config.prospector[form]['database'])
        buff += '      <input type="text" name="species" value="%s" />\n' % (config.prospector[form]['taxonomy'])
        buff += '      <input type="text" name="enzyme" value="%s" />\n' % (config.prospector[form]['enzyme'])
        buff += '      <input type="text" name="missed_cleavages" value="%s" />\n' % (config.prospector[form]['miscleavages'])
        buff += '      <input type="text" name="comment" value="%s" />\n' % (self._escape(config.prospector[form]['title']))
        buff += '      <input type="text" name="parent_mass_convert" value="%s" />\n' % (config.prospector[form]['massType'].lower())
        buff += '      <input type="text" name="instrument_name" value="%s" />\n' % (config.prospector[form]['instrument'])
        
        # MS-Fit parameters
        if config.prospector['common']['searchType'] == 'msfit':
            
            buff += '      <input type="text" name="report_title" value="MS-Fit" />\n'
            buff += '      <input type="text" name="search_name" value="msfit" />\n'
            buff += '      <input type="text" name="detailed_report" value="1" />\n'
            buff += '      <input type="text" name="display_graph" value="0" />\n'
            buff += '      <input type="text" name="sort_type" value="Score Sort" />\n'
            buff += '      <input type="text" name="mowse_on" value="1" />\n'
            buff += '      <input type="text" name="parent_contaminant_masses" value="" />\n'
            buff += '      <input type="text" name="min_parent_ion_matches" value="1" />\n'
            buff += '      <input type="text" name="ms_search_type" value="" />\n'
            buff += '      <input type="text" name="ms_parent_mass_systematic_error" value="0" />\n'
            buff += '      <input type="text" name="ms_full_mw_range" value="0" />\n'
            buff += '      <input type="text" name="full_pi_range" value="0" />\n'
            
            buff += '      <input type="text" name="mowse_pfactor" value="%s" />\n' % (config.prospector['msfit']['pfactor'])
            buff += '      <input type="text" name="min_matches" value="%s" />\n' % (config.prospector['msfit']['minMatches'])
            buff += '      <input type="text" name="ms_prot_low_mass" value="%s" />\n' % (config.prospector['msfit']['proteinMassLow']*1000)
            buff += '      <input type="text" name="ms_prot_high_mass" value="%s" />\n' % (config.prospector['msfit']['proteinMassHigh']*1000)
            buff += '      <input type="text" name="ms_parent_mass_tolerance" value="%s" />\n' % (config.prospector['msfit']['peptideTol'])
            buff += '      <input type="text" name="ms_parent_mass_tolerance_units" value="%s" />\n' % (config.prospector['msfit']['peptideTolUnits'])
            buff += '      <input type="text" name="ms_max_modifications" value="%s" />\n' % (config.prospector['msfit']['maxMods'])
            buff += '      <input type="text" name="ms_max_reported_hits" value="%s" />\n' % (config.prospector['msfit']['report'])
            
            buff += '      <select name="const_mod" multiple="multiple">\n'
            for mod in config.prospector['msfit']['fixedMods']:
                buff += '        <option selected="selected">%s</option>\n' % (mod)
            buff += '      </select>\n'
            
            for x, mod in enumerate(config.prospector['msfit']['variableMods']):
                buff += '      <input type="text" name="user%s_name" value="%s" />\n' % (x+1, mod)
            buff += '      <select name="mod_AA" multiple="multiple">\n'
            for x, mod in enumerate(config.prospector['msfit']['variableMods']):
                buff += '        <option selected="selected">User Defined %s</option>\n' % (x+1)
            buff += '      </select>\n'
            
            buff += '      <textarea name="data">%s</textarea>\n' % (self.paramQuery_value.GetValue())
        
        # MS-Tag parameters
        elif config.prospector['common']['searchType'] == 'mstag':
            
            buff += '      <input type="text" name="report_title" value="MS-Tag" />\n'
            buff += '      <input type="text" name="search_name" value="mstag" />\n'
            buff += '      <input type="text" name="display_graph" value="1" />\n'
            buff += '      <input type="text" name="allow_non_specific" value="at 0 termini" />\n'
            buff += '      <input type="text" name="expect_calc_method" value="None" />\n'
            buff += '      <input type="text" name="use_instrument_ion_types" value="1" />\n'
            buff += '      <input type="text" name="max_hits" value="9999999" />\n'
            buff += '      <input type="text" name="msms_search_type" value="" />\n'
            buff += '      <input type="text" name="msms_parent_mass_systematic_error" value="0" />\n'
            buff += '      <input type="text" name="msms_max_peaks" value="" />\n'
            buff += '      <input type="text" name="msms_prot_low_mass" value="0" />\n'
            buff += '      <input type="text" name="msms_prot_high_mass" value="500000" />\n'
            buff += '      <input type="text" name="msms_max_peptide_permutations" value="" />\n'
            buff += '      <input type="text" name="msms_full_mw_range" value="1" />\n'
            buff += '      <input type="text" name="low_pi" value="1.0" />\n'
            buff += '      <input type="text" name="high_pi" value="14.0" />\n'
            buff += '      <input type="text" name="full_pi_range" value="1" />\n'
            
            buff += '      <input type="text" name="msms_parent_mass_tolerance" value="%s" />\n' % (config.prospector['mstag']['peptideTol'])
            buff += '      <input type="text" name="msms_parent_mass_tolerance_units" value="%s" />\n' % (config.prospector['mstag']['peptideTolUnits'])
            buff += '      <input type="text" name="msms_precursor_charge" value="%s" />\n' % (config.prospector['mstag']['peptideCharge'])
            buff += '      <input type="text" name="fragment_masses_tolerance" value="%s" />\n' % (config.prospector['mstag']['msmsTol'])
            buff += '      <input type="text" name="fragment_masses_tolerance_units" value="%s" />\n' % (config.prospector['mstag']['msmsTolUnits'])
            buff += '      <input type="text" name="msms_max_modifications" value="%s" />\n' % (config.prospector['mstag']['maxMods'])
            buff += '      <input type="text" name="msms_max_reported_hits" value="%s" />\n' % (config.prospector['mstag']['report'])
            
            buff += '      <select name="const_mod" multiple="multiple">\n'
            for mod in config.prospector['mstag']['fixedMods']:
                buff += '        <option selected="selected">%s</option>\n' % (mod)
            buff += '      </select>\n'
            
            buff += '      <select name="msms_mod_AA" multiple="multiple">\n'
            for mod in config.prospector['mstag']['variableMods']:
                buff += '        <option selected="selected">%s</option>\n' % (mod)
            buff += '      </select>\n'
            
            buff += '      <textarea name="data">%s\n%s</textarea>\n' % (config.prospector['mstag']['peptideMass'], self.paramQuery_value.GetValue())
        
        buff += '    </div>\n\n'
        
        buff += '    <div id="info">\n'
        buff += '      <h1>mMass - Protein Prospector Search</h1>\n'
        buff += '      <p id="sending">Sending data to Protein Prospector &hellip;</p>\n'
        buff += '      <p id="wait">Please wait &hellip;</p>\n'
        buff += '      <p id="note">Press the <strong>Search</strong> button if data was not sent automatically.</p>\n'
        buff += '      <p id="button"><input type="submit" value="Search" /></p>\n'
        buff += '    </div>\n\n'
        
        buff += '  </form>\n'
        buff += '</body>\n'
        buff += '</html>\n'
        
        return buff
    # ----
    
    
    def _escape(self, text):
        """Clear special characters such as <> etc."""
        
        text = text.strip()
        search = ('&', '"', "'", '<', '>')
        replace = ('&amp;', '&quot;', '&#39;', '&lt;', '&gt;')
        for x, item in enumerate(search):
            text = text.replace(item, replace[x])
            
        return text
    # ----
    
    


