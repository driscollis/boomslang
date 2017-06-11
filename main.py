import lxml.etree as ET
import os
import time
import utils
import wx
import wx.lib.flatnotebook as fnb

from boom_attribute_ed import AttributeEditorPanel
from boom_tree import BoomTreePanel
from boom_xml_editor import XmlEditorPanel
from wx.lib.pubsub import pub
from wx.lib.wordwrap import wordwrap
from xml_viewer import XmlViewer


class NewPage(wx.Panel):
    """
    Create a new page for each opened XML document. This is the
    top-level widget for the majority of the application
    """

    def __init__(self, parent, xml_path, size, opened_files):
        wx.Panel.__init__(self, parent)
        self.page_id = id(self)
        self.xml_root = None
        self.size = size
        self.opened_files = opened_files
        self.current_file = xml_path
        self.title = os.path.basename(xml_path)

        self.app_location = os.path.dirname(os.path.abspath( __file__ ))

        self.tmp_location = os.path.join(self.app_location, 'drafts')

        pub.subscribe(self.save, 'save_{}'.format(self.page_id))
        pub.subscribe(self.auto_save, 'on_change_{}'.format(self.page_id))

        self.parse_xml(xml_path)

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

        if self.xml_root:
            self.create_editor()

    def create_editor(self):
        """
        Create the XML editor widgets
        """
        page_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self)
        tree_panel = BoomTreePanel(splitter, self.xml_root, self.page_id)

        xml_editor_notebook = wx.Notebook(splitter)
        xml_editor_panel = XmlEditorPanel(xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(xml_editor_panel, 'Nodes')

        attribute_panel = AttributeEditorPanel(
            xml_editor_notebook, self.page_id)
        xml_editor_notebook.AddPage(attribute_panel, 'Attributes')

        splitter.SplitVertically(tree_panel, xml_editor_notebook)
        splitter.SetMinimumPaneSize(self.size[0] / 2)
        page_sizer.Add(splitter, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(page_sizer)
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def auto_save(self, event):
        """
        Event handler that is called via pubsub to save the
        current version of the XML to disk in a temporary location
        """
        self.xml_tree.write(self.full_tmp_path)
        pub.sendMessage('on_change_status', save_path=self.full_tmp_path)

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

    def save(self, location=None):
        """
        Save the XML to disk
        """
        if not location:
            path = utils.save_file(self)
        else:
            path = location

        if path:
            if '.xml' not in path:
                path += '.xml'

            # Save the xml
            self.xml_tree.write(path)
            self.changed = False

    def on_close(self, event):
        """
        Event handler that is called when the panel is being closed
        """
        if self.current_file in self.opened_files:
            self.opened_files.remove(self.current_file)

        if os.path.exists(self.full_tmp_path):
            try:
                os.remove(self.full_tmp_path)
            except IOError:
                print('Unable to delete file: {}'.format(self.full_tmp_path))


class Boomslang(wx.Frame):

    def __init__(self):
        self.size = (800, 600)
        wx.Frame.__init__(self, parent=None, title='Boomslang XML',
                          size=(800, 600))

        self.full_tmp_path = ''
        self.full_saved_path = ''
        self.changed = False
        self.notebook = None
        self.opened_files = []
        self.last_opened_file = None
        self.current_page = None

        self.current_directory = os.path.expanduser('~')
        self.app_location = os.path.dirname(os.path.abspath( __file__ ))
        self.recent_files_path = os.path.join(
            self.app_location, 'recent_files.txt')

        pub.subscribe(self.save, 'save')
        pub.subscribe(self.auto_save_status, 'on_change_status')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        self.panel.SetSizer(self.main_sizer)

        self.create_menu_and_toolbar()

        self.Bind(wx.EVT_CLOSE, self.on_exit)

        self.Show()

    def create_new_editor(self, xml_path):
        """
        Create the tree and xml editing widgets when the user loads
        an XML file
        """
        if not self.notebook:
            self.notebook = fnb.FlatNotebook(
                self.panel)
            self.main_sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
            style = self.notebook.GetAGWWindowStyleFlag()
            style |= fnb.FNB_X_ON_TAB
            self.notebook.SetAGWWindowStyleFlag(style)
            self.notebook.Bind(
                fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.on_page_closing)

        if xml_path not in self.opened_files:
            self.current_page = NewPage(self.notebook, xml_path, self.size,
                                        self.opened_files)
            self.notebook.AddPage(self.current_page,
                                  os.path.basename(xml_path),
                                  select=True)
            self.last_opened_file = xml_path

            self.opened_files.append(self.last_opened_file)

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

        # Create a preview XML button
        preview_ico = wx.ArtProvider.GetBitmap(
            wx.ART_REPORT_VIEW, wx.ART_TOOLBAR, (16,16))
        preview_tool = self.toolbar.AddSimpleTool(
            wx.ID_ANY, preview_ico, 'Preview XML', 'Previews XML')
        self.Bind(wx.EVT_MENU, self.on_preview_xml, preview_tool)

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

    def auto_save_status(self, save_path):
        """
        This function is called via PubSub to update the frame's status
        """
        print('Autosaving to {} @ {}'.format(save_path, time.ctime()))
        msg = 'Autosaved at {}'.format(time.strftime('%H:%M:%S',
                                                     time.localtime()))
        self.status_bar.SetStatusText(msg)

        self.changed = True

    def open_xml_file(self, xml_path):
        """
        Open the specified XML file and load it in the application
        """
        self.create_new_editor(xml_path)

    def save(self, location=None):
        """
        Update the frame with save status
        """
        if self.current_page.xml_root is None:
            utils.warn_nothing_to_save()
            return

        pub.sendMessage('save_{}'.format(self.current_page.page_id))

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
            self.last_opened_file = xml_path
            self.open_xml_file(xml_path)
            self.update_recent_files(xml_path)

    def on_page_closing(self, event):
        """
        Event handler that is called when a page in the notebook is closing
        """
        print 'Page closing'
        page = self.notebook.GetCurrentPage()
        print page.title
        page.Close()
        print self.opened_files

    def on_preview_xml(self, event):
        """
        Event handler called for previewing the current state of the XML
        in memory
        """
        if self.last_opened_file:
            previewer = XmlViewer(
                xml_file=self.last_opened_file)
            previewer.ShowModal()
            previewer.Destroy()

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
        self.Destroy()

# ------------------------------------------------------------------------------
# Run the program!
if __name__ == '__main__':
    xml_path = 'books.xml'
    app = wx.App(redirect=False)
    frame = Boomslang()
    app.MainLoop()