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
import sys
import platform
import numpy
import wx

# load modules
import mwx
import config
import images


# SYSTEM ERROR
# ------------

class dlgError(wx.Dialog):
    """Show exception message."""
    
    def __init__(self, parent, exception=''):
        wx.Dialog.__init__(self, parent, -1, 'Application Error', style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        
        # get system information
        self.exception = ''
        self.exception += exception
        self.exception += '\n-------------------------'
        self.exception += '\nmMass: %s' % (config.version)
        self.exception += '\nPython: %s' % str(platform.python_version_tuple())
        self.exception += '\nwxPython: %s' % str(wx.version())
        self.exception += '\nNumPy: %s' % str(numpy.version.version)
        self.exception += '\n-------------------------'
        self.exception += '\nArchitecture: %s' % str(platform.architecture())
        self.exception += '\nMachine: %s' % str(platform.machine())
        self.exception += '\nPlatform: %s' % str(platform.platform())
        self.exception += '\nProcessor: %s' % str(platform.processor())
        self.exception += '\nSystem: %s' % str(platform.system())
        self.exception += '\nMac: %s' % str(platform.mac_ver())
        self.exception += '\nMSW: %s' % str(platform.win32_ver())
        self.exception += '\nLinux: %s' % str(platform.dist())
        self.exception += '\n-------------------------\n'
        self.exception += 'Add your comments:\n'
        
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
        
        # make elements
        self.exception_value = wx.TextCtrl(self, -1, self.exception, size=(400,250), style=wx.TE_MULTILINE)
        self.exception_value.SetFont(wx.SMALL_FONT)
        
        message_label = wx.StaticText(self, -1, "Uups, another one...\nUnfortunately, you have probably found another bug in mMass.\nPlease send me this error report to support@mmass.org and I will try to fix it.\nI apologize for any inconvenience due to this bug.\nI strongly recommend to restart mMass now.")
        message_label.SetFont(wx.SMALL_FONT)
        
        icon = wx.StaticBitmap(self, -1, images.lib['iconError'])
        
        quit_butt = wx.Button(self, -1, "Quit mMass")
        quit_butt.Bind(wx.EVT_BUTTON, self.onQuit)
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Try to Continue")
        
        # pack elements
        messageSizer = wx.BoxSizer(wx.HORIZONTAL)
        messageSizer.Add(icon, 0, wx.RIGHT, 10)
        messageSizer.Add(message_label, 0, wx.ALIGN_LEFT)
        
        buttSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttSizer.Add(quit_butt, 0, wx.RIGHT, 15)
        buttSizer.Add(cancel_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.exception_value, 0, wx.EXPAND|wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(messageSizer, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttSizer, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onQuit(self, evt):
        """Quit application."""
        sys.exit()
    # ----
    

