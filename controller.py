import os
import wx

wildcard = "XML (*.xml)|*.xml|" \
    "All files (*.*)|*.*"

def open_file(self, default_dir=os.path.expanduser('~')):
    """
    Open an XML file
    """
    dlg = wx.FileDialog(
        self, message="Choose a file",
        defaultDir=default_dir,
        defaultFile="",
        wildcard=wildcard,
        style=wx.FD_OPEN | wx.FD_CHANGE_DIR
    )
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()

    dlg.Destroy()

    return path

def save_file(self):
    """
    Save an XML file
    """
    path = None
    dlg = wx.FileDialog(
        self, message="Save file as ...",
        defaultDir=self.current_directory,
        defaultFile="", wildcard=wildcard,
        style=wx.FD_SAVE
    )
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path