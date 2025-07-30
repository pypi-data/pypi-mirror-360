"""Custom exceptions for Essencia."""


class EssenciaException(Exception):
    """Base exception for Essencia application."""
    pass


class DatabaseConnectionError(EssenciaException):
    """Raised when database connection fails."""
    pass


class ValidationError(EssenciaException):
    """Raised when data validation fails."""
    pass


class ServiceError(EssenciaException):
    """Raised when service operation fails."""
    pass


class NotFoundError(EssenciaException):
    """Raised when a requested resource is not found."""
    pass


class AuthorizationError(EssenciaException):
    """Raised when user lacks authorization for an operation."""
    pass


class CacheError(EssenciaException):
    """Raised when cache operations fail."""
    pass


class EncryptionError(EssenciaException):
    """Raised when encryption/decryption operations fail."""
    pass