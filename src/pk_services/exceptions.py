__all__ = [ 'ServiceException', 'ServiceError' ]

class ServiceException(BaseException) :
    """
    Base for Service Exceptions
    """

class ServiceError(ServiceException) :
    """
    A Service Error occurred
    """
