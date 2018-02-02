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

from gettext import gettext as _
from ..const import AUDIO_MIMES
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject


class ActionBar(Gtk.ActionBar, GObject.GObject):
    """ActionBar widget."""
    # ToolBar Instance
    instance = None
    __gsignals__ = {
        'selected-format': (GObject.SignalFlags.RUN_FIRST, None, (str, ))
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        Gtk.ActionBar.__init__(self)
        self.set_border_width(12)
        self._save_btn = Gtk.Button()
        self._output_format = Gtk.ComboBox()
        self._setup_widgets()

    @staticmethod
    def get_default():
        """Return the default isntance on ActionBar."""
        if ActionBar.instance is None:
            ActionBar.instance = ActionBar()
        return ActionBar.instance

    def _setup_widgets(self):
        """Create/Setup the main widgets of the ActionBar."""
        # Save Button
        self._save_btn.set_label(_("Save"))
        self._save_btn.connect("clicked", self._on_save)
        self._save_btn.get_style_context().add_class("suggested-action")
        self._save_btn.set_sensitive(False)
        self.pack_end(self._save_btn)
        # Output format Combo box
        model = Gtk.ListStore(str, str)
        for mimetype, desc in AUDIO_MIMES.items():
            model.append([desc, mimetype])
        renderer_text = Gtk.CellRendererText()
        self._output_format.pack_start(renderer_text, True)
        self._output_format.add_attribute(renderer_text, "text", 0)
        self._output_format.set_active(0)
        self._output_format.set_model(model)
        self._output_format.set_sensitive(False)
        self.pack_end(self._output_format)

    def set_state(self, state):
        """Set the ActionBar as active/inactive."""
        self._save_btn.set_sensitive(state)
        self._output_format.set_sensitive(state)

    def _on_save(self, button):
        active_id = self._output_format.get_active()
        audio_mimes_keys = list(AUDIO_MIMES.keys())
        try:
            output_format = audio_mimes_keys[active_id]
        except KeyError:
            output_format = audio_mimes_keys[0]
        self.emit("selected-format", output_format)