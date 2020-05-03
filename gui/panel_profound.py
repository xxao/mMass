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


# FLOATING PANEL WITH PROFOUND SEARCH
# -----------------------------------

class panelProfound(wx.MiniFrame):
    """Profound search tool."""
    
    def __init__(self, parent, tool='pmf'):
        wx.MiniFrame.__init__(self, parent, -1, 'ProFound Search', size=(300, -1), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
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
        pmf = self.makePMFPanel()
        query = self.makeQueryPanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(pmf, 1, wx.EXPAND, 0)
        self.mainSizer.Add(query, 1, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        self.pmf_butt = wx.BitmapButton(panel, ID_profoundPMF, images.lib['profoundPMFOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.pmf_butt.SetToolTip(wx.ToolTip("Peptide mass fingerprint"))
        self.pmf_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.query_butt = wx.BitmapButton(panel, ID_profoundQuery, images.lib['profoundQueryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.query_butt.SetToolTip(wx.ToolTip("Peak list"))
        self.query_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.search_butt = wx.Button(panel, -1, "Search", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.search_butt.Bind(wx.EVT_BUTTON, self.onSearch)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.TOOLBAR_LSPACE)
        sizer.Add(self.pmf_butt, 0, wx.ALIGN_CENTER_VERTICAL)
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
    
    
    def makePMFPanel(self):
        """Make controls for search form panel."""
        
        panel = wx.Panel(self, -1)
        
        # make info elements
        paramSearchTitle_label = wx.StaticText(panel, -1, "Title:")
        self.paramTitle_value = wx.TextCtrl(panel, -1, "", size=(250, -1))
        
        # make sequence elements
        paramTaxonomy_label = wx.StaticText(panel, -1, "Taxonomy:")
        self.paramTaxonomy_choice = wx.Choice(panel, -1, choices=[], size=(300, mwx.CHOICE_HEIGHT))
        
        paramDatabase_label = wx.StaticText(panel, -1, "Database:")
        self.paramDatabase_choice = wx.Choice(panel, -1, choices=[], size=(150, mwx.CHOICE_HEIGHT))
        
        paramEnzyme_label = wx.StaticText(panel, -1, " Enzyme:")
        self.paramEnzyme_choice = wx.Choice(panel, -1, choices=[], size=(130, mwx.CHOICE_HEIGHT))
        
        paramMiscleavages_label = wx.StaticText(panel, -1, " Miscl.:")
        self.paramMiscleavages_choice = wx.Choice(panel, -1, choices=['0','1','2','3','4'], size=(50, mwx.CHOICE_HEIGHT))
        self.paramMiscleavages_choice.SetStringSelection(str(config.profound['miscleavages']))
        
        # make modifications elements
        self.paramFixedMods_label = wx.StaticText(panel, -1, "Complete modifications:")
        self.paramFixedMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramFixedMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramFixedMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        self.paramVariableMods_label = wx.StaticText(panel, -1, "Partial modifications:")
        self.paramVariableMods_listbox = wx.ListBox(panel, -1, size=(200, 100), choices=[], style=wx.LB_EXTENDED)
        self.paramVariableMods_listbox.SetFont(wx.SMALL_FONT)
        self.paramVariableMods_listbox.Bind(wx.EVT_LISTBOX, self.onModificationSelected)
        
        # make masses elements
        paramProteinMass_label = wx.StaticText(panel, -1, "Protein mass:")
        self.paramProteinMassLow_value = wx.TextCtrl(panel, -1, "0", size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramProteinMassHigh_value = wx.TextCtrl(panel, -1, "300", size=(50, -1), validator=mwx.validator('floatPos'))
        paramProteinMass_dash = wx.StaticText(panel, -1, "-")
        paramProteinMassUnits_label = wx.StaticText(panel, -1, "kDa")
        
        paramProteinPI_label = wx.StaticText(panel, -1, "Protein pI:")
        self.paramProteinPILow_value = wx.TextCtrl(panel, -1, "0", size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramProteinPIHigh_value = wx.TextCtrl(panel, -1, "14", size=(50, -1), validator=mwx.validator('floatPos'))
        paramProteinPI_dash = wx.StaticText(panel, -1, "-")
        
        paramPeptideTol_label = wx.StaticText(panel, -1, "Peptide tolerance:")
        self.paramPeptideTol_value = wx.TextCtrl(panel, -1, str(config.profound['peptideTol']), size=(50, -1), validator=mwx.validator('floatPos'))
        self.paramPeptideTolUnits_choice = wx.Choice(panel, -1, choices=['Da','%','ppm'], size=(80, mwx.CHOICE_HEIGHT))
        self.paramPeptideTolUnits_choice.SetStringSelection(config.profound['peptideTolUnits'])
        
        paramMassType_label = wx.StaticText(panel, -1, "Mass type:")
        self.paramMassType_choice = wx.Choice(panel, -1, choices=['Monoisotopic', 'Average'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramMassType_choice.SetStringSelection(config.profound['massType'])
        
        paramCharge_label = wx.StaticText(panel, -1, "Charge:")
        self.paramCharge_choice = wx.Choice(panel, -1, choices=['MH+','M'], size=(150, mwx.CHOICE_HEIGHT))
        self.paramCharge_choice.SetStringSelection(config.profound['charge'])
        
        # results elements
        self.paramExpectation_radio = wx.RadioButton(panel, -1, "Expectation value:", style=wx.RB_GROUP)
        self.paramExpectation_value = wx.TextCtrl(panel, -1, str(config.profound['expectation']), size=(60, -1), validator=mwx.validator('floatPos'))
        if config.profound['ranking'] == 'expect':
            self.paramExpectation_radio.SetValue(True)
        
        self.paramZscore_radio = wx.RadioButton(panel, -1, "Z Score candidates:")
        self.paramCandidates_value = wx.TextCtrl(panel, -1, str(config.profound['candidates']), size=(60, -1), validator=mwx.validator('floatPos'))
        if config.profound['ranking'] == 'zscore':
            self.paramZscore_radio.SetValue(True)
        
        # pack elements
        infoGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        infoGrid.Add(paramSearchTitle_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        infoGrid.Add(self.paramTitle_value, (0,1), flag=wx.EXPAND)
        infoGrid.AddGrowableCol(1)
        
        sequenceGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        sequenceGrid.Add(paramTaxonomy_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramTaxonomy_choice, (0,1), (1,5), flag=wx.EXPAND)
        sequenceGrid.Add(paramDatabase_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramDatabase_choice, (1,1), flag=wx.EXPAND)
        sequenceGrid.Add(paramEnzyme_label, (1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramEnzyme_choice, (1,3), flag=wx.EXPAND)
        sequenceGrid.Add(paramMiscleavages_label, (1,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sequenceGrid.Add(self.paramMiscleavages_choice, (1,5))
        sequenceGrid.AddGrowableCol(1)
        sequenceGrid.AddGrowableCol(3)
        
        modsGrid = wx.GridBagSizer(5, 20)
        modsGrid.Add(self.paramFixedMods_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramVariableMods_label, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        modsGrid.Add(self.paramFixedMods_listbox, (1,0), flag=wx.EXPAND)
        modsGrid.Add(self.paramVariableMods_listbox, (1,1), flag=wx.EXPAND)
        modsGrid.AddGrowableCol(0)
        modsGrid.AddGrowableCol(1)
        
        massesGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        massesGrid.Add(paramProteinMass_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramProteinMassLow_value, (0,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramProteinMass_dash, (0,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramProteinMassHigh_value, (0,3), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramProteinMassUnits_label, (0,4), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramProteinPI_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramProteinPILow_value, (1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramProteinPI_dash, (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramProteinPIHigh_value, (1,3), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramPeptideTol_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPeptideTol_value, (2,1), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramPeptideTolUnits_choice, (2,3), (1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramMassType_label, (0,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramMassType_choice, (0,6), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(paramCharge_label, (1,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        massesGrid.Add(self.paramCharge_choice, (1,6), flag=wx.ALIGN_CENTER_VERTICAL)
        massesGrid.AddGrowableCol(4)
        
        resultsGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        resultsGrid.Add(self.paramExpectation_radio, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramExpectation_value, (0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramZscore_radio, (0,3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        resultsGrid.Add(self.paramCandidates_value, (0,4), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
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
        self.filterAnnotations_check.SetValue(config.profound['filterAnnotations'])
        self.filterAnnotations_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterMatches_check = wx.CheckBox(ctrlPanel, -1, "Matched")
        self.filterMatches_check.SetFont(wx.SMALL_FONT)
        self.filterMatches_check.SetValue(config.profound['filterMatches'])
        self.filterMatches_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnselected_check = wx.CheckBox(ctrlPanel, -1, "Unselected")
        self.filterUnselected_check.SetFont(wx.SMALL_FONT)
        self.filterUnselected_check.SetValue(config.profound['filterUnselected'])
        self.filterUnselected_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterIsotopes_check = wx.CheckBox(ctrlPanel, -1, "Isotopes")
        self.filterIsotopes_check.SetFont(wx.SMALL_FONT)
        self.filterIsotopes_check.SetValue(config.profound['filterIsotopes'])
        self.filterIsotopes_check.Bind(wx.EVT_CHECKBOX, self.onGetPeaklist)
        
        self.filterUnknown_check = wx.CheckBox(ctrlPanel, -1, "Unknown")
        self.filterUnknown_check.SetFont(wx.SMALL_FONT)
        self.filterUnknown_check.SetValue(config.profound['filterUnknown'])
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
            path = os.path.join(tempfile.gettempdir(), 'mmass_profound_search.html')
            os.unlink(path)
        except:
            pass
        
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'pmf'
            if evt and evt.GetId() == ID_profoundPMF:
                tool = 'pmf'
            elif evt and evt.GetId() == ID_profoundQuery:
                tool = 'query'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        
        # set icons off
        self.pmf_butt.SetBitmapLabel(images.lib['profoundPMFOff'])
        self.query_butt.SetBitmapLabel(images.lib['profoundQueryOff'])
        
        # set panel
        if tool == 'pmf':
            self.SetTitle("ProFound - Peptide Mass Fingerprint")
            self.mainSizer.Show(1)
            self.pmf_butt.SetBitmapLabel(images.lib['profoundPMFOn'])
        
        elif tool == 'query':
            self.SetTitle("ProFound - Peak List")
            self.mainSizer.Show(2)
            self.query_butt.SetBitmapLabel(images.lib['profoundQueryOn'])
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onModificationSelected(self, evt=None):
        """Count and show number of selected modifications."""
        
        if (self.paramFixedMods_label and self.paramVariableMods_label) and (not evt or self.currentTool == 'pmf'):
            label = 'Fixed modifications: (%d)' % len(self.paramFixedMods_listbox.GetSelections())
            self.paramFixedMods_label.SetLabel(label)
            label = 'Variable modifications: (%d)' % len(self.paramVariableMods_listbox.GetSelections())
            self.paramVariableMods_label.SetLabel(label)
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
            path = os.path.join(tempfile.gettempdir(), 'mmass_profound_search.html')
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
            self.paramTitle_value.SetValue('')
            self.paramQuery_value.SetValue('')
            return
        
        # change search title
        self.paramTitle_value.SetValue(document.title)
        
        # get peaklist
        self.onGetPeaklist()
    # ----
    
    
    def getParams(self):
        """Get dialog params."""
        
        try:
            
            config.profound['title'] = self.paramTitle_value.GetValue()
            config.profound['database'] = self.paramDatabase_choice.GetStringSelection()
            config.profound['taxonomy'] = self.paramTaxonomy_choice.GetStringSelection()
            config.profound['enzyme'] = self.paramEnzyme_choice.GetStringSelection()
            config.profound['miscleavages'] = self.paramMiscleavages_choice.GetStringSelection()
            config.profound['proteinMassLow'] = self.paramProteinMassLow_value.GetValue()
            config.profound['proteinMassHigh'] = self.paramProteinMassHigh_value.GetValue()
            config.profound['proteinPILow'] = self.paramProteinPILow_value.GetValue()
            config.profound['proteinPIHigh'] = self.paramProteinPIHigh_value.GetValue()
            config.profound['peptideTol'] = self.paramPeptideTol_value.GetValue()
            config.profound['peptideTolUnits'] = self.paramPeptideTolUnits_choice.GetStringSelection()
            config.profound['massType'] = self.paramMassType_choice.GetStringSelection()
            config.profound['charge'] = self.paramCharge_choice.GetStringSelection()
            config.profound['expectation'] = self.paramExpectation_value.GetValue()
            config.profound['candidates'] = self.paramCandidates_value.GetValue()
            
            if self.paramZscore_radio.GetValue():
                config.profound['ranking'] = 'zscore'
            else:
                config.profound['ranking'] = 'expect'
            
            fixedMods = self.paramFixedMods_listbox.GetStrings()
            variableMods = self.paramVariableMods_listbox.GetStrings()
            config.profound['fixedMods'] = []
            config.profound['variableMods'] = []
            for item in self.paramFixedMods_listbox.GetSelections():
                config.profound['fixedMods'].append(fixedMods[item])
            for item in self.paramVariableMods_listbox.GetSelections():
                config.profound['variableMods'].append(variableMods[item])
            
            if config.profound['proteinMassLow']:
                config.profound['proteinMassLow'] = float(config.profound['proteinMassLow'])
            
            if config.profound['proteinMassHigh']:
                config.profound['proteinMassHigh'] = float(config.profound['proteinMassHigh'])
            
            if config.profound['proteinPILow']:
                config.profound['proteinPILow'] = float(config.profound['proteinPILow'])
            
            if config.profound['proteinPIHigh']:
                config.profound['proteinPIHigh'] = float(config.profound['proteinPIHigh'])
            
            if config.profound['peptideTol']:
                config.profound['peptideTol'] = float(config.profound['peptideTol'])
            
            if config.profound['expectation']:
                config.profound['expectation'] = float(config.profound['expectation'])
            
            if config.profound['candidates']:
                config.profound['candidates'] = int(config.profound['candidates'])
            
            return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def checkParams(self):
        """Check search parameters."""
        
        errors = ''
        
        # check taxonomy and database
        if not config.profound['taxonomy']:
            errors += '- Taxonomy must be selected.\n'
        if not config.profound['database']:
            errors += '- Database must be selected.\n'
        if not config.profound['enzyme']:
            errors += '- Enzyme must be selected.\n'
        
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
            'DBSE':{
                'NCBI nr': '#1#NCBInr#nr#..\databases\#1#0',
                'IPI Human': '#100#IPI_HUMAN#ipi_human#..\databases\#0#0',
                'IPI Mouse': '#101#IPI_MOUSE#ipi_mouse#..\databases\#0#0',
                'IPI Rat': '#102#IPI_RAT#ipi_rat#..\databases\#0#0',
                'IPI Cow': '#103#IPI_BOVIN#ipi_bovin#..\databases\#0#0',
                'IPI Chicken': '#104#IPI_CHICK#ipi_chick#..\databases\#0#0',
                'IPI Zebrafish': '#105#IPI_BRARE#ipi_brare#..\databases\#0#0',
                'IPI Arabidopsis': '#106#IPI_ARATH#ipi_arath#..\databases\#0#0',
                'Ensembl Aedes aegypti': '#200#Ensembl_aedes_aegypti#Ensembl_aedes_aegypti#..\databases\#0#0',
                'Ensembl Anopheles gambiae': '#201#Ensembl_anopheles_gambiae#Ensembl_anopheles_gambiae#..\databases\#0#0',
                'Ensembl Bos taurus': '#202#Ensembl_bos_taurus#Ensembl_bos_taurus#..\databases\#0#0',
                'Ensembl Caenorhabditis elegans': '#203#Ensembl_caenorhabditis_elegans#Ensembl_caenorhabditis_elegans#..\databases\#0#0',
                'Ensembl Canis familiaris': '#204#Ensembl_canis_familiaris#Ensembl_canis_familiaris#..\databases\#0#0',
                'Ensembl Ciona intestinalis': '#205#Ensembl_ciona_intestinalis#Ensembl_ciona_intestinalis#..\databases\#0#0',
                'Ensembl Ciona savignyi': '#206#Ensembl_ciona_savignyi#Ensembl_ciona_savignyi#..\databases\#0#0',
                'Ensembl Danio rerio': '#207#Ensembl_danio_rerio#Ensembl_danio_rerio#..\databases\#0#0',
                'Ensembl Dasypus novemcinctus': '#208#Ensembl_dasypus_novemcinctus#Ensembl_dasypus_novemcinctus#..\databases\#0#0',
                'Ensembl Drosophila melanogaster': '#209#Ensembl_drosophila_melanogaster#Ensembl_drosophila_melanogaster#..\databases\#0#0',
                'Ensembl Echinops telfairi': '#210#Ensembl_echinops_telfairi#Ensembl_echinops_telfairi#..\databases\#0#0',
                'Ensembl Gallus gallus': '#211#Ensembl_gallus_gallus#Ensembl_gallus_gallus#..\databases\#0#0',
                'Ensembl Gasterosteus aculeatus': '#212#Ensembl_Gasterosteus_aculeatus#Ensembl_Gasterosteus_aculeatus#..\databases\#0#0',
                'Ensembl Homo sapiens': '#213#Ensembl_Homo_sapiens#Ensembl_Homo_sapiens#..\databases\#0#0',
                'Ensembl Loxodonta africana': '#214#Ensembl_Loxodonta_africana#Ensembl_Loxodonta_africana#..\databases\#0#0',
                'Ensembl Monodelphis domestica': '#215#Ensembl_monodelphis_domestica#Ensembl_monodelphis_domestica#..\databases\#0#0',
                'Ensembl Mus musculus': '#216#Ensembl_Mus_musculus#Ensembl_Mus_musculus#..\databases\#0#0',
                'Ensembl Ornithorhynchus anatinus': '#217#Ensembl_Ornithorhynchus_anatinus#Ensembl_ornithorhynchus_anatinus#..\databases\#0#0',
                'Ensembl Oryctolagus cuniculus': '#218#Ensembl_Oryctolagus_cuniculus#Ensembl_oryctolagus_cuniculus#..\databases\#0#0',
                'Ensembl Oryzias latipes': '#219#Ensembl_Oryzias_latipes#Ensembl_oryzias_latipes#..\databases\#0#0',
                'Ensembl Rattus norvegicus': '#220#Ensembl_Rattus_norvegicus#Ensembl_Rattus_norvegicus#..\databases\#0#0',
                'Ensembl Saccharomyces cerevisiae': '#221#Ensembl_saccharomyces_cerevisiae#Ensembl_saccharomyces_cerevisiae#..\databases\#0#0',
                'Ensembl Takifugu rubripes': '#222#Ensembl_takifugu_rubripes#Ensembl_takifugu_rubripes#..\databases\#0#0',
                'Ensembl Tetraodon nigroviridis': '#223#Ensembl_tetraodon_nigroviridis#Ensembl_tetraodon_nigroviridis#..\databases\#0#0',
                'Ensembl Xenopus tropicalis': '#224#Ensembl_xenopus_tropicalis#Ensembl_xenopus_tropicalis#..\databases\#0#0',
            },
            'SPEC':[
                'All taxa',
                '. Archaea',
                '. Bacteria',
                '. . Firmicutes',
                '. . . Bacillus subtilis',
                '. . . Mycoplasma',
                '. . . Other Firmicutes',
                '. . Proteobacteria',
                '. . . Enterobacteria',
                '. . . . Escherichia coli',
                '. . . . Other Enterobacteria',
                '. . . Other Proteobacteria',
                '. . Other Bacteria',
                '. Eukaryota',
                '. . Dictyostelium discoideum',
                '. . Fungi',
                '. . . Pneumocystis carinii',
                '. . . Saccharomyces cerevisiae',
                '. . . Schizosaccharomyces pombe',
                '. . . Other Fungi',
                '. . Metazoa',
                '. . . Caenorhabditis elegans',
                '. . . Chordata',
                '. . . . Fugu rubripes',
                '. . . . Danio rerio',
                '. . . . Mammalia',
                '. . . . . Primates',
                '. . . . . . Homo sapiens',
                '. . . . . . Other Primates',
                '. . . . . Rodentia',
                '. . . . . . Mus musculus',
                '. . . . . . Rattus',
                '. . . . . . Other Rodentia',
                '. . . . . Other Mammalia',
                '. . . . Xenopus laevis',
                '. . . . Other Chordata',
                '. . . Drosophila',
                '. . . Other Metazoa',
                '. . Plasmodium falciparum',
                '. . Viridiplantae',
                '. . . Arabidopsis thaliana',
                '. . . Oryza sativa',
                '. . . Other Viridiplantae',
                '. . Other Eukaryotes',
                '. Viroids',
                '. Viruses',
                '. . Hepatitis C virus',
                '. . Other Viruses',
                '. Others',
                '. Unclassified',
            ],
            'ENZ':{
                'Arg C': {'CLST':'R','CLMD':'','CNST':'','TERM':'CTERM'},
                'Asp N': {'CLST':'N','CLMD':'','CNST':'','TERM':'NTERM'},
                'CNBr': {'CLST':'M','CLMD':'-CH4S','CNST':'','TERM':'CTERM'},
                'Chymotrypsin': {'CLST':'YWFL','CLMD':'','CNST':'P','TERM':'CTERM'},
                'Lys C': {'CLST':'K','CLMD':'','CNST':'','TERM':'CTERM'},
                'Trypsin': {'CLST':'RK','CLMD':'','CNST':'P','TERM':'CTERM'},
                'Trypsin/P': {'CLST':'RK','CLMD':'','CNST':'','TERM':'CTERM'},
                'V8 (D,E)': {'CLST':'DE','CLMD':'','CNST':'','TERM':'CTERM'},
                'V8 (E)': {'CLST':'E','CLMD':'','CNST':'','TERM':'CTERM'},
            },
            'CMOD':{
                '4-vinyl-pyridine (C)': '+C7H7N@C',
                'Acrylamide (C)': '+C3H5ON@C',
                'Iodoacetamide (C)': '+C2H3ON@C',
                'Iodoacetic acid (C)': '+C2H2O2@C',
                'Performic acid (C+O3)': '+O3@C',
                'Performic acid (M+O2)': '+O2@M',
                'Performic acid (M+O)': '+O@M',
            },
            'PMOD':{
                '4-vinyl-pyridine (C)': '+C7H7N@C',
                'Acrylamide (C)': '+C3H5ON@C',
                'Iodoacetamide (C)': '+C2H3ON@C',
                'Iodoacetic acid (C)': '+C2H2O2@C',
                'Nitration (Y)': '+NO2-H@Y',
                'Oxidation (M)': '+O@M',
                'Oxidation (W)': '+O@W',
                'Performic acid (C+O3)': '+O@C',
                'Performic acid (M+O2)': '+O2@M',
                'Performic acid (M+O)': '+O@M',
                'Phosphorylation (S)': '+HPO3@S',
                'Phosphorylation (T)': '+HPO3@T',
                'Phosphorylation (Y)': '+HPO3@Y',
                'Phosphorylation (S,T)': '+HPO3@ST',
                'Phosphorylation (S,Y)': '+HPO3@SY',
                'Phosphorylation (T,Y)': '+HPO3@TY',
                'Phosphorylation (S,T,Y)': '+HPO3@STY',
            },
        }
        
        # update databases
        self.paramDatabase_choice.Clear()
        names = sorted(self.currentParams['DBSE'].keys())
        for item in names:
            self.paramDatabase_choice.Append(item)
        if config.profound['database'] in names:
            self.paramDatabase_choice.Select(names.index(config.profound['database']))
        
        # update taxonomy
        self.paramTaxonomy_choice.Clear()
        for item in self.currentParams['SPEC']:
            self.paramTaxonomy_choice.Append(item)
        if config.profound['taxonomy'] in self.currentParams['SPEC']:
            self.paramTaxonomy_choice.Select(self.currentParams['SPEC'].index(config.profound['taxonomy']))
        
        # update enzymes
        self.paramEnzyme_choice.Clear()
        names = sorted(self.currentParams['ENZ'].keys())
        for item in names:
            self.paramEnzyme_choice.Append(item)
        if config.profound['enzyme'] in names:
            self.paramEnzyme_choice.Select(names.index(config.profound['enzyme']))
        
        # update fixed modifications
        self.paramFixedMods_listbox.Clear()
        names = sorted(self.currentParams['CMOD'].keys())
        for item in names:
            self.paramFixedMods_listbox.Append(item)
        for item in config.profound['fixedMods']:
            if item in names:
                self.paramFixedMods_listbox.Select(names.index(item))
        
        # update variable modifications
        self.paramVariableMods_listbox.Clear()
        names = sorted(self.currentParams['PMOD'].keys())
        for item in names:
            self.paramVariableMods_listbox.Append(item)
        for item in config.profound['variableMods']:
            if item in names:
                self.paramVariableMods_listbox.Select(names.index(item))
        
        # update modifications count
        self.onModificationSelected()
    # ----
    
    
    def makeSearchHTML(self):
        """Format data to profound html."""
        
        # make html page
        buff = '<?xml version="1.0" encoding="utf-8"?>\n'
        buff += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        buff += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        buff += '<head>\n'
        buff += '  <title>mMass - ProFound Search</title>\n'
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
        buff += '  <form action="%s" id="mainSearch" method="post">\n' % (config.profound['script'])
        buff += '    <div style="display:none;">\n\n'
        
        buff += '      <input type="text" name="PASS" value="0" />\n'
        buff += '      <input type="text" name="ERRP" value="0.5" />\n'
        buff += '      <input type="text" name="SEARCHP" value="Identify Protein" />\n'
        buff += '      <input type="text" name="FORM" value="1" />\n'
        buff += '      <input type="text" name="ENZY" value="USER" />\n'
        
        buff += '      <input type="text" name="LABL" value="%s" />\n' % (self._escape(config.profound['title']))
        buff += '      <input type="text" name="DBSE" value="%s" />\n' % (self._escape(self.currentParams['DBSE'][config.profound['database']]))
        buff += '      <input type="text" name="MCLV" value="%s" />\n' % (config.profound['miscleavages'])
        buff += '      <input type="text" name="MINM" value="%s" />\n' % (config.profound['proteinMassLow'])
        buff += '      <input type="text" name="MAXM" value="%s" />\n' % (config.profound['proteinMassHigh'])
        buff += '      <input type="text" name="MINP" value="%s" />\n' % (config.profound['proteinPILow'])
        buff += '      <input type="text" name="MAXP" value="%s" />\n' % (config.profound['proteinPIHigh'])
        buff += '      <input type="text" name="ERRA" value="%s" />\n' % (config.profound['peptideTol'])
        buff += '      <input type="text" name="ERRM" value="%s" />\n' % (config.profound['peptideTol'])
        buff += '      <input type="text" name="ERRT" value="%s" />\n' % (config.profound['peptideTolUnits'])
        buff += '      <input type="text" name="CHRG" value="%s" />\n' % (config.profound['charge'])
        buff += '      <input type="text" name="EXPT" value="%s" />\n' % (config.profound['expectation'])
        buff += '      <input type="text" name="NRET" value="%s" />\n' % (config.profound['candidates'])
        buff += '      <input type="text" name="CLST" value="%s" />\n' % (self.currentParams['ENZ'][config.profound['enzyme']]['CLST'])
        buff += '      <input type="text" name="CNST" value="%s" />\n' % (self.currentParams['ENZ'][config.profound['enzyme']]['CNST'])
        buff += '      <input type="text" name="CLMD" value="%s" />\n' % (self.currentParams['ENZ'][config.profound['enzyme']]['CLMD'])
        buff += '      <input type="text" name="TERM" value="%s" />\n' % (self.currentParams['ENZ'][config.profound['enzyme']]['TERM'])
        
        taxonomy = config.profound['taxonomy'].replace('. ', '')
        taxonomy = taxonomy.replace(' ','-')
        buff += '      <input type="text" name="SPEC" value="%s" />\n' % (self._escape(taxonomy))
        
        for mod in config.profound['fixedMods']:
            buff += '      <input type="text" name="CMOD" value="%s" />\n' % (self.currentParams['CMOD'][mod])
        for mod in config.profound['variableMods']:
            buff += '      <input type="text" name="PMOD" value="%s" />\n' % (self.currentParams['PMOD'][mod])
        
        if config.profound['massType'] == 'Average':
            buff += '      <textarea name="APKS">%s</textarea>\n' % (self.paramQuery_value.GetValue())
            buff += '      <textarea name="MPKS"></textarea>\n'
        else:
            buff += '      <textarea name="APKS"></textarea>\n'
            buff += '      <textarea name="MPKS">%s</textarea>\n' % (self.paramQuery_value.GetValue())
        
        if config.profound['ranking'] == 'zscore':
            buff += '      <input type="text" name="EXPECT" value="0" />\n'
        else:
            buff += '      <input type="text" name="EXPECT" value="1" />\n'
        
        buff += '    </div>\n\n'
        
        buff += '    <div id="info">\n'
        buff += '      <h1>mMass - ProFound Search</h1>\n'
        buff += '      <p id="sending">Sending data to ProFound &hellip;</p>\n'
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
    
    

