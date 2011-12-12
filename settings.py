COLORS = {
    'normal': 'black',
    'active': 'red'
    }


# jump salt in seconds
JUMP = {
    'FORWARD': 3*60,
    'SHORT_FORWARD': 30,
    'BACKWARD': 3*60,
    'SHORT_BACKWARD': 30,
}

AUDIO_VOLUME = {
    'INCREASE': 10,
    'DECREASE': -10
}

AUDIO_VISUALIZATION = [
    'goom',
    'none',
    'spectrometer',
    'scope',
    'spectrum analyzer',
    'vu meter',
    'projectm'
    ]

SHORT_KEY = {
    # stucture: key: (Label, short-key)

    #Media menu
    'ADD_FOLDER': ('Add Folder', None),
    'REMOVE_SELECTED': ('Remove Selected', '<Control>d'),
    'LOAD_LIST': ('Load List ...', None),
    'SAVE_LIST': ('Save List As ...', None),
    'EXIT': ('Exit', '<Control>x'),

    #Playback menu
    'TOGGLE_PAUSE': ('Play/Pause', 'p'),
    'STOP': ('Stop', 's'),
    'PREV': ('Prev', 'v'),
    'NEXT': ('Next', 'n'),
    'JUMP_MEDIA': ('Jump to media', 'j'),
    'JUMP_FWD': ('Jump forward', 'f'),
    'JUMP_SHORT_FWD': ('Jump short forward', '<Control>f'),
    'JUMP_BKD': ('Jump backward', 'b'),
    'JUMP_SHORT_BKD': ('Jump short backward', '<Control>b'),
    'FULLSCREEN': ('Fullscreen', 'z'),

    #Audio menu
    'AUDIO_VOLUME_INC': ('Increase Volume', 'i'),
    'AUDIO_VOLUME_DEC': ('Decrease Volume', 'k'),
    'AUDIO_MUTE': ('Mute', 'u'),
}
