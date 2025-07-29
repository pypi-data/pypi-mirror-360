"""
Allegro API Python Client Library

A modern Python client for the Allegro REST API.
"""

__version__ = "0.1.0"
__author__ = "Allegro API Python Library Contributors"

from .client import AllegroAPI
from .exceptions import (
    AllegroAPIException,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "AllegroAPI",
    "AllegroAPIException",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]