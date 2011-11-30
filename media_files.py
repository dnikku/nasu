import sys
from os import walk, path
import mimetypes
import json


ignore_files = [
    '.txt',
    '.srt', '.sub',
    '.nfo',
    '.url',
    '.idx', '.dts', '.ac3',
    '.db', '.torrent',
    ]

def dir_files(roots):
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


def save_playlist(fp, files):
    json.dump(files, fp, indent=True)


def load_playlist(fp):
    return json.load(fp)
