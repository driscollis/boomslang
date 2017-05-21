import hashlib
import os
import wx

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


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

def get_md5(path):
    """
    Returns the MD5 hash of the given file
    """
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(4096)
            hash_md5.update(data)
            if not data:
                break
    return hash_md5.hexdigest()

def is_save_current(saved_file_path, tmp_file_path):
    """
    Returns a bool that determines if the saved file and the
    tmp file's MD5 hash are the same
    """
    saved_md5 = get_md5(saved_file_path)
    tmp_md5 = get_md5(tmp_file_path)

    return saved_md5 == tmp_md5
