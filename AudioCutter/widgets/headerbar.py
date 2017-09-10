"""
Your favorite Audio Cutter.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Artist : Alfredo Hernández
Website : https://github.com/bil-elmoussaoui/Audio-Cutter
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
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
from gettext import gettext as _
from os import path

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, GObject, Gtk


class HeaderBar(Gtk.HeaderBar, GObject.GObject):
    """Main Window's Header Bar widget."""

    # HeaderBar Instance
    instance = None

    # GObject signals
    __gsignals__ = {
        'open-file': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        Gtk.HeaderBar.__init__(self)
        self._play_btn = Gtk.Button()
        self._open_btn = Gtk.Button()
        self.menu_btn = Gtk.Button()
        self.set_title(_("Audio Cutter"))
        self.set_show_close_button(True)
        self._setup_widgets()

    @staticmethod
    def get_default():
        """Return the default instnace of HeaderBar."""
        if HeaderBar.instance is None:
            HeaderBar.instance = HeaderBar()
        return HeaderBar.instance

    def _setup_widgets(self):
        """Setup main headerbar widgets."""
        # Open button
        self._open_btn.set_label(_("Open"))
        self._open_btn.connect("clicked", self._open_file)
        self.pack_start(self._open_btn)

        menu_icn = Gio.ThemedIcon(name="open-menu-symbolic")
        menu_img = Gtk.Image.new_from_gicon(menu_icn, Gtk.IconSize.BUTTON)
        self.menu_btn.set_image(menu_img)
        self.menu_btn.set_visible(False)
        self.menu_btn.set_no_show_all(True)
        self.pack_end(self.menu_btn)

        # Play Button
        play_icn = Gio.ThemedIcon(name="media-playback-start-symbolic")
        play_img = Gtk.Image.new_from_gicon(play_icn, Gtk.IconSize.BUTTON)
        self._play_btn.set_image(play_img)
        self._play_btn.set_sensitive(False)
        self.pack_start(self._play_btn)

    def _open_file(self, *args):
        """Send a open-file signal to the Main Window."""
        self.emit("open-file")

    def set_open_file(self, filename):
        """
        Set a filename as open.
        Change the subtitle to the filename.
        Also makes the play button sensitive
        """
        self.set_subtitle(filename)
        self._play_btn.set_sensitive(True)
        self.set_has_subtitle(True)
