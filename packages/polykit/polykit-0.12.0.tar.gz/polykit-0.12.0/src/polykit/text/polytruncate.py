from __future__ import annotations

import re
from typing import ClassVar

from polykit.text.polymoji import PolyMoji
from polykit.text.types import CHAR_WIDTHS


class PolyTruncate:
    """Flexible text truncation with intelligent boundary detection.

    Provides sophisticated text truncation methods that can truncate from the beginning, end, or
    middle of text while respecting word and sentence boundaries. Offers both strict character-count
    truncation and intelligent truncation that preserves readability by avoiding mid-word cuts and
    handling punctuation gracefully.

    Also provides smart truncation methods that compensate for the visual width differences between
    characters in proportional fonts (e.g., 'i' vs 'W' vs emojis). Unlike simple character count
    truncation, this attempts to achieve consistent lengths by estimating the display width of text,
    for creating visually balanced text in UIs where consistent visual length is important.
    """

    # Default width for characters not in the mapping
    DEFAULT_WIDTH: ClassVar[float] = 1.0

    @staticmethod
    def truncate(
        text: str,
        chars: int = 200,
        from_middle: bool = False,
        strict: bool = False,
        strip_punctuation: bool = True,
        strip_line_breaks: bool = True,
        condensed: bool = False,
        limit_length: bool = False,
        max_chars: int = 4096,
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
            limit_length: If True, the method ensures the truncated text does not exceed the
                          specified character limit. Defaults to False.
            max_chars: The maximum number of characters the truncated text should contain. Uses
                       default settings value if not specified.

        Returns:
            The truncated text, potentially modified to meet the specified conditions.
        """
        if len(text) <= chars:  # Return as-is if it's already under the desired length
            return text

        if strict:  # In strict mode, truncate the text exactly to the specified limit
            truncated_text = PolyTruncate._truncate_strict(text, chars, from_middle)
        else:  # In non-strict mode, truncate at sentence or word boundaries
            truncated_text = PolyTruncate._truncate_at_boundaries(
                text, chars, from_middle, strip_punctuation, condensed
            )

        # Ensure final length does not exceed 4096 characters
        if limit_length and len(truncated_text) > max_chars:
            truncated_text = f"{truncated_text[:max_chars]}..."

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
            truncated_text = PolyTruncate._truncate_from_middle(chars, text, condensed)
        else:  # For standard (non-middle) truncation, find the optimal single truncation point
            split_index = PolyTruncate._find_index(text, chars)
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
        first_half_index = PolyTruncate._find_index(text, first_half_limit)
        second_half_index = len(text) - PolyTruncate._find_index(text[::-1], second_half_limit)
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

    @classmethod
    def calculate_visual_width(cls, text: str) -> float:
        """Calculate the estimated visual width of text for proportional fonts.

        Args:
            text: The text to measure.

        Returns:
            The estimated visual width as a float.
        """
        total_width = 0.0
        for char in text:
            if PolyMoji.is_emoji(char):
                total_width += 2.0
            else:
                total_width += CHAR_WIDTHS.get(char, cls.DEFAULT_WIDTH)
        return total_width

    @classmethod
    def truncate_by_width(
        cls,
        text: str,
        target_width: float,
        ellipsis: str = "...",
        preserve_words: bool = True,
    ) -> str:
        """Truncate text to fit within a target visual width.

        Args:
            text: The text to truncate.
            target_width: The target visual width to fit within.
            ellipsis: The ellipsis string to append when truncating.
            preserve_words: Whether to try to preserve whole words.

        Returns:
            The truncated text with ellipsis if needed.
        """
        if not text:
            return text

        # Calculate ellipsis width
        ellipsis_width = cls.calculate_visual_width(ellipsis)
        available_width = target_width - ellipsis_width

        if available_width <= 0:
            return ellipsis[: int(target_width)]

        # Find the truncation point
        current_width = 0.0
        truncate_pos = 0

        for i, char in enumerate(text):
            char_width = cls.calculate_visual_width(char)
            if current_width + char_width > available_width:
                truncate_pos = i
                break
            current_width += char_width
            truncate_pos = i + 1
        else:
            # Text fits completely
            return text

        # If preserving words, try to truncate at word boundary
        if preserve_words and truncate_pos > 0:
            # Look backwards for a space
            word_boundary = text.rfind(" ", 0, truncate_pos)
            if word_boundary > 0 and word_boundary > truncate_pos * 0.7:  # Don't go too far back
                truncate_pos = word_boundary

        return text[:truncate_pos].rstrip() + ellipsis

    @classmethod
    def truncate_to_char_equivalent(
        cls,
        text: str,
        char_count: int,
        ellipsis: str = "...",
        preserve_words: bool = True,
    ) -> str:
        """Truncate text to the visual width equivalent of char_count average characters.

        Drop-in replacement for character-based truncation that produces more consistent results.

        Args:
            text: The text to truncate.
            char_count: The number of average-width characters to target.
            ellipsis: The ellipsis string to append when truncating.
            preserve_words: Whether to try to preserve whole words.

        Returns:
            The truncated text with ellipsis if needed.
        """
        target_width = float(char_count)
        return cls.truncate_by_width(text, target_width, ellipsis, preserve_words)

    @classmethod
    def get_adjustment_factor(cls, text: str, char_count: int) -> float:
        """Get the adjustment factor for a piece of text.

        This tells you how much wider or narrower the text is compared average-width characters.

        Args:
            text: The text to analyze.
            char_count: The character count to compare against.

        Returns:
            Factor where 1.0 = average width, <1.0 = narrower, >1.0 = wider.
        """
        if not text or char_count <= 0:
            return 1.0

        actual_width = cls.calculate_visual_width(text)
        expected_width = float(char_count)
        return actual_width / expected_width

    @classmethod
    def analyze_text_width(cls, text: str) -> dict[str, float]:
        """Analyze text width characteristics for debugging.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary with width analysis data.
        """
        if not text:
            return {
                "char_count": 0,
                "visual_width": 0.0,
                "avg_char_width": 0.0,
                "width_factor": 1.0,
            }

        char_count = len(text)
        visual_width = cls.calculate_visual_width(text)
        avg_char_width = visual_width / char_count if char_count > 0 else 0.0
        width_factor = visual_width / char_count if char_count > 0 else 1.0

        return {
            "char_count": char_count,
            "visual_width": visual_width,
            "avg_char_width": avg_char_width,
            "width_factor": width_factor,
        }

    @classmethod
    def normalize_text_for_display(cls, text: str, replace_linebreaks: bool = True) -> str:
        """Normalize text for single-line display.

        Args:
            text: The text to normalize.
            replace_linebreaks: If True, replace line breaks with spaces.

        Returns:
            Normalized text suitable for single-line display.
        """
        if not text:
            return text

        if replace_linebreaks:
            # Replace various line break types with spaces
            text = re.sub(r"\r\n|\r|\n", " ", text)

        # Normalize multiple whitespace to single spaces
        text = re.sub(r"\s+", " ", text)

        # Strip leading/trailing whitespace
        return text.strip()

    @classmethod
    def calculate_available_content_width(
        cls, target_line_width: float, prefix: str, suffix: str
    ) -> float:
        """Calculate how much visual width is available for content.

        Args:
            target_line_width: Target visual width for the entire line.
            prefix: Fixed text that comes before the content (e.g., "💬 (1234) You: ").
            suffix: Fixed text that comes after the content (e.g., " (+2 files)").

        Returns:
            Available visual width for the content portion.
        """
        prefix_width = cls.calculate_visual_width(prefix)
        suffix_width = cls.calculate_visual_width(suffix)
        available = target_line_width - prefix_width - suffix_width

        # Ensure we have at least some space for content
        return max(available, 5.0)

    @classmethod
    def truncate_to_fit_line(
        cls,
        content: str,
        target_line_width: float,
        prefix: str = "",
        suffix: str = "",
        ellipsis: str = "...",
        preserve_words: bool = True,
        replace_linebreaks: bool = True,
    ) -> str:
        """Truncate content to fit within a target line width including prefix/suffix.

        Args:
            content: The content to truncate.
            target_line_width: Target visual width for the entire line.
            prefix: Fixed text before content.
            suffix: Fixed text after content.
            ellipsis: Ellipsis to use when truncating.
            preserve_words: Whether to preserve word boundaries.
            replace_linebreaks: Whether to replace line breaks with spaces.

        Returns:
            Truncated content that fits within the available space.
        """
        if not content:
            return content

        # Normalize the content first
        if replace_linebreaks:
            content = cls.normalize_text_for_display(content, replace_linebreaks=True)

        # Calculate available space for content
        available_width = cls.calculate_available_content_width(target_line_width, prefix, suffix)

        # Use the existing truncation method with the calculated width
        return cls.truncate_by_width(
            content, available_width, ellipsis=ellipsis, preserve_words=preserve_words
        )
