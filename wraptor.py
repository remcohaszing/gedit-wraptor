import json
import os
from os import path

from gi.repository import Gedit
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import PeasGtk
from xdg import BaseDirectory

#: Global whitelist which may be used by both the Wraptor as the ConfigMenu
whitelist = []
#: Global whitelist which may be used by both the Wraptor as the ConfigMenu
blacklist = []

#: The path where to store the configuration.
config_dir = path.join(BaseDirectory.xdg_config_home, 'gedit-wraptor')


def mkdirp(full):
    """
    Recursively constructs a full directory path.

    Similar to ``mkdir -p``.

    """
    assembled = ''
    for p in path.split(full):
        assembled = path.join(assembled, p)
        if not path.exists(assembled):
            os.mkdir(assembled)


class ListWidget(Gtk.ScrolledWindow):
    """
    Represents a fully preconfigured scrolled Gtk.TreeView representing a list.

    """
    def __init__(self, items, label='', location=None):
        """
        Args:
            items (list): The list of items to represent.
            label (str): The label to add to the top of the view.

        """
        super().__init__()
        self.items = items
        self.location = path.join(config_dir, location) if location else None
        self.store = Gtk.ListStore(str)
        for item in items:
            self.store.append([item])
        combo_cell_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(label, combo_cell_text, text=0)
        self.tree = Gtk.TreeView(self.store)
        self.tree.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.tree.append_column(column_text)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add(self.tree)

    def append(self, item):
        """
        Appends an item to the list and the view.

        item (str): The item to append.

        """
        self.store.append([item])
        self.items.append(item)
        self._save()

    def remove(self, row):
        """
        Removed a tree row value from the list and its iter from view.

        Args:
            row: (gi.repository.Gtk.TreeModelRow): The row to remove.

        """
        # We can't safely rely on the index after removing it from the store.
        item = row[0]
        self.store.remove(row.iter)
        self.items.remove(item)
        self._save()

    def _save(self):
        if self.location:
            with open(self.location, 'w') as f:
                json.dump(self.items, f)


def tab_added(tab):
    """
    Sets the wrap mode for whitelisted languages.

    Args:
        tab: The tab of which view to set the wrap mode.

    """
    view = tab.get_view()
    document = tab.get_document()
    language = document.get_language()
    if not language:
        return
    if language.get_name().lower() in whitelist:
        view.set_wrap_mode(Gtk.WrapMode.WORD)
    elif language.get_name().lower() in blacklist:
        view.set_wrap_mode(Gtk.WrapMode.NONE)


class WraptorInit(GObject.Object, Gedit.AppActivatable):
    """
    Load the global plugin configuration.

    """
    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        """
        Load the plugin configuration.

        """
        mkdirp(config_dir)
        try:
            with open(path.join(config_dir, 'whitelist.json')) as f:
                whitelist.extend(json.load(f))
        except FileNotFoundError:
            pass
        try:
            with open(path.join(config_dir, 'blacklist.json')) as f:
                blacklist.extend(json.load(f))
        except FileNotFoundError:
            pass


class Wraptor(GObject.Object, Gedit.WindowActivatable):
    """
    The main plugin activatable.

    """
    __gtype_name__ = 'Wraptor'
    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        """
        Binds tab changing events.

        """
        self.window.connect('tab-added', lambda _, tab: tab_added(tab))
        self.window.connect('active-tab-state-changed',
                            lambda window: tab_added(window.get_active_tab()))


class ConfigMenu(GObject.Object, Gedit.WindowActivatable,
                 PeasGtk.Configurable):
    """
    Represents the configuration screen for the plugin.

    """
    window = GObject.property(type=Gedit.Window)

    def do_create_configure_widget(self):
        box = Gtk.Box()
        language_manager = GtkSource.LanguageManager()
        self.undecided = []
        for id in language_manager.get_language_ids():
            if id not in whitelist and id not in blacklist:
                self.undecided.append(id)

        self.whitelist_widget = ListWidget(whitelist,
                                           'Always wrap', 'whitelist.json')
        self.blacklist_widget = ListWidget(blacklist,
                                           'Never wrap', 'blacklist.json')
        self.undecided_widget = ListWidget(self.undecided)

        self.button_add_whitelist = Gtk.Button('<')
        self.button_remove_whitelist = Gtk.Button('>')
        self.button_add_blacklist = Gtk.Button('>')
        self.button_remove_blacklist = Gtk.Button('<')

        self.button_add_whitelist.connect('clicked', self.whitelist_add)
        self.button_remove_whitelist.connect('clicked', self.whitelist_remove)
        self.button_add_blacklist.connect('clicked', self.blacklist_add)
        self.button_remove_blacklist.connect('clicked', self.blacklist_remove)

        box.add(self.whitelist_widget)
        box.add(self.button_add_whitelist)
        box.add(self.button_remove_whitelist)
        box.add(self.undecided_widget)
        box.add(self.button_remove_blacklist)
        box.add(self.button_add_blacklist)
        box.add(self.blacklist_widget)

        box.set_size_request(500, 700)
        return box

    def whitelist_add(self, _):
        """
        Adds the undecided selection to the whitelist.

        """
        self.move(self.undecided_widget, self.whitelist_widget)

    def whitelist_remove(self, _):
        """
        Removes the whitelist selection from the whitelist.

        """
        self.move(self.whitelist_widget, self.undecided_widget)

    def blacklist_add(self, _):
        """
        Adds the undecided selection to the blacklist.

        """
        self.move(self.undecided_widget, self.blacklist_widget)

    def blacklist_remove(self, _):
        """
        Removes the blacklist selection from the whitelist.

        """
        self.move(self.blacklist_widget, self.undecided_widget)

    def move(self, from_, to):
        """
        Move a selection from one list widget to another.

        from_ (ListWidget): The list widget from which to remove the selection.
        to (ListWidget): The list widget to which to append the selection.

        """
        selection = from_.tree.get_selection()
        model, rows = selection.get_selected_rows()
        iters = [model[r] for r in rows]
        for row in iters:
            to.append(row[0])
            from_.remove(row)
