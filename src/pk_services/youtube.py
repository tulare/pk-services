__all__ = [ 'YoutubeService' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import re
import yt_dlp as youtube_dl

from .core import Service
from .exceptions import ServiceError

# --------------------------------------------------------------------

def grab_height(chaine) :
    motif = re.compile('[0-9]{3,}')
    

# --------------------------------------------------------------------

class YoutubeService(Service) :

    def __init__(self, *args, **kwargs) :
        super().__init__(opener=None)
        self._url = None
        self._current = 0
        self._infos = {}
        self._params = {
            'skip_download' : True,
            'playliststart' : 1,
            'playlistend' : -1,
            'logger' : log,
            'verbose' : True
        }
        self._set_params(kwargs)

    def _set_params(self, params) :
        if 'format_sort' in params :
            self.format_sort = params['format_sort']

    def __getitem__(self, key) :
        # implements : self[key]
        return self.infos.get(key, None)

    def update(self) :
        self._current = 0
        try :
            with youtube_dl.YoutubeDL(self._params) as ytdl :
                infos = ytdl.extract_info(self._url)
                self._infos = ytdl.sanitize_info(infos)
        except (youtube_dl.DownloadError, TypeError) as e :
            log.error(e)
            self._infos = {'error' : e }

    @property
    def format_sort(self) :
        return self._params.get('format_sort', [])

    @format_sort.setter
    def format_sort(self, fmtsort) :
        self._params['format_sort'] = fmtsort.split(',')
        if self._url is not None :
            self.update()

    @property
    def skip_download(self) :
        return self._params.get('skip_download', False)

    @skip_download.setter
    def skip_download(self, skip_download) :
        self._params['skip_download'] = bool(skip_download)

    @property
    def verbose(self) :
        return self._params.get('verbose', False)

    @verbose.setter
    def verbose(self, verbose) :
        self._params['verbose'] = bool(verbose)

    @property
    def playlist_start(self) :
        return self._params.get('playliststart', 1)

    @playlist_start.setter
    def playlist_start(self, start) :
        i_start = int(start)
        self._params['playliststart'] = max(1, i_start)
        # correctif
        if self.playlist_end > 0 and i_start > self.playlist_end :
            self._params['playlistend'] = i_start

    @property
    def playlist_end(self) :
        return self._params.get('playlistend', -1)

    @playlist_end.setter
    def playlist_end(self, end) :
        i_end = int(end)
        self._params['playlistend'] = i_end
        # correctifs
        if i_end < self.playlist_start :
            self._params['playlistend'] = self.playlist_start
        if i_end < 0 :
            self._params['playlistend'] = -1

    @property
    def infos(self) :
        if self.is_playlist :
            return self._infos['entries'][self.current]
        else :
            return self._infos

    @property
    def url(self) :
        return self['webpage_url']

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    @property
    def selected_formats(self) :
        return '+'.join(fmt['format_id'] for fmt in self['requested_formats'] or [self])

    @property
    def resolution(self) :
        return self['resolution'] or 'unknown'

    @property
    def title(self) :
        return f"[{self.resolution}] {self['title']}"

    @property
    def id(self) :
        return self['id']

    @property
    def is_playlist(self) :
        return self._infos.get('_type') == 'playlist'

    @property
    def count(self) :
        return self.infos.get('n_entries', 1)

    @property
    def current(self) :
        return self._current

    @current.setter
    def current(self, num) :
        self._current = min(num, self.count - 1)

    def validate(self) :
        if self._url is None or self['error'] is not None :
            raise ServiceError(
                'url: {} - reason: {}'.format(
                    self._url, self['error']
                )
            )

        return True

    def get_formats(self) :
        assert self.validate()
        return [
            fmt['format'] for fmt in self.infos.get('formats',[])
        ]

    def print_formats(self) :
        for fmt in self.get_formats() :
            print(f"format: {fmt}")

    def get_format(self, format_id=None) :
        result = [
            fmt for fmt in self['formats']
            if fmt['format_id'] == (format_id or self['format_id'])
        ]
        if len(result) :
            return result.pop()

    def select_format(self, max_height=None) :
        """
        Selection d'un format video
        """
        log.debug(f"select fmt : max_height={max_height}")
        assert self.validate()

        # pas de liste de formats
        if 'formats' not in self.infos :
            return self.infos

        # identifier la clé utilisée
        keywd = ''
        heights = re.compile('[0-9]+')
        if 'quality' in self.infos :
            keywd = 'quality'
        if 'format' in self.infos :
            keywd = 'format'
        if 'height' in self.infos :
            keywd = 'height'
        log.debug(f'select_format : key="{keywd}"')

        # preselection clés
        dct_k = [
            entry for entry in self.infos['formats']
            if entry.get(keywd)
        ]

        try :
            # preselection height
            selected = min([
                entry for entry in dct_k
                if max(map(int, heights.findall(f'{entry[keywd]}#0'))) >= max_height
                ],
                key=lambda x : max(map(int, heights.findall(f'{x[keywd]}#0')))
            )
        except (ValueError, TypeError) :
            selected = max(
                dct_k,
                key=lambda x : max(map(int, heights.findall(f'{x[keywd]}#0')))
            )
        return selected

    def video(self, max_height=None) :
        """
        Retourne le titre et l'url résolue pour la vidéo sélectionnée
        """

        selected = self.select_format(max_height)

        title = '{} - {}'.format(
            self['title'],
            selected['format']
        )

        log.debug("video : title='{}'".format(title))
        log.debug("video : url='{}'".format(selected['url']))
        return title, selected['url']
