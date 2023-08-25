__all__ = [ 'Tor', 'Service' ]

import socks
import socket

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150)

class Tor :
    socketSocketMemo = socket.socket
    
    @classmethod
    def isEnabled(cls) :
        return not(cls.socketSocketMemo == socket.socket)
    
    @classmethod
    def enable(cls) :
        if not cls.isEnabled() :
            socket.socket = socks.socksocket

    @classmethod
    def disable(cls) :
        if cls.isEnabled() :
            socket.socket = cls.socketSocketMemo

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
