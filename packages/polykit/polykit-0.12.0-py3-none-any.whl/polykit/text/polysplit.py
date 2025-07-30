from __future__ import annotations

import re
from typing import Any


class PolySplit:
    """Intelligent text splitting and message segmentation utilities.

    Provides sophisticated methods for splitting long text into smaller chunks while preserving
    formatting, code blocks, and natural language boundaries. Particularly useful for messaging
    platforms with character limits (like Telegram) where content integrity and readability must be
    maintained across multiple messages.
    """

    @staticmethod
    def split_message(message: str, max_length: int = 4096) -> list[str]:
        """Split a message into smaller parts for Telegram, handling Markdown and code blocks.

        This method splits long messages into smaller parts for sending as Telegram messages. It
        handles many different edge cases, particularly with respect to code blocks. It's the bee's
        knees, refined over many months and now battle-tested and extremely reliable.
        """

        if len(message) <= max_length:
            return [message]

        split_points = {
            "paragraph": re.compile(r"\n\n"),
            "line": re.compile(r"\n"),
            "sentence": re.compile(r"(?<=\.)\s+"),
            "space": re.compile(r" "),
        }

        split_point = None
        code_block_language = ""

        for pattern in split_points.values():
            split_point = PolySplit._find_split_point(message, pattern, max_length)
            if split_point:
                break

        if not split_point:
            split_point, code_block_language = PolySplit._split_by_code_blocks(message, max_length)

        part1 = message[:split_point].rstrip()
        part2 = message[split_point:].lstrip()

        if not PolySplit._is_balanced_code_blocks(part1):
            part1 += "```"
            part2 = f"```{code_block_language}\n{part2}"

        return [part1, *PolySplit.split_message(part2, max_length)]

    @staticmethod
    def _find_split_point(text: str, pattern: re.Pattern[Any], max_len: int) -> int | None:
        matches = list(pattern.finditer(text[:max_len]))
        if not matches:
            return None

        split_point = matches[-1].start()

        # Check for Markdown headers or styled text at the beginning of the next line
        next_line_start = text.find("\n", split_point)
        if next_line_start != -1 and next_line_start + 1 < len(text):
            next_char = text[next_line_start + 1]
            # Move the split point to before the newline
            if next_char in "#*":
                return next_line_start

        return split_point

    @staticmethod
    def _split_by_code_blocks(text: str, max_len: int) -> tuple[int, str]:
        code_block_indices = [m.start() for m in re.finditer(r"```", text)]
        code_block_language = ""

        # If there's a code block marker before max_len, try to use it as split point
        for index in code_block_indices:
            if index < max_len:
                split_point = index + 3  # Include the ```
                # Only use this point if it results in balanced code blocks
                if PolySplit._is_balanced_code_blocks(text[:split_point]):
                    break
        else:  # No suitable code block split found
            split_point = max_len
            # Adjust split point to avoid breaking within backticks
            while split_point > 0 and text[split_point - 1] == "`":
                split_point -= 1
            while split_point < len(text) and text[split_point] == "`":
                split_point += 1
            split_point = min(split_point, len(text))

        # If we split within a code block, capture its language
        if "```" in text[:split_point]:
            start_of_block = text.rfind("```", 0, split_point)
            end_of_block = text.find("\n", start_of_block)
            if end_of_block != -1:
                code_block_language = text[start_of_block + 3 : end_of_block].strip()

        return split_point, code_block_language

    @staticmethod
    def _is_balanced_code_blocks(text: str) -> bool:
        return text.count("```") % 2 == 0
