import wx

from functools import partial
from wx.lib.pubsub import pub
import wx.lib.scrolledpanel as scrolled


class XmlEditorPanel(scrolled.ScrolledPanel):
    """
    The panel in the notebook that allows editing of XML element values
    """

    def __init__(self, parent):
        """Constructor"""
        scrolled.ScrolledPanel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        pub.subscribe(self.update_xml_editor, 'ui_updater')
        self.widgets = []

        self.SetSizer(self.main_sizer)

    def update_xml_editor(self, xml):
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

        if xml is not None:
            lbl_size = (75, 25)
            for child in xml.getchildren():
                if child.getchildren():
                    continue
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                tag_txt = wx.StaticText(
                    self, label=child.tag, size=lbl_size)
                sizer.Add(tag_txt, 0, wx.ALL, 5)
                self.widgets.append(tag_txt)

                text = child.text if child.text else ''

                value_txt = wx.TextCtrl(self, value=text)
                value_txt.Bind(wx.EVT_TEXT, partial(
                    self.on_element_change, xml_obj=child))
                sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
                self.widgets.append(value_txt)

                self.main_sizer.Add(sizer, 0, wx.EXPAND)
            else:
                if getattr(xml, 'tag') and getattr(xml, 'text') and xml is not None:
                    if xml.getchildren() == []:
                        self.add_single_xml_elements(xml, lbl_size)

            self.SetAutoLayout(1)
            self.SetupScrolling()

    def add_single_xml_elements(self, xml_obj, lbl_size):
        """
        Adds the single tag elements to the panel

        This function is only called when there should be just one
        tag / value
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_txt = wx.StaticText(self, label=xml_obj.tag, size=lbl_size)
        sizer.Add(tag_txt, 0, wx.ALL, 5)
        self.widgets.append(tag_txt)

        value_txt = wx.TextCtrl(self, value=xml_obj.text)
        value_txt.Bind(wx.EVT_TEXT, partial(
            self.on_element_change, xml_obj=xml_obj))
        sizer.Add(value_txt, 1, wx.ALL|wx.EXPAND, 5)
        self.widgets.append(value_txt)

        self.main_sizer.Add(sizer, 0, wx.EXPAND)

    def clear(self):
        """
        Clears the widgets from the panel in preparation for an update
        """
        for widget in self.widgets:
            widget.Destroy()

        self.widgets = []
        self.Layout()

    def on_element_change(self, event, xml_obj):
        """
        An event handler that is called when the text changes in the text
        control. This will update the passed in xml object to something
        new
        """
        print 'Old: ' + xml_obj.text
        xml_obj.text = event.GetString()
        print 'New: ' + xml_obj.text