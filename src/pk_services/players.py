import abc
import os
import sys
import subprocess

__all__ = [ 'MediaPlayer', ]

# options de démarrage pour Popen
ON_POSIX = str('posix') in sys.builtin_module_names

# --------------------------------------------------------------------

def popen_player(command, console) :
    escaped_cmd = list(map(str, command))
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
    escaped_cmd = list(map(str, command))
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

class MediaPlayer(abc.ABC) :
    """
    Fabrique Abstraite de player
    """

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
    """
    Implementation Concrete : mpv
    """

    id_player = 'mpv'
    program = 'mpv.exe'

    def __init__(self, *args, **kwargs) :
        options = {
            'console' : True,
            'nosub' : True,
            'ytdlfmt' : 'ytdl',
            'fmtsort' : 'hasvid',
        }
        options.update(kwargs)
        super().__init__(*args, **options)
        self.mpv_options(options)

    def mpv_options(self, options) :
        if options.get('nosub') :
            self.add_options('--no-sub')
        self.add_options(
            f"--ytdl-format={options.get('ytdlfmt')}",
            f"--ytdl-raw-options=format-sort=[{options.get('fmtsort')}]",
        )

    def play(self, title, video_uri) :
        command = [ self.program ]
        if title :
            command.append(f'--title={title}')
        command.append(video_uri)
        command[1:1] = self.options
        return popen_player(command, self.console)

    def check(self) :
        command = [ self.program, '--version' ]
        return check_player(command)

# --------------------------------------------------------------------

class Player_mpv720p(Player_mpv, MediaPlayer) :
    """
    Implementation Concrete : mpv 720p
    """

    id_player = 'mpv720p'

    def __init__(self, *args, **kwargs) :
        options = { 'fmtsort' : 'res:720,+tbr' }
        options.update(kwargs)
        super().__init__(*args, **options)
        
# --------------------------------------------------------------------

class Player_ffplay(MediaPlayer) :
    """
    Implementation Concrete : ffplay
    """

    id_player = 'ffplay'
    program = 'ffplay.exe'

    def __init__(self, *args, **kwargs) :
        options = { 'console' : True }
        options.update(kwargs)
        super().__init__(*args, **options)

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
    """
    Implementation Concrete : vlc
    """

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
