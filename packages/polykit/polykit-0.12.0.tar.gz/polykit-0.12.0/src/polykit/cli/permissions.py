"""Utility functions for working with the shell, such as handling keyboard interrupts, errors, and
colors, as well as reading and writing files.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TypeVar

T = TypeVar("T")


def is_root_user() -> bool:
    """Confirm that the script is running as root.

    Returns:
        Whether the script is running as root.
    """
    return False if sys.platform.startswith("win") else os.geteuid() == 0


def acquire_sudo() -> bool:
    """Acquire sudo access.

    Returns:
        Whether sudo access was successfully acquired.
    """
    try:  # Check if we already have sudo privileges
        subprocess.run(
            ["sudo", "-n", "true"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        try:  # If we don't have sudo privileges, try to acquire them
            subprocess.run(["sudo", "-v"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
