#!/usr/bin/env python

import gtk_gui


def dir_files(start_from):
    from os import walk, path
    for root, dirs, files in walk(start_from):

        if '.git' in root or 've' in root:
            pass
        else:
            for name in files:
                yield {'name': name,
                       'path': path.join(root, name)
                       }


if __name__ == '__main__':
    #play()
    gtk_gui.main(dir_files('..'))
