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


# FLOATING PANEL WITH DOCUMENT INFO
# ---------------------------------

class panelDocumentInfo(wx.MiniFrame):
    """Document info tools."""
    
    def __init__(self, parent, tool='summary'):
        wx.MiniFrame.__init__(self, parent, -1, 'Document Information', size=(400, 200), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.currentTool = tool
        self.currentDocument = None
        
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
        summary = self.makeSummaryPanel()
        spectrum = self.makeSpectrumPanel()
        notes = self.makeNotesPanel()
        
        # pack elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(summary, 1, wx.EXPAND, 0)
        self.mainSizer.Add(spectrum, 1, wx.EXPAND, 0)
        self.mainSizer.Add(notes, 1, wx.EXPAND, 0)
        
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
        
        # make buttons
        self.summary_butt = wx.BitmapButton(panel, ID_documentInfoSummary, images.lib['documentInfoSummaryOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.summary_butt.SetToolTip(wx.ToolTip("Document summary"))
        self.summary_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.spectrum_butt = wx.BitmapButton(panel, ID_documentInfoSpectrum, images.lib['documentInfoSpectrumOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.spectrum_butt.SetToolTip(wx.ToolTip("Spectrum information"))
        self.spectrum_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.notes_butt = wx.BitmapButton(panel, ID_documentInfoNotes, images.lib['documentInfoNotesOff'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.notes_butt.SetToolTip(wx.ToolTip("Analysis notes"))
        self.notes_butt.Bind(wx.EVT_BUTTON, self.onToolSelected)
        
        self.presets_butt = wx.BitmapButton(panel, -1, images.lib['toolsPresets'], size=(mwx.TOOLBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.presets_butt.SetToolTip(wx.ToolTip("Operator presets"))
        self.presets_butt.Bind(wx.EVT_BUTTON, self.onPresets)
        
        # pack elements
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_LSPACE)
        self.toolbar.Add(self.summary_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.Add(self.spectrum_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.Add(self.notes_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        self.toolbar.AddSpacer(20)
        self.toolbar.Add(self.presets_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        self.toolbar.AddSpacer(mwx.TOOLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeSummaryPanel(self):
        """Document summary panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        title_label = wx.StaticText(panel, -1, "Title:")
        self.title_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.title_value.Bind(wx.EVT_TEXT, self.onSave)
        
        operator_label = wx.StaticText(panel, -1, "Operator:")
        self.operator_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.operator_value.Bind(wx.EVT_TEXT, self.onSave)
        
        contact_label = wx.StaticText(panel, -1, "Contact:")
        self.contact_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.contact_value.Bind(wx.EVT_TEXT, self.onSave)
        
        institution_label = wx.StaticText(panel, -1, "Institution:")
        self.institution_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.institution_value.Bind(wx.EVT_TEXT, self.onSave)
        
        instrument_label = wx.StaticText(panel, -1, "Instrument:")
        self.instrument_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.instrument_value.Bind(wx.EVT_TEXT, self.onSave)
        
        date_label = wx.StaticText(panel, -1, "Date:")
        self.date_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        self.date_value.Bind(wx.EVT_TEXT, self.onSave)
        
        path_label = wx.StaticText(panel, -1, "Path:")
        self.path_value = wx.TextCtrl(panel, -1, "", size=(300, -1))
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(title_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.title_value, (0,1))
        grid.Add(operator_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.operator_value, (1,1))
        grid.Add(contact_label, (2,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.contact_value, (2,1))
        grid.Add(institution_label, (3,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.institution_value, (3,1))
        grid.Add(instrument_label, (4,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.instrument_value, (4,1))
        grid.Add(date_label, (5,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.date_value, (5,1))
        grid.Add(path_label, (6,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.path_value, (6,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeSpectrumPanel(self):
        """Spectrum info panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        scanNumber_label = wx.StaticText(panel, -1, "Scan ID:")
        self.scanNumber_value = wx.TextCtrl(panel, -1, "", size=(180, -1), validator=mwx.validator('intPos'))
        self.scanNumber_value.Bind(wx.EVT_TEXT, self.onSave)
        
        retentionTime_label = wx.StaticText(panel, -1, "Retention time:")
        self.retentionTime_value = wx.TextCtrl(panel, -1, "", size=(180, -1), validator=mwx.validator('floatPos'))
        self.retentionTime_value.Bind(wx.EVT_TEXT, self.onSave)
        
        msLevel_label = wx.StaticText(panel, -1, "MS level:")
        self.msLevel_value = wx.TextCtrl(panel, -1, "", size=(180, -1), validator=mwx.validator('intPos'))
        self.msLevel_value.Bind(wx.EVT_TEXT, self.onSave)
        
        precursorMZ_label = wx.StaticText(panel, -1, "Precursor m/z:")
        self.precursorMZ_value = wx.TextCtrl(panel, -1, "", size=(180, -1), validator=mwx.validator('floatPos'))
        self.precursorMZ_value.Bind(wx.EVT_TEXT, self.onSave)
        
        precursorCharge_label = wx.StaticText(panel, -1, "Precursor charge:")
        self.precursorCharge_value = wx.TextCtrl(panel, -1, "", size=(180, -1), validator=mwx.validator('int'))
        self.precursorCharge_value.Bind(wx.EVT_TEXT, self.onSave)
        
        polarity_label = wx.StaticText(panel, -1, "Polarity:")
        self.polarity_choice = wx.Choice(panel, -1, choices=['Unknown', 'Positive', 'Negative'], size=(180, mwx.SMALL_CHOICE_HEIGHT))
        self.polarity_choice.Bind(wx.EVT_CHOICE, self.onSave)
        
        points_label = wx.StaticText(panel, -1, "Spectrum points:")
        self.points_value = wx.TextCtrl(panel, -1, "", size=(180, -1))
        self.points_value.Enable(False)
        
        peaklist_label = wx.StaticText(panel, -1, "Peak list:")
        self.peaklist_value = wx.TextCtrl(panel, -1, "", size=(180, -1))
        self.peaklist_value.Enable(False)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(scanNumber_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.scanNumber_value, (0,1))
        grid.Add(retentionTime_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.retentionTime_value, (1,1))
        grid.Add(msLevel_label, (2,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.msLevel_value, (2,1))
        grid.Add(precursorMZ_label, (3,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.precursorMZ_value, (3,1))
        grid.Add(precursorCharge_label, (4,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.precursorCharge_value, (4,1))
        grid.Add(polarity_label, (5,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.polarity_choice, (5,1))
        grid.Add(points_label, (6,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.points_value, (6,1))
        grid.Add(peaklist_label, (7,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.peaklist_value, (7,1))
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeNotesPanel(self):
        """Document notes panel."""
        
        panel = wx.Panel(self, -1)
        
        # make elements
        self.notes_value = wx.TextCtrl(panel, -1, "", size=(400, 200), style=wx.TE_MULTILINE)
        self.notes_value.Bind(wx.EVT_TEXT, self.onSave)
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.notes_value, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Destroy this frame."""
        self.Destroy()
    # ----
    
    
    def onToolSelected(self, evt=None, tool=None):
        """Selected tool."""
        
        # get the tool
        if evt != None:
            tool = 'summary'
            if evt.GetId() == ID_documentInfoSummary:
                tool = 'summary'
            elif evt.GetId() == ID_documentInfoSpectrum:
                tool = 'spectrum'
            elif evt.GetId() == ID_documentInfoNotes:
                tool = 'notes'
        
        # set current tool
        self.currentTool = tool
        
        # hide panels
        self.mainSizer.Hide(1)
        self.mainSizer.Hide(2)
        self.mainSizer.Hide(3)
        
        # hide presets button
        self.toolbar.Hide(5)
        
        # set icons off
        self.summary_butt.SetBitmapLabel(images.lib['documentInfoSummaryOff'])
        self.spectrum_butt.SetBitmapLabel(images.lib['documentInfoSpectrumOff'])
        self.notes_butt.SetBitmapLabel(images.lib['documentInfoNotesOff'])
        
        # set panel
        if tool == 'summary':
            self.SetTitle("Document Summary")
            self.mainSizer.Show(1)
            self.toolbar.Show(5)
            self.summary_butt.SetBitmapLabel(images.lib['documentInfoSummaryOn'])
            
        elif tool == 'spectrum':
            self.SetTitle("Spectrum Info")
            self.mainSizer.Show(2)
            self.spectrum_butt.SetBitmapLabel(images.lib['documentInfoSpectrumOn'])
            
        elif tool == 'notes':
            self.SetTitle("Analysis Notes")
            self.mainSizer.Show(3)
            self.notes_butt.SetBitmapLabel(images.lib['documentInfoNotesOn'])
        
        # fit layout
        mwx.layout(self, self.mainSizer)
    # ----
    
    
    def onPresets(self, evt):
        """Show presets."""
        
        # get presets
        presets = libs.presets['operator'].keys()
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
        """Load selected presets."""
        
        # get presets
        item = self.presets_popup.FindItemById(evt.GetId())
        presets = libs.presets['operator'][item.GetText()]
        
        # set data
        self.operator_value.SetValue(presets['operator'])
        self.contact_value.SetValue(presets['contact'])
        self.institution_value.SetValue(presets['institution'])
        self.instrument_value.SetValue(presets['instrument'])
    # ----
    
    
    def onPresetsSave(self, evt):
        """Save current params as presets."""
        
        # get presets name
        dlg = dlgPresetsName(self)
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.name
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # get params
        libs.presets['operator'][name] = {}
        libs.presets['operator'][name]['operator'] = self.operator_value.GetValue()
        libs.presets['operator'][name]['contact'] = self.contact_value.GetValue()
        libs.presets['operator'][name]['institution'] = self.institution_value.GetValue()
        libs.presets['operator'][name]['instrument'] = self.instrument_value.GetValue()
        
        # save presets
        libs.savePresets()
    # ----
    
    
    def onSave(self, evt):
        """Save data."""
        
        # check document
        if not self.currentDocument:
            wx.Bell()
            return
        
        # update title
        if self.currentDocument.title != self.title_value.GetValue():
            self.currentDocument.title = self.title_value.GetValue()
            self.parent.onDocumentChanged(items=('doctitle'))
        
        # save data to document
        self.currentDocument.date = self.date_value.GetValue()
        self.currentDocument.operator = self.operator_value.GetValue()
        self.currentDocument.contact = self.contact_value.GetValue()
        self.currentDocument.institution = self.institution_value.GetValue()
        self.currentDocument.instrument = self.instrument_value.GetValue()
        self.currentDocument.notes = self.notes_value.GetValue()
        
        try: self.currentDocument.spectrum.scanNumber = int(self.scanNumber_value.GetValue())
        except: self.currentDocument.spectrum.scanNumber = None
        
        try: self.currentDocument.spectrum.retentionTime = float(self.retentionTime_value.GetValue())
        except: self.currentDocument.spectrum.retentionTime = None
        
        try: self.currentDocument.spectrum.msLevel = int(self.msLevel_value.GetValue())
        except: self.currentDocument.spectrum.msLevel = None
        
        try: self.currentDocument.spectrum.precursorMZ = float(self.precursorMZ_value.GetValue())
        except: self.currentDocument.spectrum.precursorMZ = None
        
        try: self.currentDocument.spectrum.precursorCharge = int(self.precursorCharge_value.GetValue())
        except: self.currentDocument.spectrum.precursorCharge = None
        
        if self.polarity_choice.GetStringSelection() == 'Positive':
            self.currentDocument.spectrum.polarity = 1
        elif self.polarity_choice.GetStringSelection() == 'Negative':
            self.currentDocument.spectrum.polarity = -1
        else:
            self.currentDocument.spectrum.polarity = None
        
        # set document dirty
        self.parent.onDocumentChanged(items=('info'))
    # ----
    
    
    def setData(self, document):
        """Set current document."""
        
        # set document
        self.currentDocument = document
        
        # clear previous values
        self.title_value.ChangeValue('')
        self.date_value.ChangeValue('')
        self.path_value.ChangeValue('')
        self.operator_value.ChangeValue('')
        self.contact_value.ChangeValue('')
        self.institution_value.ChangeValue('')
        self.instrument_value.ChangeValue('')
        self.scanNumber_value.ChangeValue('')
        self.retentionTime_value.ChangeValue('')
        self.msLevel_value.ChangeValue('')
        self.precursorMZ_value.ChangeValue('')
        self.precursorCharge_value.ChangeValue('')
        self.polarity_choice.SetStringSelection('Unknown')
        self.points_value.ChangeValue('')
        self.peaklist_value.ChangeValue('')
        self.notes_value.ChangeValue('')
        
        # set document values
        if self.currentDocument:
            self.title_value.ChangeValue(document.title)
            self.date_value.ChangeValue(document.date)
            self.path_value.ChangeValue(document.path)
            self.operator_value.ChangeValue(document.operator)
            self.contact_value.ChangeValue(document.contact)
            self.institution_value.ChangeValue(document.institution)
            self.instrument_value.ChangeValue(document.instrument)
            self.notes_value.ChangeValue(document.notes)
            
            if document.spectrum.scanNumber != None:
                self.scanNumber_value.ChangeValue(str(document.spectrum.scanNumber))
            if document.spectrum.retentionTime != None:
                self.retentionTime_value.ChangeValue(str(document.spectrum.retentionTime))
            if document.spectrum.msLevel != None:
                self.msLevel_value.ChangeValue(str(document.spectrum.msLevel))
            if document.spectrum.precursorMZ != None:
                self.precursorMZ_value.ChangeValue(str(document.spectrum.precursorMZ))
            if document.spectrum.precursorCharge != None:
                self.precursorCharge_value.ChangeValue(str(document.spectrum.precursorCharge))
            
            if document.spectrum.polarity == 1:
                self.polarity_choice.SetStringSelection('Positive')
            elif document.spectrum.polarity == -1:
                self.polarity_choice.SetStringSelection('Negative')
            else:
                self.polarity_choice.SetStringSelection('Unknown')
            
            self.points_value.ChangeValue(str(len(document.spectrum.profile)))
            self.peaklist_value.ChangeValue(str(len(document.spectrum.peaklist)))
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
    
