"""Custom exceptions for the sentence completion program."""

class SentenceCompletionError(Exception):
    """Base exception for all sentence completion errors."""
    pass

class FileOperationError(SentenceCompletionError):
    """Raised when file operations fail."""
    pass

class EncryptionError(SentenceCompletionError):
    """Raised when encryption/decryption operations fail."""
    pass

class ValidationError(SentenceCompletionError):
    """Raised when input validation fails."""
    pass

class ConfigurationError(SentenceCompletionError):
    """Raised when there are configuration issues."""
    pass

class BackupError(SentenceCompletionError):
    """Raised when backup operations fail."""
    pass

class ExportError(SentenceCompletionError):
    """Raised when export operations fail."""
    pass 