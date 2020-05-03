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
import webbrowser

# load modules
from ids import *
import mwx
import images
import config
import mspy


# FLOATING PANEL WITH PERIODIC TABLE OF ELEMENTS
# ----------------------------------------------

class panelPeriodicTable(wx.MiniFrame):
    """Periodic table of elements."""
    
    def __init__(self, parent):
        wx.MiniFrame.__init__(self, parent, -1, 'Periodic Table of the Elements', size=(400, 300), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BOX | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        
        self.parent = parent
        
        self.currentElement = None
        self.currentGroup = None
        
        self.elementsIDs = {}
        self.elementsButtons = {}
        
        self.groups = {
            'Metals':['Li','Na','K','Rb','Cs','Fr','Be','Mg','Ca','Sr','Ba','Ra','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Al','Ga','In','Sn','Tl','Pb','Bi'],
            'Alkali Metals':['Li','Na','K','Rb','Cs','Fr'],
            'Alkaline Earth Metals':['Be','Mg','Ca','Sr','Ba','Ra'],
            'Inner Transition Metals':['La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr'],
            'Lanthanides':['La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu'],
            'Actinides':['Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr'],
            'Transition Metals':['Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg'],
            'Post-Transition Metals':['Al','Ga','In','Sn','Tl','Pb','Bi'],
            'Nonmetals':['H','He','C','N','O','F','Ne','P','S','Cl','Ar','Se','Br','Kr','I','Xe','At','Rn'],
            'Halogens':['F','Cl','Br','I','At'],
            'Noble Gasses':['He','Ne','Ar','Kr','Xe','Rn'],
            'Other Nonmetals':['H','C','N','O','P','S','Se'],
            'Metalloids':['B','Si','Ge','As','Sb','Te','Po'],
        }
        
        # make gui items
        self.makeGUI()
        wx.EVT_CLOSE(self, self.onClose)
    # ----
    
    
    def makeGUI(self):
        """Make panel gui."""
        
        # make toolbar
        toolbar = self.makeToolbar()
        
        # make panels
        table = self.makeTablePanel()
        
        # pack element
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND, 0)
        self.mainSizer.Add(table, 1, wx.EXPAND, 0)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make toolbar."""
        
        # init toolbar
        panel = mwx.bgrPanel(self, -1, images.lib['bgrToolbar'], size=(-1, mwx.TOOLBAR_HEIGHT))
        
        # make highlights
        highlight_label = wx.StaticText(panel, -1, "Highlight:")
        highlight_label.SetFont(wx.SMALL_FONT)
        choices = ['None', '---', 'Metals', 'Alkali Metals', 'Alkaline Earth Metals', 'Inner Transition Metals', 'Lanthanides', 'Actinides', 'Transition Metals', 'Post-Transition Metals', '---', 'Nonmetals', 'Halogens', 'Noble Gasses', 'Other Nonmetals', '---', 'Metalloids']
        self.highlight_choice = wx.Choice(panel, -1, choices=choices, size=(-1, mwx.SMALL_CHOICE_HEIGHT))
        self.highlight_choice.Select(0)
        self.highlight_choice.Bind(wx.EVT_CHOICE, self.onHighlightGroup)
        
        # make buttons
        self.isotopes_butt = wx.Button(panel, -1, "Isotopes", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.isotopes_butt.Bind(wx.EVT_BUTTON, self.onIsotopes)
        self.isotopes_butt.Enable(False)
        
        self.wiki_butt = wx.Button(panel, -1, "Wikipedia", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.wiki_butt.Bind(wx.EVT_BUTTON, self.onWiki)
        
        self.photos_butt = wx.Button(panel, -1, "Photos", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.photos_butt.Bind(wx.EVT_BUTTON, self.onPhotos)
        self.photos_butt.Enable(False)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.CONTROLBAR_LSPACE)
        sizer.Add(highlight_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer.Add(self.highlight_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddStretchSpacer()
        sizer.AddSpacer(20)
        sizer.Add(self.isotopes_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.wiki_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        sizer.Add(self.photos_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.AddSpacer(mwx.CONTROLBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeTablePanel(self):
        """Make periodic table panel."""
        
        elements = (
            ('H',(0,0)), ('He',(0,17)),
            ('Li',(1,0)), ('Be',(1,1)), ('B',(1,12)), ('C',(1,13)), ('N',(1,14)), ('O',(1,15)), ('F',(1,16)), ('Ne',(1,17)),
            ('Na',(2,0)), ('Mg',(2,1)), ('Al',(2,12)), ('Si',(2,13)), ('P',(2,14)), ('S',(2,15)), ('Cl',(2,16)), ('Ar',(2,17)),
            ('K',(3,0)), ('Ca',(3,1)), ('Sc',(3,2)), ('Ti',(3,3)), ('V',(3,4)), ('Cr',(3,5)), ('Mn',(3,6)), ('Fe',(3,7)), ('Co',(3,8)), ('Ni',(3,9)), ('Cu',(3,10)), ('Zn',(3,11)), ('Ga',(3,12)), ('Ge',(3,13)), ('As',(3,14)), ('Se',(3,15)), ('Br',(3,16)), ('Kr',(3,17)),
            ('Rb',(4,0)), ('Sr',(4,1)), ('Y',(4,2)), ('Zr',(4,3)), ('Nb',(4,4)), ('Mo',(4,5)), ('Tc',(4,6)), ('Ru',(4,7)), ('Rh',(4,8)), ('Pd',(4,9)), ('Ag',(4,10)), ('Cd',(4,11)), ('In',(4,12)), ('Sn',(4,13)), ('Sb',(4,14)), ('Te',(4,15)), ('I',(4,16)), ('Xe',(4,17)),
            ('Cs',(5,0)), ('Ba',(5,1)), ('La',(5,2)), ('Hf',(5,3)), ('Ta',(5,4)), ('W',(5,5)), ('Re',(5,6)), ('Os',(5,7)), ('Ir',(5,8)), ('Pt',(5,9)), ('Au',(5,10)), ('Hg',(5,11)), ('Tl',(5,12)), ('Pb',(5,13)), ('Bi',(5,14)), ('Po',(5,15)), ('At',(5,16)), ('Rn',(5,17)),
            ('Fr',(6,0)), ('Ra',(6,1)), ('Ac',(6,2)),
            ('Ce',(8,3)), ('Pr',(8,4)), ('Nd',(8,5)), ('Pm',(8,6)), ('Sm',(8,7)), ('Eu',(8,8)), ('Gd',(8,9)), ('Tb',(8,10)), ('Dy',(8,11)), ('Ho',(8,12)), ('Er',(8,13)), ('Tm',(8,14)), ('Yb',(8,15)), ('Lu',(8,16)),
            ('Th',(9,3)), ('Pa',(9,4)), ('U',(9,5)), ('Np',(9,6)), ('Pu',(9,7)), ('Am',(9,8)), ('Cm',(9,9)), ('Bk',(9,10)), ('Cf',(9,11)), ('Es',(9,12)), ('Fm',(9,13)), ('Md',(9,14)), ('No',(9,15)), ('Lr',(9,16)),
        )
        
        panel = wx.Panel(self, -1)
        grid = wx.GridBagSizer(mwx.PERIODIC_TABLE_GRID[0], mwx.PERIODIC_TABLE_GRID[1])
        
        # make elements
        for element, position in elements:
            buttonID = wx.NewId()
            button = wx.BitmapButton(panel, buttonID, images.lib['periodicTable'+element+'Off'], style=wx.NO_BORDER)
            button.Bind(wx.EVT_BUTTON, self.onElementSelected)
            button.SetToolTip(wx.ToolTip(mspy.elements[element].name))
            
            self.elementsIDs[buttonID] = element
            self.elementsButtons[element] = button
            grid.Add(button, position)
        
        # add connection line to lanthanides and actinides
        connectionLine = wx.StaticBitmap(panel, -1, images.lib['periodicTableConnection'])
        grid.Add(connectionLine, (7,2), (3,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        # make element area
        self.elementName = wx.StaticText(panel, -1, "", size=(200, 20))
        self.elementName.SetFont(wx.Font(mwx.PERIODIC_TABLE_FONT_SIZE, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.elementMass = wx.StaticText(panel, -1, "", size=(200, 30))
        self.elementMass.SetFont(wx.SMALL_FONT)
        
        grid.Add(self.elementName, (0,3), (1,8), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.elementMass, (1,3), (2,8), flag=wx.ALIGN_CENTER_VERTICAL)
        
        # pack table
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.ALIGN_CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        
        # fit layout
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def onClose(self, evt):
        """Hide this frame."""
        
        self.Destroy()
    # ----
    
    
    def onHighlightGroup(self, evt=None):
        """Highlight elements group."""
        
        # clear previous
        self.currentGroup = None
        self.onElementSelected(None)
        
        # get group
        group = self.highlight_choice.GetStringSelection()
        if group in self.groups:
            self.currentGroup = group
        else:
            self.highlight_choice.SetStringSelection('None')
        
        # select group elements
        for element in self.elementsButtons:
            if self.currentGroup and element in self.groups[group]:
                self.elementsButtons[element].SetBitmapLabel(images.lib['periodicTable'+element+'Sel'])
            else:
                self.elementsButtons[element].SetBitmapLabel(images.lib['periodicTable'+element+'Off'])
    # ----
    
    
    def onElementSelected(self, evt=None):
        """Show information for selected element."""
        
        # unselect previous element
        if self.currentElement and self.currentGroup and self.currentElement in self.groups[self.currentGroup]:
            self.elementsButtons[self.currentElement].SetBitmapLabel(images.lib['periodicTable'+self.currentElement+'Sel'])
        elif self.currentElement:
            self.elementsButtons[self.currentElement].SetBitmapLabel(images.lib['periodicTable'+self.currentElement+'Off'])
        
        # clear element infoinfo
        if not evt:
            self.currentElement = None
            self.elementName.SetLabel('')
            self.elementMass.SetLabel('')
            self.isotopes_butt.Enable(False)
            self.photos_butt.Enable(False)
            
        # get current element
        else:
            element = self.elementsIDs[evt.GetId()]
            
            # highlight current element
            self.currentElement = element
            self.elementsButtons[element].SetBitmapLabel(images.lib['periodicTable'+element+'On'])
            
            # show element info
            self.elementName.SetLabel('%s %s (%s)' % (mspy.elements[element].name, element, mspy.elements[element].atomicNumber))
            self.elementMass.SetLabel('Mo. mass: %.6f Da\nAv. mass: %.6f Da' % mspy.elements[element].mass)
            
            # enable buttons
            self.isotopes_butt.Enable(True)
            self.photos_butt.Enable(True)
    # ----
    
    
    def onIsotopes(self, evt=None):
        """Show isotopic pattern."""
        
        if self.currentElement:
            self.parent.onToolsMassCalculator(formula=self.currentElement)
        else:
            wx.Bell()
    # ----
    
    
    def onWiki(self, evt):
        """Go to wikipedia."""
        
        # show selected element
        if self.currentElement:
            link = 'http://en.wikipedia.org/wiki/%s' % mspy.elements[self.currentElement].name
        
        # show selected group
        elif self.currentGroup:
            groups = {
                'Metals':'Metal',
                'Alkali Metals':'Alkali_metal',
                'Alkaline Earth Metals':'Alkaline_earth_metal',
                'Inner Transition Metals':'Inner_transition_element',
                'Lanthanides':'Lanthanide',
                'Actinides':'Actinide',
                'Transition Metals':'Transition_element',
                'Post-Transition Metals':'Post_transition_metal',
                'Nonmetals':'Nonmetal',
                'Halogens':'Halogen',
                'Noble Gasses':'Noble_gas',
                'Other Nonmetals':'',
                'Metalloids':'Metalloid',
            }
            
            link = 'http://en.wikipedia.org/wiki/%s' % groups[self.currentGroup]
        
        # show whole table
        else:
            link = 'http://en.wikipedia.org/wiki/Periodic_table'
        
        # show the link
        if link:
            try: webbrowser.open(link, autoraise=1)
            except: pass
    # ----
    
    
    def onPhotos(self, evt):
        """Go to photographic periodic table of elements."""
        
        # show selected element
        if self.currentElement:
            link = 'http://www.periodictable.com/Elements/%0.3d/index.html' % mspy.elements[self.currentElement].atomicNumber
            try: webbrowser.open(link, autoraise=1)
            except: pass
        else:
            wx.Bell()
    # ----
    
    
