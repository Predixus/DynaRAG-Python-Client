class BaseException(Exception):
    """Base exception for the DynaRAG API client"""


class MissingAPIToken(BaseException):
    """Raised if the DynaRAG API key cannot be found."""


class BadAPIRequest(BaseException):
    """Raised if a request to the DynaRAG API fails"""


class BadEnvironment(BaseException):
    """Raised when the environment is bad"""
