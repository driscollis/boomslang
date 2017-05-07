import wx

from lxml import etree, objectify
from wx.lib.pubsub import pub


class XmlTree(wx.TreeCtrl):

    def __init__(self, parent, id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        try:
            with open(parent.xml_path) as f:
                xml = f.read()
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return

        self.xml_root = objectify.fromstring(xml)

        root = self.AddRoot(self.xml_root.tag)
        self.SetPyData(root, ('key', 'value'))

        for top_level_item in self.xml_root.getchildren():
            child = self.AppendItem(root, top_level_item.tag)
            self.SetItemHasChildren(child)
            self.SetPyData(child, top_level_item)

        self.Expand(root)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpanding)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def onItemExpanding(self, event):
        item = event.GetItem()
        xml_obj = self.GetPyData(item)
        book_id = xml_obj.attrib

        for top_level_item in self.xml_root.getchildren():
            if top_level_item.attrib == book_id:
                book = top_level_item
                self.SetPyData(item, top_level_item)
                self.add_elements(item, book)
                break

    def add_elements(self, item, book):
        for element in book.getchildren():
            child = self.AppendItem(item, element.tag)
            self.SetPyData(child, element)
            if element.getchildren():
                self.SetItemHasChildren(child)

    def on_tree_selection(self, event):
        item = event.GetItem()
        xml_obj = self.GetPyData(item)
        pub.sendMessage('ui_updater', xml_obj=xml_obj)


class TreePanel(wx.Panel):

    #----------------------------------------------------------------------
    def __init__(self, parent, xml_path):
        wx.Panel.__init__(self, parent)
        self.xml_path = xml_path

        self.tree = XmlTree(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                            wx.TR_HAS_BUTTONS
                            | wx.TR_EDIT_LABELS)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 0, wx.EXPAND)
        self.SetSizer(sizer)


class EditorPanel(wx.Panel):
    """"""

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        pub.subscribe(self.update_ui, 'ui_updater')
        self.widgets = []

        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj):
        """
        Update the panel's user interface based on the data
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.clear()

        tag_lbl = wx.StaticText(self, label='Tags')
        value_lbl = wx.StaticText(self, label='Value')
        sizer.Add(tag_lbl, 0, wx.ALL, 5)
        sizer.AddSpacer((55, 0))
        sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.main_sizer.Add(sizer)

        self.widgets.extend([tag_lbl, value_lbl])

        if xml_obj:
            for child in xml_obj.getchildren():
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                tag_txt = wx.TextCtrl(self, value=child.tag)
                sizer.Add(tag_txt, 0, wx.ALL, 5)
                self.widgets.append(tag_txt)

                value_txt = wx.TextCtrl(self, value=child.text)
                sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                self.widgets.append(value_txt)

                self.main_sizer.Add(sizer, 0, wx.EXPAND)
            else:
                if getattr(xml_obj, 'tag') and getattr(xml_obj, 'text'):
                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    tag_txt = wx.TextCtrl(self, value=xml_obj.tag)
                    sizer.Add(tag_txt, 0, wx.ALL, 5)
                    self.widgets.append(tag_txt)

                    value_txt = wx.TextCtrl(self, value=xml_obj.text)
                    sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                    self.widgets.append(value_txt)

                    self.main_sizer.Add(sizer, 0, wx.EXPAND)


        self.Layout()

    def clear(self):
        """
        Clears the panel of widgets
        """
        for widget in self.widgets:
            widget.Destroy()

        self.widgets = []
        self.Layout()


class MainFrame(wx.Frame):

    def __init__(self, xml_path):
        wx.Frame.__init__(self, parent=None, title='XML Editor', size=(800, 600))

        splitter = wx.SplitterWindow(self)

        tree_panel = TreePanel(splitter, xml_path)
        editor_panel = EditorPanel(splitter)
        splitter.SplitVertically(tree_panel, editor_panel)
        splitter.SetMinimumPaneSize(20)

        self.Show()


if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = MainFrame(xml_path)
    app.MainLoop()