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


# DOCUMENTS PANEL
# --------------

class panelDocuments(wx.Panel):
    """Make documents panel."""
    
    def __init__(self, parent, documents):
        wx.Panel.__init__(self, parent, -1, size=(150, -1), style=wx.NO_FULL_REPAINT_ON_RESIZE)
        
        self.parent = parent
        self.documents = documents
        
        # make GUI
        self.makeGUI()
    # ----
    
    
    def makeGUI(self):
        """Make GUI elements."""
        
        # make documents tree
        self.makeDocumentTree()
        
        # init lower toolbar
        toolbar = self.makeToolbar()
        
        # pack gui elements
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.documentTree, 1, wx.EXPAND, 0)
        self.mainSizer.Add(toolbar, 0, wx.EXPAND)
        
        # fit layout
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
    # ----
    
    
    def makeToolbar(self):
        """Make bottom toolbar."""
        
        # init toolbar panel
        panel = mwx.bgrPanel(self, -1, images.lib['bgrBottombar'], size=(-1, mwx.BOTTOMBAR_HEIGHT))
        
        self.add_butt = wx.BitmapButton(panel, -1, images.lib['documentsAdd'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.add_butt.SetToolTip(wx.ToolTip("Add..."))
        self.add_butt.Bind(wx.EVT_BUTTON, self.onAdd)
        
        self.delete_butt = wx.BitmapButton(panel, -1, images.lib['documentsDelete'], size=(mwx.BOTTOMBAR_TOOLSIZE), style=wx.BORDER_NONE)
        self.delete_butt.SetToolTip(wx.ToolTip("Remove..."))
        self.delete_butt.Bind(wx.EVT_BUTTON, self.onDelete)
        
        # pack elements
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(mwx.BOTTOMBAR_LSPACE)
        sizer.Add(self.add_butt, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.delete_butt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, mwx.BUTTON_SIZE_CORRECTION)
        sizer.AddSpacer(mwx.BOTTOMBAR_RSPACE)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(sizer, 1, wx.EXPAND)
        
        panel.SetSizer(mainSizer)
        mainSizer.Fit(panel)
        
        return panel
    # ----
    
    
    def makeDocumentTree(self):
        """Make documents tree."""
        
        # init tree
        self.documentTree = documentsTree(self, -1, size=(175, -1))
        
        # bind events
        self.documentTree.Bind(wx.EVT_TREE_KEY_DOWN, self.onKey)
        self.documentTree.Bind(wx.EVT_LEFT_DOWN, self.onLMD)
        self.documentTree.Bind(wx.EVT_RIGHT_DOWN, self.onRMD)
        self.documentTree.Bind(wx.EVT_RIGHT_UP, self.onRMU)
        self.documentTree.Bind(wx.EVT_TREE_SEL_CHANGING, self.onItemSelecting)
        self.documentTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onItemSelected)
        self.documentTree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
        
        # set DnD
        dropTarget = fileDropTarget(self.parent.onDocumentDropped)
        self.documentTree.SetDropTarget(dropTarget)
    # ----
    
    
    def onKey(self, evt):
        """Delete selected item."""
        
        # get key
        key = evt.GetKeyCode()
        keyEvt = evt.GetKeyEvent()
        
        # delete
        if key==wx.WXK_DELETE or (key==wx.WXK_BACK and keyEvt.CmdDown()):
            item = self.documentTree.GetSelection()
            itemType = self.documentTree.getItemType(item)
            
            # close document
            if itemType == 'document':
                self.parent.onDocumentClose()
            
            # delete sequence
            elif itemType == 'sequence':
                self.parent.onSequenceDelete()
            
            # delete annotation or sequence match
            elif itemType in ('annotation', 'match'):
                self.onNotationDelete()
            
            else:
                wx.Bell()
            
        # other keys
        else:
            evt.Skip()
    # ----
    
    
    def onLMD(self, evt):
        """Enable / disable document."""
        
        # get item
        item, flags = self.documentTree.HitTest(evt.GetPosition())
        
        # document solo
        if (evt.AltDown() or evt.ControlDown()) and self.documentTree.getItemIndent(item) == 1:
            docIndex = self._getDocumentIndex(item)
            self.parent.onDocumentSolo(docIndex)
        
        # enable / disable document
        elif (flags & wx.TREE_HITTEST_ONITEMICON) and self.documentTree.getItemIndent(item) == 1:
            docIndex = self._getDocumentIndex(item)
            self.parent.onDocumentEnable(docIndex)
        
        # other
        else:
            evt.Skip()
    # ----
    
    
    def onRMD(self, evt):
        """Right mouse down."""
        
        if wx.Platform == '__WXMAC__':
            evt.Skip()
    # ----
    
    
    def onRMU(self, evt):
        """Show popup menu."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        
        # check item
        if not itemType:
            return
        
        # get item data
        itemData = self.documentTree.GetPyData(item)
        
        # get object index
        docIndex = self._getDocumentIndex(item)
        seqIndex = self._getSequenceIndex(item)
        
        # popup menu
        menu = wx.Menu()
        if itemType == 'document':
            menu.Append(ID_sequenceNew, "Add Sequence...")
            menu.AppendSeparator()
            menu.Append(ID_documentInfo, "Notes and Information...")
            menu.Append(ID_documentNotationsDelete, "Delete All Notations")
            menu.AppendSeparator()
            menu.Append(ID_documentColour, "Change Colour...")
            style = wx.Menu()
            style.Append(ID_documentStyleSolid, "Solid", "", wx.ITEM_RADIO)
            style.Append(ID_documentStyleDot, "Dotted", "", wx.ITEM_RADIO)
            style.Append(ID_documentStyleDash, "Dashed", "", wx.ITEM_RADIO)
            style.Append(ID_documentStyleDotDash, "Dot and Dash", "", wx.ITEM_RADIO)
            menu.AppendMenu(ID_documentStyle, "Line Style", style)
            menu.AppendSeparator()
            menu.Append(ID_documentFlip, "Flip Spectrum")
            menu.Append(ID_documentOffset, "Offset Spectrum...")
            menu.Append(ID_documentClearOffset, "Clear Offset")
            menu.AppendSeparator()
            menu.Append(ID_documentDuplicate, "Duplicate Document")
            menu.AppendSeparator()
            menu.Append(ID_documentClose, "Close Document")
            menu.Append(ID_documentCloseAll, "Close All Documents")
            
            if config.spectrum['normalize']:
                menu.Enable(ID_documentOffset, False)
            if itemData.offset == [0,0]:
                menu.Enable(ID_documentClearOffset, False)
            
            if itemData.spectrum.hasprofile() == False:
                menu.Enable(ID_documentStyle, False)
            elif itemData.style == wx.DOT:
                style.Check(ID_documentStyleDot, True)
            elif itemData.style == wx.SHORT_DASH:
                style.Check(ID_documentStyleDash, True)
            elif itemData.style == wx.DOT_DASH:
                style.Check(ID_documentStyleDotDash, True)
            else:
                style.Check(ID_documentStyleSolid, True)
        
        elif itemType == 'annotations':
            menu.Append(ID_documentAnnotationsCalibrateBy, "Calibrate by Annotations...")
            menu.AppendSeparator()
            menu.Append(ID_documentAnnotationsDelete, "Delete All Annotations")
            
            if not itemData:
                menu.Enable(ID_documentAnnotationsDelete, False)
                menu.Enable(ID_documentAnnotationsCalibrateBy, False)
        
        elif itemType == 'annotation':
            menu.Append(ID_documentAnnotationEdit, "Edit Annotation...")
            menu.AppendSeparator()
            menu.Append(ID_documentAnnotationSendToMassCalculator, "Show Isotopic Pattern...")
            menu.Append(ID_documentAnnotationSendToMassToFormula, "Send to Mass to Formula...")
            menu.Append(ID_documentAnnotationSendToEnvelopeFit, "Send to Envelope Fit...")
            menu.AppendSeparator()
            menu.Append(ID_documentAnnotationsCalibrateBy, "Calibrate by Annotations...")
            menu.AppendSeparator()
            menu.Append(ID_documentAnnotationDelete, "Delete Annotation")
            menu.Append(ID_documentAnnotationsDelete, "Delete All Annotations")
            
            if not itemData.formula:
                menu.Enable(ID_documentAnnotationSendToMassCalculator, False)
                menu.Enable(ID_documentAnnotationSendToEnvelopeFit, False)
        
        elif itemType == 'sequence':
            menu.Append(ID_sequenceEditor, "Edit Sequence...")
            menu.Append(ID_sequenceModifications, "Edit Modifications...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceDigest, "Digest Protein...")
            menu.Append(ID_sequenceFragment, "Fragment Peptide...")
            menu.Append(ID_sequenceSearch, "Mass Search...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceSendToMassCalculator, "Show Isotopic Pattern...")
            menu.Append(ID_sequenceSendToEnvelopeFit, "Send to Envelope Fit...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceMatchesCalibrateBy, "Calibrate by Matches...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceMatchesDelete, "Delete All Matches")
            menu.Append(ID_sequenceDelete, "Delete Sequence")
            
            if not itemData.matches:
                menu.Enable(ID_sequenceMatchesCalibrateBy, False)
                menu.Enable(ID_sequenceMatchesDelete, False)
        
        elif itemType == 'match':
            menu.Append(ID_sequenceMatchEdit, "Edit Match...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceMatchSendToMassCalculator, "Show Isotopic Pattern...")
            menu.Append(ID_sequenceMatchSendToEnvelopeFit, "Send to Envelope Fit...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceMatchesCalibrateBy, "Calibrate by Matches...")
            menu.AppendSeparator()
            menu.Append(ID_sequenceMatchDelete, "Delete Sequence Match")
            menu.Append(ID_sequenceMatchesDelete, "Delete All Matches")
            
            if not itemData.formula:
                menu.Enable(ID_sequenceMatchSendToMassCalculator, False)
                menu.Enable(ID_sequenceMatchSendToEnvelopeFit, False)
        
        # bind events
        self.Bind(wx.EVT_MENU, self.parent.onDocumentInfo, id=ID_documentInfo)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentColour, id=ID_documentColour)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentStyle, id=ID_documentStyleSolid)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentStyle, id=ID_documentStyleDot)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentStyle, id=ID_documentStyleDash)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentStyle, id=ID_documentStyleDotDash)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentFlip, id=ID_documentFlip)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentOffset, id=ID_documentOffset)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentOffset, id=ID_documentClearOffset)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentNotationsDelete, id=ID_documentNotationsDelete)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentDuplicate, id=ID_documentDuplicate)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentClose, id=ID_documentClose)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentCloseAll, id=ID_documentCloseAll)
        
        self.Bind(wx.EVT_MENU, self.onNotationEdit, id=ID_documentAnnotationEdit)
        self.Bind(wx.EVT_MENU, self.onSendToMassCalculator, id=ID_documentAnnotationSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onSendToMassToFormula, id=ID_documentAnnotationSendToMassToFormula)
        self.Bind(wx.EVT_MENU, self.onSendToEnvelopeFit, id=ID_documentAnnotationSendToEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentAnnotationsCalibrateBy, id=ID_documentAnnotationsCalibrateBy)
        self.Bind(wx.EVT_MENU, self.onNotationDelete, id=ID_documentAnnotationDelete)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentAnnotationsDelete, id=ID_documentAnnotationsDelete)
        
        self.Bind(wx.EVT_MENU, self.parent.onSequenceNew, id=ID_sequenceNew)
        self.Bind(wx.EVT_MENU, self.parent.onToolsSequence, id=ID_sequenceEditor)
        self.Bind(wx.EVT_MENU, self.parent.onToolsSequence, id=ID_sequenceModifications)
        self.Bind(wx.EVT_MENU, self.parent.onToolsSequence, id=ID_sequenceDigest)
        self.Bind(wx.EVT_MENU, self.parent.onToolsSequence, id=ID_sequenceFragment)
        self.Bind(wx.EVT_MENU, self.parent.onToolsSequence, id=ID_sequenceSearch)
        self.Bind(wx.EVT_MENU, self.onSendToMassCalculator, id=ID_sequenceSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onSendToEnvelopeFit, id=ID_sequenceSendToEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.parent.onSequenceDelete, id=ID_sequenceDelete)
        
        self.Bind(wx.EVT_MENU, self.onNotationEdit, id=ID_sequenceMatchEdit)
        self.Bind(wx.EVT_MENU, self.onSendToMassCalculator, id=ID_sequenceMatchSendToMassCalculator)
        self.Bind(wx.EVT_MENU, self.onSendToEnvelopeFit, id=ID_sequenceMatchSendToEnvelopeFit)
        self.Bind(wx.EVT_MENU, self.parent.onSequenceMatchesCalibrateBy, id=ID_sequenceMatchesCalibrateBy)
        self.Bind(wx.EVT_MENU, self.onNotationDelete, id=ID_sequenceMatchDelete)
        self.Bind(wx.EVT_MENU, self.parent.onSequenceMatchesDelete, id=ID_sequenceMatchesDelete)
        
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onItemSelecting(self, evt):
        """Selecting item."""
        
        # do not allow to select disabled documents
        item = evt.GetItem()
        if self.documentTree.getItemIndent(item):
            docIndex = self._getDocumentIndex(item)
            if not self.documents[docIndex].visible:
                wx.Bell()
                evt.Veto()
    # ----
    
    
    def onItemSelected(self, evt):
        """Selected item."""
        
        # get item
        item = evt.GetItem()
        itemType = self.documentTree.getItemType(item)
        evt.Skip()
        
        # root or bad item selected
        if not itemType:
            self.documentTree.highlightDocument(None)
            self.parent.onDocumentSelected(None)
            self.parent.updateNotationMarks()
            return
        
        # select parent document
        docIndex = self._getDocumentIndex(item)
        self.documentTree.highlightDocument(item)
        self.parent.onDocumentSelected(docIndex)
        
        # select parent sequence
        seqIndex = self._getSequenceIndex(item)
        self.parent.onSequenceSelected(seqIndex)
        
        # update notation marks
        self.parent.updateNotationMarks()
        
        # highlight mass of selected match or annotation
        if itemType in ('annotation', 'match'):
            matchData = self.documentTree.GetPyData(item)
            points = [matchData.mz]
            if matchData.theoretical != None:
                points.append(matchData.theoretical)
            self.parent.updateMassPoints(points)
    # ----
    
    
    def onItemActivated(self, evt):
        """Activated item."""
        
        # get item
        item = evt.GetItem()
        itemType = self.documentTree.getItemType(item)
        
        # do not allow to activate disabled documents
        if itemType:
            docIndex = self._getDocumentIndex(item)
            if not self.documents[docIndex].visible:
                wx.Bell()
                return
        else:
            return
        
        # document info
        if itemType == 'document':
            self.parent.onDocumentInfo()
        
        # sequence editing
        elif itemType == 'sequence':
            self.parent.onToolsSequence()
        
        # edit annotation or sequence match
        elif itemType in ('annotation', 'match'):
            self.onNotationEdit()
    # ----
    
    
    def onAdd(self, evt):
        """Add button pressed."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        indent = self.documentTree.getItemIndent(item)
        
        # popup menu
        menu = wx.Menu()
        menu.Append(ID_sequenceNew, "New Sequence...")
        menu.AppendSeparator()
        menu.Append(ID_documentNew, "New Document")
        menu.Append(ID_documentNewFromClipboard, "New from Clipboard")
        menu.AppendSeparator()
        menu.Append(ID_documentOpen, "Open Document...")
        
        menu.Enable(ID_sequenceNew, bool(indent))
        
        # set events
        self.Bind(wx.EVT_MENU, self.parent.onSequenceNew, id=ID_sequenceNew)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentNew, id=ID_documentNew)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentNewFromClipboard, id=ID_documentNewFromClipboard)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentOpen, id=ID_documentOpen)
        
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onDelete(self, evt):
        """Delete button pressed."""
        
        # make menu
        menu = wx.Menu()
        menu.Append(ID_documentAnnotationDelete, "Delete Annotation")
        menu.Append(ID_documentAnnotationsDelete, "Delete All Annotations")
        menu.AppendSeparator()
        menu.Append(ID_sequenceDelete, "Delete Sequence")
        menu.Append(ID_sequenceMatchDelete, "Delete Sequence Match")
        menu.Append(ID_sequenceMatchesDelete, "Delete All Matches")
        menu.AppendSeparator()
        menu.Append(ID_documentNotationsDelete, "Delete All Notations")
        menu.AppendSeparator()
        menu.Append(ID_documentClose, "Close Document")
        menu.Append(ID_documentCloseAll, "Close All Documents")
        
        # disable items
        menu.Enable(ID_documentAnnotationDelete, False)
        menu.Enable(ID_documentAnnotationsDelete, False)
        menu.Enable(ID_sequenceDelete, False)
        menu.Enable(ID_sequenceMatchDelete, False)
        menu.Enable(ID_sequenceMatchesDelete, False)
        menu.Enable(ID_documentNotationsDelete, False)
        menu.Enable(ID_documentClose, False)
        menu.Enable(ID_documentCloseAll, bool(self.documents))
        
        # bind events
        self.Bind(wx.EVT_MENU, self.onNotationDelete, id=ID_documentAnnotationDelete)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentAnnotationsDelete, id=ID_documentAnnotationsDelete)
        
        self.Bind(wx.EVT_MENU, self.parent.onSequenceDelete, id=ID_sequenceDelete)
        self.Bind(wx.EVT_MENU, self.onNotationDelete, id=ID_sequenceMatchDelete)
        self.Bind(wx.EVT_MENU, self.parent.onSequenceMatchesDelete, id=ID_sequenceMatchesDelete)
        
        self.Bind(wx.EVT_MENU, self.parent.onDocumentNotationsDelete, id=ID_documentNotationsDelete)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentClose, id=ID_documentClose)
        self.Bind(wx.EVT_MENU, self.parent.onDocumentCloseAll, id=ID_documentCloseAll)
        
        # get selected item
        item = self.documentTree.GetSelection()
        indent = self.documentTree.getItemIndent(item)
        if indent:
            
            itemType = self.documentTree.getItemType(item)
            docIndex = self._getDocumentIndex(item)
            seqIndex = self._getSequenceIndex(item)
            
            if self.documents[docIndex].annotations:
                menu.Enable(ID_documentAnnotationsDelete, True)
            if itemType == 'annotation':
                menu.Enable(ID_documentAnnotationDelete, True)
                menu.Enable(ID_documentAnnotationsDelete, True)
            if itemType == 'sequence':
                menu.Enable(ID_sequenceDelete, True)
            if itemType == 'sequence' and self.documents[docIndex].sequences[seqIndex].matches:
                menu.Enable(ID_sequenceMatchesDelete, True)
            if itemType == 'match':
                menu.Enable(ID_sequenceMatchDelete, True)
                menu.Enable(ID_sequenceMatchesDelete, True)
            if itemType != None:
                menu.Enable(ID_documentNotationsDelete, True)
                menu.Enable(ID_documentClose, True)
        
        self.PopupMenu(menu)
        menu.Destroy()
        self.SetFocus()
    # ----
    
    
    def onNotationEdit(self, evt=None):
        """Edit selected annotation or sequence match."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        itemData = self.documentTree.GetPyData(item)
        
        # show dialog
        dlg = dlgNotation(self.parent, itemData, button='Update')
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            
            if itemType == 'annotation':
                self.parent.onDocumentChanged(items=('annotations'))
            elif itemType == 'match':
                self.parent.onDocumentChanged(items=('matches'))
        
        else:
            dlg.Destroy()
    # ----
    
    
    def onNotationDelete(self, evt=None):
        """Delete selected annotation or sequence match."""
        
        # get index
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        
        # delete annotation
        if itemType == 'annotation':
            annotIndex = self._getAnnotationIndex(item)
            if annotIndex != None:
                self.parent.onDocumentAnnotationsDelete(annotIndex=annotIndex)
        
        # delete sequence match
        elif itemType == 'match':
            matchIndex = self._getMatchIndex(item)
            if matchIndex != None:
                self.parent.onSequenceMatchesDelete(matchIndex=matchIndex)
    # ----
    
    
    def onSendToMassCalculator(self, evt=None):
        """Send selected item to Mass Calculator panel."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        itemData = self.documentTree.GetPyData(item)
        
        # send data to Mass Calculator
        if itemType == 'sequence':
            self.parent.onToolsMassCalculator(formula=itemData.formula())
        elif itemType in ('annotation', 'match'):
            if itemData.radical:
                self.parent.onToolsMassCalculator(formula=itemData.formula, charge=itemData.charge, agentFormula='e', agentCharge=-1)
            else:
                self.parent.onToolsMassCalculator(formula=itemData.formula, charge=itemData.charge, agentFormula='H', agentCharge=1)
    # ----
    
    
    def onSendToMassToFormula(self, evt=None):
        """Send selected item to Mass To Formula panel."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        itemData = self.documentTree.GetPyData(item)
        
        # send data to Mass To Formula panel
        if itemData.radical:
            self.parent.onToolsMassToFormula(mass=itemData.mz, charge=itemData.charge, agentFormula='e')
        else:
            self.parent.onToolsMassToFormula(mass=itemData.mz, charge=itemData.charge, agentFormula='H')
    # ----
    
    
    def onSendToEnvelopeFit(self, evt=None):
        """Send selected item to envelope fit panel."""
        
        # get selected item
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        itemData = self.documentTree.GetPyData(item)
        
        # send data to envelope fit
        if itemType == 'sequence':
            self.parent.onToolsEnvelopeFit(sequence=itemData)
        
        elif itemType == 'annotation':
            self.parent.onToolsEnvelopeFit(formula=itemData.formula, charge=itemData.charge)
        
        elif itemType == 'match':
            
            scale = None
            if itemData.sequenceRange and config.envelopeFit['loss'] == 'H' and config.envelopeFit['gain'] == 'H{2}':
                scale = [0, itemData.sequenceRange[1]-itemData.sequenceRange[0]]
            
            self.parent.onToolsEnvelopeFit(formula=itemData.formula, charge=itemData.charge, scale=scale)
    # ----
    
    
    
    # DOCUMENT
    
    def selectDocument(self, docIndex):
        """Select document"""
        
        # deselect all documents
        if docIndex == None:
            self.documentTree.Unselect()
            self.parent.onDocumentSelected(None)
            return
        
        # get item
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        
        # select document
        self.documentTree.highlightDocument(docItem)
        self.documentTree.SelectItem(docItem)
    # ----
    
    
    def appendLastDocument(self):
        """Append document."""
        
        # get last document
        docData = self.documents[-1]
        
        # append to tree
        self.documentTree.appendDocument(docData)
    # ----
    
    
    def deleteDocument(self, docIndex):
        """Delete selected document."""
        
        # check document
        if docIndex == None:
            return
        
        # remove from tree
        self.documentTree.deleteItemByData(self.documents[docIndex])
    # ----
    
    
    def enableDocument(self, docIndex, enable):
        """Enable/disable selected document."""
        
        # check document
        if docIndex == None:
            return
        
        # get item
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        
        # update document
        self.documentTree.enableItemTree(docItem, enable)
    # ----
    
    
    def updateDocumentTitle(self, docIndex):
        """Update document title."""
        
        # check document
        if docIndex == None:
            return
        
        # get item
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        
        # get title
        title = docData.title
        if docData.dirty:
            title = '*' + title
        
        # update document title
        self.documentTree.SetItemText(docItem, title)
    # ----
    
    
    def updateDocumentColour(self, docIndex):
        """Update bullet of selected document."""
        
        # check document
        if docIndex == None:
            return
        
        # get document item
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        
        # update colour
        self.documentTree.updateDocumentColour(docItem)
    # ----
    
    
    def updateAnnotations(self, docIndex, expand=None):
        """Set new annotations for document."""
        
        # check document
        if docIndex == None:
            return
        
        # get item
        annotsData = self.documents[docIndex].annotations
        annotsItem = self.documentTree.getItemByData(annotsData)
        
        # expand parent
        if expand:
            parent = self.documentTree.GetItemParent(annotsItem)
            self.documentTree.Expand(parent)
        
        # get expand
        if not expand:
            expand = self.documentTree.IsExpanded(annotsItem)
        
        # remove old annotations
        self.documentTree.Collapse(annotsItem)
        self.documentTree.DeleteChildren(annotsItem)
        
        # add new annotations
        for annotData in annotsData:
            self.documentTree.appendNotation(annotsItem, annotData)
        
        # expand tree
        if expand:
            self.documentTree.Expand(annotsItem)
    # ----
    
    
    
    # SEQUENCE
    
    def selectSequence(self, docIndex, seqIndex):
        """Select sequence"""
        
        # check index
        if docIndex == None or seqIndex == None:
            return
        
        # get item
        seqData = self.documents[docIndex].sequences[seqIndex]
        seqItem = self.documentTree.getItemByData(seqData)
        
        # select sequence
        self.documentTree.SelectItem(seqItem)
    # ----
    
    
    def appendLastSequence(self, docIndex):
        """Append new sequence to the tree."""
        
        # check document
        if docIndex == None:
            return
        
        # get document item
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        
        # get last sequence
        seqData = docData.sequences[-1]
        
        # append to tree
        self.documentTree.appendSequence(docItem, seqData)
    # ----
    
    
    def deleteSequence(self, docIndex, seqIndex):
        """Delete selected sequence."""
        
        # check document
        if docIndex == None or seqIndex == None:
            return
        
        # collapse document first
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        self.documentTree.Collapse(docItem)
        
        # delete sequence
        seqData = self.documents[docIndex].sequences[seqIndex]
        self.documentTree.deleteItemByData(seqData)
        
        # expand tree
        self.documentTree.Expand(docItem)
    # ----
    
    
    def updateSequenceTitle(self, docIndex, seqIndex):
        """Set new label for sequence."""
        
        # check document
        if docIndex == None or seqIndex == None:
            return
        
        # get item
        seqData = self.documents[docIndex].sequences[seqIndex]
        seqItem = self.documentTree.getItemByData(seqData)
        
        # set new label
        self.documentTree.SetItemText(seqItem, seqData.title)
    # ----
    
    
    def updateSequenceMatches(self, docIndex, seqIndex, expand=False):
        """Set new matches for sequence."""
        
        # check document
        if docIndex == None or seqIndex == None:
            return
        
        # get item
        seqData = self.documents[docIndex].sequences[seqIndex]
        seqItem = self.documentTree.getItemByData(seqData)
        
        # expand parent
        if expand:
            parent = self.documentTree.GetItemParent(seqItem)
            self.documentTree.Expand(parent)
        
        # get expand
        if not expand:
            expand = self.documentTree.IsExpanded(seqItem)
        
        # remove old matches
        self.documentTree.Collapse(seqItem)
        self.documentTree.DeleteChildren(seqItem)
        
        # add new matches
        for matchData in seqData.matches:
            self.documentTree.appendNotation(seqItem, matchData)
        
        # expand tree
        if expand:
            self.documentTree.Expand(seqItem)
    # ----
    
    
    def updateSequences(self, docIndex):
        """Set new sequences for current document."""
        
        # check document
        if docIndex == None:
            return
        
        # collapse document first
        docData = self.documents[docIndex]
        docItem = self.documentTree.getItemByData(docData)
        expand = self.documentTree.IsExpanded(docItem)
        self.documentTree.Collapse(docItem)
        
        # delete sequences
        if docItem.IsOk() and self.documentTree.ItemHasChildren(docItem):
            items = []
            
            child, cookie = self.documentTree.GetFirstChild(docItem)
            while child.IsOk():
                if self.documentTree.getItemType(child) == 'sequence':
                    items.append(child)
                child, cookie = self.documentTree.GetNextChild(docItem, cookie)
            
            for item in items:
                self.documentTree.Delete(item)
        
        # set new sequences
        for seqData in self.documents[docIndex].sequences:
            seqItem = self.documentTree.appendSequence(docItem, seqData)
        
        # expand tree
        if expand:
            self.documentTree.Expand(docItem)
    # ----
    
    
    
    # UTILITIES
    
    def getSelectedItemType(self):
        """Get selected item type."""
        
        item = self.documentTree.GetSelection()
        itemType = self.documentTree.getItemType(item)
        
        return itemType
    # ----
    
    
    def _getDocumentIndex(self, item):
        """Get parent document index."""
        
        docItem = self.documentTree.getParentItem(item, 1)
        docData = self.documentTree.GetPyData(docItem)
        
        if docData in self.documents:
            return self.documents.index(docData)
        else:
            return None
    # ----
    
    
    def _getAnnotationIndex(self, item):
        """Get annotation index."""
        
        docIndex = self._getDocumentIndex(item)
        annotData = self.documentTree.GetPyData(item)
        
        if annotData in self.documents[docIndex].annotations:
            return self.documents[docIndex].annotations.index(annotData)
        else:
            return None
    # ----
    
    
    def _getSequenceIndex(self, item):
        """Get parent sequence index."""
        
        docIndex = self._getDocumentIndex(item)
        seqItem = self.documentTree.getParentItem(item, 2)
        seqData = self.documentTree.GetPyData(seqItem)
        
        if seqData in self.documents[docIndex].sequences:
            return self.documents[docIndex].sequences.index(seqData)
        else:
            return None
    # ----
    
    
    def _getMatchIndex(self, item):
        """Get match index."""
        
        docIndex = self._getDocumentIndex(item)
        seqIndex = self._getSequenceIndex(item)
        matchData = self.documentTree.GetPyData(item)
        
        if matchData in self.documents[docIndex].sequences[seqIndex].matches:
            return self.documents[docIndex].sequences[seqIndex].matches.index(matchData)
        else:
            return None
    # ----
    



class documentsTree(wx.TreeCtrl):
    """Documents tree."""
    
    def __init__(self, parent, id, size=(-1,-1), style=mwx.DOCTREE_STYLE):
        wx.TreeCtrl.__init__(self, parent, id, size=size, style=style)
        
        self.parent = parent
        
        # set font and colour
        self.SetFont(wx.SMALL_FONT)
        self.SetOwnBackgroundColour(mwx.DOCTREE_COLOUR)
        
        # init bullets
        self.bullets = wx.ImageList(13, 12)
        self.SetImageList(self.bullets)
        self._resetBullets()
        
        # add root
        root = self.AddRoot("Documents")
        self.SetItemImage(root, 0, wx.TreeItemIcon_Normal)
    # ----
    
    
    def getItemIndent(self, item):
        """Get indent of selected item."""
        
        # check item
        if not item.IsOk():
            return False
        
        # get indent
        indent = 0
        root = self.GetRootItem()
        while item.IsOk():
            if item == root:
                return indent
            else:
                item = self.GetItemParent(item)
                indent += 1
    # ----
    
    
    def getItemType(self, item):
        """Get current item type."""
        
        # check item
        if not item.IsOk() or item is self.GetRootItem():
            return None
        
        # get item type
        data = self.GetPyData(item)
        if isinstance(data, doc.document):
            return 'document'
        elif isinstance(data, list):
            return 'annotations'
        elif isinstance(data, doc.annotation):
            return 'annotation'
        elif isinstance(data, mspy.sequence):
            return 'sequence'
        elif isinstance(data, doc.match):
            return 'match'
        else:
            return None
    # ----
    
    
    def getItemByData(self, data, root=None, cookie=0):
        """Get item by its data."""
        
        # get root
        if root == None:
            root = self.GetRootItem()
        
        # check children
        if self.ItemHasChildren(root):
            firstchild, cookie = self.GetFirstChild(root)
            if self.GetPyData(firstchild) is data:
                return firstchild
            matchedItem = self.getItemByData(data, firstchild, cookie)
            if matchedItem:
                return matchedItem
        
        # check siblings
        child = self.GetNextSibling(root)
        if child and child.IsOk():
            if self.GetPyData(child) is data:
                return child
            matchedItem = self.getItemByData(data, child, cookie)
            if matchedItem:
                return matchedItem
        
        # no such item found
        return False
    # ----
    
    
    def getParentItem(self, item, level):
        """Get parent item for selected item and level."""
        
        # get item
        for x in range(level, self.getItemIndent(item)):
            item = self.GetItemParent(item)
        
        return item
    # ----
    
    
    def enableItemTree(self, item, enable=True):
        """Enable/disable all children recursively."""
        
        # enable current item
        self.enableItem(item, enable)
        
        # enable children
        (child, cookie) = self.GetFirstChild(item)
        while child.IsOk():
            
            # enable item
            self.enableItem(child, enable)
            
            # check children
            if self.ItemHasChildren(child):
                self.enableItemTree(child, enable)
            
            # get next
            (child, cookie) = self.GetNextChild(item, cookie)
    # ---
    
    
    def enableItem(self, item, enable=True):
        """Enable document and all children."""
        
        # get item indent
        itemType = self.getItemType(item)
        if not itemType:
            return
        
        # set text colour
        if enable:
            self.SetItemTextColour(item, (0,0,0))
            self.SetItemBold(item, False)
        else:
            self.SetItemTextColour(item, (150,150,150))
            self.SetItemBold(item, False)
        
        # set document bullet
        if itemType == 'document':
            if enable:
                self.SetItemImage(item, self.GetPyData(item).bulletIndex, wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(item, 1, wx.TreeItemIcon_Normal)
        
        # set annotations bullet
        elif itemType == 'annotations':
            if enable:
                self.SetItemImage(item, 2, wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(item, 3, wx.TreeItemIcon_Normal)
        
        # set sequence bullet
        elif itemType == 'sequence':
            if enable:
                self.SetItemImage(item, 4, wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(item, 5, wx.TreeItemIcon_Normal)
        
        # set match / annotation bullet
        elif itemType == 'match' or  itemType == 'annotation':
            if enable:
                self.SetItemImage(item, 6, wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(item, 7, wx.TreeItemIcon_Normal)
    # ----
    
    
    def appendDocument(self, docData):
        """Append document to tree."""
        
        # add bullet
        bullet = self._makeColourBullet(docData.colour, True)
        docData.bulletIndex = self.bullets.Add(bullet)
        
        # get title
        title = docData.title
        if docData.dirty:
            title = '*' + title
        
        # add document
        docItem = self.AppendItem(self.GetRootItem(), title)
        self.SetItemImage(docItem, docData.bulletIndex, wx.TreeItemIcon_Normal)
        self.SetPyData(docItem, docData)
        
        # add annotations
        annotsItem = self.AppendItem(docItem, 'Annotations')
        self.SetItemImage(annotsItem, 2, wx.TreeItemIcon_Normal)
        self.SetPyData(annotsItem, docData.annotations)
        for annotData in docData.annotations:
            self.appendNotation(annotsItem, annotData)
        
        # add sequences
        for seqData in docData.sequences:
            seqItem = self.appendSequence(docItem, seqData)
        
        # enable/disable document and all children
        self.enableItemTree(docItem, docData.visible)
        
        return docItem
    # ----
    
    
    def appendSequence(self, item, seqData):
        """Append sequence to tree."""
        
        # add sequence
        seqItem = self.AppendItem(item, seqData.title)
        self.SetItemImage(seqItem, 4, wx.TreeItemIcon_Normal)
        self.SetPyData(seqItem, seqData)
        
        # add matches
        for matchData in seqData.matches:
            self.appendNotation(seqItem, matchData)
        
        return seqItem
    # ----
    
    
    def appendNotation(self, item, notationData):
        """Append notation to tree."""
        
        # get mz
        mz = round(notationData.mz, config.main['mzDigits'])
        
        # get error
        error = notationData.delta(config.main['errorUnits'])
        if error != None and config.main['errorUnits'] == 'ppm':
            error = round(error, config.main['ppmDigits'])
        elif error != None:
            error = round(error, config.main['mzDigits'])
        
        # make label
        if error != None:
            label = '%s (%s %s) %s' % (mz, error, config.main['errorUnits'], notationData.label)
        else:
            label = '%s %s' % (mz, notationData.label)
        
        # add match
        notationItem = self.AppendItem(item, label)
        self.SetItemImage(notationItem, 6, wx.TreeItemIcon_Normal)
        self.SetPyData(notationItem, notationData)
        
        return notationItem
    # ----
    
    
    def deleteItemByData(self, data):
        """Delete item by data."""
        
        item = self.getItemByData(data)
        if item:
            self.Delete(item)
    # ----
    
    
    def highlightDocument(self, item):
        """Highlight parent document."""
        
        # unbold all documents
        child, cookie = self.GetFirstChild(self.GetRootItem())
        while child.IsOk():
            self.SetItemBold(child, False)
            child, cookie = self.GetNextChild(self.GetRootItem(), cookie)
        
        # select parent document
        if item != None:
            item = self.getParentItem(item, 1)
            self.SetItemBold(item, True)
    # ----
    
    
    def updateDocumentColour(self, item):
        """Set new bullet colour."""
        
        # add bullet
        item = self.getParentItem(item, 1)
        docData = self.GetPyData(item)
        
        bullet = self._makeColourBullet(docData.colour, True)
        docData.bulletIndex = self.bullets.Add(bullet)
        
        # set new bullet
        self.SetItemImage(item, docData.bulletIndex, wx.TreeItemIcon_Normal)
    # ----
    
    
    def _resetBullets(self):
        """Erase all bullets and make defaults."""
        
        self.bullets.RemoveAll()
        self.bullets.Add(images.lib['bulletsDocument'])
        self.bullets.Add(self._makeColourBullet((150,150,150), False))
        self.bullets.Add(images.lib['bulletsAnnotationsOn'])
        self.bullets.Add(images.lib['bulletsAnnotationsOff'])
        self.bullets.Add(images.lib['bulletsSequenceOn'])
        self.bullets.Add(images.lib['bulletsSequenceOff'])
        self.bullets.Add(images.lib['bulletsNotationOn'])
        self.bullets.Add(images.lib['bulletsNotationOff'])
    # ----
    
    
    def _makeColourBullet(self, colour, filled=True):
        """Make bullet bitmap with specified colour."""
        
        # create empty bitmap
        bitmap = wx.EmptyBitmap(13, 12)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)
        
        # clear background
        if wx.Platform != '__WXMAC__':
            dc.SetBackground(wx.Brush(mwx.DOCTREE_COLOUR, wx.SOLID))
            dc.Clear()
        
        # set pen and brush
        if filled:
            pencolour = [max(x-70,0) for x in colour]
            dc.SetPen(wx.Pen(pencolour, 1, wx.SOLID))
            dc.SetBrush(wx.Brush(colour, wx.SOLID))
        else:
            dc.SetPen(wx.Pen(colour, 1, wx.SOLID))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        # draw circle
        dc.DrawCircle(6, 7, mwx.DOCTREE_BULLETSIZE)
        dc.SelectObject(wx.NullBitmap)
        
        return bitmap
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
    

