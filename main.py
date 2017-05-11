import lxml.etree as ET
import wx


from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel


class Boomslang(wx.Frame):

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

        self.create_main_ui()
        self.create_menu()

        self.Show()

    def create_main_ui(self):
        splitter = wx.SplitterWindow(self)

        tree_panel = BoomTreePanel(splitter, self.xml_root)
        editor_panel = XmlEditorPanel(splitter)
        splitter.SplitVertically(tree_panel, editor_panel)
        splitter.SetMinimumPaneSize(400)


    def create_menu(self):
        """
        Creates the menu bar and menu items for the main frame
        """
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
        Event handler that saves the data to disk
        """
        self.xml_tree.write('test.xml')


if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = Boomslang(xml_path)
    app.MainLoop()