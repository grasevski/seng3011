#!/usr/bin/env python

import os
import csv
import wx

import yapsy.PluginManager

import trader
import plugins

"""Trader graphical user interface"""


class MainFrame(wx.Frame):
    """The main window"""

    ID_EXPORT = 1
    ID_RUN = 2

    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        """Initialize the window"""
        HELP_STRINGS = {
            'Open': 'Open a market data file',
            'Export': 'Save outputted trades',
            'Close': 'Close the current market data file',
            'Exit': 'Terminate the program',
            'Statusbar': 'Toggle visibility of statusbar',
            'Toolbar': 'Toggle visibility of toolbar',
            'Run': 'Run trial',
            'About': 'Information about this program'
        }
        self._status_bar = self.CreateStatusBar()
        self._tool_bar = self.CreateToolBar()
        menu_bar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_OPEN, '&Open\tCtrl+O', HELP_STRINGS['Open'])
        self.Bind(wx.EVT_MENU, self.OnOpen, item)
        self._item_export = menu.Append(wx.ID_ANY, '&Export',
                                        HELP_STRINGS['Export'])
        self.Bind(wx.EVT_MENU, self.OnExport, self._item_export)
        menu.AppendSeparator()
        self._item_close = menu.Append(wx.ID_CLOSE, '&Close\tCtrl+W',
                                       HELP_STRINGS['Close'])
        self.Bind(wx.EVT_MENU, self.OnClose, self._item_close)
        item = menu.Append(wx.ID_EXIT, 'E&xit\tCtrl+Q', HELP_STRINGS['Exit'])
        self.Bind(wx.EVT_MENU, self.OnExit, item)
        menu_bar.Append(menu, '&File')
        menu = wx.Menu()
        self._item_status_bar = menu.Append(wx.ID_ANY, 'Show &Statusbar',
                                            HELP_STRINGS['Statusbar'],
                                            wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, self._item_status_bar)
        menu.Check(self._item_status_bar.GetId(), True)
        self._item_tool_bar = menu.Append(wx.ID_ANY, 'Show &Toolbar',
                                          HELP_STRINGS['Toolbar'],
                                          wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, self._item_tool_bar)
        menu.Check(self._item_tool_bar.GetId(), True)
        menu_bar.Append(menu, '&View')
        menu = wx.Menu()
        self._item_run = menu.Append(wx.ID_ANY, '&Run', HELP_STRINGS['Run'])
        self.Bind(wx.EVT_MENU, self.OnRun, self._item_run)
        menu_bar.Append(menu, '&Tools')
        menu = wx.Menu()
        item = menu.Append(wx.ID_ABOUT, '&About', HELP_STRINGS['About'])
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        menu_bar.Append(menu, '&Help')
        self.SetMenuBar(menu_bar)
        icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN)
        tool = self._tool_bar.AddLabelTool(wx.ID_OPEN, 'Open', icon,
                                           shortHelp='Open',
                                           longHelp=HELP_STRINGS['Open'])
        self.Bind(wx.EVT_TOOL, self.OnOpen, tool)
        icon = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS)
        tool = self._tool_bar.AddLabelTool(MainFrame.ID_EXPORT, 'Export',
                                           icon, shortHelp='Export',
                                           longHelp=HELP_STRINGS['Export'])
        self.Bind(wx.EVT_TOOL, self.OnExport, tool)
        self._tool_bar.AddSeparator()
        icon = wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK)
        tool = self._tool_bar.AddLabelTool(wx.ID_CLOSE, 'Close', icon,
                                           shortHelp='Close',
                                           longHelp=HELP_STRINGS['Close'])
        self.Bind(wx.EVT_TOOL, self.OnClose, tool)
        self._tool_bar.AddSeparator()
        icon = wx.Bitmap('resources/run.png')
        tool = self._tool_bar.AddLabelTool(MainFrame.ID_RUN, 'Run',
                                           icon, shortHelp='Run',
                                           longHelp=HELP_STRINGS['Run'])
        self.Bind(wx.EVT_TOOL, self.OnRun, tool)
        self._enable_controls(False)
        panel = wx.Panel(self)
        self._notebook = wx.Notebook(panel)
        sizer = wx.BoxSizer()
        sizer.Add(self._notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

    def _enable_controls(self, enable=True):
        self._item_export.Enable(enable)
        self._item_close.Enable(enable)
        self._item_run.Enable(enable)
        self._tool_bar.EnableTool(MainFrame.ID_EXPORT, enable)
        self._tool_bar.EnableTool(wx.ID_CLOSE, enable)
        self._tool_bar.EnableTool(MainFrame.ID_RUN, enable)

    def OnOpen(self, e):
        """Open market data file"""
        wildcard = 'CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt|' \
                   'All files (*.*)|*.*'
        dlg = wx.FileDialog(self, wildcard=wildcard,
                            style=wx.OPEN|wx.MULTIPLE)
        count = self._notebook.GetPageCount()
        if dlg.ShowModal() == wx.ID_OK:
            directory = dlg.GetDirectory()
            for filename in dlg.GetFilenames():
                panel = TabPanel(self._notebook)
                panel.Open(directory, filename)
                self._notebook.AddPage(panel, filename, True)
        if count == 0 and self._notebook.GetPageCount() > 0:
            self._enable_controls()
        dlg.Destroy()

    def OnExport(self, e):
        """Save algorithmic trades"""
        wildcard = 'CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt|' \
                   'All files (*.*)|*.*'
        dlg = wx.FileDialog(self, wildcard=wildcard, style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self._notebook.GetCurrentPage().Export(dlg.GetPath())
        dlg.Destroy()

    def OnClose(self, e):
        """Close the current market data file"""
        self._notebook.DeletePage(self._notebook.GetSelection())
        if self._notebook.GetPageCount() == 0:
            self._enable_controls(False)

    def OnExit(self, e):
        """Exit the program"""
        close = True
        if self._notebook.GetPageCount() > 0:
            dlg = wx.MessageDialog(self, 'Close all tabs?', 'Quit')
            if dlg.ShowModal() != wx.ID_OK:
                close = False
            dlg.Destroy()
        if close:
            self.Close(True)

    def ToggleStatusBar(self, e):
        """Toggle the statusbar visibility"""
        if self._item_status_bar.IsChecked():
            self._status_bar.Show()
        else:
            self._status_bar.Hide()

    def ToggleToolBar(self, e):
        """Toggle the toolbar visibility"""
        if self._item_tool_bar.IsChecked():
            self._tool_bar.Show()
        else:
            self._tool_bar.Hide()

    def OnRun(self, e):
        """Run the simulation"""
        self._notebook.GetCurrentPage().Run()

    def OnAbout(self, e):
        """About the program"""
        dlg = wx.MessageDialog(self, 'Algorithmic Trading System',
                               'Algorithmic Trading System', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


class TabPanel(wx.Panel):
    """A workspace for a given market data file"""

    def Open(self, directory, filename):
        """Open the market data file"""
        pass

    def Export(self, path):
        """Export the algorithmic trades file"""
        pass

    def Run(self):
        """Run the simulation"""
        pass


def main():
    """Open the main window"""
    app = wx.App(False)
    MainFrame(None, title='Algorithmic Trading System').Show()
    app.MainLoop()

if __name__ == '__main__':
    main()