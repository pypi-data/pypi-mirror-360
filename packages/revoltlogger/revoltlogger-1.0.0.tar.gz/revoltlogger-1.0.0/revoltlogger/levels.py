from enum import Enum, auto

class LogLevel(Enum):
    TRACE = auto()
    DEBUG = auto()
    VERBOSE = auto()
    INFO = auto()
    SUCCESS = auto()
    WARN = auto()
    ERROR = auto()
    CRITICAL = auto()
    NONE = auto()