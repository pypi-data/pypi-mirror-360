__version__ = "2.0.0"
__author__ = "eesuhn"
__email__ = "eason.yihong@gmail.com"

from .ansi import Fore, Back, Style, Cursor
from .color_print import (
    print_color,
    print_error,
    print_warning,
    print_info,
    print_success,
)
from .file_utils import read_file, write_file, print_data, read_files, write_files

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "Fore",
    "Back",
    "Style",
    "Cursor",
    "print_color",
    "print_error",
    "print_warning",
    "print_info",
    "print_success",
    "read_file",
    "write_file",
    "print_data",
    "read_files",
    "write_files",
]
