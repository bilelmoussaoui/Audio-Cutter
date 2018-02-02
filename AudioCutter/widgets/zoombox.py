from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class ZoomBox(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.END)
        self.zoom_up = Gtk.Button(label="+")
        self.zoom_down = Gtk.Button(label="-")
        self._build_widgets()


    def _build_widgets(self):
        up_icn = Gio.ThemedIcon(name="list-add-symbolic")
        up_img = Gtk.Image.new_from_gicon(up_icn, Gtk.IconSize.BUTTON)
        self.zoom_up.set_image(up_img)
        self.zoom_up.get_style_context().add_class("flat")

        # Lower btn
        lower_icn = Gio.ThemedIcon(name="list-remove-symbolic")
        lower_img = Gtk.Image.new_from_gicon(lower_icn, Gtk.IconSize.BUTTON)
        self.zoom_down.set_image(lower_img)
        self.zoom_down.get_style_context().add_class("flat")

        self.pack_start(self.zoom_up, False, False, 0)
        self.pack_start(self.zoom_down, False, False, 0)
        self.show_all()



