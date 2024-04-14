# -*- coding: utf-8 -*-

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import os
import re
import codecs

import requests
import urllib.parse

from .core import Service
from .exceptions import ServiceError
from .parsers import CharsetHTMLParser, ImageLinkHTMLParser

__all__ = [ 'WebService', 'WebRequest', 'GrabService' ]

# --------------------------------------------------------------------

class WebService(Service) :

    @Service.opener.setter
    def opener(self, opener) :
        if opener is None :
            self._opener = requests.Session()
        else :
            self._opener = opener

    @property
    def headers(self) :
        return self._opener.headers

    @property
    def user_agent(self) :
        return self.headers.get('User-Agent')

    @user_agent.setter
    def user_agent(self, user_agent) :
        self.headers.update({'User-Agent' : user_agent})

    def test(self) :
        url = 'https://httpbin.org/get?option=value'
        response = self.get(url)
        return response.json()

    def get(self, url) :
        try :
            response = self.opener.get(url)
            response.raise_for_status()

        except requests.exceptions.MissingSchema as e :
            raise ServiceError(f'MissingSchema - {e}')

        except requests.exceptions.InvalidSchema as e :
            raise ServiceError(f'InvalidSchema - {e}')

        except requests.exceptions.InvalidURL as e :
            raise ServiceError(f'InvalidURL - {e}')

        except requests.ConnectionError as e :
            raise ServiceError(f'ConnectionError - {e}')

        except requests.HTTPError as e :
            raise ServiceError(f'HTTPError - {e}')
        
        return response
        
    @classmethod
    def domain(cls, url) :
        url_split = urllib.parse.urlsplit(url)
        return url_split.netloc

# --------------------------------------------------------------------

class WebRequest(WebService) :

    def __call__(self, url) :
        return self.get(url)

# --------------------------------------------------------------------

class GrabService(WebService) :

    def __init__(self, opener=None) :
        super().__init__(opener)

        self.parser = ImageLinkHTMLParser()
        self._url = None
        self._head = '.*'
        self._ext = '',

    def _grab(self, url) :
        charset_parser = CharsetHTMLParser()
        try :
            response = self.get(url)
            page = response.content
            charset_parser.parse(page)
            log.debug(f'charset - {charset_parser.charset}')
            decoded_page = codecs.decode(page, encoding=charset_parser.charset, errors='replace')
            log.debug(f'{decoded_page == response.text}')
            #self.parser.parse(decoded_page, url)
            self.parser.parse(response.text, url)
            self._url = url
        except ServiceError as e :
            log.error(f'ServiceError - {e}')
            raise ServiceError(f'ServiceError - {e}')
            
    def update(self) :
        self._grab(self.url)

    @property
    def url(self) :
        return self._url

    @url.setter
    def url(self, url) :
        self._grab(url)

    @property
    def base(self) :
        return urllib.parse.urljoin(self._url, '/')

    @property
    def head(self) :
        return self._head

    @head.setter
    def head(self, head) :
        self._head = head

    @property
    def ext(self) :
        return self._ext

    @ext.setter
    def ext(self, ext) :
        self._ext = tuple(ext)

    @property
    def images_links(self) :
        re_head = re.compile(self.head)
        log.debug('IMAGES_LINKS head="{.pattern}"'.format(re_head))
        re_ext = re.compile('\\.('+'|'.join(self.ext)+')\\?*')
        log.debug('IMAGES_LINKS ext="{.pattern}"'.format(re_ext))

        images_links = {}
        try :
            images_links = {
                urllib.parse.urljoin(self.url, image) : urllib.parse.urljoin(self.url, link)
                for image, link in self.parser.images_links.items()
                if re_head.search(os.path.basename(image))
                and re_ext.search(image)
            }
        except Exception as e :
            log.debug(repr(e))

        return images_links

    @property
    def images(self) :
        return list(self.images_links.keys())

    @property
    def links(self) :
        return list(self.images_links.values())

# --------------------------------------------------------------------
