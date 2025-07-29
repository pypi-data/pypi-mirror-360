import sys

from enum import Enum
from typing import Optional, TextIO
from .ansi import Fore


class LogLevel(Enum):
    SUCCESS = (Fore.GREEN, "success")
    WARNING = (Fore.YELLOW, "warning")
    ERROR = (Fore.RED, "error")
    INFO = (Fore.MAGENTA, "info")
    DEBUG = (Fore.CYAN, "debug")

    def __init__(self, color: str, prefix: str) -> None:
        self.color = color
        self.prefix = prefix


def _add_print_methods(cls: type) -> type:
    """
    Class decorator to add print methods for each LogLevel.
    """

    def _create_method(level: LogLevel) -> callable:
        def method(
            self,
            message: str,
            *,
            newline_before: bool = False,
            newline_after: bool = False,
            file: Optional[TextIO] = None,
        ) -> None:
            self.print_custom(
                message,
                level,
                newline_before=newline_before,
                newline_after=newline_after,
                file=file,
            )

        return method

    for level in LogLevel:
        method = _create_method(level)
        method.__name__ = level.prefix
        method.__doc__ = f"Print a {level.prefix} message with {level.color} color."
        setattr(cls, level.prefix, method)

    return cls


@_add_print_methods
class ColorPrinter:
    def __init__(
        self,
        file: Optional[TextIO] = None,
        use_color: bool = True,
        show_timestamp: bool = False,
    ) -> None:
        self.file = file or sys.stdout
        self.use_color = (
            use_color and hasattr(self.file, "isatty") and self.file.isatty()
        )
        self.show_timestamp = show_timestamp

    def print_custom(
        self,
        message: str,
        level: LogLevel,
        *,
        newline_before: bool = False,
        newline_after: bool = False,
        file: Optional[TextIO] = None,
    ) -> None:
        output_file = file or self.file

        parts = []
        if newline_before:
            parts.append("\n")

        if self.show_timestamp:
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")
            parts.append(f"[{timestamp}] ")

        if self.use_color:
            prefix = f"[{level.color}{level.prefix}{Fore.RESET}]"
        else:
            prefix = f"[{level.prefix}]"

        if newline_after:
            parts.extend([prefix, "\n", message])
        else:
            parts.extend([prefix, " ", message])

        print("".join(parts), file=output_file)


_default_printer = ColorPrinter()


def print_success(
    message: str,
    *,
    newline_before: bool = False,
    newline_after: bool = False,
    file: Optional[TextIO] = None,
) -> None:
    """Print a success message with GREEN color."""
    _default_printer.success(
        message,
        newline_before=newline_before,
        newline_after=newline_after,
        file=file,
    )


def print_warning(
    message: str,
    *,
    newline_before: bool = False,
    newline_after: bool = False,
    file: Optional[TextIO] = None,
) -> None:
    """Print a warning message with YELLOW color."""
    _default_printer.warning(
        message,
        newline_before=newline_before,
        newline_after=newline_after,
        file=file,
    )


def print_error(
    message: str,
    *,
    newline_before: bool = False,
    newline_after: bool = False,
    file: Optional[TextIO] = None,
) -> None:
    """Print an error message with RED color."""
    _default_printer.error(
        message,
        newline_before=newline_before,
        newline_after=newline_after,
        file=file,
    )


def print_info(
    message: str,
    *,
    newline_before: bool = False,
    newline_after: bool = False,
    file: Optional[TextIO] = None,
) -> None:
    """Print an info message with MAGENTA color."""
    _default_printer.info(
        message,
        newline_before=newline_before,
        newline_after=newline_after,
        file=file,
    )


def print_debug(
    message: str,
    *,
    newline_before: bool = False,
    newline_after: bool = False,
    file: Optional[TextIO] = None,
) -> None:
    """Print a debug message with CYAN color."""
    _default_printer.debug(
        message,
        newline_before=newline_before,
        newline_after=newline_after,
        file=file,
    )
