class S3ObjectNotFoundError(Exception):
    """Exception throw if object doesn't not exist"""

    pass


class NotebookTooLargeError(Exception):
    """Exception throw if notebook size larger than NOTEBOOK_SIZE_LIMIT_IN_BYTES"""

    pass


class DownloadDirectoryNotFoundError(Exception):
    """Exception throw if download directory is not found"""

    pass
