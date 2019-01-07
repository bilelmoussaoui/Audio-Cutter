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
from gi.repository import Gio, GLib
from . import Logger


class Settings(Gio.Settings):
    """Gio.Settings handler."""
    # Default instance of Settings
    instance = None

    def __init__(self):
        Gio.Settings.__init__(self)

    def new():
        """Create a new instance of Gio.Settings."""
        gsettings = Gio.Settings.new("com.github.bilelmoussaoui.Authenticator")
        gsettings.__class__ = Settings
        return gsettings

    @staticmethod
    def get_default():
        """Return the default instance of Settings."""
        if Settings.instance is None:
            Settings.instance = Settings.new()
        return Settings.instance

    @property
    def window_position(self):
        """Return a tuple (x, y) for the window's latest position."""
        window_position = tuple(self.get_value('window-position'))
        Logger.debug("[Settings] Window position: "
                     "{}".format(list(window_position)))
        return window_position

    @window_position.setter
    def window_position(self, position):
        """Set the window position."""
        position = GLib.Variant('ai', list(position))
        Logger.debug("[Settings] Window position is set to: "
                     "{}".format(list(position)))
        self.set_value('window-position', position)

    @property
    def is_night_mode(self):
        """Return if the night mode is on or off."""
        is_night_mode = self.get_boolean('night-mode')
        Logger.debug("[Settings] Night mode: "
                     "{}".format(str(is_night_mode)))
        return is_night_mode

    @is_night_mode.setter
    def is_night_mode(self, status):
        """Switch the night mode."""
        Logger.debug("[Settings] Night mode is set to: "
                     "{}".format(str(status)))
        self.set_boolean('night-mode', status)

    @property
    def last_file(self):
        """Return the latest opened file path."""
        last_file = self.get_string('last-file')
        Logger.debug("[Settings] Last opened file: "
                     "{}".format(last_file))
        return last_file

    @last_file.setter
    def last_file(self, last_file):
        self.set_string('last-file', last_file)
        Logger.debug("[Settings] Last opened file is set to: "
                     "{}".format(last_file))
