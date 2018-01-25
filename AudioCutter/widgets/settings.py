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

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk


class SettingRow(Gtk.ListBoxRow):

    def __init__(self, label, widget):
        Gtk.ListBoxRow.__init__(self)
        self.label = label
        self.widget = widget

        self._build_widgets()

    def _build_widgets(self):
        label = Gtk.Label(label=self.label)



class SettingsWindow(Gtk.Window):
    """Settings window widget."""

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_resizable(False)
        self.set_size_request(500, 400)
        self.resize(500, 400)
        self._build_widgets()

    def show_window(self):
        """Show the current settings window."""
        self.show_all()

    def _build_widgets(self):
        """Build Settings Window widgets."""
        # HeaderBar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title(_("Settings"))
        self.set_titlebar(headerbar)
