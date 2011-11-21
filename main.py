#!/usr/bin/env python

import time

def vmtk():
    from Tkinter import Tk
    w = Tk()
    w.mainloop()


def play():
    """ Sample files:
    path = 'file:///e:/downloads/lola_rennt.avi'
    #path = 'e:\downloads\lola_rennt.avi'
    """

    import vlc

    some_video = 'e:\downloads\lola_rennt.avi'
    p = vlc.MediaPlayer(some_video)
    p.play()
    time.sleep(10)


if __name__ == '__main__':
    #play()
    vmtk()
