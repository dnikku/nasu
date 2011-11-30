from functools import partial
import json

# check: http://stackoverflow.com/questions/249283/virtualenv-on-ubuntu-with-no-site-packages
import gtk, gobject
from gtk_vlcplayer import VLCWidget

from media_files import dir_files
from settings import COLORS, JUMP, AUDIO_VOLUME, SHORT_KEY


def _model_iter(model):
    it = model.get_iter_root()
    while it:
        yield it
        it = model.iter_next(it)


class MainForm(object):
    class Mode(object):
        def enter(self): pass
        def leave(self): pass

        def toggle_fullscreen(self):
            print type(self), ': invalid call'

    class PlaylistMode(Mode):
        def __init__(self, mainfrm):
            self.m = mainfrm

        def enter(self):
            self.m.playlist.enter_list_mode()

        def toggle_fullscreen(self):
            self.m.switch_mode(self.m.fullscreen_mode)
            self.m.playlist.enter_list_mode()

    class SearchlistMode(Mode):
        def __init__(self, mainfrm):
            self.m = mainfrm

        def enter(self):
            self.m.master.remove_accel_group(self.m.accelgroup)
            self.m.playlist.enter_search_mode()

        def leave(self):
            self.m.master.add_accel_group(self.m.accelgroup)

        def toggle_fullscreen(self):
            print "SearchListMode: invalid"

    class FullscreenMode(Mode):
        def __init__(self, mainfrm):
            self.m = mainfrm

        def enter(self):
            self.m.player.fullscreen()

        def toggle_fullscreen(self):
            self.m.player.unfullscreen()
            self.m.switch_mode(self.m.playlist_mode)


    def __init__(self):
        self.accelgroup = gtk.AccelGroup()

        self.master = master = gtk.Window()
        master.add_accel_group(self.accelgroup)
        master.set_title("nasu ~")
        master.set_position(gtk.WIN_POS_CENTER)
        master.connect("destroy", gtk.main_quit)

        self.playlist = Playlist(self)
        self.playlist.connect("media-selected", self.play_media)
        self.playlist.connect("media-searched", self.searched_media)

        self.player = VLCWidget() #gtk.DrawingArea()
        self.player.w.add_accel_group(self.accelgroup)

        self.player.set_size_request(400, 300)
        self.player.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse("brown"))
        self.player.connect('play-started', self.play_started)
        self.player.connect('play-ended', self.playlist.jump_to_next)

        self.pos = gtk.HScale()
        self.pos.set_range(0, 100)
        self.pos.set_increments(1, 10)
        self.pos.set_digits(0)

        self.volume = gtk.VScale()
        self.volume.set_range(0, 10)
        self.volume.set_digits(0)

        player_control_box = gtk.HBox(False, 5)
        player_control_box.pack_start(self.pos, True, True)
        player_control_box.pack_start(self.volume, False)

        self.actiongroup = gtk.ActionGroup('')
        menubar = self._create_menu_bar(self.actiongroup)

        player_box = gtk.VBox(False, 5)
        player_box.pack_start(self.player, True, True)
        #player_box.pack_start(player_control_box, False)

        main_box = gtk.HBox(False, 5)
        main_box.pack_start(player_box, True, True)
        main_box.pack_start(self.playlist, False)

        window_box = gtk.VBox(False, 5)
        window_box.pack_start(menubar, False, False)
        window_box.pack_start(main_box, True, True)
        self.master.add(window_box)
        self.master.show_all()

        self.playlist_mode = self.PlaylistMode(self)
        self.searchlist_mode = self.SearchlistMode(self)
        self.fullscreen_mode = self.FullscreenMode(self)
        self.current_mode = self.Mode()
        self.switch_mode(self.playlist_mode)

    def switch_mode(self, new_mode):
        old_mode, self.current_mode = self.current_mode, new_mode
        old_mode.leave()
        new_mode.enter()
        print 'switch_mode: %s -> %s' % (old_mode, new_mode)
        return new_mode

    def _create_menu_bar(self, actiongroup):
        menubar = gtk.MenuBar()

        media_action = gtk.Action('Media', 'Media', None, None)
        actiongroup.add_action(media_action)
        media_menuitem = media_action.create_menu_item()
        menubar.append(media_menuitem)
        media_menu = gtk.Menu()
        media_menuitem.set_submenu(media_menu)
        media_menu.append(self.create_menu_item(
                SHORT_KEY['ADD_FOLDER'], self.add_mediafiles_from_folder))
        media_menu.append(self.create_menu_item(
                SHORT_KEY['REMOVE_SELECTED'], self.playlist.remove_selected_media))
        media_menu.append(self.create_menu_item(
                SHORT_KEY['LOAD_LIST'], self.load_playlist_from_file))
        media_menu.append(self.create_menu_item(
                SHORT_KEY['SAVE_LIST'], self.save_playlist_to_file))
        media_menu.append(self.create_menu_item(
                SHORT_KEY['EXIT'], gtk.main_quit))

        playback_action = gtk.Action('Playback', 'Playback', None, None)
        actiongroup.add_action(playback_action)
        playback_menuitem = playback_action.create_menu_item()
        menubar.append(playback_menuitem)
        playback_menu = gtk.Menu()
        playback_menuitem.set_submenu(playback_menu)
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['TOGGLE_PAUSE'], self.player.toggle_pause))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['STOP'], self.player.stop))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['PREV'], self.playlist.jump_to_prev))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['NEXT'], self.playlist.jump_to_next))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['JUMP_MEDIA'],
                lambda _: self.switch_mode(self.searchlist_mode)))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['JUMP_FWD'],
                partial(self.player.jump_relative, JUMP['FORWARD'])))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['JUMP_SHORT_FWD'],
                partial(self.player.jump_relative, JUMP['SHORT_FORWARD'])))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['JUMP_BKD'],
                partial(self.player.jump_relative, -JUMP['BACKWARD'])))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['JUMP_SHORT_BKD'],
                partial(self.player.jump_relative, -JUMP['SHORT_BACKWARD'])))

        #playback_menu.append(self.create_menu_item('Jump to time', 't', self.do_somth))
        playback_menu.append(self.create_menu_item(
                SHORT_KEY['FULLSCREEN'],
                lambda _: self.current_mode.toggle_fullscreen()))

        audio_action = gtk.Action('Audio', 'Audio', None, None)
        actiongroup.add_action(audio_action)
        audio_menuitem = audio_action.create_menu_item()
        menubar.append(audio_menuitem)
        audio_menu = gtk.Menu()
        audio_menuitem.set_submenu(audio_menu)
        audio_menu.append(self.create_menu_item(
                SHORT_KEY['AUDIO_VOLUME_INC'],
                partial(self.player.set_volume, AUDIO_VOLUME['INCREASE'])))
        audio_menu.append(self.create_menu_item(
                SHORT_KEY['AUDIO_VOLUME_DEC'],
                partial(self.player.set_volume, AUDIO_VOLUME['DECREASE'])))
        audio_menu.append(self.create_menu_item(SHORT_KEY['AUDIO_MUTE'],
                                                self.player.toggle_mute))

        return menubar

    def create_menu_item(self, name_accelerator, callback):
        name, accelerator = name_accelerator
        action = gtk.Action(name, name, name, None)
        action.connect('activate', callback)
        self.actiongroup.add_action_with_accel(action, accelerator)
        action.set_accel_group(self.accelgroup)
        action.connect_accelerator()
        return action.create_menu_item()

    def set_title(self, text):
        self.master.set_title("nasu ~" + text)

    def add_mediafiles(self, files):
        self.playlist.add_media_files(files)

    def play_media(self, playlist, file_name, file_path):
        print 'play_media:', file_name, file_path
        curr, count = self.playlist.get_selected()
        self.set_title('%s/%s : %s' % (curr, count, file_name))
        self.player.play(file_path)

    def searched_media(self, playlist, file_name, file_path):
        print 'search_media:', file_name, file_path
        self.switch_mode(self.playlist_mode)
        if file_path:
            self.playlist.select_media(file_path)

    def add_mediafiles_from_folder(self, *args):
        dialog = gtk.FileChooserDialog('Add Medias from Folder',
                                       self.master,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       (gtk.STOCK_OK, gtk.RESPONSE_OK,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
                                       )
        folder = None
        if dialog.run() == gtk.RESPONSE_OK:
            folder = dialog.get_filename()
            print 'selected_folder:', folder
        dialog.destroy()
        self.add_mediafiles(dir_files([folder]))

    def save_playlist_to_file(self, *args):
        dialog = gtk.FileChooserDialog('Save Playlist to File',
                                       self.master,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_OK, gtk.RESPONSE_OK,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
                                       )
        filter_ = gtk.FileFilter()
        filter_.add_pattern('*.nasu')
        dialog.set_filter(filter_)
        f = None
        if dialog.run() == gtk.RESPONSE_OK:
            f = dialog.get_filename() + '.nasu'
            print 'selected_file_to_save:', f
        dialog.destroy()

        with open(f, 'w+') as fp:
            self.playlist.save_to(fp)

    def load_playlist_from_file(self, *args):
        dialog = gtk.FileChooserDialog('Load Playlist to File',
                                       self.master,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_OK, gtk.RESPONSE_OK,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
                                       )
        filter_ = gtk.FileFilter()
        filter_.add_pattern('*.nasu')
        dialog.set_filter(filter_)
        f = None
        if dialog.run() == gtk.RESPONSE_OK:
            f = dialog.get_filename()
            print 'selected_file_to_load:', f
        dialog.destroy()
        with open(f, 'r') as fp:
            self.playlist.load_from(fp)

    def play_started(self, *args):
        pass

    def do_somth(self, action):
        print 'do_soooo', action.get_name()


class Playlist(gtk.VBox):
    __gsignals__ = {
        'media-selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_STRING, gobject.TYPE_STRING)),
        'media-searched': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_STRING, gobject.TYPE_STRING)),
        }

    def __init__(self, mainform):
        super(Playlist, self).__init__(False, 5)

        self.mainform = mainform

        self.playlist = self._create_playlist()
        self.playlist.set_model(gtk.ListStore(str, str, str, str))
        self.playlist.connect("row-activated", self.playlist_selected)

        self.searchlist = self._create_searchlist()
        self.searchlist.connect("row-activated", self.searchlist_selected)
        self.pack_start(self.playlist, True, True)

    def _create_playlist(self):
        playlist = gtk.TreeView()
        #playlist.set_reorderable(True)
        playlist.set_enable_search(False)
        playlist.set_size_request(400, 300)
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('foreground-set', True)
        column = gtk.TreeViewColumn("name", cell_renderer, text=0, foreground=3)
        column.set_sort_column_id(1)
        playlist.append_column(column)

        box = gtk.HBox(False, 5)
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(playlist)
        box.pack_start(scrolled, True, True)
        playlist.playlist_box = box

        return playlist

    def _create_searchlist(self):
        searchlist = gtk.TreeView()
        searchlist.set_enable_search(False)
        searchlist.set_size_request(400, 300)
        column = gtk.TreeViewColumn("type", gtk.CellRendererText(), text=2)
        column.set_sort_column_id(0)
        searchlist.append_column(column)
        cell_renderer = gtk.CellRendererText()
        cell_renderer.set_property('foreground-set', True)
        column = gtk.TreeViewColumn("name", cell_renderer, text=0, foreground=3)
        column.set_sort_column_id(1)
        searchlist.append_column(column)

        def searchlist_keydown(entry, key_event):
            #print 'keyeey:', key_event, key_event.keyval
            if key_event.keyval == 65307: # escape
                self.emit('media-searched', None, None)
        searchlist.connect('key-release-event', searchlist_keydown)

        searchlist_filter_label = gtk.Label('Search')
        searchlist_filter = gtk.Entry()
        searchlist.searchlist_filter = searchlist_filter
        def searchlist_filter_keydown(entry, key_event):
            #print 'keyeey:', key_event, key_event.keyval
            if key_event.keyval == 65307: # escape
                self.emit('media-searched', None, None)
            elif key_event.keyval == 65293: # enter
                pass
            else:
                searchlist.get_model().refilter()
                searchlist_count.set_text(str(len(searchlist.get_model())))
        searchlist_filter.connect('key-release-event', searchlist_filter_keydown)

        searchlist_count = gtk.Label('<count>')
        searchlist_count.set_size_request(30, 10)

        filter_box = gtk.HBox(False, 5)
        filter_box.pack_start(searchlist_filter_label, False)
        filter_box.pack_start(searchlist_filter, True, True)
        filter_box.pack_start(searchlist_count, False)

        searchlist_box = gtk.VBox()
        searchlist_box.pack_start(filter_box, False)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(searchlist)

        searchlist_box.pack_start(scrolled, True, True)
        searchlist.searchlist_box = searchlist_box


        def filter_media(model, it, *args):
            file_name = model.get_value(it, 0)
            text = searchlist_filter.get_text() or ''
            return text in file_name
        searchlist.filter_media = filter_media

        return searchlist

    def add_media_files(self, files):
        # see os.walk, os.listdir
        model = self.playlist.get_model()
        for f in files:
            model.append([f['name'],
                          f['path'],
                          f['mime'],
                          COLORS['normal'],
                          ])

    def remove_selected_media(self, *args):
        model, it = self.playlist.get_selection().get_selected()
        if it:
            model.remove(it)
            if not model.iter_is_valid(it):
                if len(model) == 0:
                    it = None
                else:
                    #select last item
                    it = model.get_iter((len(model)-1,))
            if it:
                tree_path = model.get_path(it)
                self.playlist.set_cursor(tree_path)
                self.playlist.scroll_to_cell(tree_path)

    def enter_search_mode(self, *args):
        model_filter = self.playlist.get_model().filter_new()
        model_filter.set_visible_func(self.searchlist.filter_media)
        self.searchlist.set_model(model_filter)

        if self.playlist.playlist_box in self.get_children():
            self.remove(self.playlist.playlist_box)
        if self.searchlist.searchlist_box not in self.get_children():
            self.pack_start(self.searchlist.searchlist_box)
        self.searchlist.searchlist_box.show_all()
        self.searchlist.searchlist_filter.grab_focus()

    def enter_list_mode(self, *args):
        self.searchlist.set_model(None)
        if self.searchlist.searchlist_box in self.get_children():
            self.remove(self.searchlist.searchlist_box)
        if self.playlist.playlist_box not in self.get_children():
            self.pack_start(self.playlist.playlist_box, True, True)
        self.playlist.playlist_box.show_all()
        self.playlist.grab_focus()

    def jump_to_next(self, *args):
        model = self.playlist.get_model()
        length = len(model)
        if length:
            _, it = self.playlist.get_selection().get_selected()
            current = model.get_path(it)[0] if it else -1
            current = (current + 1 + length)% length
            self.select_media_by_path((current,))

    def jump_to_prev(self, *args):
        model = self.playlist.get_model()
        length = len(model)
        if length:
            _, it = self.playlist.get_selection().get_selected()
            current = model.get_path(it)[0] if it else 1
            current = (current - 1 + length)% length
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

    def playlist_selected(self, grid, path, *args):
        model, it = self.playlist.get_selection().get_selected()
        file_name, file_path = model.get_value(it, 0), model.get_value(it, 1)

        for reset_it in _model_iter(model):
            model.set_value(reset_it, 3, COLORS['normal'])
        model.set_value(it, 3, COLORS['active'])
        self.emit('media-selected', file_name, file_path)

    def searchlist_selected(self, grid, path, *arg):
        model, it = self.searchlist.get_selection().get_selected()
        file_name, file_path = model.get_value(it, 0), model.get_value(it, 1)
        self.emit('media-searched', file_name, file_path)


    def get_selected(self):
        """ Returns (current, total count)"""
        model, it = self.playlist.get_selection().get_selected()
        return (1 + model.get_path(it)[0] if it else 0, len(model))

    def save_to(self, fp):
        model = self.playlist.get_model()
        files = [{
                'name': model.get_value(it, 0),
                'path': model.get_value(it, 1),
                'mime': model.get_value(it, 2),
                } for it in _model_iter(model)]
        json.dump(files, fp, indent=True)

    def load_from(self, fp):
        files = json.load(fp)
        self.playlist.get_model().clear()
        self.add_media_files(files)


class PlayerForm(object):
    pass


def main():
    app = MainForm()
    #app.add_mediafiles(dir_files())
    gtk.main()
