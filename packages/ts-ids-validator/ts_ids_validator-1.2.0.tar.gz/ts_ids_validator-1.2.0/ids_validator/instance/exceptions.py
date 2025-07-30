class InvalidInstance(Exception):
    """Raised when the instance is invalid against the schema."""


class InvalidDatacube(InvalidInstance):
    """Raised when a datacube has an invalid structure."""
