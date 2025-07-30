from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from polykit.colors import Colors, Styles

# Translation table for smart quotes replacement
SMART_QUOTES_TABLE = str.maketrans({
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
})

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


COLOR_MAP = {
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

STYLE_MAP = {
    "bold": Styles.BOLD,
    "dark": Styles.DARK,
    "underline": Styles.UNDERLINE,
    "blink": Styles.BLINK,
    "reverse": Styles.REVERSE,
    "concealed": Styles.CONCEALED,
}
