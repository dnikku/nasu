# check: http://stackoverflow.com/questions/249283/virtualenv-on-ubuntu-with-no-site-packages
import gtk


class PyApp(object):
    def __init__(self, master):
        self.master = master
        master.set_title("nasu ~")
        master.set_size_request(400, 300)
        master.set_position(gtk.WIN_POS_CENTER)
        master.connect("destroy", gtk.main_quit)

        self.playlist_filter_label = gtk.Label('Search')
        self.playlist_filter = gtk.Entry()
        self.playlist_count = gtk.Label('<count>')

        self.playlist = gtk.TreeView()
        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        self.playlist.append_column(column)

        self.player = gtk.DrawingArea()
        self.player.set_size_request(200, 150)
        self.player.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse("black"))

        self.pos = gtk.HScale()
        self.pos.set_range(0, 100)
        self.pos.set_increments(1, 10)
        self.pos.set_digits(0)
        self.pos.set_size_request(200, 25)
        #scale.connect("value-changed", self.on_changed)

        self.volume = gtk.VScale()
        self.volume.set_range(0, 10)
        self.volume.set_digits(0)
        #self.volume.set_size_request(200, 25)
        #scale.connect("value-changed", self.on_changed)


        table = gtk.Table(3, 5, False)
        table.attach(self.playlist_filter_label, 2, 3, 0, 1,
                     xpadding=5)
        table.attach(self.playlist_filter, 3, 4, 0, 1)
        table.attach(self.playlist_count, 4, 5, 0, 1,
                     xpadding=5)
        table.attach(self.playlist, 2, 5, 1, 2, xpadding=5, ypadding=5)

        table.attach(self.player, 0, 2, 0, 2)
        table.attach(self.pos, 0, 1, 2, 3)
        table.attach(self.volume, 1, 2, 2, 3)

        self.master.add(table)
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
