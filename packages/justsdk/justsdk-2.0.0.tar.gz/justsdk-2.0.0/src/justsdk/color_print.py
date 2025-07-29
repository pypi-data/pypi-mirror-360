from .ansi import Fore


def print_color(
    m: str,
    prefix: str,
    color: str = Fore.RESET,
    newline_before: bool = False,
    newline_after: bool = False,
) -> None:
    before_newline = "\n" if newline_before else ""
    after_newline = "\n" if newline_after else ""
    print(f"{before_newline}[{color}{prefix}{Fore.RESET}] {m}{after_newline}")


def print_success(
    m: str, newline_before: bool = False, newline_after: bool = False
) -> None:
    print_color(m, "success", Fore.GREEN, newline_before, newline_after)


def print_warning(
    m: str, newline_before: bool = False, newline_after: bool = False
) -> None:
    print_color(m, "warning", Fore.YELLOW, newline_before, newline_after)


def print_error(
    m: str, newline_before: bool = False, newline_after: bool = False
) -> None:
    print_color(m, "error", Fore.RED, newline_before, newline_after)


def print_info(
    m: str, newline_before: bool = False, newline_after: bool = False
) -> None:
    print_color(m, "info", Fore.MAGENTA, newline_before, newline_after)
