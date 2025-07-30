from __future__ import annotations

import re
from enum import StrEnum

from polykit.text.types import SMART_QUOTES_TABLE


class PolyText(StrEnum):
    """Text format handling and markup language utilities.

    Provides enumerated text format types (Markdown, HTML) with methods for escaping special
    characters and cleaning/stripping formatting. Handles different markup syntaxes and their
    specific escape requirements, making it safe to work with user-generated content in various text
    formatting contexts.
    """

    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"

    def escape(self, text: str) -> str:
        """Escape special characters based on the current text type."""
        if self is PolyText.MARKDOWN or self is PolyText.MARKDOWN_V2:
            return self._escape_markdown(text)
        return self._escape_html(text) if self is PolyText.HTML else text

    def clean(self, text: str) -> str:
        """Remove all formatting based on the current text type."""
        if self is PolyText.MARKDOWN or self is PolyText.MARKDOWN_V2:
            return self._strip_markdown(text)
        return self._strip_html(text) if self is PolyText.HTML else text

    def _escape_markdown(self, text: str) -> str:
        if self not in {PolyText.MARKDOWN, PolyText.MARKDOWN_V2}:
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
        if self not in {PolyText.MARKDOWN, PolyText.MARKDOWN_V2}:
            return text

        escape_chars = "_*[]()~`>#+-=|{}.!"
        return re.sub(rf"([\\{escape_chars}])", r"", text)

    def _escape_html(self, text: str) -> str:
        if self != PolyText.HTML:
            return text

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _strip_html(self, text: str) -> str:
        return text if self != PolyText.HTML else re.sub(r"<[^>]*>", "", text)

    @staticmethod
    def html_escape(text: str) -> str:
        """Use the escape method directly from the HTML library."""
        import html

        return html.escape(text)

    @staticmethod
    def straighten_quotes(text: str) -> str:
        """Replace smart quotes with straight quotes."""
        return text.translate(SMART_QUOTES_TABLE)

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text by stripping whitespace, multiple spaces, and normalizing quotes."""
        text = PolyText.straighten_quotes(text)
        text = text.strip()
        return " ".join(text.split())

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
