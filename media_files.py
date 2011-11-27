import sys
from os import walk, path
import mimetypes


def get_root_path():
    root_path = 'E:\downloads\utorrent\completed'
    if sys.platform.startswith('linux'):
        root_path = '..';
    return root_path

ignore_files = [
    '.txt',
    '.srt', '.sub',
    '.nfo',
    '.url',
    '.idx', '.dts', '.ac3',
    '.db', '.torrent',
    ]

def dir_files(start_from=get_root_path()):

    for root, dirs, files in walk(start_from):
        if '.git' in root or 've' in root:
            pass
        elif root.endswith('VIDEO_TS'):
            yield {'name': path.dirname(root),
                   'path': path.abspath(root),
                   'mime': 'dvd'
                   }
        else:
            for name in files:
                if any(filter(lambda x: name.endswith(x), ignore_files)):
                    print 'skip file: "%s"' % name
                else:
                    print 'add file: "%s"' % name
                    file_path = path.abspath(path.join(root, name))
                    yield {'name': name,
                           'path': file_path,
                           'mime': path.splitext(name)[1],
                           }
