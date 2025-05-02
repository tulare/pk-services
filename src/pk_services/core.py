# -*- coding: utf-8 -*-

import os
import socks
import socket

__all__ = [ 'Tor', 'Service' ]

# ---

class Tor :
    enabled = False
    
    @classmethod
    def isEnabled(cls) :
        return cls.enabled
    
    @classmethod
    def enable(cls) :
        os.environ['HTTP_PROXY'] = 'socks5h://localhost:9150'
        os.environ['HTTPS_PROXY'] = 'socks5h://localhost:9150'
        cls.enabled = True

    @classmethod
    def disable(cls) :
        del os.environ['HTTP_PROXY']
        del os.environ['HTTPS_PROXY']
        cls.enabled = False

# ---

class Service :
    """
    Base class for all services
    """

    defaultUA = 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'

    def __init__(self, opener=None) :
        self.opener = opener

    @property
    def opener(self) :
        return self._opener

    @opener.setter
    def opener(self, opener) :
        self._opener = opener
