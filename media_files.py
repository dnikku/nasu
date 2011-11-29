import sys
from os import walk, path
import mimetypes


def get_root_paths():
    if sys.platform.startswith('linux'):
        return ['..'];
    return [
        'E:\downloads\utorrent\completed',
        'E:\\mmedia\\audio\\germana',
        ]

ignore_files = [
    '.txt',
    '.srt', '.sub',
    '.nfo',
    '.url',
    '.idx', '.dts', '.ac3',
    '.db', '.torrent',
    ]

def dir_files(roots=get_root_paths()):
    for start_from in roots:
        print start_from
        for root, dirs, files in walk(start_from):
            print root
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
