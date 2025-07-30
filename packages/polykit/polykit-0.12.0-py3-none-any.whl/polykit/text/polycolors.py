from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from polykit.text.types import COLOR_MAP, STYLE_MAP, Colors

if TYPE_CHECKING:
    from polykit.text.types import TextColor, TextStyle


class PolyColors:
    """Terminal text colorization and styling utilities.

    Provides methods for applying ANSI color codes and text styles (bold, italic, underline, etc.)
    to strings for enhanced terminal output. Includes both string formatting and direct printing
    capabilities with automatic color reset handling.
    """

    @staticmethod
    def color(
        text: Any,
        color: TextColor | None = None,
        style: TextStyle | None = None,
    ) -> str:
        """Return a string with the specified color and style attributes.

        Args:
            text: The text to colorize. If it's not a string, it'll try to convert to one.
            color: The name of the color. Has to be a color from ColorName.
            style: A list of attributes to apply to the text (e.g. ['bold', 'underline']).
        """
        text = str(text)  # Ensure text is a string

        # If no styling needed, return the original text
        if not color and not style:
            return text

        result = ""

        if style:  # Add styles
            for attr in style:
                if attr in STYLE_MAP:
                    result += STYLE_MAP[attr]

        if color:  # Add color
            if color in COLOR_MAP:
                result += COLOR_MAP[color]
            else:  # Try to get from our Colors enum (case-insensitive)
                with contextlib.suppress(AttributeError, TypeError):
                    result += getattr(Colors, color.upper(), "")

        # Add text and reset
        result += f"{text}{Colors.RESET}"
        return result

    @staticmethod
    def print_color(
        text: Any,
        color: TextColor | None = None,
        style: TextStyle | None = None,
        end: str = "\n",
    ) -> None:
        r"""Print a string with the specified color and style attributes.

        Args:
            text: The text to print in color. If it's not a string, it'll try to convert to one.
            color: The name of the color. Has to be a color from ColorName.
            style: A list of attributes to apply to the text (e.g. ['bold', 'underline']).
            end: The string to append after the last value. Defaults to "\n".
        """
        print(PolyColors.color(str(text), color, style), end=end)
