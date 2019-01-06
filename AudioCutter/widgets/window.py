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

from os import path
from gettext import gettext as _
from .actionbar import ActionBar
from .headerbar import HeaderBar
from .soundconfig import SoundConfig
from .zoombox import ZoomBox
from .notification import Notification
from .audio_graph import AudioGraph
from ..modules import Logger, Player, Settings, Exporter
from ..const import AUDIO_MIMES
from .loading import Loading

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class Window(Gtk.ApplicationWindow):
    """Main Window Object."""
    instance = None

    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect("delete-event", lambda x, y: self._on_close())
        self._main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._setup_window()
        self._setup_widgets()
        self._restore_state()
        Player.get_default().connect("playing", self._on_play)
        Player.get_default().connect("paused", self._on_paused)
        Player.get_default().connect("duration-changed", self._on_duration_changed)

    @staticmethod
    def get_default():
        """Return the dafault instance of Window."""
        if Window.instance is None:
            Window.instance = Window()
        return Window.instance

    def _setup_window(self):
        self.set_resizable(False)
        self.set_default_size(600, 300)

    def _setup_widgets(self):
        """Setup the main widgets."""
        # Main widget
        self.add(self._main)
        # Headerbar
        headerbar = HeaderBar.get_default()
        headerbar.connect("open-file", self._open_file)
        headerbar.play_btn.connect("clicked", self._play)
        # Set up the app menu in other DE than GNOME
        from ..application import Application
        app_menu = Application.get_default().app_menu
        menu_btn = headerbar.menu_btn
        popover = Gtk.Popover.new_from_model(menu_btn, app_menu)
        menu_btn.connect("clicked", self._toggle_popover, popover)
        self.set_titlebar(headerbar)

        # Action Bar
        actionbar = ActionBar.get_default()
        actionbar.connect("selected-format", self._on_export)
        self._main.pack_end(actionbar, False, False, 0)

        # Notification
        notification = Notification.get_default()
        self._main.pack_start(notification, False, False, 0)

        # Audio Graph
        self.main_stack = Gtk.Stack()

        self.audio_graph_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.audio_graph_box.get_style_context().add_class("audio-graph-container")
        self.zoombox = ZoomBox()

        overlay = Gtk.Overlay()
        overlay.add(self.audio_graph_box)
        overlay.add_overlay(self.zoombox)
        self.main_stack.add_named(overlay, "wave")

        loading = Loading()
        self.main_stack.add_named(loading, "loading")
        self._main.pack_start(self.main_stack, True, True, 0)

        # Config Box
        sound_config = SoundConfig.get_default()
        self._main.pack_end(sound_config, False, False, 0)

    def _on_play(self, player):
        HeaderBar.get_default().set_is_playing(True)

    def _on_paused(self, player):
        HeaderBar.get_default().set_is_playing(False)

    def _play(self, *args):
        player = Player.get_default()
        if player.is_playing:
            player.pause()
        else:
            player.play()

    def _open_file(self, *args):
        """Open an open file dialog to select an audio file."""
        dialog = Gtk.FileChooserNative(title=_("Please choose an audio file"),
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("Open"), Gtk.ResponseType.OK)
        dialog.set_transient_for(self)

        Window._add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            opened_file = dialog.get_filename()
            self._set_open_file(Gio.File.new_for_path(opened_file))
            Logger.debug("File Selected {}".format(opened_file))
        else:
            Logger.debug("Open file dialog closed without selecting a file.")
        dialog.destroy()

    @staticmethod
    def _add_filters(dialog):
        """Add audio filters to the open file dialog."""
        filters = Gtk.FileFilter()
        filters.set_name(_("Audio Files"))
        for mimetype in AUDIO_MIMES:
            filters.add_mime_type(mimetype)
        dialog.add_filter(filters)

    def _set_open_file(self, f):
        """Set a filename as opened."""
        player = Player.get_default()
        soundconfig = SoundConfig.get_default()
        self.main_stack.set_visible_child_name("loading")
        loading = self.main_stack.get_child_by_name("loading")
        loading.start()
        player.set_open_file(f)
        HeaderBar.get_default().set_audio_title(player.title)
        ActionBar.get_default().set_state(True)
        soundconfig.set_state(True)
        soundconfig.set_duration(player.duration)
        Settings.get_default().last_file = f.get_uri()

        audio_graph = AudioGraph(f.get_uri(), player.asset)
        for child in self.audio_graph_box.get_children():
            self.audio_graph_box.remove(child)
        self.audio_graph_box.pack_start(audio_graph, True, True, 0)
        audio_graph.connect("draw-done", self._on_waveform_ready)
        self.zoombox.zoom_up.connect("clicked", audio_graph.zoomIn)
        self.zoombox.zoom_down.connect("clicked", audio_graph.zoomOut)

    def _on_waveform_ready(self, *args):
        loading = self.main_stack.get_child_by_name("loading")
        loading.stop()
        self.main_stack.set_visible_child_name("wave")

    def _on_duration_changed(self, *args):
        sound_config = SoundConfig.get_default()
        sound_config.start_time.step_up()

    def _on_export(self, action_bar, audio_format):
        sound_config = SoundConfig.get_default()
        is_fade_in = sound_config.is_fade_in
        is_fade_out = sound_config.is_fade_out
        start_time = sound_config.start_time.time.total
        end_time = sound_config.end_time.time.total
        audio_path = Player.get_default().uri
        exporter = Exporter(start_time=start_time, end_time=end_time,
                            is_fade_in=is_fade_in, is_fade_out=is_fade_out,
                            path=audio_path, audio_format=audio_format)
        exporter.do()


    def _toggle_popover(self, button, popover):
        """Toggle the app menu popover."""
        if popover:
            if popover.get_visible():
                popover.hide()
            else:
                popover.show_all()

    def _restore_state(self):
        """Restore the latest position and opened file."""
        settings = Settings.get_default()
        pos_x, pos_y = settings.window_position
        if pos_x != 0 and pos_y != 0:
            self.move(pos_x, pos_y)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)

        last_file = Gio.File.new_for_uri(settings.last_file)
        if last_file and last_file.query_exists():
            self._set_open_file(last_file)

    def _on_close(self):
        """Window delete event handler."""
        # TODO: ask the user if he wants to save the current modification?
        # Save the latest window position
        Settings.get_default().window_position = self.get_position()
