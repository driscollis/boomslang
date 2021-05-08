import wx
import wx.lib.scrolledpanel as scrolled

from functools import partial
from pubsub import pub


class boomNodeDisplay(wx.BoxSizer):
    """
    A class to display the tag and value of a Node
    """
    def __init__(self):
        super(wx.HORIZONTAL)
        self.id = wx.ID_ANY
        self.widgets = []
        pub.subscribe(self.update_ui, f"ui_updater_{self.id}")

    def update_ui(self, xml_obj):
        """
        Update the XML Node based on a change
        
        Fundamentally, each XML node is a tag and a Value. It also has a number of attributes, but those are displayed separately.

        """
        
        
        

class XmlEditorPanel(scrolled.ScrolledPanel):
    """
    The panel in the notebook that allows editing of XML element values
    """

    def __init__(self, parent, page_id):
        """Constructor"""
        scrolled.ScrolledPanel.__init__(
            self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_id = page_id
        self.widgets = []
        self.label_spacer = None

        pub.subscribe(self.update_ui, 'ui_updater_{}'.format(self.page_id))

        self.SetSizer(self.main_sizer)

    def update_ui(self, xml_obj):
        """
        Update the panel's user interface based on the data
        """
        self.label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.clear()

        tag_lbl = wx.StaticText(self, label='Tags')
        value_lbl = wx.StaticText(self, label='Value')
        self.label_sizer.Add(tag_lbl, 0, wx.ALL, 5)
        self.label_sizer.Add((55, 0))
        self.label_sizer.Add(value_lbl, 0, wx.ALL, 5)
        self.main_sizer.Add(self.label_sizer)

        self.widgets.extend([tag_lbl, value_lbl])

        if xml_obj is not None:
            lbl_size = (75, 25)
            self.add_single_tag_elements(xml_obj, lbl_size)

            xml_children = xml_obj.getchildren()
                                         
            if xml_children:
                child_lbl = wx.StaticText(self, label="Children:", size=lbl_size)
                
                self.main_sizer.Add(child_lbl)
                self.widgets.append(child_lbl)
            
                for child in xml_children:
                    sizer = wx.BoxSizer(wx.HORIZONTAL)
                    text = child.tag
                    tag_txt = wx.TextCtrl(self, value=text if text else "", size=lbl_size)
                    sizer.Add(tag_txt, 0, wx.ALL, 5)
                    
                    text = child.text if child.text else ''
                    
                    value_txt = wx.TextCtrl(self, value=text)
                    value_txt.Bind(wx.EVT_TEXT, partial(self.on_text_change, xml_obj=child))
                    sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                    self.widgets.extend([tag_txt, value_txt])
                    
                self.main_sizer.Add(sizer, 0, wx.EXPAND)

        self.SetAutoLayout(1)
        self.SetupScrolling()

    def add_single_tag_elements(self, xml_obj, lbl_size):
        """
        Adds the single tag elements to the panel

        This function is only called when there should be just one
        tag / value
        """
        object_tag = xml_obj.tag
        object_text = xml_obj.text
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_txt = wx.TextCtrl(self, value=object_tag if object_tag else "", size=lbl_size)
        sizer.Add(tag_txt, 0, wx.ALL, 5)
        tag_txt.Bind(wx.EVT_TEXT, partial(
            self.on_text_change, xml_obj=xml_obj))
        self.widgets.append(tag_txt)

        value_txt = wx.TextCtrl(self, value=object_text if object_text else "")
        value_txt.Bind(wx.EVT_TEXT, partial(
            self.on_text_change, xml_obj=xml_obj))
        sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
        self.widgets.append(value_txt)

        add_node_btn = wx.Button(self, label='Add Node')
        add_node_btn.Bind(wx.EVT_BUTTON, self.on_add_node)
        sizer.Add(add_node_btn, 0, wx.ALL|wx.CENTER, 5)
        self.widgets.append(add_node_btn)

        self.main_sizer.Add(sizer, 0, wx.EXPAND)

    def clear(self):
        """
        Clears the widgets from the panel in preparation for an update
        """
        sizers = {}
        for widget in self.widgets:
            sizer = widget.GetContainingSizer()
            if sizer:
                sizer_id = id(sizer)
                if sizer_id not in sizers:
                    sizers[sizer_id] = sizer
            widget.Destroy()

        for sizer in sizers:
            self.main_sizer.Remove(sizers[sizer])

        self.widgets = []
        self.Layout()


    def on_text_change(self, event, xml_obj):
        """
        An event handler that is called when the text changes in the text
        control. This will update the passed in xml object to something
        new
        """
        xml_obj.text = event.GetString()
        pub.sendMessage('on_change_{}'.format(self.page_id),
                        event=None)

    def on_add_node(self, event):
        """
        Event handler that adds an XML node using pubsub
        """
        pub.sendMessage('add_node_{}'.format(self.page_id))
