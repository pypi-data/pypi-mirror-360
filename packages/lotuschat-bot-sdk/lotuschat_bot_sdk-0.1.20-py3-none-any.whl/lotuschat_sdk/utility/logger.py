import inspect
import os
from enum import Enum, auto

IS_PRINT: bool = True


class LogType(Enum):
    VERBOSE = auto()
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class AnsiColor:
    RESET = "\033[0m"
    GRAY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"


LOG_COLORS = {
    LogType.VERBOSE: AnsiColor.GRAY,
    LogType.DEBUG: AnsiColor.BLUE,
    LogType.INFO: AnsiColor.GREEN,
    LogType.WARNING: AnsiColor.YELLOW,
    LogType.ERROR: AnsiColor.RED,
}


def log_verbose(message): _log(log_type=LogType.VERBOSE, message=message)


def log_debug(message): _log(log_type=LogType.DEBUG, message=message)


def log_info(message): _log(log_type=LogType.INFO, message=message)


def log_warning(message): _log(log_type=LogType.WARNING, message=message)


def log_error(message): _log(log_type=LogType.ERROR, message=message)


def _log(log_type: LogType, message):
    frame = inspect.stack()[2]
    filename = os.path.basename(frame.filename)
    lineno = frame.lineno
    function = frame.function

    cls = None
    if 'self' in frame.frame.f_locals:
        cls = frame.frame.f_locals['self'].__class__.__name__

    location = f"{filename}:{lineno}"
    if cls:
        location += f" [{cls}.{function}]"
    else:
        location += f" [{function}]"

    color = LOG_COLORS.get(log_type, AnsiColor.RESET)
    if (IS_PRINT): print(f"{color}[{log_type.name}] {location} → {message}{AnsiColor.RESET}")
