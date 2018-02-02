"""
Your favorite Audio Cutter.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Artist : Alfredo Hernández
Website : https://github.com/bil-elmoussaoui/Audio-Cutter
This file is part of AudioCutter.
AudioCutter is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
AudioCutter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with AudioCutter. If not, see <http://www.gnu.org/licenses/>.
"""

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class ZoomBox(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.END)
        self.zoom_up = Gtk.Button()
        self.zoom_down = Gtk.Button()
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



