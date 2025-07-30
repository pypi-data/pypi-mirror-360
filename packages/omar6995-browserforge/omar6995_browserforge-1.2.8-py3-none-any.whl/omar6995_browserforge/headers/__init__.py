from omar6995_browserforge.download import DownloadIfNotExists

DownloadIfNotExists(headers=True)

from .generator import Browser, HeaderGenerator

__all__ = [
    "Browser",
    "HeaderGenerator",
]
