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
import threading
import wx
import numpy

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy

from gui.panel_match import panelMatch
from gui.panel_monomer_library import panelMonomerLibrary


# FLOATING PANEL WITH SEQUENCE TOOLS
# ----------------------------------

class panelSequence(wx.MiniFrame):
    """Sequence tools."""
    
    def __init__(self, parent, tool='editor'):
        wx.MiniFrame.__init__(self, parent, -1, 'Sequence', size=(500, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.matchPanel = None
        self.monomerLibraryPanel = None
        
        self.processing = None
        
        self.currentTool = tool
        self.currentSequence = mspy.sequence('')
        self.currentDigest = None
        self.currentFragments = None
        self.currentSearch = None
        
        self._digestFilter = 0
        self._fragmentsFilter = 0
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
        
        # select default tool
        self.onToolSelected(tool=self.currentTool)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        sequence = self.makeSequencePanel()
        modify = self.makeModificationsPanel()
        digest = self.makeDigestPanel()
        fragment = self.makeFragmentPanel()
        search = self.makeSearchPanel()
        gauge = self.makeGaugePanel()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(sequence, 1, wx.EXPAND, 0)
        self.mainSizer.Add(modify, 1, wx.EXPAND, 0)
        self.mainSizer.Add(digest, 1, wx.EXPAND, 0)
        self.mainSizer.Add(fragment, 1, wx.EXPAND, 0)
        self.mainSizer.Add(search, 1, wx.EXPAND, 0)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        self.mainSizer.Hide(5)
        self.mainSizer.Hide(6)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make buttons
        self.editor_butt = wx.BitmapButton(panel, ID_sequenceEditor, images.lib['sequenceEditorOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.editor_butt.SetToolTip(wx.ToolTip("Sequence editor"))
        self.editor_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.modifications_butt = wx.BitmapButton(panel, ID_sequenceModifications, images.lib['sequenceModificationsOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.modifications_butt.SetToolTip(wx.ToolTip("Sequence modifications"))
        self.modifications_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.digest_butt = wx.BitmapButton(panel, ID_sequenceDigest, images.lib['sequenceDigestOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.digest_butt.SetToolTip(wx.ToolTip("Protein digest"))
        self.digest_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.fragment_butt = wx.BitmapButton(panel, ID_sequenceFragment, images.lib['sequenceFragmentOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.fragment_butt.SetToolTip(wx.ToolTip("Peptide fragmentation"))
        self.fragment_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.search_butt = wx.BitmapButton(panel, ID_sequenceSearch, images.lib['sequenceSearchOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.search_butt.SetToolTip(wx.ToolTip("Mass search"))
        self.search_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        # pack elements
        tools = wx.BoxSizer(wx.HORIZONTAL)
        tools.AddSpacer(mwx.TOOLBAR_LSPACE)
        tools.Add(self.editor_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        tools.Add(self.modifications_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        tools.Add(self.digest_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        tools.Add(self.fragment_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        tools.Add(self.search_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.Add(tools, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.makeSequenceToolbar(panel), 1, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.makeModificationsToolbar(panel), 1, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.makeDigestToolbar(panel), 1, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.makeFragmentToolbar(panel), 1, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.makeSearchToolbar(panel), 1, wx.ALIGN_CENTER_VERTICAL)
        
        self.toolbar.Hide(1)
        self.toolbar.Hide(2)
        self.toolbar.Hide(3)
        self.toolbar.Hide(4)
        self.toolbar.Hide(5)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeSequenceToolbar(self, panel):
        """Make toolbar for sequence panel."""
        
        # make elements
        self.monomerLibrary_butt = wx.BitmapButton(panel, -1, images.lib['toolsLibrary'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.monomerLibrary_butt.SetToolTip(wx.ToolTip("Monomer library"))
        self.monomerLibrary_butt.Bind(wx.EVT_BUTTON, self.onMonomerLibrary)
        
        sequenceType_label = wx.StaticText(panel, -1, "Sequence type:")
        sequenceType_label.SetFont(wx.SMALL_FONT)
        
        self.sequenceType_choice = wx.Choice(panel, -1, choices=['Regular amino acids', 'Custom'], size=(-1, mwx.SMALL_CHOICE_HEIGHT))
        self.sequenceType_choice.Select(0)
        self.sequenceType_choice.Bind(wx.EVT_CHOICE, self.onSequenceType)
        
        self.sequenceCyclic_check = wx.CheckBox(panel, -1, "Cyclic")
        self.sequenceCyclic_check.SetFont(wx.SMALL_FONT)
        self.sequenceCyclic_check.Bind(wx.EVT_CHECKBOX, self.onSequenceCyclic)
        
        self.pattern_butt = wx.Button(panel, -1, "Pattern", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.pattern_butt.Bind(wx.EVT_BUTTON, self.onSequencePattern)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        sizer.Add(self.monomerLibrary_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(sequenceType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.sequenceType_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.sequenceCyclic_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.pattern_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        return sizer
    # ----
    
    
    def makeModificationsToolbar(self, panel):
        """Make toolbar for modifications panel."""
        
        # make elements
        self.modsPresets_butt = wx.BitmapButton(panel, -1, images.lib['toolsPresets'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.modsPresets_butt.SetToolTip(wx.ToolTip("Modifications presets"))
        self.modsPresets_butt.Bind(wx.EVT_BUTTON, self.onPresets)
        
        self.modsSpecifity_check = wx.CheckBox(panel, -1, "Show specific modifications only")
        self.modsSpecifity_check.SetFont(wx.SMALL_FONT)
        self.modsSpecifity_check.SetValue(True)
        self.modsSpecifity_check.Bind(wx.EVT_CHECKBOX, self.onSpecifityFilter)
        
        self.modsAdd_butt = wx.Button(panel, -1, "Add", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.modsAdd_butt.Bind(wx.EVT_BUTTON, self.onAddModification)
        
        self.modsRemove_butt = wx.Button(panel, -1, "Remove", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.modsRemove_butt.Bind(wx.EVT_BUTTON, self.onRemoveModifications)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        sizer.Add(self.modsPresets_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.modsSpecifity_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.modsAdd_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.modsRemove_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        return sizer
    # ----
    
    
    def makeDigestToolbar(self, panel):
        """Make toolbar for digest panel."""
        
        # make elements
        digestMassType_label = wx.StaticText(panel, -1, "Mass:")
        digestMassType_label.SetFont(wx.SMALL_FONT)
        
        self.digestMassTypeMo_radio = wx.RadioButton(panel, -1, "Mo", style=wx.RB_GROUP)
        self.digestMassTypeMo_radio.SetFont(wx.SMALL_FONT)
        self.digestMassTypeMo_radio.SetValue(True)
        
        self.digestMassTypeAv_radio = wx.RadioButton(panel, -1, "Av")
        self.digestMassTypeAv_radio.SetFont(wx.SMALL_FONT)
        self.digestMassTypeAv_radio.SetValue(config.sequence['digest']['massType'])
        
        digestMaxCharge_label = wx.StaticText(panel, -1, "Max charge:")
        digestMaxCharge_label.SetFont(wx.SMALL_FONT)
        
        self.digestMaxCharge_value = wx.TextCtrl(panel, -1, str(config.sequence['digest']['maxCharge']), size=(40, -1), validator=mwx.validator('int'))
        
        self.digestGenerate_butt = wx.Button(panel, -1, "Digest", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.digestGenerate_butt.Bind(wx.EVT_BUTTON, self.onDigest)
        
        self.digestMatch_butt = wx.Button(panel, -1, "Match", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.digestMatch_butt.Bind(wx.EVT_BUTTON, self.onMatch)
        
        self.digestAnnotate_butt = wx.Button(panel, -1, "Annotate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.digestAnnotate_butt.Bind(wx.EVT_BUTTON, self.onAnnotate)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        sizer.Add(digestMassType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.digestMassTypeMo_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.digestMassTypeAv_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(digestMaxCharge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.digestMaxCharge_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.digestGenerate_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.digestMatch_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.digestAnnotate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        return sizer
    # ----
    
    
    def makeFragmentToolbar(self, panel):
        """Make toolbar for fragment panel."""
        
        # make elements
        self.fragmentPresets_butt = wx.BitmapButton(panel, -1, images.lib['toolsPresets'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.fragmentPresets_butt.SetToolTip(wx.ToolTip("Fragments presets"))
        self.fragmentPresets_butt.Bind(wx.EVT_BUTTON, self.onPresets)
        
        fragmentMassType_label = wx.StaticText(panel, -1, "Mass:")
        fragmentMassType_label.SetFont(wx.SMALL_FONT)
        
        self.fragmentMassTypeMo_radio = wx.RadioButton(panel, -1, "Mo", style=wx.RB_GROUP)
        self.fragmentMassTypeMo_radio.SetFont(wx.SMALL_FONT)
        self.fragmentMassTypeMo_radio.SetValue(True)
        
        self.fragmentMassTypeAv_radio = wx.RadioButton(panel, -1, "Av")
        self.fragmentMassTypeAv_radio.SetFont(wx.SMALL_FONT)
        self.fragmentMassTypeAv_radio.SetValue(config.sequence['fragment']['massType'])
        
        fragmentMaxCharge_label = wx.StaticText(panel, -1, "Max charge:")
        fragmentMaxCharge_label.SetFont(wx.SMALL_FONT)
        
        self.fragmentMaxCharge_value = wx.TextCtrl(panel, -1, str(config.sequence['fragment']['maxCharge']), size=(40, -1), validator=mwx.validator('int'))
        
        self.fragmentGenerate_butt = wx.Button(panel, -1, "Fragment", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.fragmentGenerate_butt.Bind(wx.EVT_BUTTON, self.onFragment)
        
        self.fragmentMatch_butt = wx.Button(panel, -1, "Match", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.fragmentMatch_butt.Bind(wx.EVT_BUTTON, self.onMatch)
        
        self.fragmentAnnotate_butt = wx.Button(panel, -1, "Annotate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.fragmentAnnotate_butt.Bind(wx.EVT_BUTTON, self.onAnnotate)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        sizer.Add(self.fragmentPresets_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(fragmentMassType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fragmentMassTypeMo_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fragmentMassTypeAv_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(fragmentMaxCharge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.fragmentMaxCharge_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.fragmentGenerate_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.fragmentMatch_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.fragmentAnnotate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        return sizer
    # ----
    
    
    def makeSearchToolbar(self, panel):
        """Make toolbar for search panel."""
        
        # make elements
        searchMassType_label = wx.StaticText(panel, -1, "Mass:")
        searchMassType_label.SetFont(wx.SMALL_FONT)
        
        self.searchMass_value = wx.TextCtrl(panel, -1, "", size=(100, -1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        self.searchMass_value.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        
        self.searchMassTypeMo_radio = wx.RadioButton(panel, -1, "Mo", style=wx.RB_GROUP)
        self.searchMassTypeMo_radio.SetFont(wx.SMALL_FONT)
        self.searchMassTypeMo_radio.SetValue(True)
        
        self.searchMassTypeAv_radio = wx.RadioButton(panel, -1, "Av")
        self.searchMassTypeAv_radio.SetFont(wx.SMALL_FONT)
        self.searchMassTypeAv_radio.SetValue(config.sequence['search']['massType'])
        
        searchCharge_label = wx.StaticText(panel, -1, "Peak charge:")
        searchCharge_label.SetFont(wx.SMALL_FONT)
        
        self.searchCharge_value = wx.TextCtrl(panel, -1, str(config.sequence['search']['charge']), size=(40, -1), validator=mwx.validator('int'))
        
        self.searchGenerate_butt = wx.Button(panel, -1, "Search", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.searchGenerate_butt.Bind(wx.EVT_BUTTON, self.onSearch)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        sizer.Add(searchMassType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.searchMass_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.searchMassTypeMo_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.searchMassTypeAv_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(searchCharge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.searchCharge_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.searchGenerate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        return sizer
    # ----
    
    
    def makeSequencePanel(self):
        """Make compound summary panel."""
        
        # init panels
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        panel = wx.Panel(self, -1)
        
        # make controls
        self.sequenceInfo_label = wx.StaticText(ctrlPanel, -1, "Sequence Info", size=(600,-1))
        self.sequenceInfo_label.SetFont(wx.SMALL_FONT)
        
        # make elements
        self.sequenceTitle_value = wx.TextCtrl(panel, -1, self.currentSequence.title, size=(420, -1))
        self.sequenceTitle_value.Bind(wx.EVT_TEXT, self.onSequenceTitle)
        
        sequenceAccession_label = wx.StaticText(panel, -1, "Acc.:")
        sequenceAccession_label.SetFont(wx.SMALL_FONT)
        
        self.sequenceAccession_value = wx.TextCtrl(panel, -1, self.currentSequence.accession, size=(140, -1))
        self.sequenceAccession_value.Bind(wx.EVT_TEXT, self.onSequenceAccession)
        
        self.sequenceCanvas = sequenceCanvas(panel, -1, sequence=self.currentSequence,  size=(600, 200))
        self.sequenceCanvas.Bind(wx.EVT_KEY_DOWN, self.onSequence)
        self.sequenceCanvas.Bind(wx.EVT_LEFT_DOWN, self.onSequence)
        self.sequenceCanvas.Bind(wx.EVT_RIGHT_DOWN, self.onSequence)
        self.sequenceCanvas.Bind(wx.EVT_MOTION, self.onSequence)
        
        self.sequenceGrid = sequenceGrid(self, panel, sequence=self.currentSequence, items=config.sequence['editor']['gridSize'])
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(self.sequenceInfo_label, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack elements
        sequenceTitleSizer = wx.BoxSizer(wx.HORIZONTAL)
        sequenceTitleSizer.Add(self.sequenceTitle_value, 1, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sequenceTitleSizer.Add(sequenceAccession_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sequenceTitleSizer.Add(self.sequenceAccession_value, 0)
        
        self.sequenceEditorSizer = wx.BoxSizer(wx.VERTICAL)
        if wx.Platform == '__WXMAC__':
            self.sequenceEditorSizer.Add(sequenceTitleSizer, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        else:
            self.sequenceEditorSizer.Add(sequenceTitleSizer, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        self.sequenceEditorSizer.Add(self.sequenceCanvas, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        self.sequenceEditorSizer.Add(self.sequenceGrid, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        self.sequenceEditorSizer.Hide(2)
        
        self.sequenceEditorSizer.Fit(panel)
        panel.SetSizer(self.sequenceEditorSizer)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(panel, 1, wx.EXPAND)
        
        return mainSizer
    # ----
    
    
    def makeModificationsPanel(self):
        """Make controls for sequence modifications."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        modsPosition_label = wx.StaticText(ctrlPanel, -1, "Position:")
        modsPosition_label.SetFont(wx.SMALL_FONT)
        
        self.modsResidue_choice = wx.Choice(ctrlPanel, -1, choices=[], size=(130, mwx.SMALL_CHOICE_HEIGHT))
        self.modsResidue_choice.Bind(wx.EVT_CHOICE, self.onResidueSelected)
        
        self.modsPosition_choice = wx.Choice(ctrlPanel, -1, choices=[], size=(80, mwx.SMALL_CHOICE_HEIGHT))
        self.modsPosition_choice.Bind(wx.EVT_CHOICE, self.onPositionSelected)
        
        modsMod_label = wx.StaticText(ctrlPanel, -1, "Modification:")
        modsMod_label.SetFont(wx.SMALL_FONT)
        
        self.modsMod_choice = wx.Choice(ctrlPanel, -1, choices=[], size=(170, mwx.SMALL_CHOICE_HEIGHT))
        
        self.modsType_choice = wx.Choice(ctrlPanel, -1, choices=['Fixed', 'Variable'], size=(90, mwx.SMALL_CHOICE_HEIGHT))
        self.modsType_choice.Select(0)
        
        self.makeModificationsList()
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(modsPosition_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.modsResidue_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(10)
        controls.Add(self.modsPosition_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(modsMod_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.modsMod_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(10)
        controls.Add(self.modsType_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(self.modificationsList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makeDigestPanel(self):
        """Make controls for protein digest."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        digestEnzyme_label = wx.StaticText(ctrlPanel, -1, "Enzyme:")
        digestEnzyme_label.SetFont(wx.SMALL_FONT)
        
        enzymes = mspy.enzymes.keys()
        enzymes.sort()
        self.digestEnzyme_choice = wx.Choice(ctrlPanel, -1, choices=enzymes, size=(140, mwx.SMALL_CHOICE_HEIGHT))
        if config.sequence['digest']['enzyme'] in enzymes:
            self.digestEnzyme_choice.Select(enzymes.index(config.sequence['digest']['enzyme']))
        else:
            self.digestEnzyme_choice.Select(0)
        
        digestMiscl_label = wx.StaticText(ctrlPanel, -1, "Miscl.:")
        self.digestMiscl_value = wx.TextCtrl(ctrlPanel, -1, str(config.sequence['digest']['miscl']), size=(40, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('intPos'))
        digestMiscl_label.SetFont(wx.SMALL_FONT)
        self.digestMiscl_value.SetFont(wx.SMALL_FONT)
        
        digestLimits_label = wx.StaticText(ctrlPanel, -1, "Mass range:")
        digestLimits_label.SetFont(wx.SMALL_FONT)
        
        self.digestLowMass_value = wx.TextCtrl(ctrlPanel, -1, str(config.sequence['digest']['lowMass']), size=(45, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('intPos'))
        self.digestLowMass_value.SetFont(wx.SMALL_FONT)
        
        digestLimitsTo_label = wx.StaticText(ctrlPanel, -1, "-")
        digestLimitsTo_label.SetFont(wx.SMALL_FONT)
        
        self.digestHighMass_value = wx.TextCtrl(ctrlPanel, -1, str(config.sequence['digest']['highMass']), size=(45, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('intPos'))
        self.digestHighMass_value.SetFont(wx.SMALL_FONT)
        
        self.digestAllowMods_check = wx.CheckBox(ctrlPanel, -1, "Ignore mods")
        self.digestAllowMods_check.SetFont(wx.SMALL_FONT)
        self.digestAllowMods_check.SetValue(config.sequence['digest']['allowMods'])
        
        self.digestCoverage_label = wx.StaticText(ctrlPanel, -1, "")
        self.digestCoverage_label.SetFont(wx.SMALL_FONT)
        
        self.makeDigestList()
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(digestEnzyme_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.digestEnzyme_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(digestMiscl_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.digestMiscl_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(digestLimits_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.digestLowMass_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(digestLimitsTo_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.digestHighMass_value, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(self.digestAllowMods_check, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(self.digestCoverage_label, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(self.digestList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makeFragmentPanel(self):
        """Make controls for peptide fragmentation."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbarDouble'], size=(-1, mwx.CONTROLBAR_DOUBLE_HEIGHT))
        
        # make controls
        self.fragmentM_check = wx.CheckBox(ctrlPanel, -1, "M")
        self.fragmentM_check.SetFont(wx.SMALL_FONT)
        self.fragmentM_check.SetValue(config.sequence['fragment']['fragments'].count('M'))
        
        self.fragmentIm_check = wx.CheckBox(ctrlPanel, -1, "im")
        self.fragmentIm_check.SetFont(wx.SMALL_FONT)
        self.fragmentIm_check.SetValue(config.sequence['fragment']['fragments'].count('im'))
        
        self.fragmentA_check = wx.CheckBox(ctrlPanel, -1, "a")
        self.fragmentA_check.SetFont(wx.SMALL_FONT)
        self.fragmentA_check.SetValue(config.sequence['fragment']['fragments'].count('a'))
        
        self.fragmentB_check = wx.CheckBox(ctrlPanel, -1, "b")
        self.fragmentB_check.SetFont(wx.SMALL_FONT)
        self.fragmentB_check.SetValue(config.sequence['fragment']['fragments'].count('b'))
        
        self.fragmentC_check = wx.CheckBox(ctrlPanel, -1, "c")
        self.fragmentC_check.SetFont(wx.SMALL_FONT)
        self.fragmentC_check.SetValue(config.sequence['fragment']['fragments'].count('c'))
        
        self.fragmentX_check = wx.CheckBox(ctrlPanel, -1, "x")
        self.fragmentX_check.SetFont(wx.SMALL_FONT)
        self.fragmentX_check.SetValue(config.sequence['fragment']['fragments'].count('x'))
        
        self.fragmentY_check = wx.CheckBox(ctrlPanel, -1, "y")
        self.fragmentY_check.SetFont(wx.SMALL_FONT)
        self.fragmentY_check.SetValue(config.sequence['fragment']['fragments'].count('y'))
        
        self.fragmentZ_check = wx.CheckBox(ctrlPanel, -1, "z")
        self.fragmentZ_check.SetFont(wx.SMALL_FONT)
        self.fragmentZ_check.SetValue(config.sequence['fragment']['fragments'].count('z'))
        
        self.fragmentIntA_check = wx.CheckBox(ctrlPanel, -1, "int-a")
        self.fragmentIntA_check.SetFont(wx.SMALL_FONT)
        self.fragmentIntA_check.SetValue(config.sequence['fragment']['fragments'].count('int-a'))
        
        self.fragmentIntB_check = wx.CheckBox(ctrlPanel, -1, "int-b")
        self.fragmentIntB_check.SetFont(wx.SMALL_FONT)
        self.fragmentIntB_check.SetValue(config.sequence['fragment']['fragments'].count('int-b'))
        
        self.fragmentNLadder_check = wx.CheckBox(ctrlPanel, -1, "N-ladder")
        self.fragmentNLadder_check.SetFont(wx.SMALL_FONT)
        self.fragmentNLadder_check.SetValue(config.sequence['fragment']['fragments'].count('n-ladder'))
        
        self.fragmentCLadder_check = wx.CheckBox(ctrlPanel, -1, "C-ladder")
        self.fragmentCLadder_check.SetFont(wx.SMALL_FONT)
        self.fragmentCLadder_check.SetValue(config.sequence['fragment']['fragments'].count('c-ladder'))
        
        self.fragmentLossH2O_check = wx.CheckBox(ctrlPanel, -1, "-H2O")
        self.fragmentLossH2O_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossH2O_check.SetValue(config.sequence['fragment']['fragments'].count('-H2O'))
        
        self.fragmentLossNH3_check = wx.CheckBox(ctrlPanel, -1, "-NH3")
        self.fragmentLossNH3_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossNH3_check.SetValue(config.sequence['fragment']['fragments'].count('-NH3'))
        
        self.fragmentLossCO_check = wx.CheckBox(ctrlPanel, -1, "-CO")
        self.fragmentLossCO_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossCO_check.SetValue(config.sequence['fragment']['fragments'].count('-CO'))
        
        self.fragmentLossH3PO4_check = wx.CheckBox(ctrlPanel, -1, "-H3PO4")
        self.fragmentLossH3PO4_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossH3PO4_check.SetValue(config.sequence['fragment']['fragments'].count('-H3PO4'))
        
        self.fragmentLossDefined_check = wx.CheckBox(ctrlPanel, -1, "Defined losses")
        self.fragmentLossDefined_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossDefined_check.SetValue(config.sequence['fragment']['fragments'].count('losses'))
        self.fragmentLossDefined_check.SetToolTip(wx.ToolTip("Apply specific losses from monomer library."))
        
        self.fragmentLossCombi_check = wx.CheckBox(ctrlPanel, -1, "Combinations")
        self.fragmentLossCombi_check.SetFont(wx.SMALL_FONT)
        self.fragmentLossCombi_check.SetValue(config.sequence['fragment']['fragments'].count('losscombi'))
        
        self.fragmentGainH2O_check = wx.CheckBox(ctrlPanel, -1, "+H2O")
        self.fragmentGainH2O_check.SetFont(wx.SMALL_FONT)
        self.fragmentGainH2O_check.SetValue(config.sequence['fragment']['fragments'].count('+H2O'))
        self.fragmentGainH2O_check.SetToolTip(wx.ToolTip("Allowed for 'b' ions only."))
        
        self.fragmentGainCO_check = wx.CheckBox(ctrlPanel, -1, "+CO")
        self.fragmentGainCO_check.SetFont(wx.SMALL_FONT)
        self.fragmentGainCO_check.SetValue(config.sequence['fragment']['fragments'].count('+CO'))
        self.fragmentGainCO_check.SetToolTip(wx.ToolTip("Allowed for 'b' and 'c' ions only."))
        
        self.fragmentScrambling_check = wx.CheckBox(ctrlPanel, -1, "Allow scrambling")
        self.fragmentScrambling_check.SetFont(wx.SMALL_FONT)
        self.fragmentScrambling_check.SetValue(config.sequence['fragment']['fragments'].count('scrambling'))
        self.fragmentScrambling_check.SetToolTip(wx.ToolTip("Allow non-direct sequencing."))
        self.fragmentScrambling_check.Bind(wx.EVT_CHECKBOX, self.updateAvailableFragments)
        
        self.fragmentRemoveFiltered_check = wx.CheckBox(ctrlPanel, -1, "Remove filtered")
        self.fragmentRemoveFiltered_check.SetFont(wx.SMALL_FONT)
        self.fragmentRemoveFiltered_check.SetValue(config.sequence['fragment']['filterFragments'])
        
        self.makeFragmentsList()
        
        # pack controls
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(self.fragmentM_check, (0,0))
        grid.Add(self.fragmentIm_check, (1,0))
        
        grid.Add(self.fragmentA_check, (0,2))
        grid.Add(self.fragmentB_check, (0,3))
        grid.Add(self.fragmentC_check, (0,4))
        grid.Add(self.fragmentX_check, (1,2))
        grid.Add(self.fragmentY_check, (1,3))
        grid.Add(self.fragmentZ_check, (1,4))
        
        grid.Add(self.fragmentIntA_check, (0,6))
        grid.Add(self.fragmentIntB_check, (1,6))
        grid.Add(self.fragmentNLadder_check, (0,7))
        grid.Add(self.fragmentCLadder_check, (1,7))
        
        grid.Add(self.fragmentLossH2O_check, (0,9))
        grid.Add(self.fragmentLossNH3_check, (1,9))
        grid.Add(self.fragmentLossCO_check, (0,10))
        grid.Add(self.fragmentLossH3PO4_check, (1,10))
        grid.Add(self.fragmentLossDefined_check, (0,11))
        grid.Add(self.fragmentLossCombi_check, (1,11))
        
        grid.Add(self.fragmentGainH2O_check, (0,13))
        grid.Add(self.fragmentGainCO_check, (1,13))
        
        grid.Add(self.fragmentScrambling_check, (0,15))
        grid.Add(self.fragmentRemoveFiltered_check, (1,15))
        
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(grid, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(self.fragmentsList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makeSearchPanel(self):
        """Make controls for sequence search."""
        
        # init panel
        ctrlPanel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        searchEnzyme_label = wx.StaticText(ctrlPanel, -1, "Enzyme:")
        searchEnzyme_label.SetFont(wx.SMALL_FONT)
        
        enzymes = mspy.enzymes.keys()
        enzymes.sort()
        self.searchEnzyme_choice = wx.Choice(ctrlPanel, -1, choices=enzymes, size=(150, mwx.SMALL_CHOICE_HEIGHT))
        if config.sequence['search']['enzyme'] in enzymes:
            self.searchEnzyme_choice.Select(enzymes.index(config.sequence['search']['enzyme']))
        else:
            self.searchEnzyme_choice.Select(0)
        
        searchTolerance_label = wx.StaticText(ctrlPanel, -1, "Tolerance:")
        searchTolerance_label.SetFont(wx.SMALL_FONT)
        
        self.searchTolerance_value = wx.TextCtrl(ctrlPanel, -1, str(config.sequence['search']['tolerance']), size=(40, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        self.searchTolerance_value.SetFont(wx.SMALL_FONT)
        
        self.searchUnitsDa_radio = wx.RadioButton(ctrlPanel, -1, "Da", style=wx.RB_GROUP)
        self.searchUnitsDa_radio.SetFont(wx.SMALL_FONT)
        self.searchUnitsDa_radio.SetValue(True)
        
        self.searchUnitsPpm_radio = wx.RadioButton(ctrlPanel, -1, "ppm")
        self.searchUnitsPpm_radio.SetFont(wx.SMALL_FONT)
        
        if config.sequence['search']['units'] == 'ppm':
            self.searchUnitsPpm_radio.SetValue(True)
        
        self.searchSemiSpecific_check = wx.CheckBox(ctrlPanel, -1, "Semi-specific enzyme")
        self.searchSemiSpecific_check.SetFont(wx.SMALL_FONT)
        self.searchSemiSpecific_check.SetValue(config.sequence['search']['semiSpecific'])
        
        self.makeSearchList()
        
        # pack controls
        controls = wx.BoxSizer(wx.HORIZONTAL)
        controls.AddSpacer(mwx.CONTROLBAR_LSPACE)
        controls.Add(searchEnzyme_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.searchEnzyme_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        controls.AddSpacer(20)
        controls.Add(searchTolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.searchTolerance_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.searchUnitsDa_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        controls.Add(self.searchUnitsPpm_radio, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        controls.AddSpacer(20)
        controls.Add(self.searchSemiSpecific_check, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        controls.AddSpacer(mwx.CONTROLBAR_RSPACE)
        controls.Fit(ctrlPanel)
        ctrlPanel.SetSizer(controls)
        
        # pack main
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(ctrlPanel, 0, wx.EXPAND)
        mainSizer.Add(self.searchList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        
        return mainSizer
    # ----
    
    
    def makeGaugePanel(self):
        """Make processing gauge."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.gauge = mwx.gauge(panel, -1)
        
        stop_butt = wx.BitmapButton(panel, -1, images.lib['stopper'], style=wx.BORDER_NONE)
        stop_butt.Bind(wx.EVT_BUTTON, self.onStop)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.gauge, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(stop_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        
        # fit layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND|wx.ALL, mwx.GAUGE_SPACE)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeModificationsList(self):
        """Make modifications list."""
        
        # init peaklist
        self.modificationsList = mwx.sortListCtrl(self, -1, size=(671, 200), style=mwx.LISTCTRL_STYLE_MULTI)
        self.modificationsList.SetFont(wx.SMALL_FONT)
        self.modificationsList.setSecondarySortColumn(1)
        self.modificationsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # make columns
        self.modificationsList.InsertColumn(0, "position", wx.LIST_FORMAT_CENTER)
        self.modificationsList.InsertColumn(1, "modification", wx.LIST_FORMAT_LEFT)
        self.modificationsList.InsertColumn(2, "type", wx.LIST_FORMAT_CENTER)
        self.modificationsList.InsertColumn(3, "mo. mass", wx.LIST_FORMAT_RIGHT)
        self.modificationsList.InsertColumn(4, "av. mass", wx.LIST_FORMAT_RIGHT)
        self.modificationsList.InsertColumn(5, "formula", wx.LIST_FORMAT_LEFT)
        
        # set column widths
        for col, width in enumerate((90,143,70,90,90,168)):
            self.modificationsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeDigestList(self):
        """Make digest list."""
        
        # init peaklist
        self.digestList = mwx.sortListCtrl(self, -1, size=(778, 300), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.digestList.SetFont(wx.SMALL_FONT)
        self.digestList.setSecondarySortColumn(2)
        self.digestList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.digestList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.digestList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.digestList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        if wx.Platform == '__WXMAC__':
            self.digestList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.digestList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.digestList.InsertColumn(0, "slice", wx.LIST_FORMAT_CENTER)
        self.digestList.InsertColumn(1, "mis.", wx.LIST_FORMAT_CENTER)
        self.digestList.InsertColumn(2, "m/z", wx.LIST_FORMAT_RIGHT)
        self.digestList.InsertColumn(3, "z", wx.LIST_FORMAT_CENTER)
        self.digestList.InsertColumn(4, "sequence", wx.LIST_FORMAT_LEFT)
        self.digestList.InsertColumn(5, "error", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((80,47,90,40,440,60)):
            self.digestList.SetColumnWidth(col, width)
    # ----
    
    
    def makeFragmentsList(self):
        """Make fragments list."""
        
        # init peaklist
        self.fragmentsList = mwx.sortListCtrl(self, -1, size=(801, 300), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.fragmentsList.SetFont(wx.SMALL_FONT)
        self.fragmentsList.setSecondarySortColumn(1)
        self.fragmentsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.fragmentsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.fragmentsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.fragmentsList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        if wx.Platform == '__WXMAC__':
            self.fragmentsList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.fragmentsList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.fragmentsList.InsertColumn(0, "ion", wx.LIST_FORMAT_LEFT)
        self.fragmentsList.InsertColumn(1, "slice", wx.LIST_FORMAT_CENTER)
        self.fragmentsList.InsertColumn(2, "m/z", wx.LIST_FORMAT_RIGHT)
        self.fragmentsList.InsertColumn(3, "z", wx.LIST_FORMAT_CENTER)
        self.fragmentsList.InsertColumn(4, "sequence", wx.LIST_FORMAT_LEFT)
        self.fragmentsList.InsertColumn(5, "error", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((120,130,90,40,340,60)):
            self.fragmentsList.SetColumnWidth(col, width)
    # ----
    
    
    def makeSearchList(self):
        """Make search list."""
        
        # init peaklist
        self.searchList = mwx.sortListCtrl(self, -1, size=(656, 250), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.searchList.SetFont(wx.SMALL_FONT)
        self.searchList.setSecondarySortColumn(1)
        self.searchList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.searchList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.searchList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.searchList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        if wx.Platform == '__WXMAC__':
            self.searchList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.searchList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.searchList.InsertColumn(0, "slice", wx.LIST_FORMAT_CENTER)
        self.searchList.InsertColumn(1, "m/z", wx.LIST_FORMAT_RIGHT)
        self.searchList.InsertColumn(2, "sequence", wx.LIST_FORMAT_LEFT)
        self.searchList.InsertColumn(3, "error", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((80,90,405,60)):
            self.searchList.SetColumnWidth(col, width)
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close match panel
        if self.matchPanel:
            self.matchPanel.Close()
        
        # close library panel
        if self.monomerLibraryPanel:
            self.monomerLibraryPanel.Close()
        
        # close self
        self.Destroy()
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(6)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(6)
            self.processing = None
            mspy.start()
        
        # fit layout
        self.Layout()
        self.mainSizer.Fit(self)
        try: wx.Yield()
        except: pass
    # ----
    
    
    def onStop(self, evt):
        """Cancel current processing."""
        
        if self.processing and self.processing.isAlive():
            mspy.stop()
        else:
            wx.Bell()
    # ----
    
    
    def onPresets(self, evt):
        """Show selected presets."""
        
        # get presets
        if self.currentTool == 'modifications':
            presets = libs.presets['modifications'].keys()
        elif self.currentTool == 'fragment':
            presets = libs.presets['fragments'].keys()
        presets.sort()
        
        # make menu
        self.presets_popup = wx.Menu()
        for name in presets:
            item = self.presets_popup.Append(-1, name)
            self.presets_popup.Bind(wx.EVT_MENU, self.onPresetsSelected, item)
        
        self.presets_popup.AppendSeparator()
        item = self.presets_popup.Append(-1, "Save as Presets...")
        self.presets_popup.Bind(wx.EVT_MENU, self.onPresetsSave, item)
        
        # popup menu
        self.PopupMenu(self.presets_popup)
        self.presets_popup.Destroy()
    # ----
    
    
    def onPresetsSelected(self, evt):
        """Load selected modification presets."""
        
        # get presets name
        item = self.presets_popup.FindItemById(evt.GetId())
        name = item.GetText()
        
        # apply presets
        if self.currentTool == 'modifications':
            self.applyModificationsPresets(name)
        elif self.currentTool == 'fragment':
            self.applyFragmentsPresets(name)
    # ----
    
    
    def onPresetsSave(self, evt):
        """Save current params as presets."""
        
        # save presets
        if self.currentTool == 'modifications':
            self.saveModificationsPresets()
        elif self.currentTool == 'fragment':
            self.saveFragmentsPresets()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close match panel
        if self.matchPanel:
            self.matchPanel.Close()
        
        # get the tool
        if evt != None:
            tool = 'editor'
            if evt and evt.GetId() == ID_sequenceEditor:
                tool = 'editor'
            elif evt and evt.GetId() == ID_sequenceModifications:
                tool = 'modifications'
            elif evt and evt.GetId() == ID_sequenceDigest:
                tool = 'digest'
            elif evt and evt.GetId() == ID_sequenceFragment:
                tool = 'fragment'
            elif evt and evt.GetId() == ID_sequenceSearch:
                tool = 'search'
        
        # block some tools for cyclic or custom sequence
        if tool == 'editor':
            pass
        elif self.currentSequence == None:
            wx.Bell()
            return
        elif self.currentSequence.chainType != 'aminoacids' and not tool in ('editor', 'fragment'):
            wx.Bell()
            title = "Selected tool is not available for custom-type sequences."
            message = "To enable this tool, check the sequence type specified in the editor\nand if possible, convert your sequence to use regular amino acids."
            dlg = mwx.dlgMessage(self, title, message)
            dlg.ShowModal()
            dlg.Destroy()
            return
        elif self.currentSequence.cyclic and not tool in ('editor', 'modifications','fragment'):
            wx.Bell()
            title = "Selected tool is not available for cyclic sequences."
            message = "To enable this tool, linearize the sequence in the editor."
            dlg = mwx.dlgMessage(self, title, message)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        self.mainSizer.Hide(4)
        self.mainSizer.Hide(5)
        
        # hide toolbars
        self.toolbar.Hide(1)
        self.toolbar.Hide(2)
        self.toolbar.Hide(3)
        self.toolbar.Hide(4)
        self.toolbar.Hide(5)
        
        # set icons off
        self.editor_butt.SetBitmapLabel(images.lib['sequenceEditorOff'])
        self.modifications_butt.SetBitmapLabel(images.lib['sequenceModificationsOff'])
        self.digest_butt.SetBitmapLabel(images.lib['sequenceDigestOff'])
        self.fragment_butt.SetBitmapLabel(images.lib['sequenceFragmentOff'])
        self.search_butt.SetBitmapLabel(images.lib['sequenceSearchOff'])
        
        # set panel
        if tool == 'editor':
            self.SetTitle("Sequence Editor")
            self.editor_butt.SetBitmapLabel(images.lib['sequenceEditorOn'])
            self.toolbar.Show(1)
            self.mainSizer.Show(1)
            
        elif tool == 'modifications':
            self.SetTitle("Sequence Modifications")
            self.modifications_butt.SetBitmapLabel(images.lib['sequenceModificationsOn'])
            self.toolbar.Show(2)
            self.mainSizer.Show(2)
            
        elif tool == 'digest':
            self.SetTitle("Protein Digest")
            self.digest_butt.SetBitmapLabel(images.lib['sequenceDigestOn'])
            self.toolbar.Show(3)
            self.mainSizer.Show(3)
            
        elif tool == 'fragment':
            self.SetTitle("Peptide Fragmentation")
            self.fragment_butt.SetBitmapLabel(images.lib['sequenceFragmentOn'])
            self.toolbar.Show(4)
            self.mainSizer.Show(4)
            
        elif tool == 'search':
            self.SetTitle("Mass Search")
            self.search_butt.SetBitmapLabel(images.lib['sequenceSearchOn'])
            self.toolbar.Show(5)
            self.mainSizer.Show(5)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onMonomerLibrary(self, evt):
        """Show monomers library."""
        
        # destroy panel
        if self.monomerLibraryPanel:
            self.monomerLibraryPanel.Close()
            return
        
        # set filters
        filterIn = []
        filterOut = []
        if self.currentSequence == None or self.currentSequence.chainType == 'aminoacids':
            filterIn = ['_InternalAA']
            DnD = False
        else:
            filterOut = ['_InternalAA']
            DnD = True
        
        # init library panel
        if not self.monomerLibraryPanel:
            self.monomerLibraryPanel = panelMonomerLibrary(self, filterIn=filterIn, filterOut=filterOut, DnD=DnD)
            pos = self.GetPosition()
            size = self.monomerLibraryPanel.GetSize()
            self.monomerLibraryPanel.SetPosition((pos[0]-size[0]-20, pos[1]+50))
            self.monomerLibraryPanel.Show(True)
        
        # raise panel
        self.monomerLibraryPanel.Raise()
    # ----
    
    
    def onSequenceType(self, evt):
        """Change sequence editor and chain type."""
        
        # get chain type
        if self.sequenceType_choice.GetStringSelection() == 'Regular amino acids':
            chainType = 'aminoacids'
            before = 'Custom'
        elif self.sequenceType_choice.GetStringSelection() == 'Custom':
            chainType = 'custom'
            before = 'Regular amino acids'
        
        # ask to process
        if len(self.currentSequence):
            title = 'Do you really want to change the sequence type?'
            message = 'Current sequence definition will be lost.'
            buttons = [(wx.ID_CANCEL, "Cancel", 80, False, 15), (wx.ID_OK, "Change", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
            else:
                dlg.Destroy()
                self.sequenceType_choice.SetStringSelection(before)
                return
        
        # empty current sequence and set new type
        del self.currentSequence[:]
        self.currentSequence.chainType = chainType
        
        # set editor
        if chainType == 'aminoacids':
            self.sequenceCanvas.setData(self.currentSequence)
            self.sequenceGrid.setData(None)
            self.sequenceEditorSizer.Hide(2)
            self.sequenceEditorSizer.Show(1)
        elif chainType == 'custom':
            self.sequenceGrid.setData(self.currentSequence)
            self.sequenceCanvas.setData(None)
            self.sequenceEditorSizer.Hide(1)
            self.sequenceEditorSizer.Show(2)
        
        # set editor status
        self.sequenceCanvas.setModified(True)
        self.sequenceGrid.setModified(True)
        
        # update sequence info
        self.onSequenceChanged()
        
        # set monomer filter to library
        if self.monomerLibraryPanel:
            if chainType == 'aminoacids':
                self.monomerLibraryPanel.setFilter(filterIn=['_InternalAA'])
                self.monomerLibraryPanel.enableDnD(False)
            else:
                self.monomerLibraryPanel.setFilter(filterOut=['_InternalAA'])
                self.monomerLibraryPanel.enableDnD(True)
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onSequenceCyclic(self, evt):
        """Set current sequence cyclic or linear."""
        
        # make sequence cyclic/linear
        value = self.sequenceCyclic_check.IsChecked()
        self.currentSequence.cyclize(value)
        
        # set editor as modified
        if self.currentSequence.chainType != 'aminoacids':
            self.sequenceGrid.setModified(True)
            self.sequenceGrid.refresh()
        else:
            self.sequenceCanvas.setModified(True)
            self.sequenceCanvas.refresh()
        
        # update sequence info
        self.onSequenceChanged()
    # ----
    
    
    def onSequenceTitle(self, evt):
        """Update sequence title."""
        
        self.currentSequence.title = self.sequenceTitle_value.GetValue()
        self.parent.onDocumentChanged(items=('seqtitle'))
    # ----
    
    
    def onSequenceAccession(self, evt):
        """Update sequence accession number."""
        
        self.currentSequence.accession = self.sequenceAccession_value.GetValue()
        self.parent.onDocumentChanged(items=('seqaccession'))
    # ----
    
    
    def onSequence(self, evt):
        """Update gui."""
        evt.Skip()
        wx.CallAfter(self.onSequenceChanged)
    # ----
    
    
    def onSequenceChanged(self):
        """Update info and erase results if sequence has changed."""
        
        # update sequence info
        self.updateSequenceInfo()
        
        # check sequence
        if self.currentSequence == None:
            return
        
        # set editor
        editor = self.sequenceCanvas
        if self.currentSequence.chainType != 'aminoacids':
            editor = self.sequenceGrid
        
        # skip if sequence has not changed - cursor move only
        if editor.ismodified():
            editor.setModified(False)
            
            # update modifications panel
            self.updateAvailableResidues()
            self.updateModificationsList()
            
            # update digest panel
            if self.currentDigest != None:
                self.currentDigest = None
                self.updateDigestList()
                self.updateCoverage()
            
            # update fragment panel
            self.updateAvailableFragments()
            if self.currentFragments != None:
                self.currentFragments = None
                self.updateFragmentsList()
            
            # update search panel
            if self.currentSearch != None:
                self.currentSearch = None
                self.updateSearchList()
            
            # close match panel
            if self.matchPanel:
                self.matchPanel.Close()
            
            # erase matches
            if self.currentSequence.matches:
                del self.currentSequence.matches[:]
            
            # update document status
            self.parent.onDocumentChanged(items=('sequence', 'matches'))
    # ----
    
    
    def onSequencePattern(self, evt):
        """Show isotopic pattern for whole sequence."""
        
        # get formula
        if self.currentSequence:
            formula = self.currentSequence.formula()
        else:
            wx.Bell()
            return
        
        # send data to Mass Calculator tool
        self.parent.onToolsMassCalculator(formula=formula, fwhm=0.5)
    # ----
    
    
    def onAddModification(self, evt):
        """Get data and add modification."""
        
        # get data
        try:
            residue = self.modsResidue_choice.GetStringSelection()
            position = self.modsPosition_choice.GetStringSelection()
            modification = self.modsMod_choice.GetStringSelection()
            modtype = self.modsType_choice.GetStringSelection()
        except:
            return
        
        # check data
        if not (modification and modtype) or (not position and not residue in ('N-terminus', 'C-terminus')):
            wx.Bell()
            return
        
        # set terminal modification
        if residue == 'N-terminus':
            amino = 'nTerm'
        elif residue == 'C-terminus':
            amino = 'cTerm'
        
        # set residual modification
        else:
            pos = position.split(' ')
            if pos[0] == 'All':
                amino = str(pos[1])
            else:
                amino = int(pos[1])-1
        
        # set modification type
        modtype = str(modtype[0].lower())
        
        # check and apply modification
        if self.checkModifications(self.currentSequence, [modification, amino, modtype], config.sequence['digest']['maxMods']):
            self.currentSequence.modify(modification, amino, modtype)
            self.sequenceCanvas.setModified(True)
            self.sequenceCanvas.refresh()
            self.onSequenceChanged()
        else:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Modification cannot be applied.", message='Maximum number of modification was already applied\nto the same position.')
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onRemoveModifications(self, evt):
        """Remove selected modifications."""
        
        # get selected
        selected = self.modificationsList.getSelected()
        if not selected:
            return
        
        # delete modifications
        for index in selected:
            
            # get position
            position = self.modificationsList.GetItem(index, 0).GetText()
            pos = position.split(' ')
            if position == 'N-terminus':
                amino = 'nTerm'
            elif position == 'C-terminus':
                amino = 'cTerm'
            elif pos[0] == 'All':
                amino = str(pos[1])
            else:
                amino = int(pos[1])-1
            
            # get name
            name = self.modificationsList.GetItem(index, 1).GetText()
            
            # get type
            modtype = self.modificationsList.GetItem(index, 2).GetText()
            modtype = modtype[0]
            
            # delete modification
            self.currentSequence.unmodify(name, amino, modtype)
        
        # update gui
        self.sequenceCanvas.setModified(True)
        self.sequenceCanvas.refresh()
        self.onSequenceChanged()
    # ----
    
    
    def onSpecifityFilter(self, evt):
        """Update modifications according to specifity filter."""
        self.updateAvailableModifications()
    # ----
    
    
    def onResidueSelected(self, evt):
        """Update available positions and modifications."""
        
        self.updateAvailablePositions()
        self.updateAvailableModifications()
    # ----
    
    
    def onPositionSelected(self, evt):
        """Update available modifications for selected position."""
        self.updateAvailableModifications()
    # ----
    
    
    def onItemSelected(self, evt):
        """Show selected mass in spectrum canvas."""
        
        # get mass
        if self.currentTool=='digest':
            mz = self.currentDigest[evt.GetData()][2]
        elif self.currentTool=='fragment':
            mz = self.currentFragments[evt.GetData()][2]
        elif self.currentTool=='search':
            mz = self.currentSearch[evt.GetData()][1]
        
        # show mass
        self.parent.updateMassPoints([mz])
    # ----
    
    
    def onItemActivated(self, evt):
        """Show isotopic pattern for selected peptide/fragment."""
        self.onItemSendToMassCalculator(evt)
    # ----
    
    
    def onItemSendToMassCalculator(self, evt):
        """Send selected item to Mass Calculator panel."""
        
        # get data
        if self.currentTool == 'digest':
            selected = self.digestList.getSelected()
            if selected:
                index = self.digestList.GetItemData(selected[0])
                formula = self.currentDigest[index][6].formula()
                charge = self.currentDigest[index][3]
        
        elif self.currentTool == 'fragment':
            selected = self.fragmentsList.getSelected()
            if selected:
                index = self.fragmentsList.GetItemData(selected[0])
                formula = self.currentFragments[index][6].formula()
                charge = self.currentFragments[index][3]
        
        elif self.currentTool == 'search':
            selected = self.searchList.getSelected()
            if selected:
                index = self.searchList.GetItemData(selected[0])
                formula = self.currentSearch[index][5].formula()
                charge = self.currentSearch[index][2]
        
        # check selection
        if not selected:
            wx.Bell()
            return
        
        # send data to Masss Calculator tool
        self.parent.onToolsMassCalculator(formula=formula, charge=charge, agentFormula='H', agentCharge=1)
    # ----
    
    
    def onItemSendToEnvelopeFit(self, evt):
        """Send selected item to envelope fit panel."""
        
        # get data
        if self.currentTool == 'digest':
            selected = self.digestList.getSelected()
            if selected:
                index = self.digestList.GetItemData(selected[0])
                sequence = self.currentDigest[index][6]
                charge = self.currentDigest[index][3]
        
        elif self.currentTool == 'fragment':
            selected = self.fragmentsList.getSelected()
            if selected:
                index = self.fragmentsList.GetItemData(selected[0])
                sequence = self.currentFragments[index][6]
                charge = self.currentFragments[index][3]
        
        elif self.currentTool == 'search':
            selected = self.searchList.getSelected()
            if selected:
                index = self.searchList.GetItemData(selected[0])
                sequence = self.currentSearch[index][5]
                charge = self.currentSearch[index][2]
        
        # send data to envelope fit
        self.parent.onToolsEnvelopeFit(sequence=sequence, charge=charge)
    # ----
    
    
    def onItemCopySequence(self, evt):
        """Copy selected sequence into clipboard."""
        
        # get list
        if self.currentTool == 'digest':
            selected = self.digestList.getSelected()
            if selected:
                index = self.digestList.GetItemData(selected[0])
                sequence = self.currentDigest[index][6].format('S')
        
        elif self.currentTool == 'fragment':
            selected = self.fragmentsList.getSelected()
            if selected:
                index = self.fragmentsList.GetItemData(selected[0])
                sequence = self.currentFragments[index][6].format('S')
        
        elif self.currentTool == 'search':
            selected = self.searchList.getSelected()
            if selected:
                index = self.searchList.GetItemData(selected[0])
                sequence = self.currentSearch[index][5].format('S')
        
        # check selection
        if not selected:
            wx.Bell()
            return
        
        # make text object for data
        obj = wx.TextDataObject()
        obj.SetText(sequence)
        
        # paste to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
    # ----
    
    
    def onItemCopyFormula(self, evt):
        """Copy selected sequence formula into clipboard."""
        
        # get list
        if self.currentTool == 'digest':
            selected = self.digestList.getSelected()
            if selected:
                index = self.digestList.GetItemData(selected[0])
                formula = self.currentDigest[index][6].formula()
        
        elif self.currentTool == 'fragment':
            selected = self.fragmentsList.getSelected()
            if selected:
                index = self.fragmentsList.GetItemData(selected[0])
                formula = self.currentFragments[index][6].formula()
        
        elif self.currentTool == 'search':
            selected = self.searchList.getSelected()
            if selected:
                index = self.searchList.GetItemData(selected[0])
                formula = self.currentSearch[index][5].formula()
        
        # check selection
        if not selected:
            wx.Bell()
            return
        
        # make text object for data
        obj = wx.TextDataObject()
        obj.SetText(formula)
        
        # paste to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(obj)
            wx.TheClipboard.Close()
    # ----
    
    
    def onListKey(self, evt):
        """Export list if Ctrl+C."""
        
        # get key
        key = evt.GetKeyCode()
        
        # copy
        if key == 67 and evt.CmdDown():
            self.onListCopy()
            
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onListRMU(self, evt):
        """Show filter pop-up menu on lists."""
        
        # popup menu
        menu = wx.Menu()
        if self.currentTool in ('digest', 'fragment'):
            menu.Append(ID_listViewAll, "Show All", "", wx.ITEM_RADIO)
            menu.Append(ID_listViewMatched, "Show Matched Only", "", wx.ITEM_RADIO)
            menu.Append(ID_listViewUnmatched, "Show Unmatched Only", "", wx.ITEM_RADIO)
            menu.AppendSeparator()
        menu.Append(ID_listSendToMassCalculator, "Show Isotopic Pattern...", "")
        if self.currentTool in ('digest', 'search'):
            menu.Append(ID_listSendToEnvelopeFit, "Send to Envelope Fit...", "")
        menu.AppendSeparator()
        menu.Append(ID_listCopySequence, "Copy Sequence", "")
        menu.Append(ID_listCopyFormula, "Copy Formula", "")
        menu.Append(ID_listCopy, "Copy List")
        
        # check item
        if (self.currentTool == 'digest' and self._digestFilter == 1) \
            or (self.currentTool=='fragment' and self._fragmentsFilter == 1):
            menu.Check(ID_listViewMatched, True)
        elif (self.currentTool == 'digest' and self._digestFilter == -1) \
            or (self.currentTool=='fragment' and self._fragmentsFilter == -1):
            menu.Check(ID_listViewUnmatched, True)
        elif self.currentTool in ('digest', 'fragment'):
            menu.Check(ID_listViewAll, True)
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewAll)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewMatched)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewUnmatched)
        self.Bind(wx.EVT_MENU, self.onItemSendToMassCalculator, id=ID_listSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onItemSendToEnvelopeFit, id=ID_listSendToEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.onItemCopySequence, id=ID_listCopySequence)
        self.Bind(wx.EVT_MENU, self.onItemCopyFormula, id=ID_listCopyFormula)
        self.Bind(wx.EVT_MENU, self.onListCopy, id=ID_listCopy)
        
        # show menu
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onListFilter(self, evt):
        """Apply selected view filter on current list."""
        
        # set filter
        if evt.GetId() == ID_listViewMatched and self.currentTool == 'digest':
            self._digestFilter = 1
        elif evt.GetId() == ID_listViewMatched and self.currentTool == 'fragment':
            self._fragmentsFilter = 1
        elif evt.GetId() == ID_listViewUnmatched and self.currentTool == 'digest':
            self._digestFilter = -1
        elif evt.GetId() == ID_listViewUnmatched and self.currentTool == 'fragment':
            self._fragmentsFilter = -1
        elif self.currentTool == 'digest':
            self._digestFilter = 0
        elif self.currentTool == 'fragment':
            self._fragmentsFilter = 0
        
        # update list
        if self.currentTool == 'digest':
            self.updateDigestList()
        elif self.currentTool == 'fragment':
            self.updateFragmentsList()
    # ----
    
    
    def onListCopy(self, evt=None):
        """Copy items of selected list into clipboard."""
        
        # copy data
        if self.currentTool == 'digest':
            self.digestList.copyToClipboard()
        elif self.currentTool == 'fragment':
            self.fragmentsList.copyToClipboard()
        elif self.currentTool == 'search':
            self.searchList.copyToClipboard()
    # ----
    
    
    def onDigest(self, evt):
        """Digest sequence."""
        
        # check processing
        if self.processing:
            return
        
        # clear previous data
        self.currentDigest = None
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.clear()
        
        # get params
        if not self.getParams():
            self.updateDigestList()
            self.updateCoverage()
            return
        
        # check sequence
        if not self.currentSequence or self.currentSequence.chainType != 'aminoacids':
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.digestGenerate_butt.Enable(False)
        self.digestMatch_butt.Enable(False)
        self.digestAnnotate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runDigestion)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update digest list
        self._digestFilter = 0
        self.updateDigestList()
        self.updateCoverage()
        
        # hide processing gauge
        self.onProcessing(False)
        self.digestGenerate_butt.Enable(True)
        self.digestMatch_butt.Enable(True)
        self.digestAnnotate_butt.Enable(True)
        
        # send data to match panel
        if self.matchPanel:
            summaryData = {'sequenceLength':len(self.currentSequence)}
            self.matchPanel.setData(self.currentDigest, summaryData)
    # ----
    
    
    def onFragment(self, evt):
        """Fragment sequence."""
        
        # check processing
        if self.processing:
            return
        
        # clear previous data
        self.currentFragments = None
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.clear()
        
        # get params
        if not self.getParams():
            self.updateFragmentsList()
            return
        
        # check sequence
        if not self.currentSequence:
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.fragmentGenerate_butt.Enable(False)
        self.fragmentMatch_butt.Enable(False)
        self.fragmentAnnotate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runFragmentation)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update digest list
        self._fragmentsFilter = 0
        self.updateFragmentsList()
        
        # hide processing gauge
        self.onProcessing(False)
        self.fragmentGenerate_butt.Enable(True)
        self.fragmentMatch_butt.Enable(True)
        self.fragmentAnnotate_butt.Enable(True)
        
        # send data to match panel
        if self.matchPanel:
            summaryData = {'sequenceLength':len(self.currentSequence)}
            self.matchPanel.setData(self.currentFragments, summaryData)
    # ----
    
    
    def onSearch(self, evt):
        """Search for mass in sequence."""
        
        # check processing
        if self.processing:
            return
        
        # clear previous data
        self.currentSearch = None
        
        # get params
        if not self.getParams():
            self.updateSearchList()
            return
        
        # check sequence
        if not self.currentSequence or self.currentSequence.chainType != 'aminoacids':
            wx.Bell()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.searchGenerate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runSearch)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update search list
        self.updateSearchList()
        
        # hide processing gauge
        self.onProcessing(False)
        self.searchGenerate_butt.Enable(True)
    # ----
    
    
    def onMatch(self, evt=None):
        """Match data to current peaklist."""
        
        # init match panel
        match = True
        if not self.matchPanel:
            match = False
            self.matchPanel = panelMatch(self, self.parent, self.currentTool)
            self.matchPanel.Centre()
            self.matchPanel.Show(True)
        
        # set data
        summaryData = {'sequenceLength':len(self.currentSequence)}
        if self.currentTool == 'digest':
            self.matchPanel.setData(self.currentDigest, summaryData)
        elif self.currentTool == 'fragment':
            self.matchPanel.setData(self.currentFragments, summaryData)
        
        # raise panel
        if evt:
            self.matchPanel.Raise()
        
        # match data
        if match and evt:
            self.matchPanel.onMatch()
    # ----
    
    
    def onAnnotate(self, evt):
        """Store matches in document."""
        
        buff = []
        
        # get template
        template = 'matchTemplateAmino'
        if self.currentSequence.chainType != 'aminoacids':
            template = 'matchTemplateCustom'
        
        # get digest data
        if self.currentTool == 'digest' and self.currentDigest:
            for item in self.currentDigest:
                obj = item[6]
                title = obj.format(config.sequence['digest'][template])
                for match in item[-1]:
                    match.label = title
                    match.charge = item[3]
                    match.formula = obj.formula()
                    match.sequenceRange = [obj.history[-1][1]+1, obj.history[-1][2]]
                    buff.append((match.mz, match.delta('Da'), match))
        
        # get fragment data
        elif self.currentTool == 'fragment' and self.currentFragments:
            for item in self.currentFragments:
                obj = item[6]
                title = obj.format(config.sequence['fragment'][template])
                for match in item[-1]:
                    match.label = title
                    match.charge = item[3]
                    match.formula = obj.formula()
                    match.sequenceRange = [obj.history[-1][1]+1, obj.history[-1][2]]
                    match.fragmentSerie = obj.fragmentSerie
                    match.fragmentIndex = obj.fragmentIndex
                    buff.append((match.mz, match.delta('Da'), match))
        
        # check data
        if buff:
            buff.sort()
            matches = []
            for match in buff:
                matches.append(match[2])
        else:
            wx.Bell()
            return
            
        # store matches
        self.currentSequence.matches = matches
        self.parent.onDocumentChanged(items=('matches'))
    # ----
    
    
    def setData(self, sequence=None):
        """Set current sequence."""
        
        self.currentSequence = sequence
        
        # check sequence
        if self.currentSequence == None:
            self.sequenceType_choice.Enable(False)
            self.sequenceCyclic_check.Enable(False)
            self.sequenceTitle_value.Enable(False)
            self.sequenceAccession_value.Enable(False)
            self.sequenceCyclic_check.SetValue(False)
            self.sequenceTitle_value.ChangeValue('')
            self.sequenceAccession_value.ChangeValue('')
        else:
            self.sequenceType_choice.Enable(True)
            self.sequenceCyclic_check.Enable(True)
            self.sequenceTitle_value.Enable(True)
            self.sequenceAccession_value.Enable(True)
            self.sequenceCyclic_check.SetValue(self.currentSequence.cyclic)
            self.sequenceTitle_value.ChangeValue(self.currentSequence.title)
            self.sequenceAccession_value.ChangeValue(self.currentSequence.accession)
        
        # select editor
        if self.currentSequence == None or self.currentSequence.chainType == 'aminoacids':
            self.sequenceType_choice.Select(0)
            self.sequenceCanvas.setData(self.currentSequence)
            self.sequenceEditorSizer.Hide(2)
            self.sequenceEditorSizer.Show(1)
            if self.monomerLibraryPanel:
                self.monomerLibraryPanel.setFilter(filterIn=['_InternalAA'])
                self.monomerLibraryPanel.enableDnD(False)
        else:
            self.sequenceType_choice.Select(1)
            self.sequenceGrid.setData(self.currentSequence)
            self.sequenceEditorSizer.Hide(1)
            self.sequenceEditorSizer.Show(2)
            if self.monomerLibraryPanel:
                self.monomerLibraryPanel.setFilter(filterOut=['_InternalAA'])
                self.monomerLibraryPanel.enableDnD(True)
        
        # update sequence info
        self.updateSequenceInfo()
        
        # update modifications panel
        self.updateAvailableResidues()
        self.updateModificationsList()
        
        # update digest panel
        if self.currentDigest != None:
            self.currentDigest = None
            self.updateDigestList()
            self.updateCoverage()
        
        # update fragment panel
        self.updateAvailableFragments()
        if self.currentFragments != None:
            self.currentFragments = None
            self.updateFragmentsList()
        
        # update search panel
        if self.currentSearch != None:
            self.currentSearch = None
            self.updateSearchList()
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.Close()
        
        # select editor tool
        self.onToolSelected(tool='editor')
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            
            # digest
            if self.currentTool == 'digest':
                
                config.sequence['digest']['maxCharge'] = int(self.digestMaxCharge_value.GetValue())
                config.sequence['digest']['massType'] = 0
                if self.digestMassTypeAv_radio.GetValue():
                    config.sequence['digest']['massType'] = 1
                
                config.sequence['digest']['enzyme'] = self.digestEnzyme_choice.GetStringSelection()
                config.sequence['digest']['miscl'] = int(self.digestMiscl_value.GetValue())
                config.sequence['digest']['lowMass'] = int(self.digestLowMass_value.GetValue())
                config.sequence['digest']['highMass'] = int(self.digestHighMass_value.GetValue())
                
                config.sequence['digest']['allowMods'] = 0
                if self.digestAllowMods_check.GetValue():
                    config.sequence['digest']['allowMods'] = 1
                
            # fragments
            elif self.currentTool == 'fragment':
                
                config.sequence['fragment']['maxCharge'] = int(self.fragmentMaxCharge_value.GetValue())
                config.sequence['fragment']['massType'] = 0
                if self.fragmentMassTypeAv_radio.GetValue():
                    config.sequence['fragment']['massType'] = 1
                
                config.sequence['fragment']['fragments'] = []
                if self.fragmentM_check.GetValue():
                    config.sequence['fragment']['fragments'].append('M')
                if self.fragmentIm_check.GetValue():
                    config.sequence['fragment']['fragments'].append('im')
                if self.fragmentA_check.GetValue():
                    config.sequence['fragment']['fragments'].append('a')
                if self.fragmentB_check.GetValue():
                    config.sequence['fragment']['fragments'].append('b')
                if self.fragmentC_check.GetValue():
                    config.sequence['fragment']['fragments'].append('c')
                if self.fragmentX_check.GetValue():
                    config.sequence['fragment']['fragments'].append('x')
                if self.fragmentY_check.GetValue():
                    config.sequence['fragment']['fragments'].append('y')
                if self.fragmentZ_check.GetValue():
                    config.sequence['fragment']['fragments'].append('z')
                
                if self.fragmentIntA_check.GetValue():
                    config.sequence['fragment']['fragments'].append('int-a')
                if self.fragmentIntB_check.GetValue():
                    config.sequence['fragment']['fragments'].append('int-b')
                if self.fragmentNLadder_check.GetValue():
                    config.sequence['fragment']['fragments'].append('n-ladder')
                if self.fragmentCLadder_check.GetValue():
                    config.sequence['fragment']['fragments'].append('c-ladder')
                
                if self.fragmentLossH2O_check.GetValue():
                    config.sequence['fragment']['fragments'].append('-H2O')
                if self.fragmentLossNH3_check.GetValue():
                    config.sequence['fragment']['fragments'].append('-NH3')
                if self.fragmentLossCO_check.GetValue():
                    config.sequence['fragment']['fragments'].append('-CO')
                if self.fragmentLossH3PO4_check.GetValue():
                    config.sequence['fragment']['fragments'].append('-H3PO4')
                if self.fragmentLossDefined_check.GetValue():
                    config.sequence['fragment']['fragments'].append('losses')
                if self.fragmentLossCombi_check.GetValue():
                    config.sequence['fragment']['fragments'].append('losscombi')
                
                if self.fragmentGainH2O_check.GetValue():
                    config.sequence['fragment']['fragments'].append('+H2O')
                if self.fragmentGainCO_check.GetValue():
                    config.sequence['fragment']['fragments'].append('+CO')
                
                if self.fragmentScrambling_check.GetValue():
                    config.sequence['fragment']['fragments'].append('scrambling')
                
                if self.fragmentRemoveFiltered_check.GetValue():
                    config.sequence['fragment']['filterFragments'] = 1
                else:
                    config.sequence['fragment']['filterFragments'] = 0
            
            # search
            elif self.currentTool == 'search':
                
                config.sequence['search']['mass'] = float(self.searchMass_value.GetValue())
                
                config.sequence['search']['charge'] = int(self.searchCharge_value.GetValue())
                config.sequence['search']['massType'] = 0
                if self.searchMassTypeAv_radio.GetValue():
                    config.sequence['search']['massType'] = 1
                
                config.sequence['search']['enzyme'] = self.searchEnzyme_choice.GetStringSelection()
                config.sequence['search']['semiSpecific'] = self.searchSemiSpecific_check.GetValue()
                
                config.sequence['search']['tolerance'] = float(self.searchTolerance_value.GetValue())
                config.sequence['search']['units'] = 'Da'
                if self.searchUnitsPpm_radio.GetValue():
                    config.sequence['search']['units'] = 'ppm'
                
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateSequenceInfo(self):
        """Update sequence info."""
        
        label = ''
        
        # check sequence
        if not self.currentSequence:
            self.sequenceInfo_label.SetLabel('No sequence defined')
            return
        
        # get mass
        if len(self.currentSequence):
            format = '%0.' + `config.main['mzDigits']` + 'f'
            mass = self.currentSequence.mass()
            label += 'Mo. mass: '+format % mass[0]
            label += '     Av. mass: '+format % mass[1]
            
            if self.currentSequence.chainType != 'aminoacids':
                formula = self.currentSequence.formula()
                label += '     Formula: %s' % formula
            
        # get length
        label += '     Length: %d' % len(self.currentSequence)
        
        # get cursor position
        if len(self.currentSequence) and self.currentSequence.chainType == 'aminoacids':
            selection = self.sequenceCanvas.getSequenceSelection()
            if selection[0] == selection[1]:
                label += '     Cursor: %s' % (selection[0]+1)
            else:
                label += '     Cursor: %s-%s' % ((selection[0]+1), min(selection[1], len(self.currentSequence)))
        
        self.sequenceInfo_label.SetLabel(label)
    # ----
    
    
    def updateAvailableResidues(self):
        """Update available residues."""
        
        # clear
        self.modsResidue_choice.Clear()
        self.modsPosition_choice.Clear()
        self.modsMod_choice.Clear()
        
        # check sequence type
        if not self.currentSequence or self.currentSequence.chainType != 'aminoacids':
            return
        
        # get residues
        residues = []
        for monomer in self.currentSequence:
            name = '%s (%s)' % (mspy.monomers[monomer].name, monomer)
            if not name in residues:
                residues.append(name)
        
        # add termini
        if not self.currentSequence.cyclic:
            self.modsResidue_choice.Append('N-terminus')
            self.modsResidue_choice.Append('C-terminus')
        
        # add residues
        for res in sorted(residues):
            self.modsResidue_choice.Append(res)
    # ----
    
    
    def updateAvailablePositions(self):
        """Update available positions."""
        
        # clear
        self.modsPosition_choice.Clear()
        
        # get selected residue
        residue = self.modsResidue_choice.GetStringSelection()
        
        # check terminal modifications
        if residue in ('N-terminus', 'C-terminus'):
            return
        
        # residual modifications
        residue = residue[-2]
        positions = ['All ' + residue]
        for x, amino in enumerate(self.currentSequence):
            if amino == residue:
                pos = '%s %s' % (amino, x+1)
                positions.append(pos)
        
        # update positions
        for pos in positions:
            self.modsPosition_choice.Append(str(pos))
        
        # select first
        self.modsPosition_choice.Select(0)
    # ----
    
    
    def updateAvailableModifications(self):
        """Update available modifications."""
        
        # clear
        self.modsMod_choice.Clear()
        
        # get selected residue
        try:
            residue = self.modsResidue_choice.GetStringSelection()
            checkSpecifity = self.modsSpecifity_check.GetValue()
        except:
            return
        
        # get corresponding modifications
        mods = []
        if residue:
            for mod in mspy.modifications:
                if not checkSpecifity \
                    or (residue == 'N-terminus' and mspy.modifications[mod].termSpecifity == 'N') \
                    or (residue == 'C-terminus' and mspy.modifications[mod].termSpecifity == 'C') \
                    or residue[-2] in mspy.modifications[mod].aminoSpecifity:
                        mods.append(mod)
        
        # update modifications
        for mod in sorted(mods):
            self.modsMod_choice.Append(mod)
    # ----
    
    
    def updateModificationsList(self):
        """Update current modifications."""
        
        # clear previous data
        self.modificationsList.DeleteAllItems()
        
        # check sequence
        if self.currentSequence == None:
            return
        
        currentMods = []
        format = '%0.' + `config.main['mzDigits']` + 'f'
        
        # get modifications
        for mod in self.currentSequence.modifications:
            name = mod[0]
            
            # format position
            if type(mod[1]) == int:
                position = '%s %s' % (self.currentSequence[mod[1]], mod[1]+1)
            elif mod[1] == 'nTerm':
                position = 'N-terminus'
            elif mod[1] == 'cTerm':
                position = 'C-terminus'
            else:
                position = 'All ' + mod[1]
            
            # format type
            if mod[2] == 'f':
                modtype = 'fixed'
            else:
                modtype = 'variable'
            
            # format masses
            massMo = format % mspy.modifications[name].mass[0]
            massAv = format % mspy.modifications[name].mass[1]
            
            # format formula
            formula = mspy.modifications[name].gainFormula
            if mspy.modifications[name].lossFormula:
                formula += ' - ' + mspy.modifications[name].lossFormula
            
            # append data
            currentMods.append((position, name, modtype, massMo, massAv, formula))
        
        # set current data to sorter
        self.modificationsList.setDataMap(currentMods)
        
        # update list
        for row, item in enumerate(currentMods):
            self.modificationsList.InsertStringItem(row, item[0])
            self.modificationsList.SetStringItem(row, 1, item[1])
            self.modificationsList.SetStringItem(row, 2, item[2])
            self.modificationsList.SetStringItem(row, 3, item[3])
            self.modificationsList.SetStringItem(row, 4, item[4])
            self.modificationsList.SetStringItem(row, 5, item[5])
            self.modificationsList.SetItemData(row, row)
        
        # sort data
        self.modificationsList.sort()
        
        # scroll top
        if currentMods:
            self.modificationsList.EnsureVisible(0)
    # ----
    
    
    def updateAvailableFragments(self, evt=None):
        """Update available fragments."""
        
        # no sequence defined
        if self.currentSequence == None:
            self.fragmentIntA_check.Enable()
            self.fragmentIntB_check.Enable()
            self.fragmentNLadder_check.Enable()
            self.fragmentCLadder_check.Enable()
            self.fragmentGainCO_check.SetValue(False)
            self.fragmentGainCO_check.Disable()
        
        # cyclic sequence
        elif self.currentSequence.cyclic:
            self.fragmentIntA_check.SetValue(False)
            self.fragmentIntB_check.SetValue(False)
            self.fragmentNLadder_check.SetValue(False)
            self.fragmentCLadder_check.SetValue(False)
            self.fragmentIntA_check.Disable()
            self.fragmentIntB_check.Disable()
            self.fragmentNLadder_check.Disable()
            self.fragmentCLadder_check.Disable()
            self.fragmentGainCO_check.Enable()
        
        # linear sequence
        else:
            self.fragmentIntA_check.Enable()
            self.fragmentIntB_check.Enable()
            self.fragmentNLadder_check.Enable()
            self.fragmentCLadder_check.Enable()
            self.fragmentGainCO_check.SetValue(False)
            self.fragmentGainCO_check.Disable()
        
        # scrambling enabled
        if self.fragmentScrambling_check.IsChecked():
            self.fragmentGainCO_check.Enable()
    # ----
    
    
    def updateDigestList(self):
        """Update digest list."""
        
        # clear previous data and set new
        self.digestList.DeleteAllItems()
        self.digestList.setDataMap(self.currentDigest)
        
        # check data
        if not self.currentDigest:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.match['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        fontMatched = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        row = -1
        for index, item in enumerate(self.currentDigest):
            
            # filter data
            if self._digestFilter == 1 and item[5] == None:
                continue
            elif self._digestFilter == -1 and item[5] != None:
                continue
            
            # format data
            section = item[6].format('h')
            mz = mzFormat % (item[2])
            
            error = ''
            if item[5] != None:
                error = errFormat % (item[5])
            
            # add data
            row += 1
            self.digestList.InsertStringItem(row, section)
            self.digestList.SetStringItem(row, 1, str(item[1]))
            self.digestList.SetStringItem(row, 2, mz)
            self.digestList.SetStringItem(row, 3, str(item[3]))
            self.digestList.SetStringItem(row, 4, item[4])
            self.digestList.SetStringItem(row, 5, error)
            self.digestList.SetItemData(row, index)
            
            # mark matched
            if item[5] != None:
                self.digestList.SetItemTextColour(row, (0,200,0))
                self.digestList.SetItemFont(row, fontMatched)
        
        # sort data
        self.digestList.sort()
        
        # scroll top
        if self.digestList.GetItemCount():
            self.digestList.EnsureVisible(0)
    # ----
    
    
    def updateFragmentsList(self):
        """Update fragments list."""
        
        # clear previous data and set new
        self.fragmentsList.DeleteAllItems()
        self.fragmentsList.setDataMap(self.currentFragments)
        
        # check data
        if not self.currentFragments:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.match['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        fontMatched = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        fontFiltered = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.NORMAL)
        
        row = -1
        for index, item in enumerate(self.currentFragments):
            
            # filter data
            if self._fragmentsFilter == 1 and item[5] == None:
                continue
            elif self._fragmentsFilter == -1 and item[5] != None:
                continue
            
            # format data
            section = item[6].format('h')
            mz = mzFormat % (item[2])
            
            error = ''
            if item[5] != None:
                error = errFormat % (item[5])
            
            # add data
            row += 1
            self.fragmentsList.InsertStringItem(row, item[0])
            self.fragmentsList.SetStringItem(row, 1, section)
            self.fragmentsList.SetStringItem(row, 2, mz)
            self.fragmentsList.SetStringItem(row, 3, str(item[3]))
            self.fragmentsList.SetStringItem(row, 4, item[4])
            self.fragmentsList.SetStringItem(row, 5, error)
            self.fragmentsList.SetItemData(row, index)
            
            # mark filtered and matched fragments
            if item[6].fragmentFiltered and item[5] == None:
                self.fragmentsList.SetItemTextColour(row, (150,150,150))
                self.fragmentsList.SetItemFont(row, fontFiltered)
            elif item[6].fragmentFiltered and item[5] != None:
                self.fragmentsList.SetItemTextColour(row, (0,200,0))
                self.fragmentsList.SetItemFont(row, fontFiltered)
            elif item[5] != None:
                self.fragmentsList.SetItemTextColour(row, (0,200,0))
                self.fragmentsList.SetItemFont(row, fontMatched)
        
        # sort data
        self.fragmentsList.sort()
        
        # scroll top
        if self.fragmentsList.GetItemCount():
            self.fragmentsList.EnsureVisible(0)
    # ----
    
    
    def updateSearchList(self):
        """Update search list."""
        
        # clear previous data and set new
        self.searchList.DeleteAllItems()
        self.searchList.setDataMap(self.currentSearch)
        
        # check data
        if not self.currentSearch:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.sequence['search']['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        
        row = -1
        for index, item in enumerate(self.currentSearch):
            
            # format data
            section = item[5].format('h')
            mz = mzFormat % (item[1])
            error = errFormat % (item[4])
            
            # add data
            row += 1
            self.searchList.InsertStringItem(row, section)
            self.searchList.SetStringItem(row, 1, mz)
            self.searchList.SetStringItem(row, 2, item[3])
            self.searchList.SetStringItem(row, 3, error)
            self.searchList.SetItemData(row, index)
        
        # sort data
        self.searchList.sort()
        
        # scroll top
        if self.searchList.GetItemCount():
            self.searchList.EnsureVisible(0)
    # ----
    
    
    def updateMatches(self, resultList=None):
        """Update current list."""
        
        # choose current
        if not resultList:
            resultList = self.currentTool
        
        # update digest list
        if resultList == 'digest':
            self.updateDigestList()
            self.updateCoverage()
        
        # update fragments list
        elif resultList == 'fragment':
            self.updateFragmentsList()
    # ----
    
    
    def updateCoverage(self):
        """Update coverage info for protein digest."""
        
        # clear previous value
        self.digestCoverage_label.SetLabel('')
        if not self.currentDigest:
            return
        
        # get ranges
        totalRanges = []
        matchedRanges = []
        for peptide in self.currentDigest:
            section = [peptide[6].history[-1][1]+1, peptide[6].history[-1][2]]
            totalRanges.append(section)
            if peptide[5] != None:
                matchedRanges.append(section)
        
        # get coverages
        totalCoverage = mspy.coverage(totalRanges, len(self.currentSequence))
        matchedCoverage = mspy.coverage(matchedRanges, len(self.currentSequence))
        
        # set new label
        label = 'Coverage: %0.0f/%0.0f' % (matchedCoverage, totalCoverage)
        label += ' %'
        self.digestCoverage_label.SetLabel(label)
    # ----
    
    
    def applyModificationsPresets(self, name):
        """Load selected modification presets."""
        
        # get presets
        presets = libs.presets['modifications'][name]
        
        # check sequence
        if not self.currentSequence:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="No sequence defined.", message='Modifications cannot be applied on empty sequence.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # check modifications
        for mod in presets:
            if not mod[0] in mspy.modifications:
                wx.Bell()
                message = 'Modification entitled "%s" was not found in your database.' % mod[0]
                dlg = mwx.dlgMessage(self, title="Unknown modification found.", message=message)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # remove previous modifications if empty presets
        if not presets:
            self.currentSequence.unmodify(None)
        
        # ask to replace previous modifications
        if self.currentSequence.modifications:
            title = 'Modifications already applied!'
            message = "There are some modifications already applied to the sequence.\nYou can either replace previous or append new."
            buttons = [(ID_dlgReplace, "Replace", 80, False, 15), (ID_dlgAppend, "Append", 80, True, 0)]
            dlg = mwx.dlgMessage(self, title, message, buttons)
            if dlg.ShowModal() == ID_dlgReplace:
                self.currentSequence.unmodify(None)
        
        # check and apply modifications
        valid = True
        for mod in presets:
            if self.checkModifications(self.currentSequence, [mod[0], mod[1], mod[2]], config.sequence['digest']['maxMods']):
                self.currentSequence.modify(mod[0], mod[1], mod[2])
            else:
                valid = False
        
        if not valid:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Some of your modifications cannot be applied.", message='Corresponding amino acid is not present in your sequence or\nthe maximum number of fixed modifications per single position\nwas already applied.')
            dlg.ShowModal()
            dlg.Destroy()
        
        # update gui
        self.sequenceCanvas.setModified(True)
        self.sequenceCanvas.refresh()
        self.onSequenceChanged()
    # ----
    
    
    def applyFragmentsPresets(self, name):
        """Load fragments serie presets."""
        
        # get presets
        presets = libs.presets['fragments'][name]
        
        # set fragments
        self.fragmentM_check.SetValue(presets.count('M'))
        self.fragmentIm_check.SetValue(presets.count('im'))
        self.fragmentA_check.SetValue(presets.count('a'))
        self.fragmentB_check.SetValue(presets.count('b'))
        self.fragmentC_check.SetValue(presets.count('c'))
        self.fragmentX_check.SetValue(presets.count('x'))
        self.fragmentY_check.SetValue(presets.count('y'))
        self.fragmentZ_check.SetValue(presets.count('z'))
        
        self.fragmentIntB_check.SetValue(presets.count('int-b'))
        self.fragmentIntA_check.SetValue(presets.count('int-a'))
        self.fragmentNLadder_check.SetValue(presets.count('n-ladder'))
        self.fragmentCLadder_check.SetValue(presets.count('c-ladder'))
        
        self.fragmentLossH2O_check.SetValue(presets.count('-H2O'))
        self.fragmentLossNH3_check.SetValue(presets.count('-NH3'))
        self.fragmentLossCO_check.SetValue(presets.count('-CO'))
        self.fragmentLossH3PO4_check.SetValue(presets.count('-H3PO4'))
        self.fragmentLossDefined_check.SetValue(presets.count('losses'))
        self.fragmentLossCombi_check.SetValue(presets.count('losscombi'))
        
        self.fragmentGainCO_check.SetValue(presets.count('+CO'))
        self.fragmentGainH2O_check.SetValue(presets.count('+H2O'))
        
        self.fragmentScrambling_check.SetValue(presets.count('scrambling'))
        
        # enable/disable some fragments
        self.updateAvailableFragments()
    # ----
    
    
    def saveModificationsPresets(self):
        """Save applied global modifications as presets."""
        
        # check sequence
        if not self.currentSequence:
            wx.Bell()
            return
        
        # get modifications
        modifications = []
        for mod in self.currentSequence.modifications:
            if type(mod[1]) in (str, unicode):
                modifications.append(mod)
        
        # check presets
        if not modifications:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Presets cannot be saved.", message='Global and N-terminal modifications can only be saved in presets.')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # get presets name
        dlg = dlgPresetsName(self)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # get params
        libs.presets['modifications'][name] = modifications
        
        # save presets
        libs.savePresets()
    # ----
    
    
    def saveFragmentsPresets(self):
        """Save selected fragments as presets."""
        
        # check params
        if not self.getParams():
            wx.Bell()
            return
        
        # get presets name
        dlg = dlgPresetsName(self)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # save presets
        libs.presets['fragments'][name] = config.sequence['fragment']['fragments']
        libs.savePresets()
    # ----
    
    
    def clearMatches(self):
        """Clear matched data."""
        
        # update digest panel
        if self.currentDigest != None:
            for item in self.currentDigest:
                item[5] = None # error col
                item[-1] = [] # matches
            self.updateDigestList()
            self.updateCoverage()
        
        # update fragment panel
        if self.currentFragments != None:
            for item in self.currentFragments:
                item[5] = None # error col
                item[-1] = [] # matches
            self.updateFragmentsList()
        
        # clear match panel
        if self.matchPanel:
            summaryData = {'sequenceLength':len(self.currentSequence)}
            if self.currentTool == 'digest':
                self.matchPanel.setData(self.currentDigest, summaryData)
            elif self.currentTool == 'fragment':
                self.matchPanel.setData(self.currentFragments, summaryData)
    # ----
    
    
    def runDigestion(self):
        """Perform protein digest."""
        
        # run task
        try:
            
            self.currentDigest = []
            
            # digest sequence
            peptides = mspy.digest(
                sequence = self.currentSequence,
                enzyme = config.sequence['digest']['enzyme'],
                miscleavage = config.sequence['digest']['miscl'],
                allowMods = config.sequence['digest']['allowMods'],
                strict = False
            )
            
            # do not cleave if modified
            enzyme = config.sequence['digest']['enzyme']
            if config.sequence['digest']['allowMods']:
                enzyme = None
            
            # get variations for each peptide
            buff = []
            for peptide in peptides:
                buff += peptide.variations(maxMods=config.sequence['digest']['maxMods'], position=config.sequence['digest']['retainPos'], enzyme=enzyme)
            peptides = buff
            
            # get max charge and polarity
            polarity = 1
            if config.sequence['digest']['maxCharge'] < 0:
                polarity = -1
            maxCharge = abs(config.sequence['digest']['maxCharge'])+1
            
            # get list template
            template = config.sequence['digest']['listTemplateAmino']
            if self.currentSequence.chainType != 'aminoacids':
                template = config.sequence['digest']['listTemplateCustom']
            
            # calculate mz and check limits
            buff = []
            for peptide in peptides:
                for z in range(1, maxCharge):
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    mz = peptide.mz(z*polarity)[config.sequence['digest']['massType']]
                    if mz >= config.sequence['digest']['lowMass'] and mz <= config.sequence['digest']['highMass']:
                        buff.append([
                            peptide.history,
                            peptide.miscleavages,
                            mz,
                            z*polarity,
                            peptide.format(template),
                            None,
                            peptide,
                            [],
                        ])
            
            self.currentDigest = buff
        
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def runFragmentation(self):
        """Perform peptide fragmentation."""
        
        # run task
        try:
            
            self.currentFragments = []
            
            # get fragment series
            series = []
            if 'M' in config.sequence['fragment']['fragments']:
                series.append('M')
            if 'im' in config.sequence['fragment']['fragments']:
                series.append('im')
            if 'a' in config.sequence['fragment']['fragments']:
                series.append('a')
            if 'b' in config.sequence['fragment']['fragments']:
                series.append('b')
            if 'c' in config.sequence['fragment']['fragments']:
                series.append('c')
            if 'x' in config.sequence['fragment']['fragments']:
                series.append('x')
            if 'y' in config.sequence['fragment']['fragments']:
                series.append('y')
            if 'z' in config.sequence['fragment']['fragments']:
                series.append('z')
            if 'int-b' in config.sequence['fragment']['fragments']:
                series.append('int-b')
            if 'int-a' in config.sequence['fragment']['fragments']:
                series.append('int-a')
            if 'n-ladder' in config.sequence['fragment']['fragments']:
                series.append('n-ladder')
            if 'c-ladder' in config.sequence['fragment']['fragments']:
                series.append('c-ladder')
            
            # get losses
            userLosses = []
            definedLosses = False
            if '-H2O' in config.sequence['fragment']['fragments']:
                userLosses.append('H2O')
            if '-NH3' in config.sequence['fragment']['fragments']:
                userLosses.append('NH3')
            if '-CO' in config.sequence['fragment']['fragments']:
                userLosses.append('CO')
            if '-H3PO4' in config.sequence['fragment']['fragments']:
                userLosses.append('H3PO4')
            if 'losses' in config.sequence['fragment']['fragments']:
                definedLosses = True
            
            # get gains
            userGains = []
            if '+H2O' in config.sequence['fragment']['fragments']:
                userGains.append('H2O')
            if '+CO' in config.sequence['fragment']['fragments']:
                userGains.append('CO')
            
            # get scrambling
            scrambling = False
            if 'scrambling' in config.sequence['fragment']['fragments']:
                scrambling = True
            
            # get loss combinations
            maxLosses = 1
            if 'losscombi' in config.sequence['fragment']['fragments']:
                maxLosses = config.sequence['fragment']['maxLosses']
            
            # generate basic fragments
            fragments = mspy.fragment(
                sequence = self.currentSequence,
                series = series,
                scrambling = scrambling
            )
            
            # apply neutral losses
            fragments += mspy.fragmentlosses(
                fragments = fragments,
                losses = userLosses,
                defined = definedLosses,
                limit = maxLosses
            )
            
            # apply neutral gains
            fragments += mspy.fragmentgains(
                fragments = fragments,
                gains = userGains,
            )
            
            # variate mods
            buff = []
            for fragment in fragments:
                buff += fragment.variations(maxMods=config.sequence['fragment']['maxMods'], position=False)
            fragments = buff
            
            # get max charge and polarity
            polarity = 1
            if config.sequence['fragment']['maxCharge'] < 0:
                polarity = -1
            maxCharge = abs(config.sequence['fragment']['maxCharge'])+1
            
            # get list template
            template = config.sequence['fragment']['listTemplateAmino']
            if self.currentSequence.chainType != 'aminoacids':
                template = config.sequence['fragment']['listTemplateCustom']
            
            # calculate mz and store fragments
            buff = []
            for fragment in fragments:
                for z in range(1, maxCharge):
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    if not config.sequence['fragment']['filterFragments'] or not fragment.fragmentFiltered:
                        buff.append([
                            fragment.format('f'),
                            fragment.history,
                            fragment.mz(z*polarity)[config.sequence['fragment']['massType']],
                            z*polarity,
                            fragment.format(template),
                            None,
                            fragment,
                            [],
                        ])
            
            self.currentFragments = buff
        
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def runSearch(self):
        """Perform mass search."""
        
        # run task
        try:
            
            self.currentSearch = []
            
            # search sequence
            peptides = self.currentSequence.search(
                mass = config.sequence['search']['mass'],
                charge = config.sequence['search']['charge'],
                tolerance = config.sequence['search']['tolerance'],
                enzyme = config.sequence['search']['enzyme'],
                semiSpecific = config.sequence['search']['semiSpecific'],
                tolUnits = config.sequence['search']['units'],
                massType = config.sequence['search']['massType'],
                maxMods = config.sequence['search']['maxMods'],
                position = config.sequence['search']['retainPos']
            )
            
            # get list template
            template = config.sequence['search']['listTemplateAmino']
            if self.currentSequence.chainType != 'aminoacids':
                template = config.sequence['search']['listTemplateCustom']
            
            buff = []
            for peptide in peptides:
                mz = peptide.mz(config.sequence['search']['charge'])[config.sequence['search']['massType']]
                buff.append([
                    peptide.history,
                    mz,
                    config.sequence['search']['charge'],
                    peptide.format(template),
                    mspy.delta(mz, config.sequence['search']['mass'], config.sequence['search']['units']),
                    peptide,
                ])
            
            self.currentSearch = buff
            
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def calibrateByMatches(self, references):
        """Use matches for calibration."""
        self.parent.onToolsCalibration(references=references)
    # ----
    
    
    def checkModifications(self, sequence, modification, maxMods):
        """Do not allow multiple modifications on single residue."""
        
        # convert type
        if str(modification[1]).isdigit():
            modification[1] = int(modification[1])
        
        # check same modifications
        if modification in sequence.modifications:
            return False
        
        # check terminal modifications
        if modification[1] in ('nTerm', 'cTerm'):
            for mod in sequence.modifications:
                if mod[1] == modification[1] and (mod[2] == 'f' or modification[2] == 'f'):
                    return False
            return True
        
        # get occupied positions
        occupied = []
        for mod in sequence.modifications:
            if mod[2] == 'f' and not mod[1] in ('nTerm', 'cTerm'):
                count = max(1, sequence.count(str(mod[1])))
                occupied += [mod[1]]*count
        
        # apply current modification
        if modification[2] == 'f':
            count = max(1, sequence.count(str(modification[1])))
            occupied += [modification[1]]*count
        else:
            occupied += [modification[1]]
        
        # check combination
        for x in occupied:
            count = occupied.count(x)
            if type(x) == int and count > maxMods:
                return False
            elif type(x) in (str, unicode):
                available = sequence.count(x)
                for y in occupied:
                    if type(y) == int and sequence[y] == x:
                        available -= 1
                if count > (available*maxMods):
                    return False
        
        return True
    # ----
    
    


class sequenceCanvas(wx.TextCtrl):
    """Sequence editor canvas for amino acids."""
    
    def __init__(self, parent, id, sequence=None, size=(-1,-1), style=wx.TE_MULTILINE|wx.TE_RICH):
        wx.TextCtrl.__init__(self, parent, id, size=size, style=style)
        
        self.parent = parent
        self.modified = False
        
        # make sequence
        if isinstance(sequence, mspy.sequence):
            self.currentSequence = sequence
        elif sequence == None:
            self.currentSequence = mspy.sequence('')
        
        # get regular amino acids
        self._aminoacids = []
        for abbr in mspy.monomers:
            if mspy.monomers[abbr].category == '_InternalAA':
                self._aminoacids.append(abbr)
        
        # set events
        self.Bind(wx.EVT_KEY_DOWN, self._onKey)
        self.Bind(wx.EVT_RIGHT_DOWN, self._onRMU) # wx.EVT_RIGHT_UP does't work on Linux and Mac
        
        # set fonts
        self.styles = {
            'default': wx.TextAttr(colText=(0,0,0), font=wx.Font(mwx.SEQUENCE_FONT_SIZE, wx.MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)),
            'modified': wx.TextAttr(colText=(255,0,0), font=wx.Font(mwx.SEQUENCE_FONT_SIZE, wx.MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)),
        }
        self.SetDefaultStyle(self.styles['default'])
        
        # show current sequence
        self.refresh()
    # ----
    
    
    def _onRMU(self, evt):
        """Process right mouse button."""
        
        ID_CUT = wx.NewId()
        ID_COPY = wx.NewId()
        ID_PASTE = wx.NewId()
        ID_DELETE = wx.NewId()
        ID_SELALL = wx.NewId()
        
        menu = wx.Menu()
        menu.Append(ID_CUT, "Cut", "")
        menu.Append(ID_COPY, "Copy", "")
        menu.Append(ID_PASTE, "Paste", "")
        menu.Append(ID_DELETE, "Delete", "")
        menu.AppendSeparator()
        menu.Append(ID_SELALL, "Select All", "")
        
        if not self.CanCut():
            menu.Enable(ID_CUT, False)
        if not self.CanCopy():
            menu.Enable(ID_COPY, False)
        if not self.CanPaste():
            menu.Enable(ID_PASTE, False)
        if not self.CanCut():
            menu.Enable(ID_DELETE, False)
        if self.IsEmpty():
            menu.Enable(ID_SELALL, False)
        
        self.parent.Bind(wx.EVT_MENU, self._onCut, id=ID_CUT)
        self.parent.Bind(wx.EVT_MENU, self._onCopy, id=ID_COPY)
        self.parent.Bind(wx.EVT_MENU, self._onPaste, id=ID_PASTE)
        self.parent.Bind(wx.EVT_MENU, self._onRemove, id=ID_DELETE)
        self.parent.Bind(wx.EVT_MENU, self._onSelectAll, id=ID_SELALL)
        
        self.parent.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def _onKey(self, evt):
        """Check character and update sequence."""
        
        # get key
        key = evt.GetKeyCode()
        
        # skip navigation keys
        if key in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN):
            evt.Skip()
            return
        
        # select all
        elif key == 65 and evt.CmdDown():
            self._onSelectAll(evt)
        
        # cut
        elif key == 88 and evt.CmdDown():
            self._onCut(evt)
        
        # copy
        elif key == 67 and evt.CmdDown():
            self._onCopy(evt)
        
        # paste
        elif key == 86 and evt.CmdDown():
            self._onPaste(evt)
        
        # delete
        elif key == wx.WXK_DELETE:
            self._onDelete(evt)
        
        # backspace
        elif key == wx.WXK_BACK:
            self._onBackspace(evt)
        
        # text
        elif key >= 65 and key <= 121:
            self._onText(evt)
        
        # all other keys
        else:
            return
    # ----
    
    
    def _onText(self, evt):
        """Process text command."""
        
        char = chr(evt.GetKeyCode())
        char.upper()
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        if char in self._aminoacids:
            self.currentSequence[seqSelection[0]:seqSelection[1]] = mspy.sequence(char)
            self.refresh()
            self.setInsertionPoint(seqSelection[0]+1)
            self.modified = True
        else:
            wx.Bell()
            return
    # ----
    
    
    def _onCut(self, evt):
        """Process cut command."""
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        if seqSelection[0] != seqSelection[1]:
            self._onCopy(evt)
            self._onDelete(evt)
    # ----
    
    
    def _onCopy(self, evt):
        """Process copy command."""
        self.Copy()
    # ----
    
    
    def _onPaste(self, evt):
        """Process paste command."""
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        sequence = self._getSequenceFromClipboard()
        if sequence:
            self.currentSequence[seqSelection[0]:seqSelection[1]] = sequence
            self.refresh()
            self.setInsertionPoint(seqSelection[0]+len(sequence))
            self.modified = True
        
        else:
            wx.Bell()
            dlg = mwx.dlgMessage(self.parent, title="Sequence is not valid.", message="Your clipboard contains characters which does not correspond\nto any defined amino acid. Please check your sequence.")
            dlg.ShowModal()
            dlg.Destroy()
            return
    # ----
    
    
    def _onRemove(self, evt):
        """Process remove command."""
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        if seqSelection[0] != seqSelection[1]:
            self._onDelete(evt)
    # ----
    
    
    def _onDelete(self, evt):
        """Process delete command."""
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        if seqSelection[0] == seqSelection[1]:
            del self.currentSequence[seqSelection[0]:seqSelection[1]+1]
        else:
            del self.currentSequence[seqSelection[0]:seqSelection[1]]
        
        self.refresh()
        self.setInsertionPoint(seqSelection[0])
        self.modified = True
    # ----
    
    
    def _onBackspace(self, evt):
        """Process backspace command."""
        
        curSelection = self.GetSelection()
        seqSelection = self._positionEditorToSequence(curSelection)
        
        if seqSelection[0] == seqSelection[1] and seqSelection[0] != 0:
            del self.currentSequence[seqSelection[0]-1:seqSelection[1]]
            self.refresh()
            self.setInsertionPoint(seqSelection[0]-1)
            self.modified = True
        else:
            del self.currentSequence[seqSelection[0]:seqSelection[1]]
            self.refresh()
            self.setInsertionPoint(seqSelection[0])
            self.modified = True
    # ----
    
    
    def _onSelectAll(self, evt):
        """Process select all command."""
        self.SetSelection(-1,-1)
    # ----
    
    
    def _updateCanvas(self):
        """Show current sequence in canvas."""
        
        # check sequence
        if self.currentSequence == None:
            self.ChangeValue('')
            return
        
        # format sequence
        sequence = ''
        modifications = []
        for x, amino in enumerate(self.currentSequence):
            sequence += amino
            if not (x+1) % 10:
                sequence += ' '
            if self.currentSequence.ismodified(x, True):
                modifications.append(x)
        
        # update sequence
        self.ChangeValue(sequence)
        
        # set default style
        self.SetStyle(0, len(sequence), self.styles['default'])
        
        # highlight modifications
        for pos in modifications:
            x, y = self._positionSequenceToEditor([pos, pos])
            self.SetStyle(x, x+1, self.styles['modified'])
    # ----
    
    
    def _positionEditorToSequence(self, selection):
        """Get sequence coordinates for editor selection."""
        
        selection = list(selection)
        selection[0] -= self.GetRange(0,selection[0]).count(' ')
        selection[1] -= self.GetRange(0,selection[1]).count(' ')
        
        return selection
    # ----
    
    
    def _positionSequenceToEditor(self, selection):
        """Get editor coordinates for sequence selection."""
        
        selection = list(selection)
        selection[0] += divmod(selection[0], 10)[0]
        selection[1] += divmod(selection[1], 10)[0]
        
        return selection
    # ----
    
    
    def _getSequenceFromClipboard(self):
        """Get sequence from clipboard."""
        
        # get data from clipboard
        success = False
        data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(data)
            wx.TheClipboard.Close()
        
        # parse sequence if data in clipboard
        if success:
            
            # get text from clipboard
            data = data.GetText()
            
            # remove whitespaces
            for char in ('\t','\n','\r','\f','\v', ' ', '-', '*', '.'):
                data = data.replace(char, '')
            
            # remove numbers
            for char in ('0','1','2','3','4','5','6','7','8','9'):
                data = data.replace(char, '')
            
            # make sequence object
            try:
                sequence = mspy.sequence(data)
                return sequence
            except:
                pass
        
        wx.Bell()
        return False
    # ----
    
    
    def setData(self, sequence):
        """Set sequence object."""
        
        # set current sequence
        self.currentSequence = sequence
        
        # disable editor
        if self.currentSequence == None:
            self.refresh()
            self.enable(False)
            return
        
        # check sequence
        if not isinstance(sequence, mspy.sequence):
            raise TypeError, 'Sequence must be mspy.sequence object!'
        
        # update gui
        self.enable(True)
        self.refresh()
    # ----
    
    
    def setInsertionPoint(self, pos):
        """Set insertion point in editor for current sequence position."""
        
        start, stop = self._positionSequenceToEditor([pos,pos])
        self.SetInsertionPoint(start)
    # ----
    
    
    def setModified(self, status=True):
        """Set modified status."""
        self.modified = status
    # ----
    
    
    def getData(self):
        """Get current sequence."""
        return self.currentSequence
    # ----
    
    
    def getSequenceSelection(self):
        """Get current selection in sequence coordinations."""
        return self._positionEditorToSequence(self.GetSelection())
    # ----
    
    
    def enable(self, enable=True):
        """Enable or disable editor."""
        self.Enable(enable)
    # ----
    
    
    def refresh(self):
        """Redraw current sequence."""
        self._updateCanvas()
    # ----
    
    
    def ismodified(self):
        """Modified status."""
        return self.modified
    # ----
    
    


class sequenceGrid(wx.StaticBoxSizer):
    """Sequence editor for all monomers."""
    
    def __init__(self, parent, panel, sequence=None, items=20):
        wx.StaticBoxSizer.__init__(self, wx.StaticBox(panel, -1, ""), wx.VERTICAL)
        
        self.parent = parent
        self.panel = panel
        self.modified = False
        
        self.items = []
        
        # make sequence
        if isinstance(sequence, mspy.sequence):
            self.currentSequence = sequence
        elif sequence == None:
            self.currentSequence = mspy.sequence('')
        
        # make items grid
        items = max(items, len(self.currentSequence))
        self._makeGUI(items)
    # --
    
    
    def _onSequence(self, evt=None):
        """Get current sequence from grid."""
        
        self.modified = True
        
        # get sequence
        sequence = []
        gap = False
        for x, item in enumerate(self.items):
            monomer = item.GetValue()
            
            if not monomer:
                gap = True
                item.SetBackgroundColour(wx.NullColour)
            elif not monomer in mspy.monomers:
                gap = True
                item.SetBackgroundColour((250,100,100))
            elif not gap:
                sequence.append(monomer)
                item.SetBackgroundColour(wx.NullColour)
            else:
                item.SetBackgroundColour(wx.NullColour)
            
            item.Refresh()
        
        # update sequence
        self.currentSequence[:] = mspy.sequence(sequence, chainType='custom')
        
        # lock items
        self._lockItems()
        
        # send notification up
        self.parent.onSequenceChanged()
    # ----
    
    
    def _makeGUI(self, items):
        """Make monomer items."""
        
        # make items grid
        self.grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        
        # make items
        while len(self.items) < items:
            self.addRow()
        
        # make some rows growable
        self.grid.AddGrowableCol(1)
        self.grid.AddGrowableCol(3)
        self.grid.AddGrowableCol(5)
        self.grid.AddGrowableCol(7)
        self.grid.AddGrowableCol(9)
        
        # add to self
        self.Add(self.grid, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 10)
        
        # lock items
        self._lockItems()
    # ----
    
    
    def _updateGrid(self):
        """Show current sequence in grid."""
        
        # clear items
        for item in self.items:
            item.ChangeValue('')
            item.SetBackgroundColour(wx.NullColour)
        
        # update items
        if self.currentSequence != None:
            for x, monomer in enumerate(self.currentSequence):
                self.items[x].ChangeValue(monomer)
        
        # lock items
        self._lockItems()
    # ----
    
    
    def _lockItems(self):
        """Disable unset items."""
        
        # check sequence
        if self.currentSequence == None:
            for item in self.items:
                item.Disable()
                item.SetBackgroundColour((230,230,230))
            return
        
        # enable/disable items
        length = len(self.currentSequence)
        end = 0
        for x in reversed(range(len(self.items))):
            item = self.items[x]
            value = self.items[x].GetValue()
            
            # set sequence end by last specified item
            if x > end and value:
                end = x
            
            # value specified
            if value:
                item.Enable()
            
            # space right next to the sequence
            elif x == length and x > end:
                item.Enable()
                self.items[x].SetBackgroundColour(wx.NullColour)
            
            # space out of specified sequence
            elif x > end:
                item.Disable()
                self.items[x].SetBackgroundColour((230,230,230))
            
            # gap
            elif x < end:
                item.Enable()
                self.items[x].SetBackgroundColour((240,100,100))
    # ----
    
    
    def setData(self, sequence):
        """Set sequence object."""
        
        # set current sequence
        self.currentSequence = sequence
        
        # disable editor
        if self.currentSequence == None:
            self.refresh()
            self.enable(False)
            return
        
        # check sequence
        if not isinstance(sequence, mspy.sequence):
            raise TypeError, 'Sequence must be mspy.sequence object!'
        
        # check number of items
        while len(self.currentSequence) - len(self.items) > 0:
            self.addRow()
        
        # update gui
        self.enable(True)
        self.refresh()
    # ----
    
    
    def setModified(self, status=True):
        """Set modified status."""
        self.modified = status
    # ----
    
    
    def getData(self):
        """Get current sequence."""
        return self.currentSequence
    # ----
    
    
    def addRow(self):
        """Append new row of items."""
        
        length = len(self.items)
        for x in range(5):
            
            # make item
            item = wx.TextCtrl(self.panel, -1, '', size=(85, -1))
            item.Bind(wx.EVT_TEXT, self._onSequence)
            dropTarget = monomerDropTarget(item)
            item.SetDropTarget(dropTarget)
            self.items.append(item)
            
            # add to grid
            row = (length + x) / 5
            col = 2 * (x % 5)
            
            label = wx.StaticText(self.panel, -1, str(length+x+1))
            label.SetFont(wx.SMALL_FONT)
            
            self.grid.Add(label, (row, col), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            self.grid.Add(item, (row, col+1), flag=wx.EXPAND)
    # ----
    
    
    def enable(self, enable=True):
        """Enable or disable editor."""
        
        for item in self.items:
            item.Enable(enable)
        
        if enable:
            self._lockItems()
    # ----
    
    
    def refresh(self):
        """Redraw current sequence."""
        self._updateGrid()
    # ----
    
    
    def ismodified(self):
        """Modified status."""
        return self.modified
    # ----
    
    


class dlgPresetsName(wx.Dialog):
    """Set presets name."""
    
    def __init__(self, parent):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, "Preset Name", style=wx.DEFAULT_DIALOG_STYLE)
        
        self.name = ''
        
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
        self.name_value = wx.TextCtrl(self, -1, '', size=(300,-1), style=wx.TE_PROCESS_ENTER)
        self.name_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, "Save")
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
    
    


class monomerDropTarget(wx.TextDropTarget):
    """Monomer droptarget definition."""
    
    def __init__(self, item):
        wx.TextDropTarget.__init__(self)
        self.item = item
    # ----
    
    
    def OnDropText(self, x, y, text):
        if not self.item.IsEnabled():
            wx.Bell()
            return wx.DragNone
        elif wx.Platform == '__WXGTK__':
            self.item.SetValue('')
            return
        else:
            self.item.SetValue(text)
            return wx.DragCopy
    # ----
    
    

