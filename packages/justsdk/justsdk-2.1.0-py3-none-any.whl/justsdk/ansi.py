CSI: str = "\033["
OSC: str = "\033]"
BEL: str = "\a"


def code_to_chars(code: int) -> str:
    return CSI + str(code) + "m"


def set_title(title: str) -> str:
    return OSC + "2;" + title + BEL


def clear_screen(mode: int = 2) -> str:
    return CSI + str(mode) + "J"


def clear_line(mode: int = 2) -> str:
    return CSI + str(mode) + "K"


class AnsiCodes(object):
    def __init__(self) -> None:
        for name in dir(self):
            if not name.startswith("_"):
                value = getattr(self, name)
                setattr(self, name, code_to_chars(value))


class AnsiCursor(object):
    def UP(self, n: int = 1) -> str:
        return CSI + str(n) + "A"

    def DOWN(self, n: int = 1) -> str:
        return CSI + str(n) + "B"

    def FORWARD(self, n: int = 1) -> str:
        return CSI + str(n) + "C"

    def BACK(self, n: int = 1) -> str:
        return CSI + str(n) + "D"

    def POS(self, x: int = 1, y: int = 1) -> str:
        return CSI + str(y) + ";" + str(x) + "H"


class AnsiFore(AnsiCodes):
    BLACK: str = 30
    RED: str = 31
    GREEN: str = 32
    YELLOW: str = 33
    BLUE: str = 34
    MAGENTA: str = 35
    CYAN: str = 36
    WHITE: str = 37
    RESET: str = 39


class AnsiBack(AnsiCodes):
    BLACK: str = 40
    RED: str = 41
    GREEN: str = 42
    YELLOW: str = 43
    BLUE: str = 44
    MAGENTA: str = 45
    CYAN: str = 46
    WHITE: str = 47
    RESET: str = 49


class AnsiStyle(AnsiCodes):
    BRIGHT: str = 1
    DIM: str = 2
    NORMAL: str = 22
    RESET_ALL: str = 0


Fore: AnsiFore = AnsiFore()
Back: AnsiBack = AnsiBack()
Style: AnsiStyle = AnsiStyle()
Cursor: AnsiCursor = AnsiCursor()
