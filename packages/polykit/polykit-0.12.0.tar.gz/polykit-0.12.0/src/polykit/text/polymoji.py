from __future__ import annotations


class PolyMoji:
    """Unicode emoji detection and extraction utilities.

    Provides methods for identifying emoji characters within text strings, checking if text starts
    with emojis, and extracting emoji characters. Covers comprehensive Unicode ranges including
    emoticons, symbols, pictographs, and regional indicators for robust emoji handling in text
    processing workflows.
    """

    @staticmethod
    def is_emoji(char: str) -> bool:
        """Check if a string is an emoji."""
        if not char:
            return False

        code = ord(char)
        return (
            0x1F600 <= code <= 0x1F64F  # Emoticons
            or 0x1F300 <= code <= 0x1F5FF  # Misc Symbols and Pictographs
            or 0x1F680 <= code <= 0x1F6FF  # Transport and Map
            or 0x1F1E0 <= code <= 0x1F1FF  # Regional indicators
            or 0x2600 <= code <= 0x26FF  # Misc symbols
            or 0x2700 <= code <= 0x27BF  # Dingbats
            or 0xFE00 <= code <= 0xFE0F  # Variation Selectors
            or 0x1F900 <= code <= 0x1F9FF  # Supplemental Symbols and Pictographs
            or 0x1F018 <= code <= 0x1F270  # Various symbols
            or 0x238C <= code <= 0x2454  # Misc symbols
            or 0x20D0 <= code <= 0x20FF  # Combining marks for symbols
            or 0x2B00 <= code <= 0x2BFF  # Additional symbols
        )

    @staticmethod
    def starts_with_emoji(text: str) -> bool:
        """Check if a string starts with an emoji."""
        if not text:
            return False

        return PolyMoji.is_emoji(text[0])

    @staticmethod
    def extract_first_emoji(text: str) -> str:
        """Extract the first emoji from a string."""
        return "" if not text or not PolyMoji.starts_with_emoji(text) else text[0]
