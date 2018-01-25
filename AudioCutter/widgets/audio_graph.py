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
import numpy
from os import path
from gi import require_version
require_version("Gtk", "3.0")
require_version("GES", "1.0")
from gi.repository import Gst, Gtk, GES, GObject, GLib

from ..modules import Player
from ..utils import get_wavefile_location_for_uri


SAMPLE_DURATION = Gst.SECOND / 100


class PreviewerBin(Gst.Bin):
    """Baseclass for elements gathering datas to create previews."""

    def __init__(self, bin_desc):
        Gst.Bin.__init__(self)

        self.internal_bin = Gst.parse_bin_from_description(bin_desc, True)
        self.add(self.internal_bin)
        self.add_pad(Gst.GhostPad.new(None, self.internal_bin.sinkpads[0]))
        self.add_pad(Gst.GhostPad.new(None, self.internal_bin.srcpads[0]))

    def finalize(self, proxy=None):
        """Finalizes the previewer, saving data to the disk if needed."""
        pass


class WaveformPreviewer(PreviewerBin):
    """Bin to generate and save waveforms as a .npy file."""

    __gproperties__ = {
        "uri": (str,
                "uri of the media file",
                "A URI",
                "",
                GObject.ParamFlags.READWRITE),
        "duration": (GObject.TYPE_UINT64,
                     "Duration",
                     "Duration",
                     0, GLib.MAXUINT64 - 1, 0, GObject.ParamFlags.READWRITE)
    }

    def __init__(self):
        PreviewerBin.__init__(self,
                              "audioconvert ! audioresample ! "
                              "audio/x-raw,channels=1 ! level name=level"
                              " ! audioconvert ! audioresample")
        self.level = self.internal_bin.get_by_name("level")
        self.peaks = None

        self.uri = None
        self.wavefile = None
        self.passthrough = False
        self.samples = []
        self.n_samples = 0
        self.duration = 0
        self.prev_pos = 0

    def do_get_property(self, prop):

        if prop.name == 'uri':
            return self.uri
        elif prop.name == 'duration':
            return self.duration
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == 'uri':
            self.uri = value
            self.wavefile = get_wavefile_location_for_uri(self.uri)
            self.passthrough = path.exists(self.wavefile)
        elif prop.name == 'duration':
            self.duration = value
            self.n_samples = self.duration / SAMPLE_DURATION
        else:
            raise AttributeError('unknown property %s' % prop.name)

    # pylint: disable=arguments-differ
    def do_post_message(self, message):
        if not self.passthrough and \
                message.type == Gst.MessageType.ELEMENT and \
                message.src == self.level:
            struct = message.get_structure()
            peaks = None
            if struct:
                peaks = struct.get_value("rms")

            if peaks:
                stream_time = struct.get_value("stream-time")

                if self.peaks is None:
                    self.peaks = []
                    for unused_channel in peaks:
                        self.peaks.append([0] * int(self.n_samples))

                pos = int(stream_time / SAMPLE_DURATION)
                if pos >= len(self.peaks[0]):
                    return

                for i, val in enumerate(peaks):
                    if val < 0:
                        val = 10 ** (val / 20) * 100
                    else:
                        val = self.peaks[i][pos - 1]

                    # Linearly joins values between to known samples values.
                    unknowns = range(self.prev_pos + 1, pos)
                    if unknowns:
                        prev_val = self.peaks[i][self.prev_pos]
                        linear_const = (val - prev_val) / len(unknowns)
                        for temppos in unknowns:
                            self.peaks[i][temppos] = self.peaks[i][temppos -
                                                                   1] + linear_const

                    self.peaks[i][pos] = val

                self.prev_pos = pos

        return Gst.Bin.do_post_message(self, message)

    def finalize(self):
        """Finalizes the previewer, saving data to file if needed."""
        if not self.passthrough and self.peaks:
            # Let's go mono.
            if len(self.peaks) > 1:
                samples = (numpy.array(
                    self.peaks[0]) + numpy.array(self.peaks[1])) / 2
            else:
                samples = numpy.array(self.peaks[0])

            self.samples = list(samples)
            with open(self.wavefile, 'wb') as wavefile:
                numpy.save(wavefile, samples)


Gst.Element.register(None, "waveformbin", Gst.Rank.NONE, WaveformPreviewer)


class AudioGraph(Gtk.Layout):
    """The graph of the audio."""
    instance = None
    __gsignals__ = {
        'file-selected': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        Gtk.Layout.__init__(self)
        self.connect("file-selected", self._on_file_selected)
        self.pipeline = None
        self._wavebin = None
        self.n_samples = 0
        self.samples = None
        self.peaks = None
        self.discovered = False
        self._start = 0
        self._end = 0
        self._surface_x = 0
        self.show_all()

    @staticmethod
    def get_default():
        if AudioGraph.instance is None:
            AudioGraph.instance = AudioGraph()
        return AudioGraph.instance

    def _on_file_selected(self, *args):
        self.n_samples = Player.get_default().duration.total / SAMPLE_DURATION
        self._startLevelsDiscovery()

    def _launchPipeline(self):
        uri = Player.get_default().uri
        self.pipeline = Gst.parse_launch("uridecodebin name=decode uri=" +
                                         uri + " ! waveformbin name=wave"
                                         " ! fakesink qos=false name=faked")

        Gst.ElementFactory.make("uritranscodebin", None)
        faked = self.pipeline.get_by_name("faked")
        faked.props.sync = True
        self._wavebin = self.pipeline.get_by_name("wave")

        self._wavebin.props.uri = uri
        self._wavebin.props.duration = Player.get_default().duration.total
        decode = self.pipeline.get_by_name("decode")
        decode.connect("autoplug-select", self._autoplug_select_cb)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self.__on_bus_eos)

    def __on_bus_eos(self, *args):
        self._prepareSamples()
        self._startRendering()
        self.stop_generation()

    def _bus_message_cb(self, bus, message):

        if message.type == Gst.MessageType.ERROR:
            if self.adapter:
                self.adapter.stop()
                self.adapter = None
            # Something went wrong TODO : recover
            self.stop_generation()
            self._num_failures += 1
            if self._num_failures < 2:
                bus.disconnect_by_func(self._busMessageCb)
                self._launchPipeline()
                self.become_controlled()
            else:
                if self.pipeline:
                    Gst.debug_bin_to_dot_file_with_ts(self.pipeline,
                                                      Gst.DebugGraphDetails.ALL,
                                                      "error-generating-waveforms")

    def _autoplug_select_cb(self, unused_decode, unused_pad, unused_caps, factory):
        # Don't plug video decoders / parsers.
        if "Video" in factory.get_klass():
            return True
        return False

    def _prepareSamples(self):
        self._wavebin.finalize()
        self.samples = self._wavebin.samples

    def _startRendering(self):
        self.n_samples = len(self.samples)
        self.discovered = True
        if self.adapter:
            self.adapter.stop()
        self.queue_draw()

    def _emit_done_on_idle(self):
        self.emit("done")

    def start_generation(self):
        self._startLevelsDiscovery()
        if not self.pipeline:
            # No need to generate as we loaded pre-generated .wave file.
            GLib.idle_add(self._emit_done_on_idle, priority=GLib.PRIORITY_LOW)
            return

        self.pipeline.set_state(Gst.State.PLAYING)
        if self.adapter is not None:
            self.adapter.start()

    def stop_generation(self):
        if self.adapter is not None:
            self.adapter.stop()
            self.adapter = None

        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline.get_bus().disconnect_by_func(self._busMessageCb)
            self.pipeline = None

    def do_draw(self, context):
        if not self.discovered:
            return

        clipped_rect = Gdk.cairo_get_clip_rectangle(context)[1]

        num_inpoint_samples = self._get_num_inpoint_samples()
        drawn_start = self.pixelToNs(clipped_rect.x)
        drawn_duration = self.pixelToNs(clipped_rect.width)
        start = int(drawn_start / SAMPLE_DURATION) + num_inpoint_samples
        end = int((drawn_start + drawn_duration) /
                  SAMPLE_DURATION) + num_inpoint_samples

        if self._force_redraw or self._surface_x > clipped_rect.x or self._end < end:
            self._start = start
            end = int(min(self.n_samples, end + (self.pixelToNs(MARGIN) /
                                                 SAMPLE_DURATION)))
            self._end = end
            self._surface_x = clipped_rect.x
            surface_width = min(self.props.width_request - clipped_rect.x,
                                clipped_rect.width + MARGIN)
            surface_height = int(self.get_parent().get_allocation().height)
            self.surface = renderer.fill_surface(self.samples[start:end],
                                                 surface_width,
                                                 surface_height)

            self._force_redraw = False

        context.set_operator(cairo.OPERATOR_OVER)
        context.set_source_surface(self.surface, self._surface_x, 0)
        context.paint()

    def _startLevelsDiscovery(self):
        uri = Player.get_default().uri
        filename = get_wavefile_location_for_uri(uri)

        if path.exists(filename):
            with open(filename, "rb") as samples:
                self.samples = list(numpy.load(samples))
            self._startRendering()
        else:
            self.wavefile = filename
        self._launchPipeline()
