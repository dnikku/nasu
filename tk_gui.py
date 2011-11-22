from Tkinter import *

class App(object):
    def __init__(self, master):
        print 'hwnd=', master.frame()

        self.master = master
        self.master.title('nasu ~ ')
        frame = self.master

        self.playlist_filter_label = Label(frame, text="Search", bg='yellow')
        self.playlist_filter = Entry(frame)
        self.playlist = Listbox(frame, width=40, height=15)
        self.playlist_count = Label(frame, text="<count>", fg="red")

        self.player = Frame(frame, bg='brown')
        self.navigation = Scale(frame, orient=HORIZONTAL,
                                from_=1, to=100)
        self.volume = Scale(frame, orient=VERTICAL,
                            from_=1, to=10)

        self.player.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=N+S+W+E)
        self.navigation.grid(row=2, column=0, sticky=S+W+E)
        self.volume.grid(row=2, column=1, sticky=S+E)

        self.playlist_filter_label.grid(row=0, column=2, sticky=N+W)
        self.playlist_filter.grid(row=0, column=3, sticky=N+W+E)
        self.playlist_count.grid(row=0, column=4, sticky=N+W)
        self.playlist.grid(row=1, column=2, rowspan=2, columnspan=3, sticky=N+S+E)

        rows, cols = frame.grid_size()
        for r in range(rows):
            frame.rowconfigure(r, weight=1)
        for c in range(cols):
            frame.columnconfigure(c, weight=1)

    def set_playlist(self, files):
        # see os.walk, os.listdir
        files = list(files)
        for f in files:
            self.playlist.insert(END, f['name'])
        self.playlist_count.config(text=len(files))


def main(files):
    root = Tk()
    app = App(root)
    app.set_playlist(files)
    root.mainloop()
