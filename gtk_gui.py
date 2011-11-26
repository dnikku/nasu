# check: http://stackoverflow.com/questions/249283/virtualenv-on-ubuntu-with-no-site-packages
import gtk
from gtk_vlcplayer import VLCWidget


class MainForm(object):
    config = {
        'normal': 'black',
        'active': 'red'
        }

    def __init__(self):
        self.master = master = gtk.Window()
        master.set_title("nasu ~")
        master.set_position(gtk.WIN_POS_CENTER)
        master.connect("destroy", gtk.main_quit)

        # accelerator
        self.accelgroup = gtk.AccelGroup()
        master.add_accel_group(self.accelgroup)
        self.actiongroup = gtk.ActionGroup('')

        # Create a MenuBar
        menubar = gtk.MenuBar()
        media_action = gtk.Action('Media', 'Media', None, None)
        self.actiongroup.add_action(media_action)
        media_menuitem = media_action.create_menu_item()
        menubar.append(media_menuitem)
        media_menu = gtk.Menu()
        media_menuitem.set_submenu(media_menu)
        media_menu.append(self.create_menu_item('Add to list', 'a', self.do_somth))
        media_menu.append(self.create_menu_item('Remove from list', 'r', self.do_somth))
        media_menu.append(self.create_menu_item('Load list from file', 's', self.do_somth))
        media_menu.append(self.create_menu_item('Save list to file', 's', self.do_somth))
        media_menu.append(self.create_menu_item('Exit', '<Control>x', gtk.main_quit))

        playback_action = gtk.Action('Playback', 'Playback', None, None)
        self.actiongroup.add_action(playback_action)
        playback_menuitem = playback_action.create_menu_item()
        menubar.append(playback_menuitem)
        playback_menu = gtk.Menu()
        playback_menuitem.set_submenu(playback_menu)
        playback_menu.append(self.create_menu_item('Stop', 'a', self.do_somth))
        playback_menu.append(self.create_menu_item('Previous', 'r', self.do_somth))
        playback_menu.append(self.create_menu_item('Next', 's', self.do_somth))

        playback_menu.append(self.create_menu_item('Jump forward', 'x', self.do_somth))
        playback_menu.append(self.create_menu_item('Jump backward', 'a', self.do_somth))
        playback_menu.append(self.create_menu_item('Jump to time', 'm', self.do_somth))


        self.playlist_filter_label = gtk.Label('Search')
        self.playlist_filter = gtk.Entry()
        self.playlist_count = gtk.Label('<count>')
        self.playlist_count.set_size_request(30, 10)

        self.playlist = gtk.TreeView()
        self.playlist.set_size_request(400, 300)
        column = gtk.TreeViewColumn("type", gtk.CellRendererText(), text=2)
        column.set_sort_column_id(0)
        self.playlist.append_column(column)
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('foreground-set', True)
        column = gtk.TreeViewColumn("name", cell_renderer, text=0, foreground=3)
        column.set_sort_column_id(1)
        self.playlist.append_column(column)
        self.playlist.connect("cursor-changed", self.playlist_changed)
        self.playlist.connect("row-activated", self.play_item)

        self.player = VLCWidget() #gtk.DrawingArea()
        self.player.set_size_request(400, 300)
        self.player.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse("brown"))
        self.player.connect('play-started', self.play_started)

        self.pos = gtk.HScale()
        self.pos.set_range(0, 100)
        self.pos.set_increments(1, 10)
        self.pos.set_digits(0)

        #scale.connect("value-changed", self.on_changed)

        self.volume = gtk.VScale()
        self.volume.set_range(0, 10)
        self.volume.set_digits(0)
        #scale.connect("value-changed", self.on_changed)

        filter_box = gtk.HBox(False, 5)
        filter_box.pack_start(self.playlist_filter_label, False)
        filter_box.pack_start(self.playlist_filter, True, True)
        filter_box.pack_start(self.playlist_count, False)

        playlist_box = gtk.VBox(False, 5)
        playlist_box.pack_start(filter_box, False)
        playlist_box.pack_start(self.playlist, True, True)

        player_control_box = gtk.HBox(False, 5)
        player_control_box.pack_start(self.pos, True, True)
        player_control_box.pack_start(self.volume, False)

        player_box = gtk.VBox(False, 5)
        player_box.pack_start(self.player, True, True)
        player_box.pack_start(player_control_box, False)

        main_box = gtk.HBox(False, 5)
        main_box.pack_start(player_box, True, True)
        main_box.pack_start(playlist_box, False)

        window_box = gtk.VBox(False, 5)
        window_box.pack_start(menubar, False, False)
        window_box.pack_start(main_box, True, True)
        self.master.add(window_box)
        self.master.show_all()

    def create_menu_item(self, name, accelerator, callback):
        action = gtk.Action(name, name, name, None)
        action.connect('activate', callback)
        self.actiongroup.add_action_with_accel(action, accelerator)
        action.set_accel_group(self.accelgroup)
        action.connect_accelerator()
        return action.create_menu_item()

    def set_title(self, text):
        self.master.set_title("nasu ~" + text)

    def set_playlist(self, files):
        # see os.walk, os.listdir
        files = list(files)
        store = gtk.ListStore(str, str, str, str)
        for f in files:
            store.append([f['name'],
                          f['path'],
                          f['mime'],
                          self.config['normal'],
                          ])
        self.playlist.set_model(store)
        self.playlist_count.set_text(str(len(files)))

    def playlist_changed(self, grid, *args, **kwargs):
        model, it = self.playlist.get_selection().get_selected()
        file_name = model.get_value(it, 1)
        print 'selected:', file_name, args

    def play_item(self, grid, *args, **kwargs):
        model, it = self.playlist.get_selection().get_selected()
        file_name, file_path = model.get_value(it, 0), model.get_value(it, 1)

        print 'start_play:', file_name, file_path
        self.set_title(file_name)
        self.player.play(file_path)

        reset_it = model.get_iter_root()
        while reset_it:
            model.set_value(reset_it, 3, self.config['normal'])
            reset_it = model.iter_next(reset_it)

        model.set_value(it, 3, self.config['active'])

    def play_started(self, *args):
        print 'len:', self.player.get_length()

    def do_somth(self, *args):
        print 'do_soooo'

class JumpForm(object):
    pass


class PlayerForm(object):
    pass




def main(files):
    app = MainForm()
    app.set_playlist(files)
    gtk.main()
