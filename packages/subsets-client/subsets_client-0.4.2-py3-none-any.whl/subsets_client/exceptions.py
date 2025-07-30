"""Exceptions for Subsets client."""


class SubsetsError(Exception):
    """Base exception for all Subsets client errors."""
    pass


class AuthenticationError(SubsetsError):
    """Raised when API authentication fails."""
    pass


class UploadError(SubsetsError):
    """Raised when data upload fails."""
    pass