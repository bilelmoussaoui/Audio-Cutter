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
import numpy
import cairo
from os import path
from gi import require_version
require_version("Gtk", "3.0")
require_version("GES", "1.0")
from gi.repository import Gst, Gtk, GES, GObject, GLib, Gdk

from ..modules import Player
from ..utils import get_wavefile_location_for_uri
import renderer


SAMPLE_DURATION = Gst.SECOND / 100
MARGIN = 500


class Zoomable(object):
    """Base class for conversions between timeline timestamps and UI pixels.
    Complex Timeline interfaces v2 (01 Jul 2008)
    Zoomable
    -----------------------
    Interface for the Complex Timeline widgets for setting, getting,
    distributing and modifying the zoom ratio and the size of the widget.
    A zoomratio is the number of pixels per second
    ex : 10.0 = 10 pixels for a second
    ex : 0.1 = 1 pixel for 10 seconds
    ex : 1.0 = 1 pixel for a second
     Class Methods
    . pixelToNs(pixels)
    . nsToPixels(time)
    . setZoomRatio
    Instance Methods
    . zoomChanged()
    """

    sigid = None
    _instances = []
    max_zoom = 1000.0
    min_zoom = 0.25
    zoom_steps = 100
    zoom_range = max_zoom - min_zoom
    _cur_zoom = 20
    zoomratio = None


    def __init__(self):
        # FIXME: ideally we should deprecate this
        Zoomable.addInstance(self)
        if Zoomable.zoomratio is None:
            Zoomable.zoomratio = self.computeZoomRatio(self._cur_zoom)

    def __del__(self):
        if self in Zoomable._instances:
            # FIXME: ideally we should deprecate this and spit a warning here
            self._instances.remove(self)

    @classmethod
    def addInstance(cls, instance):
        cls._instances.append(instance)

    @classmethod
    def removeInstance(cls, instance):
        cls._instances.remove(instance)

    @classmethod
    def setZoomRatio(cls, ratio):
        ratio = min(max(cls.min_zoom, ratio), cls.max_zoom)
        if cls.zoomratio != ratio:
            cls.zoomratio = ratio
            for inst in cls._instances:
                inst.zoomChanged()

    @classmethod
    def setZoomLevel(cls, level):
        level = int(max(0, min(level, cls.zoom_steps)))
        if level != cls._cur_zoom:
            cls._cur_zoom = level
            cls.setZoomRatio(cls.computeZoomRatio(level))

    @classmethod
    def getCurrentZoomLevel(cls):
        return cls._cur_zoom

    @classmethod
    def zoomIn(cls,  *args):
        cls.setZoomLevel(cls._cur_zoom + 1)

    @classmethod
    def zoomOut(cls, *args):
        cls.setZoomLevel(cls._cur_zoom - 1)

    @classmethod
    def computeZoomRatio(cls, x):
        return ((((float(x) / cls.zoom_steps) ** 3) * cls.zoom_range) +
                cls.min_zoom)

    @classmethod
    def computeZoomLevel(cls, ratio):
        return int((
            (max(0, ratio - cls.min_zoom) /
                cls.zoom_range) ** (1.0 / 3.0)) * cls.zoom_steps)

    @classmethod
    def pixelToNs(cls, pixel):
        """Returns the duration equivalent of the specified pixel."""
        return int(pixel * Gst.SECOND / cls.zoomratio)

    @classmethod
    def pixelToNsAt(cls, pixel, ratio):
        """Returns the duration equivalent of the specified pixel."""
        return int(pixel * Gst.SECOND / ratio)

    @classmethod
    def nsToPixel(cls, duration):
        """Returns the pixel equivalent of the specified duration"""
        # Here, a long time ago (206f3a05), a pissed programmer said:
        # DIE YOU CUNTMUNCH CLOCK_TIME_NONE UBER STUPIDITY OF CRACK BINDINGS !!
        if duration == Gst.CLOCK_TIME_NONE:
            return 0
        return int((float(duration) / Gst.SECOND) * cls.zoomratio)

    @classmethod
    def nsToPixelAccurate(cls, duration):
        """Returns the pixel equivalent of the specified duration."""
        # Here, a long time ago (206f3a05), a pissed programmer said:
        # DIE YOU CUNTMUNCH CLOCK_TIME_NONE UBER STUPIDITY OF CRACK BINDINGS !!
        if duration == Gst.CLOCK_TIME_NONE:
            return 0
        return ((float(duration) / Gst.SECOND) * cls.zoomratio)

    def zoomChanged(self):
        pass

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


class AudioGraph(Gtk.Layout, Zoomable):
    """The graph of the audio."""

    __gsignals__ = {
        'draw-done': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, uri, asset):
        GObject.GObject.__init__(self)
        Gtk.Layout.__init__(self)
        Zoomable.__init__(self)

        self._asset = asset
        self._uri = uri
        self.wavefile = None
        self.pipeline = None
        self._wavebin = None
        self.n_samples = asset.get_duration() / SAMPLE_DURATION
        self.samples = None
        self._force_redraw = True
        self.peaks = None
        self.discovered = False
        self._start = 0
        self._end = 0
        self._surface_x = 0
        self._start_levels_discovery()
        self.connect("notify::height-request", self._height_changed_cb)
        self.show_all()


    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def _launch_pipeline(self):
        self.pipeline = Gst.parse_launch("uridecodebin name=decode uri=" +
                                         self._uri + " ! waveformbin name=wave"
                                         " ! fakesink qos=false name=faked")

        Gst.ElementFactory.make("uritranscodebin", None)

        clock = GObject.new(GObject.type_from_name("GstCpuThrottlingClock"))
        clock.props.cpu_usage = 90
        self.pipeline.use_clock(clock)

        faked = self.pipeline.get_by_name("faked")
        faked.props.sync = True
        self._wavebin = self.pipeline.get_by_name("wave")

        self._wavebin.props.uri = self._asset.get_id()
        self._wavebin.props.duration = self._asset.get_duration()
        decode = self.pipeline.get_by_name("decode")
        decode.connect("autoplug-select", self._autoplug_select_cb)
        bus = self.pipeline.get_bus()
        self.pipeline.set_state(Gst.State.PLAYING)
        bus.add_signal_watch()
        self.n_samples = self._asset.get_duration() / SAMPLE_DURATION
        bus.connect("message::error", self.__on_bus_error)
        bus.connect("message::eos", self.__on_bus_eos)

    def __disconnect_bus(self):
        bus = self.pipeline.get_bus()
        if bus:
            bus.disconnect_by_func(self.__on_bus_eos)
            bus.disconnect_by_func(self.__on_bus_error)

    def __on_bus_eos(self, bus, message):
        """On End of stream signal."""
        self._prepare_samples()
        self._start_rendering()
        self.stop_generation()
    
    def __on_bus_error(self, bus, message):
        """On error signal."""
        self.stop_generation()
        self._num_failures += 1
        if self._num_failures < 2:
            self.__disconnect_bus()
            self._launch_pipeline()
        elif self.pipeline:
            Gst.debug_bin_to_dot_file_with_ts(self.pipeline,
                                              Gst.DebugGraphDetails.ALL,
                                              "error-generating-waveforms")

    def _height_changed_cb(self, *args):
        self._force_redraw = True
        self.queue_draw()

    def _autoplug_select_cb(self, unused_decode, unused_pad, unused_caps, factory):
        # Don't plug video decoders / parsers.
        if "Video" in factory.get_klass():
            return True
        return False

    def _prepare_samples(self):
        self._wavebin.finalize()
        self.samples = self._wavebin.samples

    def _start_rendering(self):
        self.n_samples = len(self.samples)
        self.discovered = True
        self.queue_draw()
        self.emit("draw-done")

    def start_generation(self):
        self._start_levels_discovery()
        if not self.pipeline:
            # No need to generate as we loaded pre-generated .wave file.
            return
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop_generation(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            self.__disconnect_bus()
            self.pipeline = None

    def zoomChanged(self):
        self._force_redraw = True
        self.queue_draw()

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
            surface_width = min(self.get_parent().get_allocation().width - clipped_rect.x,
                                clipped_rect.width + MARGIN)
            surface_height = int(self.get_parent().get_allocation().height)
            self.surface = renderer.fill_surface(self.samples[start:end],
                                                 surface_width,
                                                 surface_height)

            self._force_redraw = False

        context.set_operator(cairo.OPERATOR_OVER)
        context.set_source_surface(self.surface, self._surface_x, 0)
        context.paint()

    def _get_num_inpoint_samples(self):
        asset_duration = self._asset.get_duration()
        # TODO: replace 1 with in-points
        return int(self.n_samples / (float(asset_duration)) / 1)

    def _start_levels_discovery(self, *args):
        # Get the wavefile location
        filename = get_wavefile_location_for_uri(self._uri)
        if path.exists(filename):
            # If the wavefile exists, use it to draw the waveform
            with open(filename, "rb") as samples:
                self.samples = list(numpy.load(samples))
            self._start_rendering()
        else:
            # Otherwise launch the pipeline
            self.wavefile = filename
            self._launch_pipeline()
