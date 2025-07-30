# omar6995-browserforge package initialization
from . import download
from .download import Download, DownloadIfNotExists, IsDownloaded, Remove

# Import main modules for easy access
from . import headers
from . import fingerprints
from . import injectors

# Import commonly used classes
try:
    from .headers import Browser, HeaderGenerator
    from .fingerprints import (
        Fingerprint,
        FingerprintGenerator, 
        NavigatorFingerprint,
        Screen,
        ScreenFingerprint,
        VideoCard,
    )
except ImportError:
    # If data files are not downloaded yet, these imports might fail
    # But the download module should still be available
    pass

__version__ = "1.2.8"

__all__ = [
    # Download functionality
    "download",
    "Download", 
    "DownloadIfNotExists",
    "IsDownloaded", 
    "Remove",
    # Main modules
    "headers",
    "fingerprints", 
    "injectors",
    # Common classes (if available)
    "Browser",
    "HeaderGenerator",
    "Fingerprint",
    "FingerprintGenerator",
    "NavigatorFingerprint", 
    "Screen",
    "ScreenFingerprint",
    "VideoCard",
] 