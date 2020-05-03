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

# stop exception
class ForceQuit(Exception):
    """Force quit all processing."""
    pass


# define stopper class
class stopper:
    """Deffinition of processing stopper class."""
    
    def __init__(self):
        self.value = False
    
    def __nonzero__(self):
        return self.value
    
    def __repr__(self):
        return str(self.value)
    
    def enable(self):
        self.value = True
    
    def disable(self):
        self.value = False
    
    def check(self):
        if self.value:
            self.value = False
            raise ForceQuit


# init stopper
STOPPER = stopper()
CHECK_FORCE_QUIT = STOPPER.check


# mspy stopper functions
def stop():
    """Set stopper to stop."""
    STOPPER.enable()

def start():
    """Set stopper to start."""
    STOPPER.disable()
