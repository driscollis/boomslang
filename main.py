import lxml.etree as ET
import os
import time
import utils
import wx

from boom_attribute_ed import AttributeEditorPanel
from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from wx.lib.pubsub import pub
from wx.lib.wordwrap import wordwrap


class Boomslang(wx.Frame):

    def __init__(self):
        self.size = (800, 600)
        wx.Frame.__init__(self, parent=None, title='Boomslang XML',
                          size=(800, 600))

        self.xml_root = None
        self.full_tmp_path = ''
        self.full_saved_path = ''
        self.changed = False

        self.current_directory = os.path.expanduser('~')
        self.app_location = os.path.dirname(os.path.abspath( __file__ ))
        self.tmp_location = os.path.join(self.app_location, 'drafts')
        self.recent_files_path = os.path.join(
            self.app_location, 'recent_files.txt')

        pub.subscribe(self.save, 'save')
        pub.subscribe(self.auto_save, 'on_change')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(self.main_sizer)

        self.create_menu_and_toolbar()

        self.auto_save_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.auto_save, self.auto_save_timer)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Show()

    def create_display(self):
        """
        Create the tree and xml editing widgets when the user loads
        an XML file
        """
        splitter = wx.SplitterWindow(self.panel)

        tree_panel = BoomTreePanel(splitter, self.xml_root)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        attribute_panel = AttributeEditorPanel(xml_editor_notebook)
        xml_editor_notebook.AddPage(attribute_panel, 'Attributes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(self.size[0] / 2)
        self.main_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.Layout()

    def create_menu_and_toolbar(self):
        """
        Creates the menu bar, menu items, toolbar and accelerator table
        for the main frame
        """
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        help_menu = wx.Menu()

        # add menu items to the file menu
        open_menu_item = file_menu.Append(
            wx.NewId(), 'Open', '')
        self.Bind(wx.EVT_MENU, self.on_open, open_menu_item)

        sub_menu = self.create_recent_items()
        file_menu.AppendMenu(wx.NewId(), 'Recent', sub_menu)

        save_menu_item = file_menu.Append(
            wx.NewId(), 'Save', '')
        self.Bind(wx.EVT_MENU, self.on_save, save_menu_item)

        exit_menu_item = file_menu.Append(
            wx.NewId(), 'Quit', '')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_menu_item)
        menu_bar.Append(file_menu, "&File")

        # add menu items to the help menu
        about_menu_item = help_menu.Append(
            wx.NewId(), 'About')
        self.Bind(wx.EVT_MENU, self.on_about_box, about_menu_item)
        menu_bar.Append(help_menu, '&Help')

        self.SetMenuBar(menu_bar)

        #-----------------------------------------------------------------------
        # Create toolbar
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((16,16))

        open_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (16,16))
        open_tool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, open_ico, "Open", "Open an XML File")
        self.Bind(wx.EVT_MENU, self.on_open, open_tool)

        save_ico = wx.ArtProvider.GetBitmap(
            wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (16,16))
        save_tool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, save_ico, "Save", "Saves the XML")
        self.Bind(wx.EVT_MENU, self.on_save, save_tool)

        self.toolbar.AddSeparator()

        # Create the add node toolbar button
        add_ico = wx.ArtProvider.GetBitmap(
            wx.ART_PLUS, wx.ART_TOOLBAR, (16,16))
        add_tool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, add_ico, "Add Node", "Adds an XML Node")
        self.Bind(wx.EVT_MENU, self.on_add_node, add_tool)

        # Create the delete node button
        remove_ico = wx.ArtProvider.GetBitmap(
            wx.ART_MINUS, wx.ART_TOOLBAR, (16,16))
        remove_node_tool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, remove_ico, "Remove Node", "Removes the XML Node")
        self.Bind(wx.EVT_MENU, self.on_remove_node, remove_node_tool)

        self.toolbar.Realize()

        #-----------------------------------------------------------------------
        # Create an accelerator table
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('O'),
                                          open_menu_item.GetId() ),
                                         (wx.ACCEL_CTRL, ord('S'),
                                          save_menu_item.GetId() ),
                                         (wx.ACCEL_CTRL, ord('A'),
                                          add_tool.GetId() ),
                                         (wx.ACCEL_CTRL, ord('X'),
                                          remove_node_tool.GetId())
                                         ])

        self.SetAcceleratorTable(accel_tbl)

        #-----------------------------------------------------------------------
        # Create status bar
        self.status_bar = self.CreateStatusBar(1, wx.ST_SIZEGRIP)

        msg = 'Welcome to Boomslang XML (c) Michael Driscoll - 2017'
        self.status_bar.SetStatusText(msg)

    def create_recent_items(self):
        """
        Create the recent items sub_menu and return it
        """
        self.recent_dict = {}
        if os.path.exists(self.recent_files_path):
            submenu = wx.Menu()
            try:
                with open(self.recent_files_path) as fobj:
                    for line in fobj:
                        menu_id = wx.NewId()
                        submenu.Append(menu_id, line)
                        self.recent_dict[menu_id] = line.strip()
                        self.Bind(wx.EVT_MENU,
                                  self.on_open_recent_file,
                                  id=menu_id)
                return submenu
            except:
                pass

    def parse_xml(self, xml_path):
        """
        Parses the XML from the file that is passed in
        """
        self.current_directory = os.path.dirname(xml_path)
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

    def auto_save(self, event):
        """
        Event handler that is called via timer or pubsub to save the
        current version of the XML to disk in a temporary location
        """
        print('Autosaving to {} @ {}'.format(self.full_tmp_path, time.ctime()))
        msg = 'Autosaved at {}'.format(time.strftime('%H:%M:%S',
                                                     time.localtime()))
        self.status_bar.SetStatusText(msg)

        self.xml_tree.write(self.full_tmp_path)
        self.changed = True

    def open_xml_file(self, xml_path):
        """
        Open the specified XML file and load it in the application
        """
        current_time = time.strftime('%Y-%m-%d.%H.%M.%S', time.localtime())
        self.full_tmp_path = os.path.join(
            self.tmp_location,
            current_time + '-' + os.path.basename(xml_path))

        if not os.path.exists(self.tmp_location):
            try:
                os.makedirs(self.tmp_location)
            except IOError:
                raise IOError('Unable to create file at {}'.format(
                    self.tmp_location))

        self.parse_xml(xml_path)
        self.create_display()
        # Run the timer every 30 seconds
        self.auto_save_timer.Start(30000)

    def save(self, location=None):
        """
        Save the XML to disk
        """
        if self.xml_root is None:
            utils.warn_nothing_to_save()
            return

        if not location:
            path = utils.save_file(self)
        else:
            path = location

        if path:
            if '.xml' not in path:
                path += '.xml'

            # Update the current directory to the save location
            self.current_directory = os.path.dirname(path)
            self.full_saved_path = path

            # Save the xml
            self.xml_tree.write(path)
            self.changed = False
            msg = 'Last saved at {}'.format(time.strftime('%H:%M:%S',
                                                          time.localtime()))
            self.status_bar.SetStatusText(msg)

    def on_about_box(self, event):
        """
        Event handler that builds and shows an about box
        """
        info = wx.AboutDialogInfo()
        info.Name = "About Boomslang"
        info.Version = "0.1 Beta"
        info.Copyright = "(C) 2017 Mike Driscoll"
        info.Description = wordwrap(
            "Boomslang is a Python-based XML editor ",
            350, wx.ClientDC(self.panel))
        info.WebSite = ("https://github.com/driscollis/boomslang",
                        "Boomslang on Github")
        info.Developers = ["Mike Driscoll"]
        info.License = wordwrap("wxWindows Library Licence", 500,
                                wx.ClientDC(self.panel))
        # Show the wx.AboutBox
        wx.AboutBox(info)

    def on_add_node(self, event):
        """
        Event handler that is fired when an XML node is added to the
        selected node
        """
        pub.sendMessage('add_node')

    def on_remove_node(self, event):
        """
        Event handler that is fired when an XML node is removed
        """
        pub.sendMessage('remove_node')

    def on_open(self, event):
        """
        Event handler that is called when you need to open an XML file
        """
        xml_path = utils.open_file(self)

        if xml_path:
            self.open_xml_file(xml_path)
            self.update_recent_files(xml_path)

    def update_recent_files(self, xml_path):
        """
        Update the recent files file
        """
        lines = []
        try:
            with open(self.recent_files_path) as fobj:
                lines = fobj.readlines()
        except:
            pass

        lines = [line.strip() for line in lines]

        if xml_path not in lines:
            try:
                with open(self.recent_files_path, 'a') as fobj:
                    fobj.write(xml_path)
                    fobj.write('\n')
            except:
                pass
        elif xml_path != lines[0]:
            for index, item in enumerate(lines):
                if xml_path == item:
                    lines.pop(index)
                    break
            lines.insert(0, xml_path)

        if len(lines) > 10:
            lines = lines[0:9]

            # rewrite the file
            try:
                with open(self.recent_files_path, 'w') as fobj:
                    for line in lines:
                        fobj.write(line)
                        fobj.write('\n')
            except:
                pass

    def on_open_recent_file(self, event):
        """
        Event handler that is called when a recent file is selected
        for opening
        """
        self.open_xml_file(self.recent_dict[event.GetId()])

    def on_save(self, event):
        """
        Event handler that saves the data to disk
        """
        self.save()

    def on_exit(self, event):
        """
        Event handler that closes the application
        """
        if self.full_saved_path and self.full_tmp_path and self.changed:
            # verify that the draft file is actually different from the
            # in-memory version via md5 hash
            current = utils.is_save_current(self.full_saved_path,
                                                 self.full_tmp_path)
            if not current:
                utils.warn_not_saved()

        if self.auto_save_timer.IsRunning():
            self.auto_save_timer.Stop()
        if os.path.exists(self.full_tmp_path):
            try:
                os.remove(self.full_tmp_path)
            except IOError:
                print('Unable to delete file: {}'.format(self.full_tmp_path))

        self.Destroy()

# ------------------------------------------------------------------------------
# Run the program!
if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = Boomslang()
    app.MainLoop()