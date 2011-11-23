import gtk
gtk.gdk.threads_init()

import sys
import gobject

class Windowed(gtk.DrawingArea):
    def __init__(self):
        super(Windowed, self).__init__()

        self.w = gtk.Window(gtk.WINDOW_POPUP)
        self.w.set_decorated(False)
        self.w.show()

        def handle_move(*args, **kwargs):
            x,y = self.get_toplevel().window.get_position()
            print 'do_pos', [x, y]
            self.w.window.move(x, y)
        def handle_embed(*args, **kwargs):
            self.w.set_transient_for(self.get_toplevel())
            self.get_toplevel().connect('configure-event',
                                        handle_move)
            return True
        self.connect("map", handle_embed)

    def do_size_allocate(self, allocation):
        print 'do_size:', allocation
        self.w.resize(allocation.width, allocation.height)
        #if self.flags() & gtk.REALIZED:
        #super(Windowed, self).do_size_allocate(self, allocation)


gobject.type_register(Windowed)


class WindowsVLCWidget(Windowed):
    def __init__(self):
        super(WindowsVLCWidget, self).__init__()

        self._player = self.vlc_instance.media_player_new()
        self._player.set_hwnd(self.w.window.handle)

        self.set_size_request(320, 200)

    def play(self, file_path):
        self._player.set_media(self.vlc_instance.media_new(file_path))
        self._player.play()


class _WindowsVLCWidget(gtk.DrawingArea):
    def __init__(self):
        super(WindowsVLCWidget, self).__init__()

        self._player = self.vlc_instance.media_player_new()
        def handle_embed(*args):
            print 'overlay:', self.window.handle
            self._w = w = gtk.Window(gtk.WINDOW_POPUP)
            w.set_transient_for(self.get_toplevel())
            w.set_decorated(False)
            w.show()
            self._player.set_hwnd(w.window.handle)

            return True
        self.connect("map", handle_embed)


        self.set_size_request(320, 200)

    def play(self, file_path):
        self._player.set_media(self.vlc_instance.media_new(file_path))
        self._player.play()


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
