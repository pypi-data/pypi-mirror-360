from __future__ import annotations

import contextlib
import re
from collections.abc import Iterable
from enum import StrEnum
from typing import Any

from polykit.colors import COLOR_MAP, STYLE_MAP, Colors
from polykit.core.deprecate import deprecated
from polykit.text.types import SMART_QUOTES_TABLE, TextColor, TextStyle


class Text(StrEnum):
    """Text formatting types with escape and cleaning utility methods.

    NOTE: This class is deprecated. You should use the new separate text classes instead, including
    PolyColors, PolyMoji, PolyNumbers, PolySplit, PolyText, PolyTruncate, and PolyTime.
    """

    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"

    @deprecated("Use PolyColors.color instead.")
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

    @deprecated("Use PolyColors.print instead.")
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
        print(Text.color(str(text), color, style), end=end)

    @deprecated("Use PolyText.escape instead.")
    def escape(self, text: str) -> str:
        """Escape special characters based on the current text type."""
        if self is Text.MARKDOWN or self is Text.MARKDOWN_V2:
            return self._escape_markdown(text)
        return self._escape_html(text) if self is Text.HTML else text

    @deprecated("Use PolyText.clean instead.")
    def clean(self, text: str) -> str:
        """Remove all formatting based on the current text type."""
        if self is Text.MARKDOWN or self is Text.MARKDOWN_V2:
            return self._strip_markdown(text)
        return self._strip_html(text) if self is Text.HTML else text

    def _escape_markdown(self, text: str) -> str:
        if self not in {Text.MARKDOWN, Text.MARKDOWN_V2}:
            return text

        text = text.replace("\\", "\\\\")  # Handle actual backslashes first

        def escape(esc_text: str) -> str:
            esc_chars = [
                "\\.",
                "_",
                "-",
                r"\(",
                r"\)",
                r"\!",
                "<",
                ">",
                "#",
                r"\+",
                "~",
                r"\`",
                "|",
                "{",
                "}",
                "=",
                "[",
                "]",
            ]
            return re.sub(rf"(?<!\\)([{re.escape(''.join(esc_chars))}])", r"\\\1", esc_text)

        pattern = r"(```.*?```|`[^`\n]*`)|([^`]+|`)"
        escaped_text = []
        inside_code_block = False

        for match in re.finditer(pattern, text, re.DOTALL):
            if match.group(1):  # This is a code block
                escaped_text.append(match.group(1))
                if match.group(1).startswith("```") and match.group(1).endswith("```"):
                    inside_code_block = not inside_code_block
            else:  # This is non-code block text
                escaped_text.append(escape(match.group(2)))

        return "".join(escaped_text)

    def _strip_markdown(self, text: str) -> str:
        if self not in {Text.MARKDOWN, Text.MARKDOWN_V2}:
            return text

        escape_chars = "_*[]()~`>#+-=|{}.!"
        return re.sub(rf"([\\{escape_chars}])", r"", text)

    def _escape_html(self, text: str) -> str:
        if self != Text.HTML:
            return text

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _strip_html(self, text: str) -> str:
        return text if self != Text.HTML else re.sub(r"<[^>]*>", "", text)

    @deprecated("Use PolyText.escape_html instead.")
    @staticmethod
    def html_escape(text: str) -> str:
        """Use the escape method directly from the HTML library."""
        import html

        return html.escape(text)

    @deprecated("Use PolySplit.split_message instead.")
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
            split_point = Text._find_split_point(message, pattern, max_length)
            if split_point:
                break

        if not split_point:
            split_point, code_block_language = Text._split_by_code_blocks(message, max_length)

        part1 = message[:split_point].rstrip()
        part2 = message[split_point:].lstrip()

        if not Text._is_balanced_code_blocks(part1):
            part1 += "```"
            part2 = f"```{code_block_language}\n{part2}"

        return [part1, *Text.split_message(part2, max_length)]

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
                if Text._is_balanced_code_blocks(text[:split_point]):
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

    @deprecated("Use PolyTruncate.truncate instead.")
    @staticmethod
    def truncate(
        text: str,
        chars: int = 200,
        from_middle: bool = False,
        strict: bool = False,
        strip_punctuation: bool = True,
        strip_line_breaks: bool = True,
        condensed: bool = False,
    ) -> str:
        """Truncate text to a specified length.

        In strict mode, truncation strictly adheres to the character limit. In non-strict mode, the
        method seeks to end on full sentences or words. When truncating from the middle, text is cut
        from the center to preserve the start and end of the text, adding an ellipsis in the middle.

        Args:
            text: The text to be truncated.
            chars: The maximum number of characters the truncated text should contain. Uses default
                settings value if not specified.
            from_middle: Whether to truncate the text from its middle. Defaults to False.
            strict: When True, truncation will strictly adhere to the 'chars' limit, possibly
                cutting words or sentences. Defaults to False.
            strip_punctuation: If True, the method ensures the truncated text does not end with
                punctuation, improving readability. Defaults to True.
            strip_line_breaks: If True, the method ensures the truncated text does not contain line
                breaks. Defaults to True.
            condensed: Switches to a more condensed ellipses when using from_middle, so ' [...] '
                becomes '...'. This is better for logging, as one example. Defaults to False.

        Returns:
            The truncated text, potentially modified to meet the specified conditions.
        """
        if len(text) <= chars:  # Return as-is if it's already under the desired length
            return text

        if strict:  # In strict mode, truncate the text exactly to the specified limit
            truncated_text = Text._truncate_strict(text, chars, from_middle)
        else:  # In non-strict mode, truncate at sentence or word boundaries
            truncated_text = Text._truncate_at_boundaries(
                text, chars, from_middle, strip_punctuation, condensed
            )

        # Ensure final length does not exceed 4096 characters
        if len(truncated_text) > 4096:
            truncated_text = f"{truncated_text[:4093]}..."

        if strip_line_breaks:  # Remove line breaks if specified
            truncated_text = truncated_text.replace("\n", " ")

        return truncated_text

    @staticmethod
    def _truncate_strict(text: str, chars: int, from_middle: bool) -> str:
        return (
            f"{text[: chars // 2].strip()}...{text[-chars // 2 :].strip()}"
            if from_middle
            else f"{text[:chars].strip()}..."
        )

    @staticmethod
    def _truncate_at_boundaries(
        text: str, chars: int, from_middle: bool, strip: bool, condensed: bool
    ) -> str:
        # Truncate from the middle or end, attempting to preserve whole sentences or words
        if from_middle:
            truncated_text = Text._truncate_from_middle(chars, text, condensed)
        else:  # For standard (non-middle) truncation, find the optimal single truncation point
            split_index = Text._find_index(text, chars)
            truncated_text = f"{text[:split_index].rstrip()}..."

        # Clean up and ensure it doesn't end with punctuation
        truncated_text = re.sub(r"\s+", " ", truncated_text)
        if strip and not from_middle and truncated_text[-1] in ".?!":
            truncated_text = f"{truncated_text[:-1]}..."

        # Ensure there are never more than three dots at the end, and replace with ellipsis
        while truncated_text.endswith("...."):
            truncated_text = truncated_text[:-1]
        if truncated_text.endswith("..."):
            truncated_text = f"{truncated_text[:-3]}..."

        return truncated_text

    @staticmethod
    def _truncate_from_middle(chars: int, text: str, condensed: bool) -> str:
        separator = "..." if condensed else " [...] "
        first_half_limit = chars // 2  # Calculate limit for first and second half
        second_half_limit = chars - first_half_limit
        # Find truncation points for both halves and combine with an ellipsis in between
        first_half_index = Text._find_index(text, first_half_limit)
        second_half_index = len(text) - Text._find_index(text[::-1], second_half_limit)
        result = f"{text[:first_half_index]}{separator}{text[second_half_index:]}"

        return result.rstrip() if result.endswith(tuple(".?!")) else f"{result.rstrip()}..."

    @staticmethod
    def _find_index(text: str, limit: int) -> int:
        # Search for sentence-ending punctuation to end on a complete sentence if possible
        for punct in [". ", "? ", "! "]:
            index = text.rfind(punct, 0, limit)
            if index != -1:
                return index + len(punct)  # Return the index just after the punctuation
        # If no suitable punctuation is found, fall back to the last space within the limit
        space_index = text.rfind(" ", 0, limit)
        return space_index if space_index != -1 else limit  # Use limit if no space is found

    @deprecated("Use PolyNumbers.plural instead.")
    @staticmethod
    def plural(word: str, count: int, with_count: bool = True) -> str:
        """Pluralize a word based on the count of items.

        Args:
            word: The word to pluralize.
            count: The number of items, which determines the pluralization.
            with_count: Whether to include the count number before the word. Defaults to True.
        """
        if count == 1:
            return f"1 {word}" if with_count else word
        if with_count:
            if word.endswith("s"):
                return f"{count} {word}es"
            return f"{count} {word}s"
        return f"{word}es" if word.endswith("s") else f"{word}s"

    @deprecated("Use PolyNumbers.plural instead.")
    @staticmethod
    def pluralize(*args: Any, **kwargs: Any) -> str:
        """Pluralize (for backward compatibility; use `Text.plural` now)."""
        import warnings

        warnings.warn(
            "'pluralize' is deprecated, use 'plural' instead", DeprecationWarning, stacklevel=2
        )
        return Text.plural(*args, **kwargs)

    @deprecated("Use PolyTime.format_duration instead.")
    @staticmethod
    def format_duration(hours: int = 0, minutes: int = 0, seconds: int = 0) -> str:
        """Print a formatted time duration."""
        sec_str = Text.plural("second", seconds, with_count=True)
        min_str = Text.plural("minute", minutes, with_count=True)
        hour_str = Text.plural("hour", hours, with_count=True)

        if hours == 0:
            if minutes == 0 and seconds == 0:
                return sec_str
            if seconds == 0:
                return min_str
            return sec_str if minutes == 0 else f"{min_str} and {sec_str}"
        if minutes == 0:
            return hour_str if seconds == 0 else f"{hour_str} and {sec_str}"
        if seconds == 0:
            return f"{hour_str} and {min_str}"
        return f"{hour_str}, {min_str} and {sec_str}"

    @deprecated("Use PolyNumbers.num_to_word instead.")
    @staticmethod
    def num_to_word(
        number: int, word_to_pluralize: str | None = None, capitalize: bool = False
    ) -> str:
        """Convert numbers 1-9 into their word equivalents. Pluralize and capitalize if needed.

        Args:
            number: The number to convert.
            word_to_pluralize: The word to pluralize. Defaults to None.
            capitalize: Whether to capitalize the result. Defaults to False.

        Returns:
            The converted word or number with optional pluralization and capitalization.
        """
        number_words = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
        }

        word = number_words.get(number, str(number))
        if word_to_pluralize:
            word_to_pluralize = Text.plural(word_to_pluralize, number, with_count=False)
            result = f"{word} {word_to_pluralize}"
        else:
            result = word

        return result.capitalize() if capitalize else result

    @deprecated("Use PolyNumbers.ordinal instead.")
    @staticmethod
    def ordinal_num(n: int) -> str:
        """Convert an integer into its ordinal representation.

        Args:
            n: An integer number.

        Returns:
            The ordinal string of the integer, e.g., '1st', '2nd', '3rd', etc.
        """
        suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    @deprecated("Use PolyNumbers.format instead.")
    @staticmethod
    def format_number(
        number: int,
        word: str | None = None,
        *,
        with_count: bool = True,
        as_word: bool = False,
        as_ordinal: bool = False,
        capitalize: bool = False,
    ) -> str:
        """Format a number with various options for text representation.

        Args:
            number: The number to format.
            word: Optional word to append (will be pluralized if needed).
            with_count: Include the number with the word. Defaults to True.
            as_word: Convert numbers 0-9 to words ("one", "two", etc.). Defaults to False.
            as_ordinal: Convert to ordinal form ("1st", "2nd", etc.). Defaults to False.
            capitalize: Capitalize the result. Defaults to False.

        NOTE: Setting BOTH `as_word` AND `as_ordinal` WILL work, giving you words like "twond" and
        "threerd". This is not a bug, it's a feature. It's literally what you asked for.

        Examples:
            ```python
            format_number(2)                                 -> 2
            format_number(2, "cat")                          -> cats
            format_number(2, "cat", with_count=True)         -> 2 cats

            # As word
            format_number(2, as_word=True)                   -> two
            format_number(2, "cat", as_word=True)            -> two cats

            # As ordinal
            format_number(2, as_ordinal=True)                -> 2nd
            format_number(2, "cat", as_ordinal=True)         -> 2nd cat

            # And yes...
            format_number(2, as_word=True, as_ordinal=True)  -> twond
            ```
        """
        number_words = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
        }

        # Combine word numbers with ordinals because it's hilarious and you literally asked for it
        if as_word and as_ordinal and number in number_words:
            ordinal_suffix = Text.ordinal_num(number).replace(str(number), "")
            num_str = f"{number_words[number]}{ordinal_suffix}"  # e.g. "twond", "threerd"
        elif as_ordinal:
            num_str = Text.ordinal_num(number)
        elif as_word and number in number_words:
            num_str = number_words[number]
        else:
            num_str = str(number)

        if word:  # Handle word if provided
            if as_ordinal:
                result = f"{num_str} {word}"
            else:
                pluralized = Text.plural(word, number, with_count=False)
                result = f"{num_str} {pluralized}" if with_count else pluralized
        else:
            result = num_str

        return result.capitalize() if capitalize else result

    @deprecated("Use PolyText.straighten_quotes instead.")
    @staticmethod
    def straighten_quotes(text: str) -> str:
        """Replace smart quotes with straight quotes."""
        return text.translate(SMART_QUOTES_TABLE)

    @deprecated("Use PolyText.normalize instead.")
    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text by stripping whitespace, multiple spaces, and normalizing quotes."""
        text = Text.straighten_quotes(text)
        text = text.strip()
        return " ".join(text.split())

    @deprecated("Use PolyNumbers.list_ids instead.")
    @staticmethod
    def list_ids(ids: list[int] | list[str]) -> str:
        """Format a list of IDs as a string with commas and 'and'."""
        if not ids:
            return ""
        if len(ids) == 1:
            return str(ids[0])
        if len(ids) == 2:
            return f"{ids[0]} and {ids[1]}"
        return ", ".join(map(str, ids[:-1])) + ", and " + str(ids[-1])

    @deprecated("Use PolyNumbers.join_ids instead.")
    @staticmethod
    def join_ids(ids: Any, separator: str = ", ") -> str:
        """Join any iterable of IDs into a string.

        Args:
            ids: An iterable (list, set, tuple, etc.) of IDs, or a single value.
            separator: The separator to use between IDs. Defaults to ', '.

        Returns:
            A string of joined IDs.

        Examples:
            ```python
            join_ids({1, 2, 3}) -> '1, 2, 3'
            join_ids([1, '2', 3.0]) -> '1, 2, 3.0'
            join_ids(123) -> '123'
            join_ids(range(3)) -> '0, 1, 2'
            ```
        """
        # If input is not iterable, convert to a single-item list
        if not isinstance(ids, Iterable) or isinstance(ids, str):
            ids = [ids]

        # Convert all elements to strings and join
        return separator.join(str(join_id) for join_id in ids)

    @deprecated("Use PolyText.clean_newlines instead.")
    @staticmethod
    def clean_newlines(text: str, leave_one: bool = True) -> str:
        """Clean up excessive newlines in text.

        Args:
            text: The text to clean.
            leave_one: If True, leaves one newline between paragraphs.
                       Otherwise leaves no blank lines. Defaults to True.
        """
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n" if leave_one else "\n")
        return text

    @deprecated("Use PolyNumbers.parse_ratio_input instead.")
    @staticmethod
    def parse_ratio_input(user_input: str) -> float:
        """Parse user input for a ratio value from a percentage, ratio, or multiplier.

        Valid inputs include:
            - Percentages: '30%', '30 %', '30.5%'
            - Ratios: '0.3', '.3', '1.5'
            - Multipliers: '1.5x', '2X'
            - Whole numbers: '30' (treated as percentage)

        Raises:
            ValueError: If the input is invalid or out of acceptable range.

        Returns:
            The parsed ratio value as a float.
        """
        # Remove any whitespace and convert to lowercase
        cleaned_input = user_input.strip().lower()

        # Define regex patterns
        percentage_pattern = r"^(\d+(\.\d+)?)\s*%$"
        multiplier_pattern = r"^(\d+(\.\d+)?)\s*x$"
        number_pattern = r"^(\d+(\.\d+)?)$"

        try:
            if match := re.match(percentage_pattern, cleaned_input):  # Percentage input
                ratio_value = float(match[1]) / 100
            elif match := re.match(multiplier_pattern, cleaned_input):  # Multiplier input
                ratio_value = float(match[1])
            elif match := re.match(number_pattern, cleaned_input):  # Direct number input
                ratio_value = float(match[1])
                # If it's a whole number greater than 1, treat as percentage
                if ratio_value > 1 and ratio_value.is_integer():
                    ratio_value /= 100
            else:
                msg = "Invalid input format"
                raise ValueError(msg)

        except ValueError as e:
            msg = (
                "Invalid format. Please enter a valid number, "
                "a percentage (e.g., 20 or 20%), "
                "or a multiplier (e.g., 2 or 2x)."
            )
            raise ValueError(msg) from e

        # Validate the range
        if ratio_value < 0:
            msg = "The ratio must be a non-negative value"
            raise ValueError(msg)
        if ratio_value > 100:
            msg = "The ratio exceeds the maximum allowed value of 10000% (100x)"
            raise ValueError(msg)

        return ratio_value

    @deprecated("Use PolyMoji.starts_with_emoji instead.")
    @staticmethod
    def starts_with_emoji(text: str) -> bool:
        """Check if a string starts with an emoji."""
        if not text:
            return False

        # Check if the first character is in the emoji unicode ranges
        first_char = text[0]
        return any(
            start <= ord(first_char) <= end
            for start, end in [
                (0x1F300, 0x1F9FF),  # Miscellaneous Symbols and Pictographs
                (0x2600, 0x26FF),  # Miscellaneous Symbols
                (0x2700, 0x27BF),  # Dingbats
                (0x1F600, 0x1F64F),  # Emoticons
                (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            ]
        )

    @deprecated("Use PolyMoji.extract_first_emoji instead.")
    @staticmethod
    def extract_first_emoji(text: str) -> str:
        """Extract the first emoji from a string."""
        return "" if not text or not Text.starts_with_emoji(text) else text[0]
