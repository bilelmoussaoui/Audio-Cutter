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
from .log import Logger
from ..utils import format_ns

from gi import require_version
require_version('Gst', '1.0')
require_version('GstPbutils', '1.0')
require_version('GES', '1.0')
from gi.repository import GLib, GObject, Gst, GstPbutils, GES

class Player(GObject.GObject):
    """GStreamer player object."""

    __gsignals__ = {
        'playing': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'duration-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'paused': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    # Player's instance
    instance = None

    def __init__(self):
        GObject.GObject.__init__(self)
        GstPbutils.pb_utils_init()
        self._discoverer = GstPbutils.Discoverer.new(10 * Gst.SECOND)

        self.is_playing = False
        self.filepath = None
        self._duration = Gst.CLOCK_TIME_NONE
        self.asset = None

        self._playbin = Gst.ElementFactory.make("playbin", "player")
        bus = self._playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message::error", self.__on_bus_error)
        bus.connect("message::eos", self.__on_bus_eos)
        bus.connect("message::element", self.__on_bus_element)
        bus.connect("message::stream-start", self._on_stream_start)

    @staticmethod
    def get_default():
        """Return default player instance."""
        if Player.instance is None:
            Player.instance = Player()
        return Player.instance

    def play(self, *args):
        """Play the current audio file."""
        def on_duration_changed():
            self.emit("duration-changed")
            return self.is_playing
        if self.is_playing:
            # Stop the current audio file from playing
            self.stop()
        self._playbin.set_state(Gst.State.PLAYING)
        self.is_playing = True
        self.emit("playing")
        GLib.timeout_add_seconds(1, on_duration_changed)

    def pause(self, *args):
        """Pause the audio player."""
        self._playbin.set_state(Gst.State.PAUSED)
        self.is_playing = False
        self.emit("paused")

    def stop(self, *args):
        """Stop the audio Player."""
        self.is_playing = False
        self.emit("paused")
        self._playbin.set_state(Gst.State.NULL)

    def set_open_file(self, filepath):
        """Set the current open file."""
        self.filepath = filepath
        self.asset = GES.UriClipAsset.request_sync(self.filepath.get_uri())
        self.stop()
        self._playbin.set_property('uri', self.filepath.get_uri())

    @property
    def duration(self):
        """Return the current file duration."""
        if self.asset:
            return self.asset.get_duration()
        return None

    @property
    def title(self):
        if self.asset:
            tags = self.asset.get_info().get_tags()
            if tags:
                (exists, title) = tags.get_string_index("title", 0)
                if exists and title.strip():
                    return title
        return GLib.path_get_basename(self.filepath.get_path())

    @property
    def uri(self):
        return self.filepath.get_uri()

    def __on_bus_eos(self, *args):
        """End of stream handler."""
        Logger.debug("[Player] End of stream reacher")
        self.stop()

    def __on_bus_element(self, bus, message):
        print("element {} {}".format(bus, message))

    def __on_bus_error(self, bus, message):
        error = message.parse_error()[0].message
        Logger.error("[Player] Stream Error: {}".format(error))
        self.stop()

    def _on_stream_start(self, *args):
        Logger.debug("[Player] Stream started")
