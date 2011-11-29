import gtk
gtk.gdk.threads_init()

import sys
import gobject
import os


class Windowed(gtk.DrawingArea):
    def __init__(self):
        super(Windowed, self).__init__()

        self.w = gtk.Window()
        self.w.set_decorated(False)
        self.w.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        self.w.show()

        def sync_move(*args, **kwargs):
            x,y = self.get_toplevel().window.get_position()
            o_x, o_y = gtk_translate_coordinates(self, self.get_toplevel(), 0, 0)
            print 'do_pos:', o_x, o_y
            self.w.window.move(x + o_x, y + 28)
        def sync_state(w, event, *args):
            print 'sync_state:', event.new_window_state
            if event.new_window_state == gtk.gdk.WINDOW_STATE_ICONIFIED:
                self.w.hide()
            else:
                self.w.show()

        def handle_embed(*args, **kwargs):
            self.w.set_transient_for(self.get_toplevel())
            self.get_toplevel().connect('configure-event',
                                        sync_move)
            self.get_toplevel().connect('window-state-event',
                                         sync_state)
            return True

        self.connect("map", handle_embed)

    def do_size_allocate(self, allocation):
        #print 'do_size:', allocation
        self.w.resize(allocation.width, allocation.height)
        #if self.flags() & gtk.REALIZED:
        #super(Windowed, self).do_size_allocate(self, allocation)


def gtk_translate_coordinates(widget, relative_widget, x, y):
    """ replacement for:
    self.translate_coordinates(self.get_toplevel(), -1, -1)
    """
    parent = widget
    while parent != relative_widget:
        x += parent.get_allocation()[0]
        y += parent.get_allocation()[1]
        parent = parent.get_parent()

    return (x, y)


class WindowsVLCWidget(Windowed):
    __gsignals__ = {
        'play-started': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-paused': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-ended': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-stopped': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self):
        super(WindowsVLCWidget, self).__init__()

        self._player = self.vlc_instance.media_player_new()
        self._player.set_hwnd(self.w.window.handle)

        self.set_size_request(320, 200)
        gobject.timeout_add(1000, self._play_status)

    def play(self, file_path):
        self._player.set_media(self.vlc_instance.media_new(
                file_path,
                'sub-filter=marq', #'vout=caca'
                ))

        self._player.play()
        _, file_name = os.path.split(file_path)

        self.set_text(file_name)

        self.emit('play-started')

    def set_text(self, text, **kwargs):
        self._player.video_set_marquee_string(vlc.VideoMarqueeOption.Text, text)
        self._player.video_set_marquee_int(vlc.VideoMarqueeOption.Timeout,
                                           kwargs.get('timeout', 3000))
        self._player.video_set_marquee_int(vlc.VideoMarqueeOption.Position,
                                           kwargs.get('position', 8))

    def toggle_pause(self, *args):
        if self._player.get_state() == vlc.State.Paused:
            self._player.play()
            self.set_text('PLAY', position=5, timeout=2000)
            self.emit('play-started')
        else:
            self._player.pause()
            self.set_text('PAUSED', position=5, timeout=0)
            self.emit('play-paused')

    def stop(self, *args):
        self._player.stop()
        self.emit('play-stopped')

    def jump_relative(self, relative, *args):
        print 'jump_relative:', relative
        new_time = self.get_time() + relative
        if new_time <= 0:
            new_time = 0
        elif new_time >= self.get_length():
            new_time = self.get_length()
        self._player.set_time(new_time*1000)
        self.set_text('%s / %s' % (format_duration(new_time),
                                   format_duration(self.get_length())))
        print ('new_play_status: pos=%s/%s, st=%s'
               % (self.get_time(), self.get_length(), self._player.get_state()))

    def set_volume(self, relative, *args):
        pass

    def get_length(self):
        """ total play duration, in seconds """
        return int(self._player.get_length()/1000)

    def get_time(self):
        """ current play pos in seconds """
        return int(self._player.get_time()/1000)

    def _play_status(self, *args):
        #print ('play_status: pos=%s/%s, st=%s'
        #       % (self.get_time(), self.get_length(), self._player.get_state()))
        if self._player.get_state() == vlc.State.Ended:
            self.emit('play-ended')
        return True # enble repetation

    def fullscreen(self, *args):
        self.w.fullscreen()

    def unfullscreen(self, *args):
        self.w.unfullscreen()


class FakeWidget(Windowed):
    __gsignals__ = {
        'play-started': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-paused': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-ended': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'play-stopped': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__(self):
        super(FakeWidget, self).__init__()
        self.label = gtk.Label()
        self.label.set_size_request(320, 200)
        self.w.add(self.label)
        self.label.show()

        self.set_size_request(320, 200)

    def play(self, file_path):
        self.label.set_text(file_path)

    def toggle_pause(self, *args):
        pass

    def stop(self, *args):
        pass

    def jump_relative(self, relative, *args):
        print 'jump_relative:', relative
        pass

    def fullscreen(self, *args):
        self.w.fullscreen()

    def unfullscreen(self, *args):
        self.w.unfullscreen()


def format_duration(seconds):
    hours = int(seconds/ 3600)
    seconds = seconds - hours * 3600
    minutes = int(seconds/60)
    seconds = seconds - minutes*60

    s = ''
    if hours:
        s += '%sh ' % hours
    if minutes:
        s += '%smin ' % minutes
    s += '%ssec' % seconds
    return s


if sys.platform == 'win32':
    VLCWidget = WindowsVLCWidget

    import vlc
    WindowsVLCWidget.vlc_instance = vlc.Instance()
else:
    VLCWidget = FakeWidget

gobject.type_register(VLCWidget)
