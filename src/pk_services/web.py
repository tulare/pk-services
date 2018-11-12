# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

__all__ = [ 'WebService', 'WebRequest', 'GrabService' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import os
import re
import json

try : # python 2.7
    import urllib2 as requests
    import urlparse
except ImportError :
    import urllib.request as requests
    import urllib.parse as urlparse

from .core import Service
from .exceptions import ServiceError
from .parsers import CharsetHTMLParser, MediaHTMLParser

# --------------------------------------------------------------------

class WebService(Service) :

    @Service.opener.setter
    def opener(self, opener) :
        if opener is None :
            self._opener = requests.build_opener()
        else :
            self._opener = opener

    @property
    def headers(self) :
        return {
            header[0].lower() : header[1]
            for header in self.opener.addheaders
        }

    @property
    def user_agent(self) :
        return self.headers.get('user-agent')

    @user_agent.setter
    def user_agent(self, user_agent) :
        headers = self.headers
        headers['user-agent'] = user_agent
        self.opener.addheaders = headers.items()

    def test(self) :
        response = self.opener.open('http://httpbin.org/get?option=value')
        return json.load(response)

    @classmethod
    def domain(cls, url) :
        url_split = urlparse.urlsplit(url)
        return url_split.netloc
        

# --------------------------------------------------------------------

class WebRequest(WebService) :
    def __call__(self, url) :
        request = requests.Request(url)
        try :
            response = self.opener.open(request)
        except requests.URLError as e:
            if hasattr(e, 'reason') :
                raise ServiceError(e.reason)
            elif hasattr(e, 'code') :
                raise ServiceError(e.code)
        else :
            return response

# --------------------------------------------------------------------

class GrabService(WebService) :

    def __init__(self, opener=None) :
        super(GrabService, self).__init__(opener)

        self.parser = MediaHTMLParser()
        self._url = None
        self._head = '.*'
        self._ext = '',

    def _grab(self, url) :
        charset_parser = CharsetHTMLParser()
        request = requests.Request(url)
        try :
            response = self.opener.open(request)
            page = response.read()
            charset_parser.parse(page)
            self.parser.parse(page.decode(charset_parser.charset))
            self._url = url
        except requests.URLError as e:
            if hasattr(e, 'reason') :
                raise ServiceError(e.reason)
            elif hasattr(e, 'code') :
                raise ServiceError(e.code)            
            
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
        return urlparse.urljoin(self._url, '/')

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
    def images(self) :
        re_head = re.compile(self.head)
        log.debug('IMAGES head="{.pattern}"'.format(re_head))
        re_ext = re.compile('\.('+'|'.join(self.ext)+')\?*')
        log.debug('IMAGES ext="{.pattern}"'.format(re_ext))

        images = list()
        try :
            images = [
                urlparse.urljoin(self.url, image)
                for image in filter(
                    lambda img : (
                        re_head.search(os.path.basename(img))
                        and re_ext.search(img)
                    ),
                    self.parser.images
                )
            ]
        except Exception as e :
            log.debug(repr(e))

        return images

    @property
    def links(self) :
        re_head = re.compile(self.head)
        log.debug('LINKS head="{.pattern}"'.format(re_head))

        links = list()
        try :
            links = [
            urlparse.urljoin(self.url, link)
                for link in filter(
                    lambda lnk :
                        re_head.search(urlparse.urlsplit(lnk).path),
                    self.parser.links
                )
            ]
        except Exception as e :
            log.debug(repr(e))
    
        return links

# --------------------------------------------------------------------
