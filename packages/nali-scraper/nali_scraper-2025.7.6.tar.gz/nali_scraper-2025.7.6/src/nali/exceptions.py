class NaliError(Exception):
    """Base exception for Nali package."""
    pass


class InvalidSchoolError(NaliError):
    """Raised when an invalid school is provided."""
    pass


class ScrapingError(NaliError):
    """Raised when scraping fails."""
    pass


class UnsupportedHTTPMethodError(NaliError):
    """Raised when an unsupported HTTP method is provided."""
    pass
