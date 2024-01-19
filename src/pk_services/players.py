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

class MPVOptions :
    #
    def __init__(self) :
        self._options = set()
        self._raw_options = {}
        self._ytdl_format = []
    #
    @property
    def options(self) :
        options = list(self._options)
        options.append(self.formats)
        options.append(self.raw_options)
        return options
    #
    @property
    def formats(self) :
        options = '+'.join(self._ytdl_format)
        return f"--ytdl-format={options or 'ytdl'}"
    #
    @formats.setter
    def formats(self, formats) :
        if not isinstance(formats, tuple) :
            formats = formats,
        print(formats, type(formats))
        self._ytdl_format = [ str(fmt) for fmt in formats if fmt ]
    #
    @property
    def raw_options(self) :
        options = ','.join(f"{key}=[{value}]" for key, value in self._raw_options.items())
        return f"--ytdl-raw-options={options}"
    #
    def set_options(self, *options) :
        for option in options :
            if option :
                self._options.add(f"--{option}")
    #
    def clear_options(self, *options) :
        for option in options :
            self._options.discard(f"--{option}")
    #
    def set_formats(self, *formats) :
        self._ytdl_format = [ str(fmt) for fmt in formats if fmt ]
    #
    def set_raw_options(self, *options) :
        # grouper les options par couple (option, valeur)
        for i in range(0, len(options), 2) :
            optionsval = options[i:i+2]
            option, valeur = optionsval if len(optionsval) == 2 else (optionsval[0], '')
            self._raw_options[option] = str(valeur or '')
    #
    def clear_raw_options(self, *options) :
        for option in options :
            self._raw_options.pop(option, None)

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
        self._mpv_options = MPVOptions()
        self.init_mpv_options(options)

    @property
    def mpv_options(self) :
        return self._mpv_options

    def init_mpv_options(self, options) :
        if options.get('nosub', False) :
            self.mpv_options.set_options('no-sub')
        else :
            self.mpv_options.clear_options('no-sub')
        self.mpv_options.set_formats(options.get('ytdlfmt','ytdl'))
        self.mpv_options.set_raw_options('format-sort', options.get('fmtsort','hasvid'))

    def play(self, title, video_uri) :
        command = [ self.program ]
        if title :
            command.append(f'--title={title}')
        command.append(video_uri)
        command[1:1] = self.mpv_options.options
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
