# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

import abc
import os
import sys
import subprocess

__all__ = [ 'MediaPlayer', ]

# compatible with Python 2.x *and* 3.x
PY3 = sys.version_info > (3,)
ABC = abc.ABCMeta(str('ABC'), (object,), { '__slots__' : ()})

# options de démarrage pour Popen
ON_POSIX = str('posix') in sys.builtin_module_names

# --------------------------------------------------------------------

def stringify(chaine) :
    if PY3 :
        return chaine

    if isinstance(chaine, unicode) :
        return chaine.encode('cp1252')

    if isinstance(chaine, str) :
        try :
            uni = chaine.decode('utf8')
        except UnicodeDecodeError :
            uni = chaine.decode(sys.stdout.encoding)

        return uni.encode('cp1252')
    
# --------------------------------------------------------------------

def popen_player(command, console) :
    escaped_cmd = list(map(stringify, command))
    startupinfo = subprocess.STARTUPINFO()
    if not console :
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(
        escaped_cmd,
        startupinfo=startupinfo,
        close_fds=ON_POSIX,
    )

# --------------------------------------------------------------------

def check_player(command) :
    escaped_cmd = list(map(stringify, command))
    try :
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            escaped_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            close_fds=ON_POSIX,
        )
    except WindowsError :
        return False

    returncode = proc.wait()
    return returncode == 0        
    
# --------------------------------------------------------------------

class MediaPlayer(ABC) :
    """Fabrique Abstraite de player"""

    def __new__(cls, *args, **kwargs) :
        for sub in cls.__subclasses__() :
            try :
                if kwargs['id'] == sub.id_player :
                    player = super(cls, sub).__new__(sub)
                    return player
            except KeyError :
                pass
            
        return super(MediaPlayer, cls).__new__(cls)

    def __init__(self, *args, **kwargs) :
        options = {
            'console' : False
        }
        options.update(kwargs)
        self.console = options['console']
        self.options = []

    @classmethod
    def getList(cls) :
        return [sub.id_player for sub in cls.__subclasses__()]

    @classmethod
    def getPlayer(cls, player=None) :
        if player :
            return cls(id=player)

        for player in cls.getList() :
            if player != 'dummy' and cls(id=player).check() :
                return cls(id=player)

        return cls(id='dummy')

    def add_options(self, *options) :
        self.options.extend(options)
        
    @abc.abstractmethod
    def play(self, title, video_uri) :
        pass

    @abc.abstractmethod
    def check(self) :
        pass
    
# --------------------------------------------------------------------

class Player_dummy(MediaPlayer) :

    id_player = 'dummy'
    program = None

    def play(self, title, video_uri) :
        return 'Player_dummy(title={}, video_uri={})'.format(title, video_uri)

    def check(self) :
        return True
    
# --------------------------------------------------------------------

class Player_mpv(MediaPlayer) :
    """Implementation Concrete : mpv """

    id_player = 'mpv'
    program = 'mpv.exe'

    def play(self, title, video_uri) :
        command = [
            self.program,
            '--title', title,
            video_uri
        ]
        command[1:1] = self.options
        return popen_player(command, self.console)

    def check(self) :
        command = [ self.program, '--version' ]
        return check_player(command)
        
# --------------------------------------------------------------------

class Player_ffplay(MediaPlayer) :
    """Implementation Concrete : ffplay"""

    id_player = 'ffplay'
    program = 'ffplay.exe'

    def play(self, title, video_uri) :
        command = [
            self.program,
            '-window_title', title,
            '-loglevel', 'quiet',
            '-i', video_uri   
        ]
        command[1:1] = self.options
        return popen_player(command, self.console)

    def check(self) :
        command = [ self.program, '-version' ]
        return check_player(command)

# --------------------------------------------------------------------

class Player_vlc(MediaPlayer) :
    """Implementation Concrete : vlc"""

    id_player = 'vlc'
    program = 'C:/Program Files/VideoLAN/VLC/vlc.exe'

    def play(self, title, video_uri) :
        command = [
            self.program,
            '--intf', 'dummy',
            video_uri,
            'vlc://quit'
        ]
        command[1:1] = self.options
        return popen_player(command, self.console)

    def check(self) :
        command = [ self.program, '--intf', 'dummy', 'vlc://quit' ]
        return check_player(command)

# --------------------------------------------------------------------
