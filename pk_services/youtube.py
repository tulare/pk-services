# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

__all__ = [ 'YoutubeService' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import youtube_dl

from .core import Service
from .exceptions import ServiceError

# --------------------------------------------------------------------

class YoutubeService(Service) :

    def __init__(self) :
        super(YoutubeService, self).__init__(opener=None)
        self._url = None
        self._infos = {}
        self.ytdl = youtube_dl.YoutubeDL({
            'skip_download' : True,
            'logger' : log
        })

    def __getitem__(self, key) :
        return self._infos.get(key, None)

    def update(self) :
        try :
            self._infos = self.ytdl.extract_info(self._url)
        except (youtube_dl.DownloadError, TypeError) as e :
            log.error(e)
            self._infos = {'error' : e }

    @property
    def infos(self) :
        return self._infos

    @property
    def url(self) :
        return self['webpage_url']

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    def validate(self) :
        if self._url is None or self['error'] is not None :
            raise ServiceError(
                'url: {} - reason: {}'.format(
                    self._url, self['error']
                )
            )

        return True

    def print_formats(self) :
        assert self.validate()
        
        for fmt in self['formats'] :
            print(
                '{}'.format(
                    fmt['format']
                )
            )
        
    def select_format(self, max_height=None) :
        """
        Selection d'un format video
        A revoir : quelques lourdeurs dues aux noms des champs qui diffèrent
        en fonction de l'extracteur
        """
        assert self.validate()

        # pas de liste de formats
        if self['formats'] is None :
            return self

        # identifier la clé utilisée
        if 'quality' in self._infos :
            key = 'quality'
        if 'height' in self._infos :
            key = 'height'

        # filtre pour ne garder que les formats Video
        video_formats = list(
            filter(
                lambda f : key in f,
                self['formats']
            )
        )

        # filter pour ne garder que les formats Audio/Video
        try :
            av_formats = list(
                filter(
                    lambda f : f['acodec'] is not 'none',
                    video_formats
                )
            )
        except Exception as e :
            av_formats = video_formats

        # selection par la hauteur maximum de la video
        try :
            selected = max(
                filter(
                    lambda f : f[key] <= max_height,
                    av_formats
                ),
                key = lambda f : f[key]
            )
        except (TypeError, ValueError) :
            if max_height is None :
                selected = max(
                    av_formats,
                    key = lambda f : f[key]
                )
            else :
                selected = min(
                    av_formats,
                    key = lambda f : f[key]
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

        return title, selected['url']
        
