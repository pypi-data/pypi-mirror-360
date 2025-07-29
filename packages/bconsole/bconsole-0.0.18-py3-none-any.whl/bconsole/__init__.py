"""A simple module to make it a little less painful to make console applications."""

__title__ = "bconsole"
__author__ = "BetaKors"
__version__ = "0.0.18"
__license__ = "MIT"
__url__ = "https://github.com/BetaKors/bconsole"

from typing import Callable

from colorama import just_fix_windows_console

from .console import Console
from .core import Background, Cursor, Erase, Foreground, Modifier
from .extras import CSSBackground, CSSForeground
from .logger import ColoredFileLogger, ColoredLogger, Logger, LogLevel, LogLevelLike

just_fix_windows_console()
del just_fix_windows_console

__all__ = [
    "Background",
    "ColoredFileLogger",
    "ColoredLogger",
    "Console",
    "CSSBackground",
    "CSSForeground",
    "Cursor",
    "Erase",
    "Foreground",
    "Logger",
    "LogLevel",
    "LogLevelLike",
    "Modifier",
]

_loggers = dict[str, Logger]()


def get_logger[T: Logger](
    name: str, /, cls_or_factory: type[T] | Callable[[], T] = ColoredLogger
) -> T:
    """
    Gets a logger with the specified name.\n
    If the logger does not exist, it is created and added to the `loggers` dictionary.\n
    Purely for compatibility with the `logging` module.

    ### Args:
        name (str): The name of the logger.
        cls_or_factory (type[Logger], optional): The class or factory to use to create the logger. Defaults to ColoredLogger.

    ### Returns:
        Logger: The logger.
    """
    if name not in _loggers:
        _loggers[name] = cls_or_factory()
    return _loggers[name]  # type: ignore


getLogger = get_logger
