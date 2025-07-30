from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Literal

# Translation table for smart quotes replacement
SMART_QUOTES_TABLE = str.maketrans({
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
})


class Colors(StrEnum):
    """Available types of log formatting."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    WHITE = "\033[37m"
    BLACK = "\033[30m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    GREEN = "\033[32m"
    MAGENTA = "\033[95m"
    PURPLE = "\033[35m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_WHITE = "\033[97m"
    BRIGHT_YELLOW = "\033[93m"


COLOR_MAP: dict[str, Colors] = {
    "black": Colors.BLACK,
    "grey": Colors.GRAY,
    "red": Colors.RED,
    "green": Colors.GREEN,
    "yellow": Colors.YELLOW,
    "blue": Colors.BLUE,
    "magenta": Colors.MAGENTA,
    "cyan": Colors.CYAN,
    "light_grey": Colors.BRIGHT_WHITE,
    "dark_grey": Colors.GRAY,
    "light_red": Colors.BRIGHT_RED,
    "light_green": Colors.BRIGHT_GREEN,
    "light_yellow": Colors.BRIGHT_YELLOW,
    "light_blue": Colors.BRIGHT_BLUE,
    "light_magenta": Colors.MAGENTA,
    "light_cyan": Colors.BRIGHT_CYAN,
    "white": Colors.WHITE,
}

# Color names for termcolor
TextColor = Literal[
    "black",
    "grey",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "light_grey",
    "dark_grey",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_magenta",
    "light_cyan",
    "white",
]


class Styles(StrEnum):
    """Available types of style formatting."""

    BOLD = "\033[1m"
    DARK = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    CONCEALED = "\033[8m"


STYLE_MAP: dict[str, Styles] = {
    "bold": Styles.BOLD,
    "dark": Styles.DARK,
    "underline": Styles.UNDERLINE,
    "blink": Styles.BLINK,
    "reverse": Styles.REVERSE,
    "concealed": Styles.CONCEALED,
}


# Color attributes for termcolor
TextStyle = Iterable[
    Literal[
        "bold",
        "dark",
        "underline",
        "blink",
        "reverse",
        "concealed",
    ]
]

CHAR_WIDTHS: dict[str, float] = {
    " ": 0.3,
    "!": 0.3,
    '"': 0.4,
    "#": 0.7,
    "$": 0.7,
    "%": 1.1,
    "&": 0.8,
    "'": 0.2,
    "(": 0.4,
    ")": 0.4,
    "*": 0.5,
    "+": 0.7,
    ",": 0.3,
    "-": 0.4,
    ".": 0.3,
    "/": 0.4,
    "0": 0.7,
    "1": 0.7,
    "2": 0.7,
    "3": 0.7,
    "4": 0.7,
    "5": 0.7,
    "6": 0.7,
    "7": 0.7,
    "8": 0.7,
    "9": 0.7,
    ":": 0.3,
    ";": 0.3,
    "<": 0.8,
    "=": 0.7,
    ">": 0.8,
    "?": 0.7,
    "@": 1.2,
    "A": 0.8,
    "B": 0.8,
    "C": 0.9,
    "D": 0.9,
    "E": 0.8,
    "F": 0.7,
    "G": 0.9,
    "H": 0.9,
    "I": 0.3,
    "J": 0.6,
    "K": 0.8,
    "L": 0.7,
    "M": 1.0,
    "N": 0.9,
    "O": 0.9,
    "P": 0.8,
    "Q": 0.9,
    "R": 0.9,
    "S": 0.8,
    "T": 0.8,
    "U": 0.9,
    "V": 0.8,
    "W": 1.2,
    "X": 0.8,
    "Y": 0.8,
    "Z": 0.8,
    "[": 0.3,
    "\\": 0.5,
    "]": 0.3,
    "^": 0.6,
    "_": 0.7,
    "`": 0.4,
    "a": 0.7,
    "b": 0.7,
    "c": 0.6,
    "d": 0.7,
    "e": 0.7,
    "f": 0.4,
    "g": 0.7,
    "h": 0.7,
    "i": 0.3,
    "j": 0.4,
    "k": 0.6,
    "l": 0.3,
    "m": 1.0,
    "n": 0.7,
    "o": 0.7,
    "p": 0.7,
    "q": 0.7,
    "r": 0.4,
    "s": 0.6,
    "t": 0.4,
    "u": 0.7,
    "v": 0.6,
    "w": 0.9,
    "x": 0.6,
    "y": 0.6,
    "z": 0.6,
    "{": 0.5,
    "|": 0.3,
    "}": 0.5,
    "~": 0.8,
    "§": 0.7,
    "©": 0.9,
    "®": 0.9,
    "°": 0.5,
    "±": 0.7,
    "¶": 0.8,
    "À": 0.8,
    "Á": 0.8,
    "Â": 0.8,
    "Ã": 0.8,
    "Ä": 0.8,
    "Å": 0.8,
    "Æ": 1.2,
    "Ç": 0.9,
    "È": 0.8,
    "É": 0.8,
    "Ê": 0.8,
    "Ë": 0.8,
    "Ì": 0.3,
    "Í": 0.3,
    "Î": 0.5,
    "Ï": 0.4,
    "Ñ": 0.9,
    "Ò": 0.9,
    "Ó": 0.9,
    "Ô": 0.9,
    "Õ": 0.9,
    "Ö": 0.9,
    "×": 0.7,
    "Ø": 0.9,
    "Ù": 0.9,
    "Ú": 0.9,
    "Û": 0.9,
    "Ü": 0.9,
    "Ý": 0.8,
    "à": 0.7,
    "á": 0.7,
    "â": 0.7,
    "ã": 0.7,
    "ä": 0.7,
    "å": 0.7,
    "æ": 1.1,
    "ç": 0.6,
    "è": 0.7,
    "é": 0.7,
    "ê": 0.7,
    "ë": 0.7,
    "ì": 0.3,
    "í": 0.3,
    "î": 0.4,
    "ï": 0.4,
    "ñ": 0.7,
    "ò": 0.7,
    "ó": 0.7,
    "ô": 0.7,
    "õ": 0.7,
    "ö": 0.7,
    "÷": 0.7,
    "ø": 0.7,
    "ù": 0.7,
    "ú": 0.7,
    "û": 0.7,
    "ü": 0.7,
    "ý": 0.6,
    "ÿ": 0.6,
    "Ÿ": 0.8,
    "–": 0.8,
    "—": 1.2,
    "†": 0.7,
    "‡": 0.7,
    "•": 0.4,
    "…": 1.2,
    "™": 1.2,
}
