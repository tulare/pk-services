__all__ = [ 'DomainParserConfig', 'CharsetHTMLParser', 'ImageLinkHTMLParser', 'MediaHMTLParser' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import json
import pathlib
import urllib.parse
import html.parser
import lxml.etree

# --------------------------------------------------------------------

class DomainParserConfig :

    def __init__(self) :
        self._data = {
            'default' : [
                "//a[descendant::img]/descendant::img/@src",
                "//a[descendant::img]/@href"
            ],
        }

    def __str__(self) :
        return self.toJSON(indent=2)

    def __eq__(self, other) :
        return self._data == other._data

    def __getitem__(self, key) :
        return self.get_domain(key)

    @property
    def keys(self) :
        return self._data.keys()

    @property
    def items(self) :
        return self._data.items()

    def toJSON(self, indent=None) :
        return json.dumps(self._data, indent=indent)

    def saveJSON(self, jsonFilename) :
        with open(jsonFilename, 'w') as fd :
            fd.write(self.toJSON(indent=2))

    def fromJSON(self, json_data) :
        self.update(json.loads(json_data))

    def loadJSON(self, jsonFilename) :
        with open(jsonFilename, 'r') as fd :
            self.fromJSON(fd.read())

    def update(self, dico) :
        self._data.update(dico)

    def add_domain(self, domain, xpath_img, xpath_link) :
        self._data[domain] = (xpath_img, xpath_link)

    def get_domain(self, domain) :
        return self._data.get(domain, self._data.get('default'))

    def find_url(self, url) :
        url_split = urllib.parse.urlsplit(url)
        domain_items = url_split.netloc.split('.')
        domain = '.'.join(domain_items[-2:])
        return self.get_domain(domain)

# --------------------------------------------------------------------

class ImageLinkHTMLParser :

    def __init__(self) :
        self._images_links = {}
        self._domain_parser_config = DomainParserConfig()
        self._ns = lxml.etree.FunctionNamespace('http://mydomain.org/functions')
        self._ns.prefix = 'fn'
        self._ns['urljoin'] = self.urljoin

    @property
    def config(self) :
        return self._domain_parser_config

    @property
    def images(self) :
        return list(self.images_links.keys())

    @property
    def links(self) :
        return list(self.images_links.values())

    @property
    def images_links(self) :
        try :
            il = self._images_links
        except AttributeError :
            il = {}
        return il

    def urljoin(self, context, nodes, baseurl) : 
            return [f"{urllib.parse.urljoin(baseurl, pathlib.Path(n).stem)}" for n in nodes]

    def parse(self, data, url) :
        self._images_links = {}
        motif_image, motif_link = self._domain_parser_config.find_url(url)
        self.add_parse(data, motif_image, motif_link)

    def add_parse(self, data, motif_image, motif_link) :
        tree = lxml.etree.HTML(data)
        self._images_links.update(zip(
            tree.xpath(motif_image),
            tree.xpath(motif_link)
        ))
        log.debug(f"add_parse: {motif_image} / {motif_link} : {len(self.images_links)}")
        

# --------------------------------------------------------------------

class CharsetHTMLParser(html.parser.HTMLParser) :

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

class MediaHTMLParser(html.parser.HTMLParser) :

    def parse(self, data) :
        self._images_links = {}
        self._linkopen = False        
        self.feed(data)

    @property
    def images(self) :
        return list(self.images_links.keys())

    @property
    def links(self) :
        return list(self.images_links.values())

    @property
    def images_links(self) :
        try :
            il = self._images_links
        except AttributeError :
            il = {}
        return il

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if tag == 'a' and 'href' in attributes :
            log.debug(f"<a> : href={attributes['href']}")
            self._linkopen = attributes['href']

        if tag == 'div' and 'style' in attributes :
            log.debug(f"<div> : style={attributes['style']}")
            if 'background-image:url(' in attributes['style'] :
                if self._linkopen is not None :
                    image = attributes['style'].split('(')[-1].split(')')[0]
                    log.info(f"background-image:url = {image} => link href={self._linkopen}")
                    self._images_links[image] = self._linkopen
            
        if tag == 'img' and 'src' in attributes :
            log.debug(f"<img> : src={attributes['src']}")
            if self._linkopen is not None :
                log.info(f"image src={attributes['src']} => link href={self._linkopen}")
                self._images_links[attributes['src']] = self._linkopen

    def handle_endtag(self, tag) :
        if tag == 'a' :
            self._linkopen = None
            log.debug(f"<a> END")

# --------------------------------------------------------------------
    
