from gi.repository import Gedit
from gi.repository import GObject
from gi.repository import Gtk


def tab_added(tab):
    view = tab.get_view()
    document = tab.get_document()
    language = document.get_language()
    if not language:
        return
    if language.get_name().lower() in ['markdown', 'restructuredtext']:
        view.set_wrap_mode(Gtk.WrapMode.WORD)


class Wraptor(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = 'Wraptor'

    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        self.window.connect('tab-added', lambda _, tab: tab_added(tab))
        self.window.connect('active-tab-state-changed',
                            lambda window: tab_added(window.get_active_tab()))
