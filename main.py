import wx

class XmlTree(wx.TreeCtrl):
    
    def __init__(self, parent, id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        

class TreePanel(wx.Panel):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.tree = XmlTree(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                            wx.TR_HAS_BUTTONS
                            | wx.TR_EDIT_LABELS)    
        
        self.root = self.tree.AddRoot('Something goes here')
        self.tree.SetPyData(self.root, ('key', 'value'))
        os = self.tree.AppendItem(self.root, 'Operating Systems')
        self.tree.Expand(self.root)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 0, wx.EXPAND)
        self.SetSizer(sizer)
        
        
class MainFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='XML Editor')
        panel = TreePanel(self)
        self.Show()
        
        
if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()