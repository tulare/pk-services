# -*- encoding: utf-8 -*-

__all__ = [ 'Service' ]

class Service(object) :
    """Base class for all services"""

    def __init__(self, opener=None) :
        self.opener = opener

    @property
    def opener(self) :
        return self._opener

    @opener.setter
    def opener(self, opener) :
        self._opener = opener
