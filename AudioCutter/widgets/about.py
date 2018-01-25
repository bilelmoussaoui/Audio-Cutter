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


class AboutDialog(Gtk.AboutDialog):
    """About Dialog widget."""

    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        self.set_modal(True)
        self._setup_widget()

    def _setup_widget(self):
        """Setup the about dialog widget."""
        self.set_authors(["Bilal Elmoussaoui"])
        self.set_artists(["Alfredo Hernández"])
        self.set_logo_icon_name("org.gnome.AudioCutter")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_program_name(_("Audio Cutter"))
        self.set_translator_credits(_("translator-credits"))
        self.set_version("0.1")
        self.set_comments(_("Cut your audio files like no one does"))
        self.set_website("https://github.com/bil-elmoussaoui/Audio-Cutter")
