"""A simple module to make it a little less painful to make console applications."""

__title__ = "bconsole"
__author__ = "BetaKors"
__version__ = "0.0.24"
__license__ = "MIT"
__url__ = "https://github.com/BetaKors/bconsole"

from typing import Callable, cast

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


def get_logger[T: Logger = ColoredLogger](
    name: str, /, cls_obj_or_factory: T | type[T] | Callable[[], T] = ColoredLogger
) -> T:
    """
    Gets a logger with the specified name.
    If it does not exist, it will be generated using the class or factory provided or simply added if a direct instance of Logger is provided instead.\n
    Purely for compatibility with the `logging` module.

    ### Args:
        name (str): The name of the logger.
        cls_obj_or_factory (T, type[T], Callable[[], T], optional): A direct instance, or the class or factory needed to create the Logger. Defaults to ColoredLogger.

    ### Returns:
        Logger: The logger.
    """
    if name not in _loggers:
        _loggers[name] = (
            cls_obj_or_factory
            if isinstance(cls_obj_or_factory, Logger)
            else cls_obj_or_factory()
        )
    return cast(T, _loggers[name])


getLogger = get_logger
