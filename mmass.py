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

# load main config and libs
from gui import config
from gui import libs

# load libs
import sys
import os
import threading
import socket
import socketserver
import wx

# load modules
from gui import mwx
from gui.main_frame import mainFrame


class mMass(wx.App):
    """Run mMass run..."""
    
    def OnInit(self):
        """Init application."""
        
        # set some special wx params
        mwx.appInit()
        
        # init frame
        self.frame = mainFrame(None, -1, 'mMass')
        
        # bind main app frame to server
        #if server != None:
        #    server.app = self.frame
        
        # show frame
        self.SetTopWindow(self.frame)
        # TODO: organise code to not need Yield
        # http://wxpython-users.1045709.n5.nabble.com/wxpython-4-0-3-wx-yield-depreciated-td5728983.html
        # https://stackoverflow.com/questions/22327494/multiple-wx-yield-alternative
        # https://wiki.wxpython.org/LongRunningTasks
        try: wx.GetApp().Yield()
        except: pass
        
        # open file from commandline
        if len(sys.argv) >= 2:
            self.frame.onDocumentDropped(paths=sys.argv[1:])
        
        return True
    # ----
    
    
    def OnExit(self):
        """Exit application."""
        
        # delete instance lock file
        # del self.instance
        pass
    # ----
    
    
    def MacOpenFile(self, path):
        """"Enable drag/drop under Mac."""
        
        if path != 'mmass.py':
            self.frame.onDocumentOpen(path=path)
    # ----
    
    
    def MacReopenApp(self):
        """Called when the doc icon is clicked."""
        
        try:
            self.GetTopWindow().Raise()
        except:
            pass
    # ----
    
    

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """TCP communication server."""
    
    def __init__(self, server_address, RequestHandlerClass):
        self.allow_reuse_address = True
        self.stopped = False
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass, False)
    # ----
    
    
    def serve_forever(self):
        while not self.stopped:
            self.handle_request()
    # ----
    
    
    def force_stop(self):
        self.server_close()
        self.stopped = True
    # ----
    
    

class TCPServerHandler(socketserver.BaseRequestHandler):
    """TCP communication server handler."""
    
    def handle(self):
        
        # get command
        command = self.request.recv(1024)
        self.request.sendall("Command received...\n")
        
        # raise main app frame
        self.server.app.Raise()
        
        # open path
        self.server.app.onServerCommand(command)
    # ----
    
    

def main():    
    server = None
    
    # use server
    #if config.main['useServer'] and sys.platform != 'darwin':
    if False:   # TODO: fix this, having worked out what the server is for
        
        # init server params
        HOST = socket.gethostname()
        PORT = config.main['serverPort']
        
        # get command
        command = ''
        if len(sys.argv) > 1:
            command = sys.argv[-1]
        
        # try to connect to existing server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f'host: {HOST}')
            print(f'port: {PORT}')
            sock.connect((HOST, PORT))
            sock.sendall(command)
            sock.close()
            sys.exit()
        
        # init new app and server
        except socket.error:
            
            server = TCPServer((HOST, PORT), TCPServerHandler)
            server.server_bind()
            server.server_activate()
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.setDaemon(True)
            server_thread.start()
            
            app = mMass(0)
            app.MainLoop()
    
    # skip server
    else:
        app = mMass(0)
        app.MainLoop()
