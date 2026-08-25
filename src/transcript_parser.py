"""
Transcript parsing utilities for Kalam CX.

This module is responsible only for cleaning and organizing the raw text of
a call transcript before it enters the analysis pipeline. It strips
extraneous whitespace and normalizes blank lines while preserving the
actual conversation content.

It does NOT perform sentiment analysis, categorization, disposition or
priority determination, summary generation, AI analysis, grounding, safety
checks, decision making, customer lookup, or handbook rule retrieval.
"""

import re


def parse_transcript(transcript: str) -> str:
    """Clean and normalize a raw call transcript.

    This performs simple text hygiene only:
        - Strips leading/trailing whitespace from the transcript as a whole.
        - Strips trailing whitespace from each line.
        - Collapses runs of multiple blank lines into a single blank line.

    It does not analyze, interpret, or alter the conversational content.

    Args:
        transcript: The raw transcript text.

    Returns:
        The cleaned transcript string.

    Raises:
        TypeError: If transcript is not a string.
        ValueError: If transcript is empty or contains only whitespace.
    """
    if not isinstance(transcript, str):
        raise TypeError("transcript must be a string")

    if not transcript.strip():
        raise ValueError("transcript must not be empty or whitespace-only")

    # Remove trailing whitespace from each line while preserving content.
    lines = [line.rstrip() for line in transcript.splitlines()]
    normalized = "\n".join(lines)

    # Collapse three or more consecutive newlines (i.e. multiple blank
    # lines) down to a single blank line (two newlines).
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()
