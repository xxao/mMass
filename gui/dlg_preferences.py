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


# PREFERENCES
# -----------

class dlgPreferences(wx.Dialog):
    """Set mMass preferences."""
    
    def __init__(self, parent):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, 'Preferences', style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # make GUI
        mainSizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        mainSizer.Fit(self)
        self.SetSizer(mainSizer)
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # init notebook
        self.notebook = wx.Notebook(self, -1)
        
        # add pages
        if wx.Platform == '__WXMSW__':
            self.notebook.AddPage(self.makeCompassPanel(), 'CompassXport')
        self.notebook.AddPage(self.makeUpdatesPage(), 'Software Updates')
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def makeUpdatesPage(self):
        """Automatic updates panel."""
        
        panel = wx.Panel(self.notebook, -1)
        
        # make elements
        label_label = wx.StaticText(panel, -1, "mMass can use your internet connection to automatically\ncheck for newer versions and updates.")
        
        self.updatesEnabled_check = wx.CheckBox(panel, -1, "Automatically check for updates")
        self.updatesEnabled_check.SetValue(config.main['updatesEnabled'])
        self.updatesEnabled_check.Bind(wx.EVT_CHECKBOX, self.onUpdates)
        
        updateNow_butt = wx.Button(panel, -1, "Check Now", size=(100,-1))
        updateNow_butt.Bind(wx.EVT_BUTTON, self.onUpdateNow)
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(label_label, 0, wx.CENTER|wx.ALL, 10)
        mainSizer.Add(self.updatesEnabled_check, 0, wx.CENTER|wx.ALL, 10)
        mainSizer.Add(updateNow_butt, 0, wx.CENTER|wx.ALL, 10)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def makeCompassPanel(self):
        """CompassXport panel."""
        
        panel = wx.Panel(self.notebook, -1)
        
        # make elements
        label_label = wx.StaticText(panel, -1, "Bruker's CompassXport tool can be used to automatically convert\ndata from Bruker instruments. This feature is available on Windows\nplatform only and CompassXport utility must be installed.")
        
        compassMode_label = wx.StaticText(panel, -1, "Extracted data:")
        self.compassMode_choice = wx.Choice(panel, -1, choices=['Profile', 'Line'], size=(120, mwx.CHOICE_HEIGHT))
        self.compassMode_choice.SetStringSelection(config.main['compassMode'])
        self.compassMode_choice.Bind(wx.EVT_CHOICE, self.onCompass)
        
        compassFormat_label = wx.StaticText(panel, -1, "Data format:")
        self.compassFormat_choice = wx.Choice(panel, -1, choices=['mzXML', 'mzData', 'mzML'], size=(120, mwx.CHOICE_HEIGHT))
        self.compassFormat_choice.SetStringSelection(config.main['compassFormat'])
        self.compassFormat_choice.Bind(wx.EVT_CHOICE, self.onCompass)
        
        compassDeleteFile_label = wx.StaticText(panel, -1, "Delete converted file:")
        self.compassDeleteFile_check = wx.CheckBox(panel, -1, "")
        self.compassDeleteFile_check.SetValue(config.main['compassDeleteFile'])
        self.compassDeleteFile_check.Bind(wx.EVT_CHECKBOX, self.onCompass)
        
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(compassMode_label, (0,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.compassMode_choice, (0,1))
        grid.Add(compassFormat_label, (1,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.compassFormat_choice, (1,1))
        grid.Add(compassDeleteFile_label, (2,0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        grid.Add(self.compassDeleteFile_check, (2,1))
        
        # pack elements
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(label_label, 0, wx.CENTER|wx.ALL, 10)
        mainSizer.Add(grid, 0, wx.CENTER|wx.ALL, 10)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onUpdates(self, evt):
        """Store settings for automatic updates."""
        
        # get values
        config.main['updatesEnabled'] = int(self.updatesEnabled_check.GetValue())
    # ----
    
    
    def onUpdateNow(self, evt):
        """Check for available updates now."""
        self.parent.onHelpUpdate()
    # ----
    
    
    def onCompass(self, evt):
        """Store settings for compass conversion."""
        
        # get values
        config.main['compassMode'] = self.compassMode_choice.GetStringSelection()
        config.main['compassFormat'] = self.compassFormat_choice.GetStringSelection()
        config.main['compassDeleteFile'] = int(self.compassDeleteFile_check.GetValue())
    # ----
    
    