"""
Custom exceptions for Contextcol SDK
"""

from typing import Optional, Dict, Any


class ContextcolError(Exception):
    """Base exception for Contextcol SDK"""

    pass


class APIError(ContextcolError):
    """Exception raised when API calls fail"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ConfigError(ContextcolError):
    """Exception raised when configuration is invalid"""

    pass


class BinanceAPIError(ContextcolError):
    """Exception raised when Binance API calls fail"""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code


class AuthenticationError(ContextcolError):
    """Exception raised when authentication fails"""

    pass


class ValidationError(ContextcolError):
    """Exception raised when input validation fails"""

    pass
