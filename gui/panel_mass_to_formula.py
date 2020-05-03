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
import webbrowser
import tempfile
import os.path
import numpy

# load modules
from ids import *
import mwx
import images
import config
import mspy


# FLOATING PANEL WITH MASS TO FORMULA TOOL
# ----------------------------------------

class panelMassToFormula(wx.MiniFrame):
    """Mass to formula tool."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Mass To Formula', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.processing = None
        
        self.currentDocument = None
        self.currentFormulae = None
        self.currentMass = None
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbars
        toolbar = self.makeToolbar()
        controlbar1 = self.makeControlbar1()
        controlbar2 = self.makeControlbar2()
        
        # make panels
        self.makeFormulaeList()
        gauge = self.makeGaugePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar1, 0, wx.EXPAND, 0)
        self.mainSizer.Add(controlbar2, 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.formulaeList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        self.mainSizer.Add(gauge, 0, wx.EXPAND, 0)
        
        # hide panels
        self.mainSizer.Hide(4)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.SetMinSize(self.GetSize())
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make elements
        mass_label = wx.StaticText(panel, -1, "Mo. mass:")
        mass_label.SetFont(wx.SMALL_FONT)
        self.mass_value = wx.TextCtrl(panel, -1, "", size=(120, -1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        self.mass_value.Bind(wx.EVT_TEXT_ENTER, self.onGenerate)
        
        charge_label = wx.StaticText(panel, -1, "Charge:")
        charge_label.SetFont(wx.SMALL_FONT)
        self.charge_value = wx.TextCtrl(panel, -1, str(config.massToFormula['charge']), size=(40, -1), validator=mwx.validator('int'))
        
        choices = ['M', 'M*', 'H+', 'Na+', 'K+', 'Li+', 'NH4+']
        self.ionization_choice = wx.Choice(panel, -1, choices=choices, size=(80, mwx.SMALL_CHOICE_HEIGHT))
        choices = ['', 'e', 'H', 'Na', 'K', 'Li', 'NH4']
        if config.massToFormula['ionization'] in choices:
            self.ionization_choice.Select(choices.index(config.massToFormula['ionization']))
        
        tolerance_label = wx.StaticText(panel, -1, "Tolerance:")
        tolerance_label.SetFont(wx.SMALL_FONT)
        self.tolerance_value = wx.TextCtrl(panel, -1, str(config.massToFormula['tolerance']), size=(50, -1), validator=mwx.validator('floatPos'))
        self.tolerance_value.Bind(wx.EVT_TEXT_ENTER, self.onGenerate)
        
        self.unitsDa_radio = wx.RadioButton(panel, -1, "Da", style=wx.RB_GROUP)
        self.unitsDa_radio.SetFont(wx.SMALL_FONT)
        self.unitsDa_radio.SetValue(True)
        self.unitsDa_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        
        self.unitsPpm_radio = wx.RadioButton(panel, -1, "ppm")
        self.unitsPpm_radio.SetFont(wx.SMALL_FONT)
        self.unitsPpm_radio.Bind(wx.EVT_RADIOBUTTON, self.onUnitsChanged)
        self.unitsPpm_radio.SetValue((config.massToFormula['units'] == 'ppm'))
        
        self.generate_butt = wx.Button(panel, -1, "Generate", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.generate_butt.Bind(wx.EVT_BUTTON, self.onGenerate)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(mass_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.mass_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(charge_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.charge_value, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.ionization_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(tolerance_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.tolerance_value, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(10)
        sizer.Add(self.unitsDa_radio, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.unitsPpm_radio, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.generate_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeControlbar1(self):
        """Make composition controlbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrControlbarBorder'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        formulaMin_label = wx.StaticText(panel, -1, "Minimal formula:")
        formulaMin_label.SetFont(wx.SMALL_FONT)
        self.formulaMin_value = mwx.formulaCtrl(panel, -1, config.massToFormula['formulaMin'], size=(150, -1))
        
        formulaMax_label = wx.StaticText(panel, -1, "Maximal formula:")
        formulaMax_label.SetFont(wx.SMALL_FONT)
        self.formulaMax_value = mwx.formulaCtrl(panel, -1, config.massToFormula['formulaMax'], size=(150, -1))
        
        # pack controls
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(formulaMin_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.formulaMin_value, 1, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.AddSpacer(20)
        sizer.Add(formulaMax_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.formulaMax_value, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeControlbar2(self):
        """Make rules controlbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrControlbar'], size=(-1, mwx.CONTROLBAR_HEIGHT))
        
        # make controls
        rules_label = wx.StaticText(panel, -1, "Composition rules:")
        rules_label.SetFont(wx.SMALL_FONT)
        
        self.ruleHC_check = wx.CheckBox(panel, -1, "H/C")
        self.ruleHC_check.SetFont(wx.SMALL_FONT)
        self.ruleHC_check.SetValue(('HC' in config.massToFormula['rules']))
        self.ruleHC_check.Bind(wx.EVT_CHECKBOX, self.onApplyRules)
        
        self.ruleNOPSC_check = wx.CheckBox(panel, -1, "NOPS/C")
        self.ruleNOPSC_check.SetFont(wx.SMALL_FONT)
        self.ruleNOPSC_check.SetValue(('NOPSC' in config.massToFormula['rules']))
        self.ruleNOPSC_check.Bind(wx.EVT_CHECKBOX, self.onApplyRules)
        
        self.ruleNOPS_check = wx.CheckBox(panel, -1, "NOPS")
        self.ruleNOPS_check.SetFont(wx.SMALL_FONT)
        self.ruleNOPS_check.SetValue(('NOPS' in config.massToFormula['rules']))
        self.ruleNOPS_check.Bind(wx.EVT_CHECKBOX, self.onApplyRules)
        
        self.ruleRDBE_check = wx.CheckBox(panel, -1, "RDBE")
        self.ruleRDBE_check.SetFont(wx.SMALL_FONT)
        self.ruleRDBE_check.SetValue(('RDBE' in config.massToFormula['rules']))
        self.ruleRDBE_check.Bind(wx.EVT_CHECKBOX, self.onApplyRules)
        
        self.ruleRDBEInt_check = wx.CheckBox(panel, -1, "Integer RDBE")
        self.ruleRDBEInt_check.SetFont(wx.SMALL_FONT)
        self.ruleRDBEInt_check.SetValue(('RDBEInt' in config.massToFormula['rules']))
        self.ruleRDBEInt_check.Bind(wx.EVT_CHECKBOX, self.onApplyRules)
        
        self.checkPattern_check = wx.CheckBox(panel, -1, "Check isotopic pattern")
        self.checkPattern_check.SetFont(wx.SMALL_FONT)
        self.checkPattern_check.SetValue(config.massToFormula['checkPattern'])
        
        # pack controls
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(rules_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ruleHC_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ruleNOPSC_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ruleNOPS_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ruleRDBE_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.ruleRDBEInt_check, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 40)
        sizer.Add(self.checkPattern_check, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeFormulaeList(self):
        """Make compounds list."""
        
        # init list
        self.formulaeList = mwx.sortListCtrl(self, -1, size=(751, 250), style=mwx.LISTCTRL_STYLE_SINGLE)
        self.formulaeList.SetFont(wx.SMALL_FONT)
        self.formulaeList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.formulaeList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.formulaeList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.formulaeList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        
        if wx.Platform == '__WXMAC__':
            self.formulaeList.Bind(wx.EVT_RIGHT_UP, self.onListRMU)
        else:
            self.formulaeList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onListRMU)
        
        # make columns
        self.formulaeList.InsertColumn(0, "neutral formula", wx.LIST_FORMAT_LEFT)
        self.formulaeList.InsertColumn(1, "mass", wx.LIST_FORMAT_RIGHT)
        self.formulaeList.InsertColumn(2, "m/z", wx.LIST_FORMAT_RIGHT)
        self.formulaeList.InsertColumn(3, "error", wx.LIST_FORMAT_RIGHT)
        self.formulaeList.InsertColumn(4, "H/C", wx.LIST_FORMAT_RIGHT)
        self.formulaeList.InsertColumn(5, "rdbe", wx.LIST_FORMAT_RIGHT)
        self.formulaeList.InsertColumn(6, "pattern", wx.LIST_FORMAT_RIGHT)
        
        # set column widths
        for col, width in enumerate((200,110,100,80,80,80,80)):
            self.formulaeList.SetColumnWidth(col, width)
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
        if wx.Platform == '__WXMAC__':
            mainSizer.Add(wx.StaticLine(panel), 0, wx.EXPAND|wx.TOP, -1)
        mainSizer.Add(sizer, 1, wx.EXPAND|wx.ALL, mwx.GAUGE_SPACE)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Destroy this frame."""
        
        # check processing
        if self.processing != None:
            wx.Bell()
            return
        
        # close self
        self.Destroy()
    # ----
    
    
    def onProcessing(self, status=True):
        """Show processing gauge."""
        
        self.gauge.SetValue(0)
        
        if status:
            self.MakeModal(True)
            self.mainSizer.Show(4)
        else:
            self.MakeModal(False)
            self.mainSizer.Hide(4)
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
    
    
    def onItemSelected(self, evt):
        """Show selected mass in spectrum canvas."""
        
        mz = self.currentFormulae[evt.GetData()][2]
        self.parent.updateMassPoints([mz])
    # ----
    
    
    def onItemActivated(self, evt):
        """Show isotopic pattern for selected compound."""
        self.onItemSendToMassCalculator(evt)
    # ----
    
    
    def onItemSendToMassCalculator(self, evt):
        """Show isotopic pattern for selected compound."""
        
        # get data
        selected = self.formulaeList.getSelected()
        if selected:
            index = self.formulaeList.GetItemData(selected[0])
            formula = self.currentFormulae[index][0]
        else:
            wx.Bell()
            return
        
        # get agent charge
        agentCharge = 1
        if config.massToFormula['ionization'] == 'e':
            agentCharge = -1
        
        # send data to Mass Caclulator tool
        self.parent.onToolsMassCalculator(
            formula = formula,
            charge = config.massToFormula['charge'],
            agentFormula = config.massToFormula['ionization'],
            agentCharge = agentCharge
        )
    # ----
    
    
    def onItemSearch(self, evt):
        """Make query and send formula to selected database."""
        
        # get selected formula
        selected = self.formulaeList.getSelected()
        if selected:
            index = self.formulaeList.GetItemData(selected[0])
            formula = self.currentFormulae[index][0]
        else:
            wx.Bell()
            return
        
        # get selected server
        if evt.GetId() == ID_massToFormulaSearchPubChem:
            server = 'PubChem'
        elif evt.GetId() == ID_massToFormulaSearchChemSpider:
            server = 'ChemSpider'
        elif evt.GetId() == ID_massToFormulaSearchMETLIN:
            server = 'METLIN'
        elif evt.GetId() == ID_massToFormulaSearchHMDB:
            server = 'HMDB'
        elif evt.GetId() == ID_massToFormulaSearchLipidMaps:
            server = 'Lipid MAPS'
        else:
            wx.Bell()
            return
        
        # make search html
        htmlData = self.makeSearchHTML(server, formula)
        
        # run search
        try:
            path = os.path.join(tempfile.gettempdir(), 'mmass_formula_search.html')
            htmlFile = file(path, 'w')
            htmlFile.write(htmlData.encode("utf-8"))
            htmlFile.close()
            webbrowser.open('file://'+path, autoraise=1)
        except:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title='Unable to send data to '+server+' server.', message='Unknown error occured while creating the search page.')
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onItemCopyFormula(self, evt):
        """Copy selected compound formula into clipboard."""
        
        # get data
        selected = self.formulaeList.getSelected()
        if selected:
            index = self.formulaeList.GetItemData(selected[0])
            formula = self.currentFormulae[index][0]
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
        menu.Append(ID_listSendToMassCalculator, "Show Isotopic Pattern", "")
        menu.AppendSeparator()
        menu.Append(ID_massToFormulaSearchPubChem, "Search in PubChem", "")
        menu.Append(ID_massToFormulaSearchChemSpider, "Search in ChemSpider", "")
        menu.Append(ID_massToFormulaSearchMETLIN, "Search in METLIN", "")
        menu.Append(ID_massToFormulaSearchHMDB, "Search in HMDB", "")
        menu.Append(ID_massToFormulaSearchLipidMaps, "Search in Lipid MAPS", "")
        menu.AppendSeparator()
        menu.Append(ID_listCopyFormula, "Copy Formula")
        menu.Append(ID_listCopy, "Copy List")
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onItemSendToMassCalculator, id=ID_listSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onItemSearch, id=ID_massToFormulaSearchPubChem)
        self.Bind(wx.EVT_MENU, self.onItemSearch, id=ID_massToFormulaSearchChemSpider)
        self.Bind(wx.EVT_MENU, self.onItemSearch, id=ID_massToFormulaSearchMETLIN)
        self.Bind(wx.EVT_MENU, self.onItemSearch, id=ID_massToFormulaSearchHMDB)
        self.Bind(wx.EVT_MENU, self.onItemSearch, id=ID_massToFormulaSearchLipidMaps)
        self.Bind(wx.EVT_MENU, self.onItemCopyFormula, id=ID_listCopyFormula)
        self.Bind(wx.EVT_MENU, self.onListCopy, id=ID_listCopy)
        
        # show menu
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onListCopy(self, evt=None):
        """Copy items into clipboard."""
        self.formulaeList.copyToClipboard()
    # ----
    
    
    def onGenerate(self, evt=None):
        """Generate formulae."""
        
        # check processing
        if self.processing:
            return
        
        # clear previous data
        self.currentFormulae = None
        
        # get params
        if not self.getParams():
            self.updateFormulaeList()
            wx.Bell()
            return
        
        # check mass limit
        if not self.checkMassLimit():
            wx.Bell()
            message = "Neutral mass of your specified ion is too high (%.0f Da max)." % config.massToFormula['massLimit']
            dlg = mwx.dlgMessage(self, title="Neutral mass is too high.", message=message)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # show processing gauge
        self.onProcessing(True)
        self.generate_butt.Enable(False)
        
        # do processing
        self.processing = threading.Thread(target=self.runGenerator)
        self.processing.start()
        
        # pulse gauge while working
        while self.processing and self.processing.isAlive():
            self.gauge.pulse()
        
        # update gui
        self.updateFormulaeList()
        
        # hide processing gauge
        self.onProcessing(False)
        self.generate_butt.Enable(True)
        
        # show limit warning
        if self.currentFormulae and len(self.currentFormulae) >= config.massToFormula['countLimit']:
            wx.Bell()
            dlg = mwx.dlgMessage(self, title="Maximum number of formulae reached.", message="The internal limit for number of formulae has been reached.\nPlease note that your formula could be missing.")
            dlg.ShowModal()
            dlg.Destroy()
    # ----
    
    
    def onUnitsChanged(self, evt):
        """Set current units and update data."""
        
        # get units
        config.massToFormula['units'] = 'ppm'
        if self.unitsDa_radio.GetValue():
            config.massToFormula['units'] = 'Da'
        
        # recalculate errors
        if self.currentFormulae:
            for x, item in enumerate(self.currentFormulae):
                self.currentFormulae[x][3] = mspy.delta(self.currentMass, item[2], config.massToFormula['units'])
        
        # update GUI
        self.updateFormulaeList()
    # ----
    
    
    def onApplyRules(self, evt=None):
        """Filter current compounds by selected rules."""
        
        # get rules
        self.getRules()
        
        # update compounds list
        self.updateFormulaeList()
    # ----
    
    
    def setData(self, document=None, mass=None, charge=None, tolerance=None, units=None, agentFormula=None):
        """Set data."""
        
        # set new document
        self.currentDocument = document
        
        # enable/disable profile check
        self.checkPattern_check.Enable(True)
        if self.currentDocument == None or not self.currentDocument.spectrum.hasprofile():
            self.checkPattern_check.Enable(False)
        
        # check mass
        if not mass:
            return
        
        # clear previous results
        self.currentFormulae = None
        
        # update values
        self.mass_value.ChangeValue(str(mass))
        
        if charge != None:
            self.charge_value.ChangeValue(str(charge))
        
        if tolerance != None:
            self.tolerance_value.ChangeValue(str(tolerance))
        
        if units != None:
            self.unitsDa_radio.SetValue(bool(units == 'Da'))
            self.unitsPpm_radio.SetValue(bool(units == 'ppm'))
        
        choices = ['', 'e', 'H', 'Na', 'K', 'Li', 'NH4']
        if agentFormula in choices:
            self.ionization_choice.Select(choices.index(agentFormula))
        
        # update compounds list
        self.updateFormulaeList()
    # ----
    
    
    def getParams(self):
        """Get all params from dialog."""
        
        # try to get values
        try:
            self.currentMass = float(self.mass_value.GetValue())
            config.massToFormula['charge'] = int(self.charge_value.GetValue())
            config.massToFormula['tolerance'] = float(self.tolerance_value.GetValue())
            config.massToFormula['formulaMin'] = self.formulaMin_value.GetValue()
            config.massToFormula['formulaMax'] = self.formulaMax_value.GetValue()
            config.massToFormula['checkPattern'] = self.checkPattern_check.GetValue()
            
            config.massToFormula['units'] = 'ppm'
            if self.unitsDa_radio.GetValue():
                config.massToFormula['units'] = 'Da'
            
            choices = ['', 'e', 'H', 'Na', 'K', 'Li', 'NH4']
            config.massToFormula['ionization'] = choices[self.ionization_choice.GetSelection()]
            
            self.getRules()
            
            return True
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def getRules(self):
        """Get current rules to be applied."""
        
        config.massToFormula['rules'] = []
        
        if self.ruleHC_check.GetValue():
            config.massToFormula['rules'].append('HC')
        
        if self.ruleNOPSC_check.GetValue():
            config.massToFormula['rules'].append('NOPSC')
        
        if self.ruleNOPS_check.GetValue():
            config.massToFormula['rules'].append('NOPS')
        
        if self.ruleRDBE_check.GetValue():
            config.massToFormula['rules'].append('RDBE')
        
        if self.ruleRDBEInt_check.GetValue():
            config.massToFormula['rules'].append('RDBEInt')
    # ----
    
    
    def runGenerator(self):
        """Generate formula for given mass."""
        
        # run task
        try:
            
            self.currentFormulae = []
            
            # get agent charge
            agentCharge = 1
            if config.massToFormula['ionization'] == 'e':
                agentCharge = -1
            
            # approximate CHNO composition from neutral mass
            mass = mspy.mz(
                mass = self.currentMass,
                charge = 0,
                currentCharge = config.massToFormula['charge'],
                agentFormula = config.massToFormula['ionization'],
                agentCharge = agentCharge
            )
            
            composition = {}
            if config.massToFormula['autoCHNO']:
                if mass < 500:
                    composition = {'C':[0,40], 'H':[0,80], 'N':[0,20], 'O':[0,20]}
                elif mass < 1000:
                    composition = {'C':[0,80], 'H':[0,130], 'N':[0,30], 'O':[0,30]}
                elif mass < 2000:
                    composition = {'C':[0,160], 'H':[0,250], 'N':[0,40], 'O':[0,70]}
                else:
                    composition = {'C':[0,180], 'H':[0,300], 'N':[0,60], 'O':[0,90]}
            
            # add user-specified compositions
            minComposition = mspy.compound(config.massToFormula['formulaMin']).composition()
            for el in minComposition:
                if el in composition:
                    composition[el][0] = minComposition[el]
                else:
                    composition[el] = [minComposition[el], minComposition[el]]
            
            maxComposition = mspy.compound(config.massToFormula['formulaMax']).composition()
            for el in maxComposition:
                if el in composition:
                    composition[el][1] = maxComposition[el]
                else:
                    composition[el] = [0, maxComposition[el]]
            
            # calculate formulae
            formulae = mspy.formulator(
                mz = self.currentMass,
                charge = config.massToFormula['charge'],
                tolerance = config.massToFormula['tolerance'],
                units = config.massToFormula['units'],
                composition = composition,
                agentFormula = config.massToFormula['ionization'],
                agentCharge = agentCharge,
                limit = config.massToFormula['countLimit']
            )
            
            # make compounds
            buff = []
            for formula in formulae:
                
                # make compound
                cmpd = mspy.compound(formula)
                mass = cmpd.mass(0)
                mz = cmpd.mz(config.massToFormula['charge'], config.massToFormula['ionization'], 1)[0]
                error = mspy.delta(self.currentMass, mz, config.massToFormula['units'])
                errorDa = mspy.delta(self.currentMass, mz, 'Da')
                
                # compare isotopic pattern
                similarity = None
                if config.massToFormula['checkPattern'] and cmpd.isvalid(charge=config.massToFormula['charge'], agentFormula=config.massToFormula['ionization']):
                    similarity = self.compareIsotopicPattern(cmpd, config.massToFormula['charge'], config.massToFormula['ionization'], errorDa)
                
                # count ratios
                countC = float(cmpd.count('C', groupIsotopes=True))
                countH = float(cmpd.count('H', groupIsotopes=True))
                hc = None
                if countC:
                    hc = countH/countC
                
                # count rdbe
                rdbe = cmpd.rdbe()
                
                # add item
                buff.append([cmpd.formula(), mass, mz, error, hc, rdbe, similarity, cmpd])
            
            self.currentFormulae = buff
        
        # task canceled
        except mspy.ForceQuit:
            return
    # ----
    
    
    def updateFormulaeList(self):
        """Update formulae list."""
        
        # clear previous data and set new
        self.formulaeList.DeleteAllItems()
        self.formulaeList.setDataMap(self.currentFormulae)
        
        # check data
        if not self.currentFormulae:
            return
        
        # add new data
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        errFormat = '%0.' + `config.main['mzDigits']` + 'f'
        
        if config.massToFormula['units'] == 'ppm':
            errFormat = '%0.' + `config.main['ppmDigits']` + 'f'
        
        row = -1
        for index, item in enumerate(self.currentFormulae):
            
            # apply rules
            if not self.applyRules(item[7]):
                continue
            
            # format data
            mass = mzFormat % (item[1])
            mz = mzFormat % (item[2])
            error = errFormat % (item[3])
            rdbe = '%.1f' % item[5]
            
            hc = 'n/a'
            if item[4] != None:
                hc = '%.1f' % item[4]
            
            similarity = 'n/a'
            if item[6] != None:
                similarity = '%.1f' % item[6]
            
            # add data
            row += 1
            self.formulaeList.InsertStringItem(row, item[0])
            self.formulaeList.SetStringItem(row, 1, mass)
            self.formulaeList.SetStringItem(row, 2, mz)
            self.formulaeList.SetStringItem(row, 3, error)
            self.formulaeList.SetStringItem(row, 4, hc)
            self.formulaeList.SetStringItem(row, 5, rdbe)
            self.formulaeList.SetStringItem(row, 6, similarity)
            self.formulaeList.SetItemData(row, index)
        
        # sort data
        self.formulaeList.sort()
        
        # scroll top
        if self.formulaeList.GetItemCount():
            self.formulaeList.EnsureVisible(0)
    # ----
    
    
    def compareIsotopicPattern(self, compound, charge, ionization, shift=0.0):
        """Compare theoretical and real isotopic pattern."""
        
        # check document
        if self.currentDocument == None or not self.currentDocument.spectrum.hasprofile():
            return None
        
        # get baseline window
        baselineWindow = 1.
        if config.processing['peakpicking']['baseline']:
            baselineWindow = 1./config.processing['baseline']['precision']
        
        # get baseline
        baseline = self.currentDocument.spectrum.baseline(
            window = baselineWindow,
            offset = config.processing['baseline']['offset']
        )
        
        # approximate fwhm
        fwhm = 0.1
        mz = compound.mz(charge, ionization, 1)[0]
        peak = mspy.labelpeak(
            signal = self.currentDocument.spectrum.profile,
            mz = mz+shift,
            pickingHeight = config.processing['peakpicking']['pickingHeight'],
            baseline = baseline
        )
        if peak:
            fwhm = peak.fwhm
        
        # make pattern
        pattern = compound.pattern(
            fwhm = fwhm,
            threshold = 0.01,
            charge = charge,
            agentFormula = ionization,
            agentCharge = 1,
            real = True
        )
        
        # add error shift to pattern
        for x in range(len(pattern)):
            pattern[x][0] += shift
        
        # match pattern to signal
        rms = mspy.matchpattern(
            signal = self.currentDocument.spectrum.profile,
            pattern = pattern,
            pickingHeight = config.processing['peakpicking']['pickingHeight'],
            baseline = baseline,
        )
        
        # calc similarity
        if rms != None:
            rms = (1-rms)*100
        
        return rms
    # ----
    
    
    def applyRules(self, compound):
        """Apply current rules."""
        
        HC = (config.massToFormula['HCMin'], config.massToFormula['HCMax'])
        NOPSC = (config.massToFormula['NCMax'], config.massToFormula['OCMax'], config.massToFormula['PCMax'], config.massToFormula['SCMax'])
        RDBE = (config.massToFormula['RDBEMin'], config.massToFormula['RDBEMax'])
        
        return compound.frules(
            rules = config.massToFormula['rules'],
            HC = HC,
            NOPSC = NOPSC,
            RDBE = RDBE,
        )
    # ----
    
    
    def makeSearchHTML(self, server, formula):
        """Format data to HMDB html."""
        
        # get script
        script = config.massToFormula[server.replace(' ', '')+'Script']
        
        # get method
        method = 'post'
        if server in ['ChemSpider', 'HMDB']:
            method = 'get'
        
        # get formula
        formula = self._escape(formula)
        
        # make html page
        buff = '<?xml version="1.0" encoding="utf-8"?>\n'
        buff += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
        buff += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        buff += '<head>\n'
        buff += '  <title>mMass - %s Search</title>\n' % (server)
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
        
        # page start
        buff += '<body onload="runsearch()">\n'
        buff += '<body>\n'
        buff += '  <form action="%s" id="mainSearch" enctype="multipart/form-data" method="%s">\n' % (script, method)
        buff += '    <div style="display:none;">\n\n'
            
        # search query
        if server == 'PubChem':
            buff += '      <input type="hidden" name="cmd" value="search" />\n'
            buff += '      <input type="hidden" name="subcmd" value="" />\n'
            buff += '      <input type="hidden" name="retmode" value="" />\n'
            buff += '      <input type="hidden" name="mode" value="simplequery" />\n'
            buff += '      <input type="hidden" name="mf_md" value="simplequery" />\n'
            buff += '      <input type="hidden" name="mf_qtp" value="dt" />\n'
            buff += '      <input type="hidden" name="in_tp" value="mf" />\n'
            buff += '      <input type="hidden" name="q_type" value="mf" />\n'
            buff += '      <input type="text" name="q_data" value="%s" />\n' % (formula)
        
        elif server == 'ChemSpider':
            buff += '      <input type="text" name="q" value="%s"  />\n' % (formula)
        
        elif server == 'METLIN':
            buff += '      <input type="text" name="formula" value="%s"  />\n' % (formula)
        
        elif server == 'HMDB':
            buff += '      <input type="text" name="query" value="%s"  />\n' % (formula)
        
        elif server == 'Lipid MAPS':
            buff += '      <input type="hidden" name="Mode" value="ProcessTextOntologySearch" />\n'
            buff += '      <input type="hidden" name="ResultsPerPage" value="50" />\n'
            buff += '      <input type="text" name="Formula" value="%s" />\n' % (formula)
        
        # page end
        buff += '    </div>\n\n'
        buff += '    <div id="info">\n'
        buff += '      <h1>mMass - %s Search</h1>\n' % (server)
        buff += '      <p id="sending">Sending data to %s &hellip;</p>\n' % (server)
        buff += '      <p id="wait">Please wait &hellip;</p>\n'
        buff += '      <p id="note">Press the <strong>Search</strong> button if data was not sent automatically.</p>\n'
        buff += '      <p id="button"><input type="submit" value="Search" /></p>\n'
        buff += '    </div>\n\n'
        
        buff += '  </form>\n'
        buff += '</body>\n'
        buff += '</html>\n'
        
        return buff
    # ----
    
    
    def checkMassLimit(self):
        """Check maximim neutral mass allowed."""
        
        # get agent charge
        agentCharge = 1
        if config.massToFormula['ionization'] == 'e':
            agentCharge = -1
        
        # approximate CHNO composition from neutral mass
        mass = mspy.mz(
            mass = self.currentMass,
            charge = 0,
            currentCharge = config.massToFormula['charge'],
            agentFormula = config.massToFormula['ionization'],
            agentCharge = agentCharge
        )
        
        # check mass limit
        if mass <= config.massToFormula['massLimit']:
            return True
        
        return False
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
    
    

