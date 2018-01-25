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
from .objects import Time
from hashlib import sha256
from os import path, makedirs
from gi.repository import GLib


def show_app_menu():
    """Return if we should use the app_menu or use a popover."""
    return "gnome" in GLib.getenv("XDG_CURRENT_DESKTOP").lower()

def get_wavefile_location_for_uri(uri):
    filename = sha256(uri.encode("utf-8")).hexdigest()
    cachedir = path.join(GLib.get_user_cache_dir(), "AudioCutter")
    if not path.exists(cachedir):
        makedirs(cachedir)
    return path.join(cachedir, filename)



def format_ns(nanoseconds):
    """
    Convert nano seconds to a Time object.
    Original code:
    https://github.com/gkralik/python-gst-tutorial/blob/master/helper.py
    """
    seconds, nanoseconds = divmod(nanoseconds, 1000000000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return Time(hours, minutes, seconds)
