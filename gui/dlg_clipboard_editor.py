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


# CLIPBOARD EDITOR DIALOG
# -----------------------

class dlgClipboardEditor(wx.Dialog):
    """Clipboard data editor for document import."""
    
    def __init__(self, parent, data):
        
        # initialize document frame
        wx.Dialog.__init__(self, parent, -1, "Import Data Points", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.RESIZE_BORDER)
        
        self.data = data
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        self.Layout()
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
        
        # show data
        self.data = self.data.replace('\n\n', '\n')
        self.data_value.SetValue(self.data)
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make elements
        self.data_value = wx.TextCtrl(self, -1, "Reading data...", size=(250,300), style=wx.TE_MULTILINE)
        self.data_value.SetFont(wx.SMALL_FONT)
        
        note_label = wx.StaticText(self, -1, "Please edit your clipboard data to consist\nof m/z and intensity columns only.\nRemove all non-digit characters.", style=wx.ALIGN_CENTER)
        note_label.SetFont(wx.SMALL_FONT)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_butt = wx.Button(self, wx.ID_OK, "Import")
        ok_butt.Bind(wx.EVT_BUTTON, self.onOK)
        
        # pack elements
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttons.Add(ok_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.data_value, 1, wx.EXPAND|wx.CENTER|wx.TOP|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(note_label, 0, wx.CENTER|wx.TOP|wx.LEFT|wx.RIGHT, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttons, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onOK(self, evt):
        """Get name."""
        
        # get data
        self.data = self.data_value.GetValue()
        
        # close dialog
        if self.data:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
