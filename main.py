#!/usr/bin/env python

from media_files import dir_files
import gtk_gui


if __name__ == '__main__':
    #play()
    gtk_gui.main(dir_files())
