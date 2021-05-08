import wx
import wx.lib.scrolledpanel as scrolled

from functools import partial
from pubsub import pub

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
        self.main_sizer.Add(self.label_sizer, 0, wx.EXPAND|wx.BOTTOM, 5)

        self.widgets.extend([tag_lbl, value_lbl])
        
        lbl_size = wx.Size(75, 25)
        self.add_single_tag_elements(xml_obj, lbl_size)
        
        xml_children = xml_obj.getchildren()
        
        if xml_children:
            child_lbl = wx.StaticText(self.main_sizer.GetContainingWindow(), label="Children:", size=lbl_size)
            
            self.main_sizer.Add(child_lbl, 0, wx.BOTTOM|wx.ALIGN_CENTRE, 5)
            self.widgets.append(child_lbl)
            
            for child in xml_children:
                self.add_single_tag_elements(child, lbl_size)

        self.SetAutoLayout(1)
        self.SetupScrolling()

    def add_single_tag_elements(self, xml_obj, lbl_size):
        """
        Adds the single tag elements to the panel

        This function is only called when there should be just one
        tag / value
        """
        # TODO: The update process for some elements isn't working as expected - especially xml tags. Each tag and text in here should have its own ID and be able to have 'update' called on it.
        object_tag = xml_obj.tag if xml_obj.tag else ""
        object_text = xml_obj.text if xml_obj.text else ""
        
        single_node_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_txt = wx.TextCtrl(self, value=object_tag, size=lbl_size)
        single_node_sizer.Add(tag_txt, 0, wx.ALL, 5)
        tag_txt.Bind(wx.EVT_TEXT, partial(
            self.on_text_change, xml_obj=xml_obj))
        self.widgets.append(tag_txt)

        value_txt = wx.TextCtrl(self, value=object_text, style=wx.TE_MULTILINE)
        value_txt.Bind(wx.EVT_TEXT, partial(
            self.on_text_change, xml_obj=xml_obj))
        single_node_sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
        self.widgets.append(value_txt)

        add_node_btn = wx.Button(self, label='Add Node')
        add_node_btn.Bind(wx.EVT_BUTTON, self.on_add_node)
        single_node_sizer.Add(add_node_btn, 0, wx.ALL|wx.CENTER, 5)
        self.widgets.append(add_node_btn)

        self.main_sizer.Add(single_node_sizer, 0, wx.EXPAND, 5)

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
        # BUG: TODO: This method assumed that the event is updating text, rather than tag on an xml object. Silly.
        xml_obj.text = event.GetString()
        pub.sendMessage('on_change_{}'.format(self.page_id),
                        event=None)

    def on_add_node(self, event):
        """
        Event handler that adds an XML node using pubsub
        """
        pub.sendMessage('add_node_{}'.format(self.page_id))
