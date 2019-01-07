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
from copy import copy


class Time:

    def __init__(self, hours, minutes, seconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __eq__(self, time):
        return (time.minutes == self.minutes and
                time.seconds == self.seconds and
                time.hours == self.hours)

    def copy(self):
        """Return a copy of the object."""
        return copy(self)

    def __ge__(self, time):
        return self.total > time.total

    def __le__(self, time):
        return self.total < time.total

    def __repr__(self):
        return("Hours: {} Minutes: {} Seconds: {}".format(self.hours,
                                                          self.minutes,
                                                          self.seconds))

    def up(self):
        seconds_ = self.seconds + 1
        if seconds_ >= 60:
            self.seconds = 0
            self.minutes += 1
            if self.minutes > 60:
                self.minutes = 0
                self.hours += 1
        else:
            self.seconds = seconds_

    def down(self):
        seconds_ = self.seconds - 1
        if seconds_ < 0:
            self.seconds = 0
            self.minutes -= 1
            if self.minutes < 0:
                self.minutes = 0
                self.hours -= 1
        elif seconds_ == 0:
            self.seconds = 59
            self.minutes -= 1
            if self.minutes < 0:
                self.minutes = 0
                self.hours -= 1
        else:
            self.seconds = seconds_

    @property
    def total(self):
        return self.hours * 3600 + self.minutes * 60 + self.seconds
