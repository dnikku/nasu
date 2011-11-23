import gtk
gtk.gdk.threads_init()

import sys
from gettext import gettext as _


class WindowsVLCWidget(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self._player = self.vlc_instance.media_player_new()
        def handle_embed(*args):
            self.player.set_hwnd(self.window.handle)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(320, 200)

    def play(self, file_path):
        pass


class FakeWidget(gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self)
        self.set_size_request(320, 200)

    def play(self, file_path):
        self.set_text(file_path)

if sys.platform == 'win32':
    VLCWidget = WindowsVLCWidget

    import vlc
    WindowsVLCWidget.vlc_instance = vlc.Instance()
else:
    VLCWidget = FakeWidget
