"""
Define the root error class for all QMENTA exceptions. All exceptions raised
by the QMENTA Core library are subclasses of ``qmenta.core.errors.Error`` and
thus are expected exceptions. If other exceptions are raised, this indicates
unexpected behavior of the library.
"""


class Error(Exception):
    """
    Base class for all QMENTA Core errors.
    """
    def __init__(self, *args: str) -> None:
        Exception.__init__(self, *args)


class CannotReadFileError(Error):
    """
    When a file cannot be read.
    """
    pass


class PlatformError(Error):
    """
    When there is a problem in the communication with the platform.
    """
    pass


class ConnectionError(PlatformError):
    """
    When there was a problem setting up the connection with QMENTA platform.
    """
    def __init__(self, message: str) -> None:
        Error.__init__(self, f'Connection error: {message}')


class InvalidResponseError(PlatformError):
    """
    The QMENTA platform returned an unexpected response.
    """
    pass


class ActionFailedError(PlatformError):
    """
    When the requested action was not successful.
    """
    pass
