"""
project_utils: Shared utilities for configuration and logging.
"""
__all__ = []

# Import Config parser and writer
try:
    from .config import parse_config, write_config
    __all__.append("parse_config")
    __all__.append("write_config")
except (ImportError, ModuleNotFoundError):
    pass

# Import Logger module
try:
    from .logger import Logger, LogDecorator, LogWrapper, log
    __all__.append("Logger")
    __all__.append("LogDecorator")
    __all__.append("LogWrapper")
    __all__.append("log")
except (ImportError, ModuleNotFoundError):
    pass

# Import Gitlab utils
try:
    from .gitlab import GitlabClient, CommitMetadata, MergeRequestMetadata
    __all__.append("GitlabClient")
    __all__.append("CommitMetadata")
    __all__.append("MergeRequestMetadata")
except (ImportError, ModuleNotFoundError):
    pass

# Import Jira utils
try:
    from .jira import JiraClient
    __all__.append("JiraClient")
except (ImportError, ModuleNotFoundError):
    pass

# Import Excel utils
try:
    from .excel import ExcelComparer
    __all__.append("ExcelComparer")
except (ImportError, ModuleNotFoundError):
    pass

# Import OS utils
try:
    from .os import DirectoryWatcher, DirectoryChangeEvent, FileScanner, ContentScanner, TraversalMethod
    __all__.append("DirectoryWatcher")
    __all__.append("DirectoryChangeEvent")
    __all__.append("FileScanner")
    __all__.append("ContentScanner")
    __all__.append("TraversalMethod")
except (ImportError, ModuleNotFoundError):
    pass

# Import Teams module
try:
    from .teams import TeamsClient
    __all__.append("TeamsClient")
except (ImportError, ModuleNotFoundError):
    pass

# Import AI utils
try:
    from .ai import AzureOpenAIClient, OpenAIClientError, AzureDocumentIntelligenceClient, DocumentIntelligenceClientError
    __all__.append("AzureOpenAIClient")
    __all__.append("OpenAIClientError")
    __all__.append("AzureDocumentIntelligenceClient")
    __all__.append("DocumentIntelligenceClientError")
except (ImportError, ModuleNotFoundError):
    pass
