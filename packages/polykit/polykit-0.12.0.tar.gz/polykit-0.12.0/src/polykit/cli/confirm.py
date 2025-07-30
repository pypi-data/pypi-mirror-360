"""Utility functions for working with the shell, such as handling keyboard interrupts, errors, and
colors, as well as reading and writing files.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, TypeVar

from polykit.text import color

if TYPE_CHECKING:
    from polykit.text.types import TextColor

T = TypeVar("T")


def get_single_char_input(prompt: str = "") -> str:
    """Read a single character without requiring the Enter key. Mainly for confirmation prompts.
    Supports Windows using msvcrt and Unix-like systems using termios.

    Args:
        prompt: The prompt to display to the user.

    Returns:
        The character that was entered.
    """
    print(prompt, end="", flush=True)

    if sys.platform.startswith("win"):  # Windows-specific implementation
        import msvcrt

        char = msvcrt.getch().decode()  # type: ignore
    else:  # macOS and Linux (adult operating systems)
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char


def confirm_action(
    prompt: str, default_to_yes: bool = False, prompt_color: TextColor | None = None
) -> bool:
    """Ask the user to confirm an action before proceeding.

    Usage:
        if confirm_action("Do you want to proceed?"):

    Args:
        prompt: The prompt to display to the user.
        default_to_yes: Whether to default to "yes" instead of "no".
        prompt_color: The color of the prompt. Defaults to "white".

    Returns:
        Whether the user confirmed the action.
    """
    options = "[Y/n]" if default_to_yes else "[y/N]"
    full_prompt = color(f"{prompt} {options} ", prompt_color)
    sys.stdout.write(full_prompt)

    char = get_single_char_input("").lower()

    sys.stdout.write(char + "\n")
    sys.stdout.flush()

    return char != "n" if default_to_yes else char == "y"
