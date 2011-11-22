import time
import vlc


def play():
    """ Sample files:
    path = 'file:///e:/downloads/lola_rennt.avi'
    #path = 'e:\downloads\lola_rennt.avi'
    """

    some_video = 'e:\downloads\lola_rennt.avi'
    p = vlc.MediaPlayer(some_video)
    p.play()
    time.sleep(10)
