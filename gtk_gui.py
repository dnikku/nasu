# check: http://stackoverflow.com/questions/249283/virtualenv-on-ubuntu-with-no-site-packages
import gtk
from gtk_vlcplayer import VLCWidget


def _model_iter(model):
    it = model.get_iter_root()
    while it:
        yield it
        it = model.iter_next(it)


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
        media_menu.append(self.create_menu_item('Add Folder', None, self.do_somth))
        media_menu.append(self.create_menu_item('Remove Selected', '<Control>d', self.do_somth))
        media_menu.append(self.create_menu_item('Load List ...', None, self.do_somth))
        media_menu.append(self.create_menu_item('Save List As ...', '<Control>s', self.do_somth))
        media_menu.append(self.create_menu_item('Exit', '<Control>x', gtk.main_quit))

        playback_action = gtk.Action('Playback', 'Playback', None, None)
        self.actiongroup.add_action(playback_action)
        playback_menuitem = playback_action.create_menu_item()
        menubar.append(playback_menuitem)
        playback_menu = gtk.Menu()
        playback_menuitem.set_submenu(playback_menu)
        playback_menu.append(self.create_menu_item('Play/Pause', 'p', self.do_somth))
        playback_menu.append(self.create_menu_item('Stop', 's', self.do_somth))
        playback_menu.append(self.create_menu_item('Prev', 'v', self.jump_prev_media))
        playback_menu.append(self.create_menu_item('Next', 'n', self.jump_next_media))
        playback_menu.append(self.create_menu_item('Jump to media', 'j', self.jump_to_media))

        playback_menu.append(self.create_menu_item('Jump forward', 'f', self.do_somth))
        playback_menu.append(self.create_menu_item('Jump backward', 'b', self.do_somth))
        playback_menu.append(self.create_menu_item('Jump to time', 't', self.do_somth))


        self.playlist = gtk.TreeView()
        self.playlist.set_reorderable(True)
        self.playlist.set_enable_search(False)
        self.playlist.set_size_request(400, 300)
        column = gtk.TreeViewColumn("type", gtk.CellRendererText(), text=2)
        column.set_sort_column_id(0)
        self.playlist.append_column(column)
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('foreground-set', True)
        column = gtk.TreeViewColumn("name", cell_renderer, text=0, foreground=3)
        column.set_sort_column_id(1)
        self.playlist.append_column(column)
        self.playlist.connect("row-activated", self.play_media)

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

        player_control_box = gtk.HBox(False, 5)
        player_control_box.pack_start(self.pos, True, True)
        player_control_box.pack_start(self.volume, False)

        player_box = gtk.VBox(False, 5)
        player_box.pack_start(self.player, True, True)
        player_box.pack_start(player_control_box, False)

        main_box = gtk.HBox(False, 5)
        main_box.pack_start(player_box, True, True)
        main_box.pack_start(self.playlist, False)

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
        store = gtk.ListStore(str, str, str, str)
        for f in files:
            store.append([f['name'],
                          f['path'],
                          f['mime'],
                          self.config['normal'],
                          ])
        self.playlist.set_model(store)

    def play_media(self, grid, path, *args, **kwargs):
        model, it = self.playlist.get_selection().get_selected()
        file_name, file_path = model.get_value(it, 0), model.get_value(it, 1)

        print 'play_item:', file_name, file_path, path
        self.set_title(file_name)
        self.player.play(file_path)

        for reset_it in _model_iter(model):
            model.set_value(reset_it, 3, self.config['normal'])
        model.set_value(it, 3, self.config['active'])

    def play_started(self, *args):
        print 'len:', self.player.get_length()

    def do_somth(self, *args):
        print 'do_soooo'

    def jump_to_media(self, *args):
        f = JumpForm(self.master, self.playlist.get_model())
        media = f.get_selected_media()
        print 'jump_to_media: ', media
        self.select_media(media)

    def jump_prev_media(self, *args):
        model = self.playlist.get_model()
        l = len(model)
        if l:
            _, it = self.playlist.get_selection().get_selected()
            current = model.get_path(it)[0] if it else 1
            current = (current - 1 + l)% l
            self.select_media_by_path((current,))

    def jump_next_media(self, *args):
        model = self.playlist.get_model()
        l = len(model)
        if l:
            _, it = self.playlist.get_selection().get_selected()
            current = model.get_path(it)[0] if it else -1
            print 'inainte curr:', current, current + 1 + l, l
            current = (current + 1 + l)% l
            print 'dupa curr:', current
            self.select_media_by_path((current,))

    def select_media(self, media):
        model = self.playlist.get_model()
        for it in _model_iter(model):
            if media == model.get_value(it, 1):
                tree_path = model.get_path(it)
                self.select_media_by_path(tree_path)
                break
        else:
            print 'ERROR: invalid media to select', media

    def select_media_by_path(self, tree_path):
        self.playlist.set_cursor(tree_path)
        self.playlist.row_activated(tree_path, self.playlist.get_column(0))
        self.playlist.scroll_to_cell(tree_path)


class PlayerForm(object):
    pass


class JumpForm(object):
    def __init__(self, parent, files):
        self.model_filter = files.filter_new()
        self.model_filter.set_visible_func(self.filter_media)

        self.form = form = gtk.Dialog('Jump to media', parent)
        form.set_modal(True)
        form.set_position(gtk.WIN_POS_CENTER)

        self.playlist_filter_label = gtk.Label('Search')
        self.playlist_filter = gtk.Entry()
        self.playlist_filter.connect('key-release-event', self.refilter_medias)
        self.playlist_count = gtk.Label('<count>')
        self.playlist_count.set_size_request(30, 10)

        self.playlist = gtk.TreeView()
        self.playlist.set_model(self.model_filter)
        self.playlist.set_enable_search(False)
        self.playlist.set_size_request(400, 300)
        column = gtk.TreeViewColumn("type", gtk.CellRendererText(), text=2)
        column.set_sort_column_id(0)
        self.playlist.append_column(column)
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('foreground-set', True)
        column = gtk.TreeViewColumn("name", cell_renderer, text=0, foreground=3)
        column.set_sort_column_id(1)
        self.playlist.append_column(column)
        self.playlist.connect("row-activated", self.media_selected)

        filter_box = gtk.HBox(False, 5)
        filter_box.pack_start(self.playlist_filter_label, False)
        filter_box.pack_start(self.playlist_filter, True, True)
        filter_box.pack_start(self.playlist_count, False)

        playlist_box = self.form.get_content_area()
        playlist_box.pack_start(filter_box, False)
        playlist_box.pack_start(self.playlist, True, True)
        self.form.show_all()

    def get_selected_media(self):
        result = None
        if gtk.RESPONSE_OK == self.form.run():
            model, it = self.playlist.get_selection().get_selected()
            result = model.get_value(it, 1)
        self.form.destroy()
        return result

    def filter_media(self, model, it, *args):
        file_name = model.get_value(it, 0)
        text = self.playlist_filter.get_text() or ''
        return text in file_name

    def refilter_medias(self, *args):
        print 'text:', self.playlist_filter.get_text() or ''
        self.model_filter.refilter()
        self.playlist_count.set_text(str(len(self.model_filter)))

    def media_selected(self, *args):
        self.form.response(gtk.RESPONSE_OK)

def main(files):
    app = MainForm()
    app.set_playlist(files)
    gtk.main()
