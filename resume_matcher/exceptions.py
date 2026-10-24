"""Custom exceptions for the Smart Resume-to-Job Matcher."""


class ResumeMatcherError(Exception):
    """Base exception for all resume matcher errors."""


class FileValidationError(ResumeMatcherError):
    """Raised when a file fails validation (missing, wrong type, empty)."""


class FileReadError(ResumeMatcherError):
    """Raised when a file exists but cannot be read."""


class ParsingError(ResumeMatcherError):
    """Raised when parsing resume or job description content fails."""


class EmptyContentError(FileValidationError):
    """Raised when a file is empty or contains only whitespace."""


class UnsupportedFileTypeError(FileValidationError):
    """Raised when a file extension is not supported."""
