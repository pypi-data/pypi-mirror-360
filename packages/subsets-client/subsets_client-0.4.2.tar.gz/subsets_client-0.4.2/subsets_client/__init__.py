"""Subsets Client - Simple Python client for the Subsets data platform."""

__version__ = "0.5.0"

from .client import SubsetsClient
from .exceptions import AuthenticationError, SubsetsError, UploadError

__all__ = ["SubsetsClient", "SubsetsError", "AuthenticationError", "UploadError"]