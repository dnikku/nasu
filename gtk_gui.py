# check: http://stackoverflow.com/questions/249283/virtualenv-on-ubuntu-with-no-site-packages
import gtk


class PyApp(object):
    def __init__(self, master):
        self.master = master
        master.set_title("nasu ~")
        master.set_position(gtk.WIN_POS_CENTER)
        master.connect("destroy", gtk.main_quit)

        self.playlist_filter_label = gtk.Label('Search')
        self.playlist_filter = gtk.Entry()
        self.playlist_count = gtk.Label('<count>')
        self.playlist_count.set_size_request(30, 10)

        self.playlist = gtk.TreeView()
        self.playlist.set_size_request(100, 300)
        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.playlist.append_column(column)

        self.player = gtk.DrawingArea()
        self.player.set_size_request(400, 300)
        self.player.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse("black"))

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

        self.master.add(main_box)
        self.master.show_all()

    def set_playlist(self, files):
        # see os.walk, os.listdir
        files = list(files)
        store = gtk.ListStore(str)
        for f in files:
            store.append([f['name']])
        self.playlist.set_model(store)

        self.playlist_count.set_text(str(len(files)))


    def __test_init__(self):
        super(PyApp, self).__init__()

        self.set_title("Alignment")
        self.set_size_request(260, 150)
        self.set_position(gtk.WIN_POS_CENTER)

        vbox = gtk.VBox(False, 5)
        hbox = gtk.HBox(True, 3)

        valign = gtk.Alignment(0, 1, 0, 0)
        vbox.pack_start(valign)

        ok = gtk.Button("OK")
        ok.set_size_request(70, 30)
        close = gtk.Button("Close")

        hbox.add(ok)
        hbox.add(close)

        halign = gtk.Alignment(1, 0, 0, 0)
        halign.add(hbox)

        vbox.pack_start(halign, False, False, 3)

        self.add(vbox)

        self.connect("destroy", gtk.main_quit)
        self.show_all()

def main(files):
    root = gtk.Window()
    app = PyApp(root)
    app.set_playlist(files)
    gtk.main()
