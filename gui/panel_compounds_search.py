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
import math
import wx

# load modules
from ids import *
import mwx
import images
import config
import libs
import mspy
import doc

from gui.panel_match import panelMatch


# FLOATING PANEL WITH COUPOUND SEARCH TOOL
# ----------------------------------------

class panelCompoundsSearch(wx.MiniFrame):
    """Compounds search tool."""
    
    def __init__(self, parent, tool='compounds'):
        wx.MiniFrame.__init__(self, parent, -1, 'Compounds Search', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        self.matchPanel = None
        
        self.processing = None
        
        self.currentTool = tool
        self.currentDocument = None
        self.currentCompounds = None
        
        self._compoundsFilter = 0
        
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
        controlbar = self.makeControlbar()
        
        # make panels
        self.makeCompoundsList()
        gauge = self.makeGaugePanel()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.compoundsList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide gauge
        self.mainSizer.Hide(3)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make tools
        self.compounds_butt = wx.BitmapButton(panel, ID_compoundsSearchCompounds, images.lib['compoundsSearchCompoundsOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.compounds_butt.SetToolTip(wx.ToolTip("Compounds search"))
        self.compounds_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.formula_butt = wx.BitmapButton(panel, ID_compoundsSearchFormula, images.lib['compoundsSearchFormulaOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.formula_butt.SetToolTip(wx.ToolTip("Formula search"))
        self.formula_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.tool_label = wx.StaticText(panel, -1, "Compounds:")
        self.tool_label.SetFont(wx.SMALL_FONT)
        
        choices = libs.compounds.keys()
        choices.sort()
        choices.insert(0,'Compounds lists')
        self.compounds_choice = wx.Choice(panel, -1, choices=choices, size=(250, mwx.SMALL_CHOICE_HEIGHT))
        self.compounds_choice.Select(0)
        self.compounds_choice.Bind(wx.EVT_CHOICE, self.onGenerate)
        
        self.formula_value = wx.TextCtrl(panel, -1, "", size=(270,-1))
        
        # make buttons
        self.generate_butt = wx.Button(panel, -1, "Generate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.generate_butt.Bind(wx.EVT_BUTTON, self.onGenerate)
        
        self.match_butt = wx.Button(panel, -1, "Match", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.match_butt.Bind(wx.EVT_BUTTON, self.onMatch)
        
        self.annotate_butt = wx.Button(panel, -1, "Annotate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.annotate_butt.Bind(wx.EVT_BUTTON, self.onAnnotate)
        
        # pack elements
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_LSPACE)
        self.toolbar.Add(self.compounds_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.formula_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.tool_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        self.toolbar.Add(self.compounds_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.formula_value, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddStretchSpacer()
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.generate_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        self.toolbar.Add(self.match_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        self.toolbar.Add(self.annotate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        self.toolbar.Hide(5)
        self.toolbar.Hide(6)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeControlbar(self):
        """Make controlbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make elements
        massType_label = wx.StaticText(panel, -1, "Mass:")
        massType_label.SetFont(wx.SMALL_FONT)
        
        self.massTypeMo_radio = wx.RadioButton(panel, -1, "Mo", style=wx.RB_GROUP)
        self.massTypeMo_radio.SetFont(wx.SMALL_FONT)
        self.massTypeMo_radio.SetValue(True)
        
        self.massTypeAv_radio = wx.RadioButton(panel, -1, "Av")
        self.massTypeAv_radio.SetFont(wx.SMALL_FONT)
        self.massTypeAv_radio.SetValue(config.compoundsSearch['massType'])
        
        maxCharge_label = wx.StaticText(panel, -1, "Max charge:")
        maxCharge_label.SetFont(wx.SMALL_FONT)
        
        self.maxCharge_value = wx.TextCtrl(panel, -1, str(config.compoundsSearch['maxCharge']), size=(30, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('int'))
        self.maxCharge_value.SetFont(wx.SMALL_FONT)
        
        self.radicals_check = wx.CheckBox(panel, -1, "M*")
        self.radicals_check.SetFont(wx.SMALL_FONT)
        self.radicals_check.SetValue(config.compoundsSearch['radicals'])
        
        adducts_label = wx.StaticText(panel, -1, "Adducts:")
        adducts_label.SetFont(wx.SMALL_FONT)
        
        self.adductNa_check = wx.CheckBox(panel, -1, "Na")
        self.adductNa_check.SetFont(wx.SMALL_FONT)
        self.adductNa_check.SetValue(config.compoundsSearch['adducts'].count('Na'))
        
        self.adductK_check = wx.CheckBox(panel, -1, "K")
        self.adductK_check.SetFont(wx.SMALL_FONT)
        self.adductK_check.SetValue(config.compoundsSearch['adducts'].count('K'))
        
        self.adductLi_check = wx.CheckBox(panel, -1, "Li")
        self.adductLi_check.SetFont(wx.SMALL_FONT)
        self.adductLi_check.SetValue(config.compoundsSearch['adducts'].count('Li'))
        
        self.adductNH4_check = wx.CheckBox(panel, -1, "NH4")
        self.adductNH4_check.SetFont(wx.SMALL_FONT)
        self.adductNH4_check.SetValue(config.compoundsSearch['adducts'].count('NH4'))
        
        self.adductH2O_check = wx.CheckBox(panel, -1, "-H2O")
        self.adductH2O_check.SetFont(wx.SMALL_FONT)
        self.adductH2O_check.SetValue(config.compoundsSearch['adducts'].count('-H2O'))
        
        self.adductACN_check = wx.CheckBox(panel, -1, "ACN")
        self.adductACN_check.SetFont(wx.SMALL_FONT)
        self.adductACN_check.SetValue(config.compoundsSearch['adducts'].count('ACN'))
        
        self.adductMeOH_check = wx.CheckBox(panel, -1, "MeOH")
        self.adductMeOH_check.SetFont(wx.SMALL_FONT)
        self.adductMeOH_check.SetValue(config.compoundsSearch['adducts'].count('MeOH'))
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(massType_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.massTypeMo_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.massTypeAv_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(maxCharge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.maxCharge_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.radicals_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(adducts_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductNa_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductK_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductLi_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductNH4_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.adductH2O_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductACN_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.adductMeOH_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeCompoundsList(self):
        """Make compounds list."""
        
        # init list
        self.compoundsList = mwx.sortListCtrl(self, -1, size=(721, 300), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.compoundsList.SetFont(wx.SMALL_FONT)
        self.compoundsList.setSecondarySortColumn(1)
        self.compoundsList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.compoundsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.compoundsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.compoundsList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        if wx.Platform == '__WXMAC__':
            self.compoundsList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.compoundsList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.compoundsList.InsertColumn(0, "compound", wx.LIST_FORMAT_LEFT)
        self.compoundsList.InsertColumn(1, "m/z", wx.LIST_FORMAT_RIGHT)
        self.compoundsList.InsertColumn(2, "z", wx.LIST_FORMAT_CENTER)
        self.compoundsList.InsertColumn(3, "adduct", wx.LIST_FORMAT_CENTER)
        self.compoundsList.InsertColumn(4, "formula", wx.LIST_FORMAT_LEFT)
        self.compoundsList.InsertColumn(5, "error", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((230,90,40,90,180,70)):
            self.compoundsList.SetColumnWidth(col, width)
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
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close match panel
        if self.matchPanel:
            self.matchPanel.Close()
        
        # close self
        self.Destroy()
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(3)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(3)
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
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'compounds'
            if evt.GetId() == ID_compoundsSearchCompounds:
                tool = 'compounds'
            elif evt.GetId() == ID_compoundsSearchFormula:
                tool = 'formula'
        
        # set current tool
        self.currentTool = tool
        
        # hide toolbars
        self.toolbar.Hide(5)
        self.toolbar.Hide(6)
        
        # set icons off
        self.compounds_butt.SetBitmapLabel(images.lib['compoundsSearchCompoundsOff'])
        self.formula_butt.SetBitmapLabel(images.lib['compoundsSearchFormulaOff'])
        
        # set panel
        if tool == 'compounds':
            self.SetTitle("Compounds Search")
            self.tool_label.SetLabel('Compounds:')
            self.compounds_butt.SetBitmapLabel(images.lib['compoundsSearchCompoundsOn'])
            self.toolbar.Show(5)
            
        elif tool == 'formula':
            self.SetTitle("Formula Search")
            self.tool_label.SetLabel('Formula:')
            self.formula_butt.SetBitmapLabel(images.lib['compoundsSearchFormulaOn'])
            self.toolbar.Show(6)
        
        # fit layout
        self.toolbar.Layout()
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onItemSelected(self, evt):
        """Show selected mass in spectrum canvas."""
        
        mz = self.currentCompounds[evt.GetData()][1]
        self.parent.updateMassPoints([mz])
    # ----
    
    
    def onItemActivated(self, evt):
        """Show isotopic pattern for selected compound."""
        self.onItemSendToMassCalculator(evt)
    # ----
    
    
    def onItemSendToMassCalculator(self, evt):
        """Show isotopic pattern for selected compound."""
        
        # get data
        selected = self.compoundsList.getSelected()
        if selected:
            index = self.compoundsList.GetItemData(selected[0])
            formula = self.currentCompounds[index][4]
            charge = self.currentCompounds[index][2]
            radical = self.currentCompounds[index][3]
        else:
            wx.Bell()
            return
        
        # send data to Mass Calculator tool
        if radical == 'radical':
            self.parent.onToolsMassCalculator(formula=formula, charge=charge, agentFormula='e', agentCharge=-1)
        else:
            self.parent.onToolsMassCalculator(formula=formula, charge=charge, agentFormula='H', agentCharge=1)
    # ----
    
    
    def onItemCopyFormula(self, evt):
        """Copy selected compound formula into clipboard."""
        
        # get data
        selected = self.compoundsList.getSelected()
        if selected:
            index = self.compoundsList.GetItemData(selected[0])
            formula = self.currentCompounds[index][4]
        else:
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
        menu.Append(ID_listViewAll, "Show All", "", wx.ITEM_RADIO)
        menu.Append(ID_listViewMatched, "Show Matched Only", "", wx.ITEM_RADIO)
        menu.Append(ID_listViewUnmatched, "Show Unmatched Only", "", wx.ITEM_RADIO)
        menu.AppendSeparator()
        menu.Append(ID_listSendToMassCalculator, "Show Isotopic Pattern", "")
        menu.AppendSeparator()
        menu.Append(ID_listCopyFormula, "Copy Formula")
        menu.Append(ID_listCopy, "Copy List")
        
        # check item
        if self._compoundsFilter == 1:
            menu.Check(ID_listViewMatched, True)
        elif self._compoundsFilter == -1:
            menu.Check(ID_listViewUnmatched, True)
        else:
            menu.Check(ID_listViewAll, True)
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewAll)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewMatched)
        self.Bind(wx.EVT_MENU, self.onListFilter, id=ID_listViewUnmatched)
        self.Bind(wx.EVT_MENU, self.onItemSendToMassCalculator, id=ID_listSendToMassCalculator)
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
        if evt.GetId() == ID_listViewMatched:
            self._compoundsFilter = 1
        elif evt.GetId() == ID_listViewUnmatched:
            self._compoundsFilter = -1
        else:
            self._compoundsFilter = 0
        
        # update list
        self.updateCompoundsList()
    # ----
    
    
    def onListCopy(self, evt=None):
        """Copy items into clipboard."""
        self.compoundsList.copyToClipboard()
    # ----
    
    
    def onGenerate(self, evt=None):
        """Generate compounds ions."""
        
        # check processing
        if self.processing:
            return
        
        # clear recent
        self.currentCompounds = None
        compounds = {}
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.clear()
        
        # get params
        if not self.getParams():
            self.updateCompoundsList()
            return
        
        # get compounds from selected group or formula
        if self.currentTool == 'compounds':
            group = self.compounds_choice.GetStringSelection()
            if group and group in libs.compounds:
                compounds = libs.compounds[group]
        else:
            formula = self.formula_value.GetValue()
            if formula:
                try:
                    compounds[formula] = mspy.compound(formula)
                except:
                    wx.Bell()
        
        # check compounds
        if not compounds:
            self.updateCompoundsList()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.generate_butt.Enable(False)
        self.match_butt.Enable(False)
        self.annotate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runGenerateIons, kwargs={'compounds':compounds})
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update compounds list
        self._compoundsFilter = 0
        self.updateCompoundsList()
        
        # hide processing gauge
        self.onProcessing(False)
        self.generate_butt.Enable(True)
        self.match_butt.Enable(True)
        self.annotate_butt.Enable(True)
        
        # send data to match panel
        if self.matchPanel:
            self.matchPanel.setData(self.currentCompounds)
    # ----
    
    
    def onMatch(self, evt=None):
        """Match data to current peaklist."""
        
        # init match panel
        match = True
        if not self.matchPanel:
            match = False
            self.matchPanel = panelMatch(self, self.parent, 'compounds')
            self.matchPanel.Centre()
            self.matchPanel.Show(True)
        
        # set data
        self.matchPanel.setData(self.currentCompounds)
        
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
        
        # check compounds
        if not self.currentCompounds:
            wx.Bell()
            return
        
        # get annotations
        annotations = []
        for item in self.currentCompounds:
            for annotation in item[-1]:
                annotation.label = item[0]
                if item[3] == 'radical':
                    annotation.label += ' (radical)'
                    annotation.radical = 1
                elif item[3]:
                    annotation.label += ' (%s adduct)' % item[3]
                annotation.charge = item[2]
                annotation.formula = item[4]
                annotations.append(annotation)
        
        # store annotation
        self.currentDocument.backup(('annotations'))
        self.currentDocument.annotations += annotations
        self.currentDocument.sortAnnotations()
        self.parent.onDocumentChanged(items=('annotations'))
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set new document
        self.currentDocument = document
        
        # clear previous matches
        self.clearMatches()
    # ----
    
    
    def getParams(self):
        """Get generate params."""
        
        # try to get values
        try:
            config.compoundsSearch['massType'] = 0
            if self.massTypeAv_radio.GetValue():
                config.compoundsSearch['massType'] = 1
            
            config.compoundsSearch['maxCharge'] = int(self.maxCharge_value.GetValue())
            config.compoundsSearch['radicals'] = int(self.radicals_check.GetValue())
            
            config.compoundsSearch['adducts'] = []
            if self.adductNa_check.GetValue():
                config.compoundsSearch['adducts'].append('Na')
            if self.adductK_check.GetValue():
                config.compoundsSearch['adducts'].append('K')
            if self.adductLi_check.GetValue():
                config.compoundsSearch['adducts'].append('Li')
            if self.adductNH4_check.GetValue():
                config.compoundsSearch['adducts'].append('NH4')
            if self.adductH2O_check.GetValue():
                config.compoundsSearch['adducts'].append('-H2O')
            if self.adductACN_check.GetValue():
                config.compoundsSearch['adducts'].append('ACN')
            if self.adductMeOH_check.GetValue():
                config.compoundsSearch['adducts'].append('MeOH')
            
            return True
            
        except:
            wx.Bell()
            return False
    # ----
    
    
    def updateCompoundsList(self):
        """Update compounds mass list."""
        
        # clear previous data and set new
        self.compoundsList.DeleteAllItems()
        self.compoundsList.setDataMap(self.currentCompounds)
        
        # check data
        if not self.currentCompounds:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        if config.match['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        fontMatched = wx.Font(mwx.SMALL_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        row = -1
        for index, item in enumerate(self.currentCompounds):
            
            # filter data
            if self._compoundsFilter == 1 and item[5] == None:
                continue
            elif self._compoundsFilter == -1 and item[5] != None:
                continue
            
            # format data
            mz = ''
            z = ''
            adduct = ''
            formula = ''
            error = ''
            if item[1] != None:
                mz = mzFormat % (item[1])
            if item[2] != None:
                z = str(item[2])
            if item[3] != None:
                adduct = item[3]
            if item[4] != None:
                formula = item[4]
            if item[5] != None:
                error = errFormat % (item[5])
            
            # add data
            row += 1
            self.compoundsList.InsertStringItem(row, '')
            self.compoundsList.SetStringItem(row, 0, item[0])
            self.compoundsList.SetStringItem(row, 1, mz)
            self.compoundsList.SetStringItem(row, 2, z)
            self.compoundsList.SetStringItem(row, 3, adduct)
            self.compoundsList.SetStringItem(row, 4, formula)
            self.compoundsList.SetStringItem(row, 5, error)
            self.compoundsList.SetItemData(row, index)
            
            # mark matched
            if item[5] != None:
                self.compoundsList.SetItemTextColour(row, (0,200,0))
                self.compoundsList.SetItemFont(row, fontMatched)
        
        # sort data
        self.compoundsList.sort()
        
        # scroll top
        if self.compoundsList.GetItemCount():
            self.compoundsList.EnsureVisible(0)
    # ----
    
    
    def updateMatches(self, resultList=None):
        """Update compounds list."""
        
        # update compounds list
        self.updateCompoundsList()
    # ----
    
    
    def clearMatches(self):
        """Clear matched data."""
        
        # update compounds panel
        if self.currentCompounds !=None:
            for item in self.currentCompounds:
                item[5] = None
                item[-1] = []
            self.updateCompoundsList()
        
        # clear match panel
        if self.matchPanel:
            self.matchPanel.setData(self.currentCompounds)
    # ----
    
    
    def runGenerateIons(self, compounds):
        """Calculate compounds ions."""
        
        # run task
        try:
            
            # set adducts
            adducts = {'Na':'Na', 'K':'K', 'Li':'Li', 'NH4':'NH4', '-H2O':'H-2O-1', 'ACN':'CH3CN', 'MeOH':'CH3OH'}
            
            # get max charge and polarity
            polarity = 1
            if config.compoundsSearch['maxCharge'] < 0:
                polarity = -1
            maxCharge = abs(config.compoundsSearch['maxCharge'])+1
            
            # generate compounds ions
            self.currentCompounds = []
            for name, compound in sorted(compounds.items()):
                
                # check compound
                if not compound.isvalid():
                    continue
                
                # walk in charges
                for z in range(1, maxCharge):
                    
                    # 0 name, 1 m/z, 2 z, 3 adduct, 4 formula, 5 error, 6 matches
                    
                    # main ion
                    mz = compound.mz(z*polarity)[config.compoundsSearch['massType']]
                    self.currentCompounds.append([name, mz, z*polarity, None, compound.expression, None, []])
                    
                    # radicals
                    if config.compoundsSearch['radicals']:
                        mz = compound.mz(z*polarity, agentFormula='e', agentCharge=-1)[config.compoundsSearch['massType']]
                        self.currentCompounds.append([name, mz, z*polarity, 'radical', compound.expression, None, []])
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    # add adducts
                    for item in config.compoundsSearch['adducts']:
                        
                        if item in ('Na', 'K', 'Li', 'NH4', 'ACN', 'MeOH'):
                            formula = '%s(%s)(H-1)' % (compound.expression, adducts[item])
                        elif item in ('-H2O'):
                            formula = '%s(%s)' % (compound.expression, adducts[item])
                        
                        formula = mspy.compound(formula)
                        if formula.isvalid():
                            mz = formula.mz(z*polarity)[config.compoundsSearch['massType']]
                            self.currentCompounds.append([name, mz, z*polarity, item, formula.expression, None, []])
                    
                    mspy.CHECK_FORCE_QUIT()
                    
                    # add combinations
                    for item1 in ('Na', 'K', 'Li', 'NH4'):
                        if item1 in config.compoundsSearch['adducts']:
                            for item2 in ('ACN', 'MeOH', '-H2O'):
                                if item2 in config.compoundsSearch['adducts']:
                                    
                                    if item2 in ('ACN', 'MeOH'):
                                        adduct = '%s+%s' % (item1, item2)
                                        formula = '%s(%s)(%s)(H-2)' % (compound.expression, adducts[item1], adducts[item2])
                                    elif item2 in ('-H2O'):
                                        adduct = '%s%s' % (item1, item2)
                                        formula = '%s(%s)(%s)(H-1)' % (compound.expression, adducts[item1], adducts[item2])
                                    
                                    formula = mspy.compound(formula)
                                    if formula.isvalid():
                                        mz = formula.mz(z*polarity)[config.compoundsSearch['massType']]
                                        self.currentCompounds.append([name, mz, z*polarity, adduct, formula.expression, None, []])
        
        # task canceled
        except mspy.ForceQuit:
            self.currentCompounds = []
            return
    # ----
    
    
    def calibrateByMatches(self, references):
        """Use matches for calibration."""
        self.parent.onToolsCalibration(references=references)
    # ----
    
    
