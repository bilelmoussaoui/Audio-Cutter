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

from ..objects import Time

from .notification import Notification

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


class TimeButton(Gtk.Box):
    """A Time widget. used for start/end time."""

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self._entry = Gtk.Entry()
        self._up_btn = Gtk.Button()
        self._lower_btn = Gtk.Button()
        self._duration = Time(0, 0, 0)
        self.time = Time(0, 0, 0)
        self._setup_widgets()

    def _setup_widgets(self):
        """Create the Time Button widgets."""
        # Time entry
        self._entry.set_max_length(8)
        self._entry.set_width_chars(8)
        self._entry.connect("changed", self._on_type)
        self._entry.set_max_width_chars(8)

        # Up btn
        up_icn = Gio.ThemedIcon(name="list-add-symbolic")
        up_img = Gtk.Image.new_from_gicon(up_icn, Gtk.IconSize.BUTTON)
        self._up_btn.set_image(up_img)
        self._up_btn.connect("clicked", self.step_up)
        self._up_btn.get_style_context().add_class("flat")

        # Lower btn
        lower_icn = Gio.ThemedIcon(name="list-remove-symbolic")
        lower_img = Gtk.Image.new_from_gicon(lower_icn, Gtk.IconSize.BUTTON)
        self._lower_btn.set_image(lower_img)
        self._lower_btn.connect("clicked", self.step_down)
        self._lower_btn.get_style_context().add_class("flat")

        self.pack_start(self._entry, False, False, 0)
        self.pack_start(self._lower_btn, False, False, 0)
        self.pack_start(self._up_btn, False, False, 0)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        """
            Set the max duration based on the Time object.
            The time object (player.duration)
        """
        self._duration = duration.copy()
        self.__redraw()

    def step_down(self, *args):
        self.time.down()
        if self.time.total < 0:
            time = Time(0, 0, 0)
        else:
            time = self.time
        self.time = time

    def step_up(self, *args):
        self.time.up()
        if self.time.total >= self.duration.total:
            time = self.duration.copy()
        else:
            time = self.time
        self.time = time

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time.copy()
        self.__redraw()

    def __redraw(self):
        if self.duration and self._time.total >= self.duration.total:
            self._up_btn.set_sensitive(False)
        else:
            self._up_btn.set_sensitive(True)
        if self._time.total <= 0:
            self._lower_btn.set_sensitive(False)
        else:
            self._lower_btn.set_sensitive(True)
        label = "{0:02d}:{1:02d}:{2:02d}".format(self._time.hours,
                                                 self._time.minutes,
                                                 self._time.seconds)
        self._entry.set_text(label)

    def _on_type(self, entry):
        song_time = entry.get_text().strip().split(":")
        # Make sure we have got hh:mm:ss
        message = None
        if len(song_time) == 3:
            try:
                hours, minutes, seconds = list(map(int, song_time))
                if hours > 24:
                    message = _("Hours should be less than 24")
                elif minutes > 60:
                    message = _("Minutes must be less than 60")
                elif seconds > 60:
                    message = _("Seconds must be less than 60")
            except (TypeError, ValueError):
                message = _("Invalid time format, please follow hh:mm:ss")
        else:
            message = _("Invalid time format, please follow hh:mm:ss")
        if message:
            Notification.get_default().message = message
            entry.get_style_context().add_class("entry-error")
        else:
            entry.get_style_context().remove_class("entry-error")
