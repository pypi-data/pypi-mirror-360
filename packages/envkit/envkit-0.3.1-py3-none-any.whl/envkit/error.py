class MissingEnvVarError(Exception):
    """Exception raised when an environment variable is missing."""


class ValidationError(Exception):
    """Exception raised when a value fails validation."""
