import wx

from wx.lib.pubsub import pub


class XmlTree(wx.TreeCtrl):
    """
    The class that holds all the functionality for the tree control
    widget
    """

    def __init__(self, parent, id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.xml_root = parent.xml_root

        root = self.AddRoot(self.xml_root.tag)

        for top_level_item in self.xml_root.getchildren():
            child = self.AppendItem(root, top_level_item.tag)
            self.SetItemHasChildren(child)
            self.SetPyData(child, top_level_item)

        self.Expand(root)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_item_expanding)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

    def add_elements(self, item, book):
        """
        Add items to the tree control
        """
        for element in book.getchildren():
            child = self.AppendItem(item, element.tag)
            self.SetPyData(child, element)
            if element.getchildren():
                self.SetItemHasChildren(child)

    def on_item_expanding(self, event):
        """
        A handler that fires when a tree item is being expanded

        This will cause the sub-elements of the tree to be created
        and added to the tree
        """
        item = event.GetItem()
        xml_obj = self.GetPyData(item)

        for element in xml_obj.getchildren():
            child = self.AppendItem(item, element.tag)
            self.SetPyData(item, element)
            if element.getchildren():
                self.SetItemHasChildren(child)

    def on_tree_selection(self, event):
        """
        A handler that fires when an item in the tree is selected

        This will cause an update to be sent to the XmlEditorPanel
        to allow editing of the XML
        """
        item = event.GetItem()
        xml_obj = self.GetPyData(item)
        pub.sendMessage('ui_updater', xml=xml_obj)


class BoomTreePanel(wx.Panel):
    """
    The panel class that contains the XML tree control
    """

    def __init__(self, parent, xml_obj):
        wx.Panel.__init__(self, parent)
        self.xml_root = xml_obj

        self.tree = XmlTree(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.TR_HAS_BUTTONS)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)