import sys

from .file_scanner import FileScanner, TraversalMethod
from .content_scanner import ContentScanner
from .directory_event import DirectoryChangeEvent

if sys.platform.startswith("win"):
    try:
        from .directory_watcher_windows import DirectoryWatcherWindows as DirectoryWatcher
    except (ImportError, ModuleNotFoundError):

        try:
            from .directory_watcher_crossplatform import DirectoryWatcherCrossplatform as DirectoryWatcher
        except (ImportError, ModuleNotFoundError):
            raise Exception("No PyWin32 nor watchdog is installed. Install any of those before using the OS utility module.")
 
else:
    try:
        from .directory_watcher_crossplatform import DirectoryWatcherCrossplatform as DirectoryWatcher
    except (ImportError, ModuleNotFoundError):
        raise Exception("Watchdog package is not installed. Install it before using the OS utility module.") 

__all__ = ["DirectoryWatcher", "DirectoryChangeEvent", "FileScanner", "ContentScanner", "TraversalMethod"]