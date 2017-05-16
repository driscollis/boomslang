import controller
import lxml.etree as ET
import wx

from functools import partial

from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from wx.lib.pubsub import pub


class Boomslang(wx.Frame):

    def __init__(self, xml_path):
        size = (800, 600)
        wx.Frame.__init__(self, parent=None, title='Boomslang XML',
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

        tree_panel = BoomTreePanel(splitter, self.xml_root)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(size[0] / 2)
        self.create_menu()

        self.Show()

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
        path = controller.save_xml_file(self)
        if path:
            if '.xml' not in path:
                path += '.xml'

            # Update the current directory to the save location
            self.current_directory = os.path.dirname(path)

            # Save the xml
            self.xml_tree.write(path)


if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = Boomslang(xml_path)
    app.MainLoop()