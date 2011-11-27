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
            #print 'do_pos', [x, y]
            self.w.window.move(x, y)
        def handle_embed(*args, **kwargs):
            self.w.set_transient_for(self.get_toplevel())
            self.get_toplevel().connect('configure-event',
                                        handle_move)
            return True
        self.connect("map", handle_embed)

        def update_state(w, event, *args):
            print 'update_state:', event.new_window_state
            self.is_fullscreen = (event.new_window_state == gtk.gdk.WINDOW_STATE_FULLSCREEN)
        self.w.connect('window-state-event', update_state)

    def do_size_allocate(self, allocation):
        #print 'do_size:', allocation
        self.w.resize(allocation.width, allocation.height)
        #if self.flags() & gtk.REALIZED:
        #super(Windowed, self).do_size_allocate(self, allocation)



class WindowsVLCWidget(Windowed):
    __gsignals__ = {
        'play-started': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-stopped': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self):
        super(WindowsVLCWidget, self).__init__()

        self._player = self.vlc_instance.media_player_new()
        self._player.set_hwnd(self.w.window.handle)

        self.set_size_request(320, 200)
        #gobject.timeout_add(1000, self._play_status)

    def play(self, file_path):
        self._player.set_media(self.vlc_instance.media_new(file_path))
        self._player.play()

        self.emit('play-started')

    def get_length(self):
        """ total play duration, in seconds """
        return int(self._player.get_length()/1000)

    def get_time(self):
        """ current play pos in seconds """
        return int(self._player.get_time()/1000)

    def _play_status(self, *args):
        print 'play_status: ', self.get_length(), self.get_time()
        return True # enble repetation

    def toggle_fullscreen(self, *args):
        is_fullscreen =  getattr(self, 'is_fullscreen', None)
        print 'is_full:', is_fullscreen
        if is_fullscreen:
            self.w.unfullscreen()
        else:
            self.w.fullscreen()


class FakeWidget(gtk.Label):
    __gsignals__ = {
        'play-started': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-stopped': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

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

gobject.type_register(VLCWidget)
