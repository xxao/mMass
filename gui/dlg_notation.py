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


# NOTATION LABEL
# --------------

class dlgNotation(wx.Dialog):
    """Set notation label."""
    
    def __init__(self, parent, notation, button='Add'):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, 'Notation', style=wx.DEFAULT_DIALOG_STYLE)
        
        self.notation = notation
        self.button = button
        
        # set dlg title
        format = 'Notation for m/z: %0.' + `config.main['mzDigits']` + 'f'
        title = format % (self.notation.mz)
        self.SetTitle(title)
        
        # make GUI
        sizer = self.makeGUI()
        self.setData()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        labelBox = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.HORIZONTAL)
        formulaBox = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.HORIZONTAL)
        
        # make elements
        label_label = wx.StaticText(self, -1, "Label:", style=wx.ALIGN_RIGHT)
        self.label_value = wx.TextCtrl(self, -1, '', size=(300,-1), style=wx.TE_PROCESS_ENTER)
        self.label_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        formula_label = wx.StaticText(self, -1, "Formula:", style=wx.ALIGN_RIGHT)
        self.formula_value = mwx.formulaCtrl(self, -1, '', size=(300,-1), style=wx.TE_PROCESS_ENTER)
        self.formula_value.Bind(wx.EVT_TEXT, self.onFormula)
        self.formula_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        theoreticalMZ_label = wx.StaticText(self, -1, "Theoretical m/z:", style=wx.ALIGN_RIGHT)
        self.theoreticalMZ_value = wx.TextCtrl(self, -1, '', size=(120,-1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('float'))
        self.theoreticalMZ_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        charge_label = wx.StaticText(self, -1, " z:")
        self.charge_value = wx.TextCtrl(self, -1, '', size=(30,-1), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('int'))
        self.charge_value.Bind(wx.EVT_TEXT, self.onFormula)
        self.charge_value.Bind(wx.EVT_TEXT_ENTER, self.onOK)
        
        self.radical_check = wx.CheckBox(self, -1, "M*", size=(50,-1))
        self.radical_check.Bind(wx.EVT_CHECKBOX, self.onMassType)
        
        self.mzByUser_radio = wx.RadioButton(self, -1, "Manual", style=wx.RB_GROUP)
        self.mzByUser_radio.SetFont(wx.SMALL_FONT)
        self.mzByUser_radio.Bind(wx.EVT_RADIOBUTTON, self.onMassType)
        self.mzByUser_radio.SetValue(True)
        
        self.mzByFormulaMo_radio = wx.RadioButton(self, -1, "Mo")
        self.mzByFormulaMo_radio.SetFont(wx.SMALL_FONT)
        self.mzByFormulaMo_radio.Bind(wx.EVT_RADIOBUTTON, self.onMassType)
        
        self.mzByFormulaAv_radio = wx.RadioButton(self, -1, "Av")
        self.mzByFormulaAv_radio.SetFont(wx.SMALL_FONT)
        self.mzByFormulaAv_radio.Bind(wx.EVT_RADIOBUTTON, self.onMassType)
        
        buttons = self.makeButtons()
        
        # pack elements
        labelBox.Add(label_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        labelBox.Add(self.label_value, 1, wx.TOP|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 10)
        
        formulaGrid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        formulaGrid.Add(formula_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        formulaGrid.Add(self.formula_value, (0,1), (1,7), flag=wx.EXPAND)
        formulaGrid.Add(theoreticalMZ_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        formulaGrid.Add(self.theoreticalMZ_value, (1,1))
        formulaGrid.Add(charge_label, (1,2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        formulaGrid.Add(self.charge_value, (1,3))
        formulaGrid.Add(self.radical_check, (1,4), flag=wx.ALIGN_CENTER_VERTICAL)
        formulaGrid.Add(self.mzByUser_radio, (1,5), flag=wx.ALIGN_CENTER_VERTICAL)
        formulaGrid.Add(self.mzByFormulaMo_radio, (1,6), flag=wx.ALIGN_CENTER_VERTICAL)
        formulaGrid.Add(self.mzByFormulaAv_radio, (1,7), flag=wx.ALIGN_CENTER_VERTICAL)
        formulaGrid.AddGrowableCol(1)
        
        formulaBox.Add(formulaGrid, 1, wx.EXPAND|wx.ALL, 10)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(labelBox, 0, wx.EXPAND|wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(formulaBox, 0, wx.EXPAND|wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttons, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def makeButtons(self):
        """Make buttons."""
        
        # make items
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, self.button)
        ok_butt.Bind(wx.EVT_BUTTON, self.onOK)
        ok_butt.SetDefault()
        
        # pack items
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        sizer.Add(ok_butt, 0)
        
        return sizer
    # ----
    
    
    def setData(self):
        """Set data to elements."""
        
        # set label
        self.label_value.SetValue(self.notation.label)
        
        # set formula
        if self.notation.formula:
            self.formula_value.SetValue(self.notation.formula)
        
        # set calc. m/z
        self.mzByUser_radio.SetValue(True)
        if self.notation.theoretical:
            self.theoreticalMZ_value.SetValue(str(self.notation.theoretical))
        
        # set charge
        if self.notation.charge != None:
            self.charge_value.SetValue(str(self.notation.charge))
        
        # set radical
        self.radical_check.SetValue(bool(self.notation.radical))
    # ----
    
    
    def onOK(self, evt=None):
        """Get label."""
        
        # get data
        label = self.label_value.GetValue()
        formula = self.formula_value.GetValue()
        theoretical = self.theoreticalMZ_value.GetValue()
        charge = self.charge_value.GetValue()
        radical = self.radical_check.GetValue()
        
        # check label
        if label:
            self.notation.label = label
        else:
            wx.Bell()
            return
        
        # get formula
        if formula:
            try:
                mspy.compound(formula)
                self.notation.formula = formula
            except:
                wx.Bell()
                return
        else:
            self.notation.formula = None
        
        # get m/z
        if theoretical:
            try:
                self.notation.theoretical = float(theoretical)
            except:
                wx.Bell()
                return
        else:
            self.notation.theoretical = None
        
        # get charge
        if charge:
            try:
                self.notation.charge = int(charge)
            except:
                wx.Bell()
                return
        else:
            self.notation.charge = None
        
        # get radical
        if radical:
            self.notation.radical = 1
        else:
            self.notation.radical = 0
        
        # close dialog
        self.EndModal(wx.ID_OK)
    # ----
    
    
    def onMassType(self, evt=None):
        """Mass type changed."""
        
        if self.mzByUser_radio.GetValue():
            self.theoreticalMZ_value.Enable(True)
        else:
            self.theoreticalMZ_value.Enable(False)
            self.onFormula()
    # ----
    
    
    def onFormula(self, evt=None):
        """Check formula and calculate m/z."""
        
        if evt != None:
            evt.Skip()
        
        # user-defined m/z
        if self.mzByUser_radio.GetValue():
            return
        
        # get data
        formula = self.formula_value.GetValue()
        charge = self.charge_value.GetValue()
        radical = self.radical_check.GetValue()
        if not formula or not charge:
            self.theoreticalMZ_value.SetValue('')
            return
        
        # get m/z from formula
        try:
            compound = mspy.compound(formula)
            charge = int(charge)
            if radical:
                mz = compound.mz(charge=charge, agentFormula='e', agentCharge=-1)
            else:
                mz = compound.mz(charge=charge, agentFormula='H', agentCharge=1)
        except:
            self.theoreticalMZ_value.SetValue('')
            return
        
        # set formula
        if self.mzByFormulaMo_radio.GetValue():
            theoretical = '%0.6f' % mz[0]
            self.theoreticalMZ_value.SetValue(theoretical)
        elif self.mzByFormulaAv_radio.GetValue():
            theoretical = '%0.6f' % mz[1]
            self.theoreticalMZ_value.SetValue(theoretical)
    # ----
    

