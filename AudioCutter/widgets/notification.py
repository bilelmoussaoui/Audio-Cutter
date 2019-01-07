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

from gi.repository import Gtk

class Notification(Gtk.Revealer):
    instance = None
    def __init__(self):
        Gtk.Revealer.__init__(self)
        self._message = None
        self._message_label = Gtk.Label()
        self.set_reveal_child(False)
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self._build_widget()

    @property
    def message(self):
        """Return the message value:str."""
        return self._message

    @message.setter
    def message(self, new_msg):
        self._message = new_msg
        self._message_label.set_label(new_msg)
        self.set_reveal_child(True)


    @staticmethod
    def get_default():
        """Return the default instance of Notification."""
        if Notification.instance is None:
            Notification.instance = Notification()
        return Notification.instance


    def _build_widget(self):
        container = Gtk.InfoBar()
        container.set_show_close_button(True)
        container.get_content_area().pack_start(self._message_label, False,
                                                False, 0)
        container.connect("response", self._on_infobar_response)

        self.add(container)

    def _on_infobar_response(self, infobar, response_id):
        if response_id  == Gtk.ResponseType.CLOSE:
            self.set_reveal_child(False)
