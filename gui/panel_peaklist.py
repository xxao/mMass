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
import mspy
import doc

from dlg_notation import dlgNotation


# PEAKLIST PANEL
# --------------

class panelPeaklist(wx.Panel):
    """Make peaklist panel."""
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, size=(150, -1), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.parent = parent
        
        self.currentDocument = None
        self.peakListMap = None
        self.selectedPeak = None
        
        # make GUI
        self.makeGUI()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make peaklist list
        self.makePeakList()
        
        # init editing panel
        editor = self.makeEditor()
        
        # init lower toolbar
        toolbar = self.makeToolbar()
        
        # pack gui elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.peakList, 1, wx.EXPAND|wx.ALL, mwx.LISTCTRL_NO_SPACE)
        self.mainSizer.Add(editor, 0, wx.EXPAND)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND)
        
        # hide peak editor
        self.mainSizer.Hide(1)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make bottom toolbar."""
        
        # init toolbar panel
        panel = mwx.bgrPanel(self, -1, images.lib['bgrBottombar'], size=(-1, mwx.BOTTOMBAR_HEIGHT))
        
        self.addPeak_butt = wx.BitmapButton(panel, -1, images.lib['peaklistAdd'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.addPeak_butt.SetToolTip(wx.ToolTip("Add peak manually..."))
        self.addPeak_butt.Bind(wx.EVT_BUTTON, self.onAdd)
        
        self.deletePeak_butt = wx.BitmapButton(panel, -1, images.lib['peaklistDelete'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.deletePeak_butt.SetToolTip(wx.ToolTip("Remove peaks..."))
        self.deletePeak_butt.Bind(wx.EVT_BUTTON, self.onDelete)
        
        self.annotatePeak_butt = wx.BitmapButton(panel, -1, images.lib['peaklistAnnotate'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.annotatePeak_butt.SetToolTip(wx.ToolTip("Annotate peak..."))
        self.annotatePeak_butt.Bind(wx.EVT_BUTTON, self.onAnnotate)
        
        self.editPeak_butt = wx.BitmapButton(panel, -1, images.lib['peaklistEditorOff'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.editPeak_butt.SetToolTip(wx.ToolTip("Show / hide peak editor"))
        self.editPeak_butt.Bind(wx.EVT_BUTTON, self.onEdit)
        
        self.peaksCount = wx.StaticText(panel, -1, "")
        self.peaksCount.SetFont(wx.SMALL_FONT)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.BOTTOMBAR_LSPACE)
        sizer.Add(self.addPeak_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.deletePeak_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.annotatePeak_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.Add(self.editPeak_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(10)
        sizer.Add(self.peaksCount, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.AddSpacer(mwx.BOTTOMBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makePeakList(self):
        """Make peaklist list."""
        
        # init peaklist
        self.peakList = mwx.sortListCtrl(self, -1, size=(201, -1), style=mwx.LISTCTRL_STYLE_MULTI)
        self.peakList.SetFont(wx.SMALL_FONT)
        self.peakList.setSecondarySortColumn(0)
        self.peakList.setAltColour(mwx.LISTCTRL_ALTCOLOUR)
        
        # set events
        self.peakList.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.onColumnRMU)
        self.peakList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.peakList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
        self.peakList.Bind(wx.EVT_KEY_DOWN, self.onListKey)
        
        if wx.Platform == '__WXMAC__':
            self.peakList.Bind(wx.EVT_RIGHT_UP, self.onItemRMU)
        else:
            self.peakList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onItemRMU)
        
        # make columns
        self.makePeakListColumns()
        
        # set DnD
        dropTarget = fileDropTarget(self.parent.onDocumentDropped)
        self.peakList.SetDropTarget(dropTarget)
    # ----
    
    
    def makePeakListColumns(self):
        """Make peaklist columns according to config."""
        
        # delete current columns
        self.peakList.deleteColumns()
        
        # add new columns
        x = 0
        for column in config.main['peaklistColumns']:
            
            if column == 'mz':
                self.peakList.InsertColumn(x, "m/z", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 90)
                x += 1
            
            elif column == 'ai':
                self.peakList.InsertColumn(x, "a.i.", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 90)
                x += 1
            
            elif column == 'int':
                self.peakList.InsertColumn(x, "int.", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 90)
                x += 1
            
            elif column == 'base':
                self.peakList.InsertColumn(x, "base", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 60)
                x += 1
            
            elif column == 'rel':
                self.peakList.InsertColumn(x, "r. int.", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 55)
                x += 1
            
            elif column == 'sn':
                self.peakList.InsertColumn(x, "s/n", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 50)
                x += 1
            
            elif column == 'z':
                self.peakList.InsertColumn(x, "z", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 30)
                x += 1
            
            elif column == 'mass':
                self.peakList.InsertColumn(x, "mass", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 90)
                x += 1
            
            elif column == 'fwhm':
                self.peakList.InsertColumn(x, "fwhm", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 60)
                x += 1
            
            elif column == 'resol':
                self.peakList.InsertColumn(x, "resol.", wx.LIST_FORMAT_RIGHT)
                self.peakList.SetColumnWidth(x, 60)
                x += 1
            
            elif column == 'group':
                self.peakList.InsertColumn(x, "group", wx.LIST_FORMAT_LEFT)
                self.peakList.SetColumnWidth(x, 60)
                x += 1
            
            else:
                continue
    # ----
    
    
    def makeEditor(self):
        """Make panel for peak editing."""
        
        # init panel
        panel = mwx.bgrPanel(self, -1, images.lib['bgrPeakEditor'])
        
        # make elements
        peakMz_label = wx.StaticText(panel, -1, "m/z:")
        self.peakMz_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        peakMz_label.SetFont(wx.SMALL_FONT)
        self.peakMz_value.SetFont(wx.SMALL_FONT)
        
        peakAi_label = wx.StaticText(panel, -1, "a.i.:")
        self.peakAi_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        peakAi_label.SetFont(wx.SMALL_FONT)
        self.peakAi_value.SetFont(wx.SMALL_FONT)
        
        peakBase_label = wx.StaticText(panel, -1, "base:")
        self.peakBase_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        peakBase_label.SetFont(wx.SMALL_FONT)
        self.peakBase_value.SetFont(wx.SMALL_FONT)
        
        peakSN_label = wx.StaticText(panel, -1, "s/n:")
        self.peakSN_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('floatPos'))
        peakSN_label.SetFont(wx.SMALL_FONT)
        self.peakSN_value.SetFont(wx.SMALL_FONT)
        
        peakCharge_label = wx.StaticText(panel, -1, "charge:")
        self.peakCharge_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), validator=mwx.validator('int'))
        peakCharge_label.SetFont(wx.SMALL_FONT)
        self.peakCharge_value.SetFont(wx.SMALL_FONT)
        
        peakFwhm_label = wx.StaticText(panel, -1, "fwhm:")
        self.peakFwhm_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), style=wx.TE_PROCESS_ENTER, validator=mwx.validator('floatPos'))
        peakFwhm_label.SetFont(wx.SMALL_FONT)
        self.peakFwhm_value.SetFont(wx.SMALL_FONT)
        
        peakGroup_label = wx.StaticText(panel, -1, "group:")
        self.peakGroup_value = wx.TextCtrl(panel, -1, '', size=(80, mwx.SMALL_TEXTCTRL_HEIGHT), style=wx.TE_PROCESS_ENTER)
        peakGroup_label.SetFont(wx.SMALL_FONT)
        self.peakGroup_value.SetFont(wx.SMALL_FONT)
        
        self.peakMonoisotopic_check = wx.CheckBox(panel, -1, "monoisotopic")
        self.peakMonoisotopic_check.SetValue(True)
        self.peakMonoisotopic_check.SetFont(wx.SMALL_FONT)
        
        self.peakAdd_butt = wx.Button(panel, -1, "Add", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.peakAdd_butt.Bind(wx.EVT_BUTTON, self.onAddPeak)
        
        self.peakReplace_butt = wx.Button(panel, -1, "Update", size=(-1, mwx.SMALL_BUTTON_HEIGHT))
        self.peakReplace_butt.Bind(wx.EVT_BUTTON, self.onReplacePeak)
        self.peakReplace_butt.Enable(False)
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(peakMz_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakMz_value, (0,1), flag=wx.EXPAND)
        grid.Add(peakAi_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakAi_value, (1,1), flag=wx.EXPAND)
        grid.Add(peakBase_label, (2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakBase_value, (2,1), flag=wx.EXPAND)
        grid.Add(peakSN_label, (3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakSN_value, (3,1), flag=wx.EXPAND)
        grid.Add(peakCharge_label, (4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakCharge_value, (4,1), flag=wx.EXPAND)
        grid.Add(peakFwhm_label, (5,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakFwhm_value, (5,1), flag=wx.EXPAND)
        grid.Add(peakGroup_label, (6,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peakGroup_value, (6,1), flag=wx.EXPAND)
        grid.Add(self.peakMonoisotopic_check, (7,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        grid.AddGrowableCol(1)
        
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(self.peakAdd_butt, 0, wx.RIGHT, 10)
        buttons.Add(self.peakReplace_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(grid, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 10)
        mainSizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT|wx.BOTTOM, 10)
        
        # fit layout
        mainSizer.Fit(panel)
        panel.SetSizer(mainSizer)
        
        return panel
    # ----
    
    
    def onItemSelected(self, evt):
        """Highlight selected peak in the spectrum and refresh peak editor."""
        
        evt.Skip()
        
        # get selected peak
        self.selectedPeak = evt.GetData()
        peak = self.currentDocument.spectrum.peaklist[self.selectedPeak]
        
        # highlight point in the spectrum
        selected = self.peakList.getSelected()
        if len(selected) == 1:
            self.parent.updateMassPoints([peak.mz])
        
        # show current peak in editing panel
        self.updatePeakEditor(peak)
    # ----
    
    
    def onItemActivated(self, evt):
        """Create annotation for activated peak."""
        self.onAnnotate()
    # ----
    
    
    def onItemRMU(self, evt):
        """Show item pop-up menu."""
        
        evt.Skip()
        
        # check document and selected peak
        if self.currentDocument == None or self.selectedPeak == None:
            return
        
        # popup menu
        menu = wx.Menu()
        menu.Append(ID_peaklistAnnotate, "Annotate Peak...", "")
        menu.AppendSeparator()
        menu.Append(ID_peaklistSendToMassToFormula, "Send to Mass to Formula...", "")
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onAnnotate, id=ID_peaklistAnnotate)
        self.Bind(wx.EVT_MENU, self.onSendToMassToFormula, id=ID_peaklistSendToMassToFormula)
        
        # show menu
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onColumnRMU(self, evt):
        """Show column popup menu."""
        
        menu = wx.Menu()
        menu.Append(ID_viewPeaklistColumnMz, "m/z", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnAi, "a.i", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnInt, "Intensity", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnBase, "Baseline", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnRel, "Rel. Intensity", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnSn, "s/n", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnZ, "Charge", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnMass, "Mass", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnFwhm, "FWHM", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnResol, "Resolution", "", wx.ITEM_CHECK)
        menu.Append(ID_viewPeaklistColumnGroup, "Group", "", wx.ITEM_CHECK)
        
        menu.Check(ID_viewPeaklistColumnMz, bool('mz' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnAi, bool('ai' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnInt, bool('int' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnBase, bool('base' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnRel, bool('rel' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnSn, bool('sn' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnZ, bool('z' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnMass, bool('mass' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnFwhm, bool('fwhm' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnResol, bool('resol' in config.main['peaklistColumns']))
        menu.Check(ID_viewPeaklistColumnGroup, bool('group' in config.main['peaklistColumns']))
        
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnMz)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnAi)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnInt)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnBase)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnRel)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnSn)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnZ)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnMass)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnFwhm)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnResol)
        self.Bind(wx.EVT_MENU, self.parent.onViewPeaklistColumns, id=ID_viewPeaklistColumnGroup)
        
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onListKey(self, evt):
        """Key pressed."""
        
        # get key
        key = evt.GetKeyCode()
        
        # select all
        if key == 65 and evt.CmdDown():
            for x in range(self.peakList.GetItemCount()):
                self.peakList.SetItemState(x, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        
        # copy
        elif key == 67 and evt.CmdDown():
            self.copyToClipboard()
        
        # delete
        elif key==wx.WXK_DELETE or (key==wx.WXK_BACK and evt.CmdDown()):
            self.onDeleteSelected()
            
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onAdd(self, evt):
        """Plus button pressed."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
            
        # empty data in peak editor
        self.updatePeakEditor(None)
        
        # show editing panel if not shown
        if not self.mainSizer.IsShown(1):
            self.editPeak_butt.SetBitmapLabel(images.lib['peaklistEditorOn'])
            self.mainSizer.Show(1)
            self.Layout()
    # ----
    
    
    def onDelete(self, evt):
        """Minus button pressed."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # popup menu
        menuDeleteSelectedID = wx.NewId()
        menuDeleteByThresholdID = wx.NewId()
        menuDeleteAllID = wx.NewId()
        
        menu = wx.Menu()
        menu.Append(menuDeleteSelectedID, "Delete Selected")
        menu.Append(menuDeleteByThresholdID, "Delete by Threshold...")
        menu.AppendSeparator()
        menu.Append(menuDeleteAllID, "Delete All")
        
        self.Bind(wx.EVT_MENU, self.onDeleteSelected, id=menuDeleteSelectedID)
        self.Bind(wx.EVT_MENU, self.onDeleteByThreshold, id=menuDeleteByThresholdID)
        self.Bind(wx.EVT_MENU, self.onDeleteAll, id=menuDeleteAllID)
        
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onAnnotate(self, evt=None):
        """Annotate selected peak."""
        
        # check document and selected peak
        if self.currentDocument == None or self.selectedPeak == None:
            wx.Bell()
            return
        
        # make annotation
        peak = self.currentDocument.spectrum.peaklist[self.selectedPeak]
        annot = doc.annotation(label='', mz=peak.mz, ai=peak.ai, base=peak.base, charge=peak.charge)
        
        # get annotation label
        dlg = dlgNotation(self.parent, annot, button='Add')
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # add annotation
        self.currentDocument.annotations.append(annot)
        self.currentDocument.sortAnnotations()
        self.parent.onDocumentChanged(items=('annotations'))
    # ----
    
    
    def onEdit(self, evt):
        """Show / hide peak editing panel."""
        
        # hide peak editing panel
        if self.mainSizer.IsShown(1):
            self.editPeak_butt.SetBitmapLabel(images.lib['peaklistEditorOff'])
            self.mainSizer.Hide(1)
            self.Layout()
        
        # show peak editing panel
        else:
            self.editPeak_butt.SetBitmapLabel(images.lib['peaklistEditorOn'])
            self.mainSizer.Show(1)
            self.Layout()
    # ----
    
    
    def onDeleteSelected(self, evt=None):
        """Delete selected peaks."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # get selected peaks
        indexes = []
        for item in self.peakList.getSelected():
            indexes.append(self.peakList.GetItemData(item))
        
        # update data
        self.currentDocument.backup(('spectrum'))
        self.currentDocument.spectrum.peaklist.delete(indexes)
        self.parent.onDocumentChanged(items=('spectrum'))
    # ---
    
    
    def onDeleteByThreshold(self, evt=None):
        """Delete peaks by selected threshold."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # show threshold dialog
        dlg = dlgThreshold(self.parent)
        if dlg.ShowModal() == wx.ID_OK:
            threshold, thresholdType = dlg.getData()
            dlg.Destroy()
            
            indexes = []
            
            # use m/z
            if thresholdType == 'm/z':
                for i, peak in enumerate(self.currentDocument.spectrum.peaklist):
                    if peak.mz < threshold:
                        indexes.append(i)
            
            # use a.i.
            elif thresholdType == 'a.i.':
                for i, peak in enumerate(self.currentDocument.spectrum.peaklist):
                    if peak.ai < threshold:
                        indexes.append(i)
            
            # use intensity
            if thresholdType == 'Intensity':
                for i, peak in enumerate(self.currentDocument.spectrum.peaklist):
                    if peak.intensity < threshold:
                        indexes.append(i)
            
            # use relative intensity
            elif thresholdType == 'Relative Intensity':
                threshold /= 100
                for i, peak in enumerate(self.currentDocument.spectrum.peaklist):
                    if peak.ri < threshold:
                        indexes.append(i)
            
            # use s/n
            elif thresholdType == 's/n':
                for i, peak in enumerate(self.currentDocument.spectrum.peaklist):
                    if peak.sn != None and peak.sn < threshold:
                        indexes.append(i)
            
            # delete peaks
            if indexes:
                self.currentDocument.backup(('spectrum'))
                self.currentDocument.spectrum.peaklist.delete(indexes)
                self.parent.onDocumentChanged(items=('spectrum'))
        
        else:
            dlg.Destroy()
            return
    # ----
    
    
    def onDeleteAll(self, evt=None):
        """Delete all peaks."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # empty peaklist
        self.currentDocument.backup(('spectrum'))
        self.currentDocument.spectrum.peaklist.empty()
        self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def onAddPeak(self, evt):
        """Get peak data and add peak."""
        
        # check document
        if self.currentDocument == None:
            wx.Bell()
            return
        
        # add new peak
        peak = self.getPeakEditorData()
        if peak:
            self.currentDocument.backup(('spectrum'))
            self.currentDocument.spectrum.peaklist.append(peak)
            self.parent.onDocumentChanged(items=('spectrum'))
        
        # set focus to mz
        self.peakMz_value.SetFocus()
    # ----
    
    
    def onReplacePeak(self, evt):
        """Get peak data and refresh current peak."""
        
        # check selection
        if self.selectedPeak == None:
            wx.Bell()
            return
        
        # set new data to peak
        peak = self.getPeakEditorData()
        if peak:
            self.currentDocument.backup(('spectrum'))
            self.currentDocument.spectrum.peaklist[self.selectedPeak] = peak
            self.parent.onDocumentChanged(items=('spectrum'))
    # ----
    
    
    def onSendToMassToFormula(self, evt=None):
        """Send selected peak to mass to formula tool."""
        
        # check document and selected peak
        if self.currentDocument == None or self.selectedPeak == None:
            wx.Bell()
            return
        
        # get peak data
        peak = self.currentDocument.spectrum.peaklist[self.selectedPeak]
        
        # send peak to mass to formula tool
        self.parent.onToolsMassToFormula(mass=peak.mz, charge=peak.charge)
    # ----
    
    
    def setData(self, document):
        """Set new document."""
        
        # set new data
        self.currentDocument = document
        
        # update peaklist
        self.updatePeakList()
    # ----
    
    
    def updatePeaklistColumns(self):
        """Set new peaklist columns and update."""
        
        self.makePeakListColumns()
        self.Layout()
        self.updatePeakList()
    # ----
    
    
    def updatePeakList(self):
        """Refresh peaklist."""
        
        # clear previous data
        self.peakList.DeleteAllItems()
        self.selectedPeak = None
        self.updatePeakEditor(None)
        
        # check data
        if not self.currentDocument:
            self.peaksCount.SetLabel('')
            self.peakListMap = None
            self.peakList.setDataMap(None)
            return
        
        # update peaks count
        count = '%d' % len(self.currentDocument.spectrum.peaklist)
        if count != '0':
            self.peaksCount.SetLabel(count)
        else:
            self.peaksCount.SetLabel('')
        
        # set new data map
        self.peakListMap = []
        for peak in self.currentDocument.spectrum.peaklist:
            row = []
            for column in config.main['peaklistColumns']:
                if column == 'mz':
                    row.append(peak.mz)
                elif column == 'ai':
                    row.append(peak.ai)
                elif column == 'int':
                    row.append(peak.intensity)
                elif column == 'base':
                    row.append(peak.base)
                elif column == 'rel':
                    row.append(peak.ri*100)
                elif column == 'sn':
                    row.append(peak.sn)
                elif column == 'z':
                    row.append(peak.charge)
                elif column == 'mass':
                    row.append(peak.mass())
                elif column == 'fwhm':
                    row.append(peak.fwhm)
                elif column == 'resol':
                    row.append(peak.resolution)
                elif column == 'group':
                    row.append(peak.group)
                else:
                    continue
            
            self.peakListMap.append((row))
            
        self.peakList.setDataMap(self.peakListMap)
        
        # add new data
        for row, item in enumerate(self.peakListMap):
            self.updatePeakListItem(row, item, insert=True)
            self.peakList.SetItemData(row, row)
        
        # sort data
        self.peakList.sort()
        
        # scroll top
        if len(self.currentDocument.spectrum.peaklist) > 0:
            self.peakList.EnsureVisible(0)
    # ----
    
    
    def updatePeakListItem(self, row, item, insert=False):
        """Refresh item data in the list."""
        
        # set formats
        mzFormat = '%0.' + `config.main['mzDigits']` + 'f'
        intFormat = '%0.' + `config.main['intDigits']` + 'f'
        fwhmFormat = '%0.' + `max(config.main['mzDigits'],3)` + 'f'
        
        # insert data
        x = 0
        for column in config.main['peaklistColumns']:
            
            # get data
            data = ''
            
            if column == 'mz':
                data = mzFormat % (item[x])
            
            elif column == 'ai':
                data = intFormat % (item[x])
            
            elif column == 'int':
                data = intFormat % (item[x])
            
            elif column == 'base':
                data = intFormat % (item[x])
            
            elif column == 'rel':
                if item[x]:
                    data = '%0.2f' % (item[x])
            
            elif column == 'sn':
                if item[x] != None:
                    data = '%0.1f' % (item[x])
            
            elif column == 'z':
                if item[x] != None:
                    data = str(item[x])
            
            elif column == 'mass':
                if item[x]:
                    data = mzFormat % (item[x])
            
            elif column == 'fwhm':
                if item[x]:
                    data = fwhmFormat % (item[x])
            
            elif column == 'resol':
                if item[x]:
                    data = '%0.0f' % (item[x])
            
            elif column == 'group':
                if item[x] != None:
                    data = unicode(item[x])
            
            else:
                continue
            
            # add data
            if x == 0 and insert:
                self.peakList.InsertStringItem(row, data)
            else:
                self.peakList.SetStringItem(row, x, data)
            
            x += 1
    # ----
    
    
    def updatePeakEditor(self, peak=None):
        """Refresh peak editing panel."""
        
        # empty data
        self.peakMz_value.SetValue('')
        self.peakAi_value.SetValue('')
        self.peakBase_value.SetValue('')
        self.peakSN_value.SetValue('')
        self.peakCharge_value.SetValue('')
        self.peakFwhm_value.SetValue('')
        self.peakGroup_value.SetValue('')
        self.peakMonoisotopic_check.SetValue(True)
        self.peakReplace_butt.Enable(False)
        
        # set peak data
        if peak:
            self.peakMz_value.SetValue(str(round(peak.mz,6)))
            self.peakAi_value.SetValue(str(peak.ai))
            self.peakBase_value.SetValue(str(peak.base))
            if peak.sn:
                self.peakSN_value.SetValue(str(round(peak.sn,3)))
            if peak.charge:
                self.peakCharge_value.SetValue(str(peak.charge))
            if peak.fwhm:
                self.peakFwhm_value.SetValue(str(round(peak.fwhm,6)))
            if peak.group:
                self.peakGroup_value.SetValue(unicode(peak.group))
            if peak.isotope == 0:
                self.peakMonoisotopic_check.SetValue(True)
            else:
                self.peakMonoisotopic_check.SetValue(False)
            self.peakReplace_butt.Enable(True)
    # ----
    
    
    def getPeakEditorData(self):
        """Get data of edited peak."""
        
        try:
            # get data
            mz = self.peakMz_value.GetValue()
            ai = self.peakAi_value.GetValue()
            base = self.peakBase_value.GetValue()
            sn = self.peakSN_value.GetValue()
            charge = self.peakCharge_value.GetValue()
            fwhm = self.peakFwhm_value.GetValue()
            group = self.peakGroup_value.GetValue()
            monoisotope = self.peakMonoisotopic_check.GetValue()
            
            # format data
            mz = float(mz)
            ai = float(ai)
            
            if ai == 0:
                raise ValueError
            
            if base:
                base = float(base)
            else:
                base = 0.
            
            if sn:
                sn = float(sn)
            else:
                sn = None
            
            if charge:
                charge = int(charge)
            else:
                charge = None
            
            if fwhm:
                fwhm = float(fwhm)
            else:
                fwhm = None
            
            if not group:
                group = ''
            
            if monoisotope:
                isotope = 0
            else:
                isotope = None
            
            # make peak
            peak = mspy.peak(mz=mz, ai=ai, base=base, sn=sn, charge=charge, isotope=isotope, fwhm=fwhm, group=group)
            return peak
        
        except:
            wx.Bell()
            return False
    # ----
    
    
    def getSelectedPeaks(self):
        """Get selected peaks."""
        
        # get peaklist
        peaklist = []
        for item in self.peakList.getSelected():
            peak = self.currentDocument.spectrum.peaklist[self.peakList.GetItemData(item)]
            peaklist.append(peak)
        
        return peaklist
    # ----
    
    
    def copyToClipboard(self):
        """Copy current selection to clipboard."""
        
        # get selected
        selection = self.peakList.getSelected()
        if not selection:
            return
        
        # show copy dialog
        dlg = dlgCopy(self.parent)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.getData()
            dlg.Destroy()
            
            # export data
            buff = ''
            for row in selection:
                peak = self.currentDocument.spectrum.peaklist[self.peakList.GetItemData(row)]
                
                line = ''
                if 'mz' in config.export['peaklistColumns']:
                    line += str(peak.mz) + '\t'
                if 'ai' in config.export['peaklistColumns']:
                    line += str(peak.ai) + '\t'
                if 'base' in config.export['peaklistColumns']:
                    line += str(peak.base) + '\t'
                if 'int' in config.export['peaklistColumns']:
                    line += str(peak.intensity) + '\t'
                if 'rel' in config.export['peaklistColumns']:
                    line += str(peak.ri*100) + '\t'
                if 'sn' in config.export['peaklistColumns']:
                    line += str(peak.sn) + '\t'
                if 'z' in config.export['peaklistColumns']:
                    line += str(peak.charge) + '\t'
                if 'mass' in config.export['peaklistColumns']:
                    line += str(peak.mass()) + '\t'
                if 'fwhm' in config.export['peaklistColumns']:
                    line += str(peak.fwhm) + '\t'
                if 'resol' in config.export['peaklistColumns']:
                    line += str(peak.resolution) + '\t'
                if 'group' in config.export['peaklistColumns']:
                    line += unicode(peak.group) + '\t'
                buff += '%s\n' % (line.rstrip())
            
            # make text object for data
            obj = wx.TextDataObject()
            obj.SetText(buff.rstrip())
            
            # paste to clipboard
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(obj)
                wx.TheClipboard.Close()
        
        else:
            dlg.Destroy()
    # ----
    
    


class dlgThreshold(wx.Dialog):
    """Set threshold."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Delete by Threshold", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        
        self.parent = parent
        self.threshold = None
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        threshold_label = wx.StaticText(self, -1, "Minimal value:")
        self.threshold_value = wx.TextCtrl(self, -1, "", size=(150, -1), validator=mwx.validator('floatPos'))
        self.threshold_value.Bind(wx.EVT_TEXT, self.onChange)
        
        thresholdType_label = wx.StaticText(self, -1, "Threshold type:")
        choices=['m/z', 'a.i.', 'Intensity', 'Relative Intensity', 's/n']
        self.thresholdType_choice = wx.Choice(self, -1, choices=choices, size=(150, mwx.CHOICE_HEIGHT))
        self.thresholdType_choice.Select(0)
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        delete_butt = wx.Button(self, wx.ID_OK, "Delete")
        delete_butt.Bind(wx.EVT_BUTTON, self.onDelete)
        delete_butt.SetDefault()
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(threshold_label, (0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.threshold_value, (0,1))
        grid.Add(thresholdType_label, (1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.thresholdType_choice, (1,1))
        
        staticSizer.Add(grid, 0, wx.ALL, 5)
        
        buttSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttSizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttSizer.Add(delete_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttSizer, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def onChange(self, evt):
        """Check data."""
        
        # get data
        try:
            self.threshold = float(self.threshold_value.GetValue())
        except:
            self.threshold = None
    # ----
    
    
    def onDelete(self, evt):
        """Delete."""
        
        # check value and end
        if self.threshold != None:
            self.EndModal(wx.ID_OK)
        else:
            wx.Bell()
    # ----
    
    
    def getData(self):
        """Return values."""
        return self.threshold, self.thresholdType_choice.GetStringSelection()
    # ----
    
    


class dlgCopy(wx.Dialog):
    """Set coumns to copy."""
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Select Columns to Copy", style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
        
        self.parent = parent
        
        # make GUI
        sizer = self.makeGUI()
        
        # fit layout
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetMinSize(self.GetSize())
        self.Centre()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        staticSizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)
        
        # make elements
        self.peaklistColumnMz_check = wx.CheckBox(self, -1, "m/z")
        self.peaklistColumnMz_check.SetValue(config.export['peaklistColumns'].count('mz'))
        
        self.peaklistColumnAi_check = wx.CheckBox(self, -1, "a.i.")
        self.peaklistColumnAi_check.SetValue(config.export['peaklistColumns'].count('ai'))
        
        self.peaklistColumnBase_check = wx.CheckBox(self, -1, "Baseline")
        self.peaklistColumnBase_check.SetValue(config.export['peaklistColumns'].count('base'))
        
        self.peaklistColumnInt_check = wx.CheckBox(self, -1, "Intensity")
        self.peaklistColumnInt_check.SetValue(config.export['peaklistColumns'].count('int'))
        
        self.peaklistColumnRel_check = wx.CheckBox(self, -1, "Relative intensity")
        self.peaklistColumnRel_check.SetValue(config.export['peaklistColumns'].count('rel'))
        
        self.peaklistColumnSn_check = wx.CheckBox(self, -1, "s/n")
        self.peaklistColumnSn_check.SetValue(config.export['peaklistColumns'].count('sn'))
        
        self.peaklistColumnZ_check = wx.CheckBox(self, -1, "Charge")
        self.peaklistColumnZ_check.SetValue(config.export['peaklistColumns'].count('z'))
        
        self.peaklistColumnMass_check = wx.CheckBox(self, -1, "Mass")
        self.peaklistColumnMass_check.SetValue(config.export['peaklistColumns'].count('mass'))
        
        self.peaklistColumnFwhm_check = wx.CheckBox(self, -1, "FWHM")
        self.peaklistColumnFwhm_check.SetValue(config.export['peaklistColumns'].count('fwhm'))
        
        self.peaklistColumnResol_check = wx.CheckBox(self, -1, "Resolution")
        self.peaklistColumnResol_check.SetValue(config.export['peaklistColumns'].count('resol'))
        
        self.peaklistColumnGroup_check = wx.CheckBox(self, -1, "Group")
        self.peaklistColumnGroup_check.SetValue(config.export['peaklistColumns'].count('group'))
        
        cancel_butt = wx.Button(self, wx.ID_CANCEL, "Cancel")
        copy_butt = wx.Button(self, wx.ID_OK, "Copy")
        copy_butt.SetDefault()
        
        # pack elements
        grid = wx.GridBagSizer(mwx.GRIDBAG_VSPACE, mwx.GRIDBAG_HSPACE)
        grid.Add(self.peaklistColumnMz_check, (0,0))
        grid.Add(self.peaklistColumnAi_check, (1,0))
        grid.Add(self.peaklistColumnBase_check, (2,0))
        grid.Add(self.peaklistColumnInt_check, (3,0))
        grid.Add(self.peaklistColumnRel_check, (4,0))
        grid.Add(self.peaklistColumnSn_check, (5,0))
        grid.Add(self.peaklistColumnZ_check, (0,2))
        grid.Add(self.peaklistColumnMass_check, (1,2))
        grid.Add(self.peaklistColumnFwhm_check, (2,2))
        grid.Add(self.peaklistColumnResol_check, (3,2))
        grid.Add(self.peaklistColumnGroup_check, (4,2))
        
        staticSizer.Add(grid, 0, wx.ALL, 5)
        
        buttSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttSizer.Add(cancel_butt, 0, wx.RIGHT, 15)
        buttSizer.Add(copy_butt, 0)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(staticSizer, 0, wx.CENTER|wx.ALL, mwx.PANEL_SPACE_MAIN)
        mainSizer.Add(buttSizer, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, mwx.PANEL_SPACE_MAIN)
        
        return mainSizer
    # ----
    
    
    def getData(self):
        """Set selected columns to export presets."""
        
        # get data
        config.export['peaklistColumns'] = []
        if self.peaklistColumnMz_check.IsChecked():
            config.export['peaklistColumns'].append('mz')
        if self.peaklistColumnAi_check.IsChecked():
            config.export['peaklistColumns'].append('ai')
        if self.peaklistColumnBase_check.IsChecked():
            config.export['peaklistColumns'].append('base')
        if self.peaklistColumnInt_check.IsChecked():
            config.export['peaklistColumns'].append('int')
        if self.peaklistColumnRel_check.IsChecked():
            config.export['peaklistColumns'].append('rel')
        if self.peaklistColumnZ_check.IsChecked():
            config.export['peaklistColumns'].append('z')
        if self.peaklistColumnMass_check.IsChecked():
            config.export['peaklistColumns'].append('mass')
        if self.peaklistColumnSn_check.IsChecked():
            config.export['peaklistColumns'].append('sn')
        if self.peaklistColumnFwhm_check.IsChecked():
            config.export['peaklistColumns'].append('fwhm')
        if self.peaklistColumnResol_check.IsChecked():
            config.export['peaklistColumns'].append('resol')
        if self.peaklistColumnGroup_check.IsChecked():
            config.export['peaklistColumns'].append('group')
    # ----
    
    


class fileDropTarget(wx.FileDropTarget):
    """Generic drop target for files."""
    
    def __init__(self, fn):
        wx.FileDropTarget.__init__(self)
        self.fn = fn
    # ----
    
    
    def OnDropFiles(self, x, y, paths):
        """Open dropped files."""
        self.fn(paths=paths)
    # ----
    

    