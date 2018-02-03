from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk

class Loading(Gtk.Box):


    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        
        self._spinner = Gtk.Spinner()

        self.add(self._spinner)
        self.show_all()

    def start(self):
        self._spinner.start()

    def stop(self):
        self._spinner.stop()