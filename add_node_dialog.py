import controller
import lxml.etree as ET
import wx

from wx.lib.pubsub import pub


class NodeDialog(wx.Dialog):

    def __init__(self, xml_obj):
        wx.Dialog.__init__(self, None, title='New Node')
        self.xml_obj = xml_obj

        lbl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tag_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_size = (95, 20)

        tag_lbl = wx.StaticText(self, label='Element Tag', size=lbl_size)
        value_lbl = wx.StaticText(self, label='Element Value')

        lbl_sizer.Add(tag_lbl, 0, wx.ALL, 5)
        lbl_sizer.Add(value_lbl, 0, wx.ALL, 5)

        self.tag_txt = wx.TextCtrl(self, value='')
        self.value_txt  = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.value_txt.Bind(wx.EVT_KEY_DOWN, self.on_enter)
        tag_sizer.Add(self.tag_txt, 0, wx.ALL, 5)
        tag_sizer.Add(self.value_txt, 0, wx.ALL, 5)

        main_sizer.Add(lbl_sizer)
        main_sizer.Add(tag_sizer)

        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL|wx.CENTER, 5)

        cancel_btn = wx.Button(self, label='Cancel')
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(cancel_btn, 0, wx.ALL|wx.CENTER, 5)
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
        element = ET.SubElement(
            self.xml_obj, self.tag_txt.GetValue())
        element.text = self.value_txt.GetValue()
        pub.sendMessage('tree_update', xml_obj=element)
        self.Close()

if __name__ == '__main__':
    app = wx.App(False)
    dlg = NodeDialog('')
    dlg.Destroy()
    app.MainLoop()