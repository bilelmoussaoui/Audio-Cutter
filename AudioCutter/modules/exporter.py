


class Exporter:


    def __init__(self, *args, **kwargs):
        self._start_time = kwargs.get("start_time", 0)
        self._end_time = kwargs.get("end_time", 0)
        self._is_fade_in = kwargs.get("is_fade_in", False)
        self._is_fade_out = kwargs.get("is_fade_out", False)
        self._audio_format = kwargs.get("audio_format", "")
        self._audio_path = kwargs.get("path", "")

    def do(self):
        pass