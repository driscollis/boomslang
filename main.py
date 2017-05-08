import xml.etree.ElementTree as ET
import wx

from functools import partial
from lxml import etree, objectify
from wx.lib.pubsub import pub


class XmlTree(wx.TreeCtrl):

    def __init__(self, parent, id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.xml_root = parent.xml_root

        root = self.AddRoot(self.xml_root.tag)

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
    def __init__(self, parent, xml_obj):
        wx.Panel.__init__(self, parent)
        self.xml_root = xml_obj

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
            lbl_size = (75, 25)
            for child in xml_obj.getchildren():
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                tag_txt = wx.StaticText(self, label=child.tag, size=lbl_size)
                sizer.Add(tag_txt, 0, wx.ALL, 5)
                self.widgets.append(tag_txt)

                value_txt = wx.TextCtrl(self, value=child.text)
                value_txt.Bind(wx.EVT_TEXT, partial(self.on_text_change, xml_obj=child))
                sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                self.widgets.append(value_txt)

                self.main_sizer.Add(sizer, 0, wx.EXPAND)
            else:
                if getattr(xml_obj, 'tag') and getattr(xml_obj, 'text'):
                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    tag_txt = wx.StaticText(self, label=xml_obj.tag, size=lbl_size)
                    sizer.Add(tag_txt, 0, wx.ALL, 5)
                    self.widgets.append(tag_txt)

                    value_txt = wx.TextCtrl(self, value=xml_obj.text)
                    value_txt.Bind(wx.EVT_TEXT, partial(self.on_text_change, xml_obj=xml_obj))
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

    def on_text_change(self, event, xml_obj):
        print 'Old: ' + xml_obj.text
        xml_obj.text = event.GetString()
        print 'New: ' + xml_obj.text


class MainFrame(wx.Frame):

    def __init__(self, xml_path):
        wx.Frame.__init__(self, parent=None, title='XML Editor',
                          size=(800, 600))

        try:
            self.xml_tree = ET.parse(xml_path)
        except IOError:
            print('Bad file')
            return
        except Exception as e:
            print('Really bad error')
            print(e)
            return

        self.xml_root = self.xml_tree.getroot()

        splitter = wx.SplitterWindow(self)

        tree_panel = TreePanel(splitter, self.xml_root)
        editor_panel = EditorPanel(splitter)
        splitter.SplitVertically(tree_panel, editor_panel)
        splitter.SetMinimumPaneSize(400)
        self.create_menu()

        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        save_menu_item = file_menu.Append(wx.NewId(), 'Save',
                                          'Save the XML')
        self.Bind(wx.EVT_MENU, self.on_save, save_menu_item)


        exitMenuItem = file_menu.Append(wx.NewId(), "Exit",
                                        "Exit the application")
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)

    def on_save(self, event):
        """
        Save the data
        """
        self.xml_tree.write('test.xml')


if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = MainFrame(xml_path)
    app.MainLoop()