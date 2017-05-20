import wx

from wx.lib.pubsub import pub


class AttributeDialog(wx.Dialog):

    def __init__(self, xml_obj):
        wx.Dialog.__init__(self, None, title='Add Attribute')
        self.xml_obj = xml_obj

        lbl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        attr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        attr_lbl = wx.StaticText(self, label='Attribute')
        lbl_sizer.Add(attr_lbl, 0, wx.ALL, 5)
        lbl_sizer.AddSpacer((140, -1))
        value_lbl = wx.StaticText(self, label='Value')
        lbl_sizer.Add(value_lbl, 0, wx.ALL, 5)

        self.attr_text = wx.TextCtrl(self)
        attr_sizer.Add(self.attr_text, 1, wx.ALL, 5)
        self.value_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.value_text.Bind(wx.EVT_KEY_DOWN, self.on_enter)
        attr_sizer.Add(self.value_text, 1, wx.ALL, 5)

        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL|wx.CENTER, 5)

        cancel_btn = wx.Button(self, label='Cancel')
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(cancel_btn, 0, wx.ALL|wx.CENTER, 5)

        main_sizer.Add(lbl_sizer)
        main_sizer.Add(attr_sizer, 0, wx.EXPAND)
        main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(main_sizer)

        self.ShowModal()

    def on_enter(self, event):
        """
        Event handler that fires when a key is pressed in the
        attribute value text control
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            self.on_save(event=None)
        event.Skip()

    def on_cancel(self, event):
        """
        Event handler that is called when the Cancel button is
        pressed.

        Will destroy the dialog
        """
        self.Close()

    def on_save(self, event):
        """
        Event handler that is called when the Save button is
        pressed.

        Updates the XML object with the new node element and
        tells the UI to update to display the new element
        before destroying the dialog
        """
        attr = self.attr_text.GetValue()
        value = self.value_text.GetValue()
        if attr:
            self.xml_obj.attrib[attr] = value
            pub.sendMessage('ui_updater', xml_obj=self.xml_obj)
        else:
            # TODO - Show a dialog telling the user that there is no attr to save
            raise NotImplemented

        self.Close()
