# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

__all__ = [ 'CharsetHTMLParser', 'MediaHMTLParser' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

try : # python 2.7
    import HTMLParser as htmlparser
except ImportError :
    import html.parser as htmlparser

# --------------------------------------------------------------------

class CharsetHTMLParser(htmlparser.HTMLParser, object) :

    def parse(self, data) :
        self._content = []
        for line in data.splitlines() :
            self.feed(line.decode('utf-8'))
            if len(self._content) > 0 :
                break

    @property
    def charset(self) :
        try :
            return self._content[0]
        except IndexError :
            return 'utf-8'

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if ( tag == 'meta' and 'http-equiv' in attributes
             and 'content' in attributes ) :
            if 'charset' in attributes['content'] :
                self._content.append(attributes['content'].split('=').pop())
            

# --------------------------------------------------------------------

class MediaHTMLParser(htmlparser.HTMLParser, object) :

    def parse(self, data) :
        self._images = []
        self._links = []
        self.feed(data)

    @property
    def images(self) :
        return self._images

    @property
    def links(self) :
        return self._links

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if tag == 'a' and 'href' in attributes :
            log.debug("start tag : {} href={}".format(tag, attributes['href']))
            self._links.append(attributes['href'])
        if tag == 'img' and 'src' in attributes :
            log.debug("start tag : {} src={}".format(tag, attributes['src']))
            self._images.append(attributes['src'])
        

# --------------------------------------------------------------------
