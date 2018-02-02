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
import logging


class Logger:
    """Logging handler."""
    # Default instance of Logger
    instance = None
    # Message format
    FORMAT = "[%(levelname)-s] %(asctime)s %(message)s"
    # Date format
    DATE = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        logger = logging.getLogger('audio-cutter')
        handler = logging.StreamHandler()
        formater = logging.Formatter(Logger.FORMAT, Logger.DATE)
        handler.setFormatter(formater)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    @staticmethod
    def get_default():
        """Return the default instance of Logger."""
        if Logger.instance is None:
            Logger.instance = logging.getLogger("audio-cutter")
        return Logger.instance

    @staticmethod
    def warning(msg):
        """Log a warning message."""
        Logger.get_default().warning(msg)

    @staticmethod
    def debug(msg):
        """Log a debug message."""
        Logger.get_default().debug(msg)

    @staticmethod
    def info(msg):
        """Log an info message."""
        Logger.get_default().info(msg)

    @staticmethod
    def error(msg):
        """Log an error message."""
        Logger.get_default().error(msg)
