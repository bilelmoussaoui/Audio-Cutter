from gi import require_version
require_version("Gtk", "3.0")

from gi.repository import Gtk

class Notification(Gtk.Revealer):
    instance = None
    def __init__(self):
        Gtk.Revealer.__init__(self)
        self._message = None
        self._message_label = Gtk.Label()
        self.set_reveal_child(False)
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self._build_widget()

    @property
    def message(self):
        """Return the message value:str."""
        return self._message

    @message.setter
    def message(self, new_msg):
        self._message = new_msg
        self._message_label.set_label(new_msg)
        self.set_reveal_child(True)


    @staticmethod
    def get_default():
        """Return the default instance of Notification."""
        if Notification.instance is None:
            Notification.instance = Notification()
        return Notification.instance


    def _build_widget(self):
        container = Gtk.InfoBar()
        container.set_show_close_button(True)
        container.get_content_area().pack_start(self._message_label, False,
                                                False, 0)
        container.connect("response", self._on_infobar_response)

        self.add(container)

    def _on_infobar_response(self, infobar, response_id):
        if response_id  == Gtk.ResponseType.CLOSE:
            self.set_reveal_child(False)
