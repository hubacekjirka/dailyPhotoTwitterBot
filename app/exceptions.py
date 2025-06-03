class ConfigLoadError(Exception):
    """Custom exception for configuration loading errors."""

    pass


class S3ConfigError(Exception):
    """Custom exception for S3 configuration errors."""

    pass


class PictureResizeError(Exception):
    """Custom exception for errors related to resizing pictures."""

    pass
