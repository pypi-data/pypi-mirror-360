import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from sys import stderr, stdout
from typing import Any, Literal, Self, TextIO, override

from .core import Foreground, Modifier
from .utils import clear_ansi

__all__ = ["LogLevel", "LogLevelLike", "Logger", "ColoredLogger", "ColoredFileLogger"]

"""Type alias for a log level or a string representing a log level."""
type LogLevelLike = (
    LogLevel | Literal["verbose", "debug", "info", "warning", "error", "critical"]
)


class LogLevel(Enum):
    """Logging levels."""

    Verbose = "verbose"
    Debug = "debug"
    Info = "info"
    Warning = "warning"
    Error = "error"
    Critical = "critical"

    @classmethod
    def ensure(cls, level: LogLevelLike, /) -> Self:
        """
        Converts a string to a LogLevel if necessary.

        ### Args:
            level (LogLevelLike): The log level to convert.

        ### Returns:
            LogLevel: The log level.
        """
        return cls[level.title()] if isinstance(level, str) else level  # type: ignore


class Logger:
    """Logger class."""

    def log(
        self,
        message: str,
        /,
        level: LogLevelLike = LogLevel.Info,
        *,
        end: str = "\n",
        flush: bool = False,
    ) -> str:
        """
        Logs a message with the specified log level to the console.

        ### Args:
            message (str): The message to log.
            level (LogLevelLike, optional): The log level. Defaults to LogLevel.INFO.
            end (str, optional): The end to use. Defaults to "\n".

        ### Returns:
            str: The formatted, logged message.
        """
        formatted = self._format(message, level, end)

        if file := self._get_file(message, level):
            file.write(formatted)
            _ = flush and file.flush()

        return formatted

    def verbose(self, message: str, /) -> None:
        """
        Logs a message with LogLevel.VERBOSE to the console.

        ### Args:
            message (str): The message to log.
        """
        self.log(message, LogLevel.Verbose)

    def debug(self, message: str, /) -> None:
        """
        Logs a message with LogLevel.DEBUG to the console.

        ### Args:
            message (str): The message to log.
        """
        self.log(message, LogLevel.Debug)

    def info(self, message: str, /) -> None:
        """
        Logs a message with LogLevel.INFO to the console.

        ### Args:
            message (str): The message to log.
        """
        self.log(message, LogLevel.Info)

    def warning(self, message: Warning | str, /) -> None:
        """
        Logs a message with LogLevel.WARNING to the console.

        ### Args:
            message (str): The message to log.
        """
        self.log(str(message), LogLevel.Warning)

    def error(self, message: Exception | str, /) -> None:
        """
        Logs a message with LogLevel.ERROR to the console.

        ### Args:
            message (Exception | str): The message or exception to log.
        """
        self.log(str(message), LogLevel.Error)

    def critical(self, message: Exception | str, /) -> None:
        """
        Logs a message with LogLevel.CRITICAL to the console.

        ### Args:
            message (Exception | str): The message or exception to log.
        """
        self.log(str(message), LogLevel.Critical)

    def _get_file(
        self, message: str, level: LogLevelLike = LogLevel.Info, /
    ) -> TextIO | None:
        """
        Gets the file to write the log message to based on message or log level.\n
        Can be overriden to write to a different file for different messages or log levels.\n
        If `None`, the message will simply not be logged and no exceptions will be thrown.\n
        By default, uses `stderr` if `level` is `LogLevel.Error` or `LogLevel.Critical`, and `stdout` otherwise, and `message` is unused.

        ### Args:
            message (str): The message being logged.
            level (LogLevelLike, optional): The log level. Defaults to `LogLevel.Info`.

        ### Returns:
            TextIO | None: The file to write the log message to. If `None`, the message will not be logged.
        """
        return (
            stderr
            if LogLevel.ensure(level) in (LogLevel.Error, LogLevel.Critical)
            else stdout
        )

    def _format(
        self, message: str, level: LogLevelLike = LogLevel.Info, /, end: str = "\n"
    ) -> str:
        """
        Formats the log message with the specified log level.\n
        Can be overriden to provide different formatting styles based on the log level.

        ### Args:
            message (str): The message to format.
            level (LogLevelLike, optional): The log level. Defaults to LogLevel.INFO.

        ### Returns:
            str: The formatted log message.
        """
        return f"[{LogLevel.ensure(level).name}] {message}{end}"


class ColoredLogger(Logger):
    """An example of how to override the Logger class to provide colored logging with timestamps and stack information."""

    COLORS = {
        LogLevel.Verbose: Foreground.CYAN,
        LogLevel.Debug: Foreground.GREEN,
        LogLevel.Info: Foreground.WHITE,
        LogLevel.Warning: Foreground.from_rgb(255, 164, 0),  # orange
        LogLevel.Error: Foreground.RED,
        LogLevel.Critical: Foreground.RED,
    }

    MODIFIERS = {
        LogLevel.Verbose: Modifier.ITALIC,
        LogLevel.Debug: Modifier.ITALIC,
        LogLevel.Info: Modifier.NONE,
        LogLevel.Warning: Modifier.BOLD,
        LogLevel.Error: Modifier.BOLD,
        LogLevel.Critical: Modifier.INVERSE,
    }

    @override
    def _format(
        self, message: str, level: LogLevelLike = LogLevel.Info, /, end: str = "\n"
    ) -> str:
        frame = traceback.extract_stack(limit=5)[0]

        level = LogLevel.ensure(level)
        dt = datetime.now().strftime("%Y-%m-%d@%H:%M:%S")
        file = Path(frame.filename).stem
        loc = frame.lineno or 0

        return (
            f"{Foreground.CYAN}({dt}){Modifier.RESET} "
            f"{Foreground.YELLOW}[{file}@L{loc}]{Modifier.RESET} "
            f"{self.MODIFIERS[level]}{self.COLORS[level]}{super()._format(message, level)}{Modifier.RESET}"
        )


@dataclass
class ColoredFileLogger(ColoredLogger):
    """A logger that logs both to a file and the terminal. Can be used as a context manager."""

    _file: TextIO

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    @property
    def file(self) -> TextIO:
        """The file to log to."""
        return self._file

    @file.setter
    def file(self, value: TextIO) -> None:
        self.close()
        self._file = value

    @classmethod
    def from_path(cls, path: Path | str, /, encoding: str = "utf-8") -> Self:
        """
        Creates a new `ColoredFileLogger` instance from the specified path and creates the parent directories if they don't exist.

        ### Args:
            path (Path | str): The path to the file.
            encoding (str, optional): The encoding to use. Defaults to "utf-8".

        ### Returns:
            Self: The new `ColoredFileLogger` instance.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return cls(open(path, mode="w+", encoding=encoding))

    @override
    def log(
        self,
        message: str,
        /,
        level: LogLevelLike = LogLevel.Info,
        *,
        end: str = "\n",
        flush: bool = False,
    ) -> str:
        self._file.write(
            clear_ansi(formatted := super().log(message, level, end=end, flush=flush))
        )
        _ = flush and self._file.flush()
        return formatted

    def close(self) -> None:
        """Closes the file."""
        if self._file is not None and not self._file.closed:  # type: ignore
            self._file.close()
