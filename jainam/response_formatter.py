"""
=========================================================
MedIntel360
AI Response Formatter
=========================================================

Formats raw LLM responses into clean, consistent,
user-friendly Markdown for the MedIntel360 dashboard.

Responsibilities:
- Clean unnecessary whitespace
- Normalize Markdown formatting
- Improve readability
- Format common financial/numeric values
- Preserve the meaning of the original response

This module does NOT:
- Query datasets
- Call an LLM
- Perform calculations
- Validate factual correctness
- Route user queries

Author : Jainam Gada
"""

import re
from typing import Any


class ResponseFormatter:
    """
    Presentation layer for AI-generated responses.
    """

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    @staticmethod
    def format(response: Any) -> str:
        """
        Format an AI response into clean Markdown.

        Parameters
        ----------
        response:
            Raw response returned by the AI/LLM layer.

        Returns
        -------
        str
            Clean, user-friendly Markdown response.
        """

        if response is None:
            return ""

        # Convert non-string responses safely.
        text = str(response)

        if not text.strip():
            return ""

        text = ResponseFormatter._normalize_line_endings(text)
        text = ResponseFormatter._remove_code_wrapper(text)
        text = ResponseFormatter._clean_whitespace(text)
        text = ResponseFormatter._clean_markdown(text)
        text = ResponseFormatter._format_numbers(text)
        text = ResponseFormatter._clean_whitespace(text)

        return text.strip()

    # -------------------------------------------------
    # Basic Cleanup
    # -------------------------------------------------

    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """
        Normalize Windows/Mac line endings.
        """

        return text.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def _remove_code_wrapper(text: str) -> str:
        """
        Remove accidental outer Markdown code fences.

        Handles both normally formatted and indented
        multiline responses.
        """

        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

        # Remove empty lines around the response.
        while lines and not lines[0].strip():
            lines.pop(0)

        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            return ""

        # Remove common indentation first.
        indentation_levels = []

        for line in lines:

            if line.strip():

                indentation_levels.append(
                    len(line) - len(line.lstrip())
                )

        if indentation_levels:

            common_indent = min(indentation_levels)

            if common_indent > 0:

                lines = [
                    line[common_indent:]
                    if line.strip()
                    else ""
                    for line in lines
                ]

        text = "\n".join(lines).strip()

        # Remove outer Markdown code fence.
        match = re.fullmatch(
            r"```(?:markdown|md|text)?\s*(.*?)\s*```",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            return match.group(1).strip()

        return text

    @staticmethod
    def _clean_whitespace(text: str) -> str:
        """
        Remove unnecessary indentation, spaces and blank lines
        while preserving Markdown structure.
        """

        lines = text.split("\n")

        # Remove completely empty lines from the beginning/end.
        while lines and not lines[0].strip():
            lines.pop(0)

        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            return ""

        # -------------------------------------------------
        # Remove common indentation
        # -------------------------------------------------
        #
        # This is important for multiline LLM responses
        # and triple-quoted Python strings.
        #
        # Example:
        #
        #     ### Revenue
        #
        #     Total revenue is ₹25 Cr.
        #
        # becomes:
        #
        # ### Revenue
        #
        # Total revenue is ₹25 Cr.
        # -------------------------------------------------

        non_empty_indentation = []

        for line in lines:

            if line.strip():

                indentation = len(line) - len(line.lstrip())

                non_empty_indentation.append(indentation)

        if non_empty_indentation:

            common_indent = min(non_empty_indentation)

            if common_indent > 0:

                lines = [
                    line[common_indent:]
                    if line.strip()
                    else ""
                    for line in lines
                ]

        # -------------------------------------------------
        # Clean individual lines
        # -------------------------------------------------

        cleaned_lines = []

        for line in lines:

            # Remove trailing whitespace.
            line = line.rstrip()

            # Collapse excessive spaces.
            line = re.sub(r"[ \t]+", " ", line)

            cleaned_lines.append(line)

        # -------------------------------------------------
        # Collapse excessive blank lines
        # -------------------------------------------------

        result = []

        blank_count = 0

        for line in cleaned_lines:

            if not line.strip():

                blank_count += 1

                if blank_count <= 1:
                    result.append("")

            else:

                blank_count = 0
                result.append(line)

        return "\n".join(result)

    # -------------------------------------------------
    # Markdown Cleanup
    # -------------------------------------------------

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """
        Normalize common Markdown patterns without
        changing the actual content.
        """

        lines = text.split("\n")
        cleaned = []

        for line in lines:

            stripped = line.strip()

            # Normalize Markdown headings.
            if stripped.startswith("####"):
                line = "###" + stripped[4:]

            elif stripped.startswith("###"):
                line = "###" + stripped[3:]

            elif stripped.startswith("##"):
                line = "##" + stripped[2:]

            elif stripped.startswith("#"):
                line = "#" + stripped[1:]

            # Normalize bullet styles.
            elif re.match(r"^[•▪◦]\s+", stripped):
                line = re.sub(
                    r"^[•▪◦]\s+",
                    "- ",
                    stripped
                )

            cleaned.append(line)

        return "\n".join(cleaned)

    # -------------------------------------------------
    # Number Formatting
    # -------------------------------------------------

    @staticmethod
    def _format_numbers(text: str) -> str:
        """
        Improve readability of large plain numbers.

        Examples:

        245678934
        → 245,678,934

        1234567.89
        → 1,234,567.89

        Numbers already containing commas are left alone.
        """

        def replace_number(match):

            prefix = match.group(1) or ""
            number = match.group(2)

            # Don't modify numbers that are part of words.
            start = match.start()

            # Avoid years such as 2024 / 2025.
            if len(number.split(".")[0]) == 4:
                try:
                    year = int(number.split(".")[0])

                    if 1900 <= year <= 2100:
                        return prefix + number
                except ValueError:
                    pass

            # Avoid decimal values with too many formatting risks.
            try:
                if "." in number:

                    integer_part, decimal_part = number.split(".", 1)

                    formatted_integer = f"{int(integer_part):,}"

                    return (
                        prefix
                        + formatted_integer
                        + "."
                        + decimal_part
                    )

                return prefix + f"{int(number):,}"

            except ValueError:
                return match.group(0)

        # Match standalone numbers that don't already contain commas.
        pattern = r"(?<![\w,])([₹$€£]?\s*)(\d+(?:\.\d+)?)(?![\w,])"

        return re.sub(
            pattern,
            replace_number,
            text
        )


# -----------------------------------------------------
# Convenience Function
# -----------------------------------------------------

def format_response(response: Any) -> str:
    """
    Convenience wrapper around ResponseFormatter.format().
    """

    return ResponseFormatter.format(response)