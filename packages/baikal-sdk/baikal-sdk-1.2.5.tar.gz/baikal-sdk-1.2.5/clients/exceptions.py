"""Custom Exceptions launched in clients"""
__author__ = "4th Platform team"
__license__ = "see LICENSE file"


class ConfigurationError(BaseException):
    """
    Exception raised when there is an issue with the configuration.

    This exception is typically raised when required configuration parameters
    are not properly set or are missing.
    """


class AuthserverError(BaseException):
    """
    Exception raised when an error occurs during communication with the
    authentication server.

    This exception is used to capture errors related to interactions with the
    authentication server, such as invalid credentials or unexpected responses.
    """


class InvalidSignature(BaseException):
    """
    Exception raised when the signature of a received message is invalid.

    This exception is used to signal that the cryptographic signature of a
    received message, such as a token or request, cannot be verified.
    """
