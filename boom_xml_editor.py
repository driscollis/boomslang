import wx

from wx.lib.pubsub import pub


class XmlEditorPanel(wx.Panel):
    """
    The panel in the notebook that allows editing of XML element values
    """

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
        Clears the widgets from the panel in preparation for an update
        """
        for widget in self.widgets:
            widget.Destroy()

        self.widgets = []
        self.Layout()

    def on_text_change(self, event, xml_obj):
        """
        An event handler that is called when the text changes in the text
        control. This will update the passed in xml object to something
        new
        """
        print 'Old: ' + xml_obj.text
        xml_obj.text = event.GetString()
        print 'New: ' + xml_obj.text