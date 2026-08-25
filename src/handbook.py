"""
Handbook retrieval utilities for Kalam CX.

This module retrieves handbook rules that match a given call. It supports
both category-based retrieval (legacy) and keyword-based relevance search
for transcript-driven classification.

It does not load files from disk, perform AI analysis, validate data,
make decisions, or perform any safety logic.
"""

from typing import List

from src.schemas import HandbookRule


def get_handbook_rules(
    category: str,
    rules: List[dict],
) -> List[HandbookRule]:
    """Retrieve handbook rules matching a category.

    Args:
        category: The call category used to find relevant rules.
        rules: Already-loaded handbook rule dictionaries.

    Returns:
        A list of matching HandbookRule objects.

    Raises:
        TypeError: If category is not a string.
        ValueError: If category is empty or whitespace-only.
        LookupError: If no matching rules are found.
    """
    if not isinstance(category, str):
        raise TypeError("category must be a string")

    if not category.strip():
        raise ValueError("category must not be empty or whitespace-only")

    matching_rules = [
        HandbookRule(**rule)
        for rule in rules
        if rule.get("category") == category
    ]

    if not matching_rules:
        raise LookupError(
            f"No handbook rules found for category: {category}"
        )

    return matching_rules


def get_all_rules(rules: List[dict]) -> List[HandbookRule]:
    """Convert all raw rule dicts into HandbookRule objects.

    Args:
        rules: Already-loaded handbook rule dictionaries.

    Returns:
        A list of all HandbookRule objects.
    """
    return [HandbookRule(**rule) for rule in rules]


def get_rules_by_section(section: str, rules: List[HandbookRule]) -> List[HandbookRule]:
    """Retrieve rules belonging to a specific handbook section.

    Args:
        section: The handbook section name (e.g. "taxonomy", "escalation").
        rules: A list of HandbookRule objects.

    Returns:
        A list of matching HandbookRule objects.
    """
    return [rule for rule in rules if rule.section == section]


def search_by_keywords(transcript_lower: str, rules: List[HandbookRule]) -> List[HandbookRule]:
    """Find taxonomy rules whose keywords appear in the transcript.

    Args:
        transcript_lower: Lowercased transcript text.
        rules: A list of HandbookRule objects.

    Returns:
        A list of HandbookRule objects ordered by keyword match count
        (descending).
    """
    scored: list[tuple[int, HandbookRule]] = []

    for rule in rules:
        if not rule.keywords:
            continue
        count = sum(1 for kw in rule.keywords if kw in transcript_lower)
        if count > 0:
            scored.append((count, rule))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [rule for _, rule in scored]


def get_rule_by_id(rule_id: str, rules: List[HandbookRule]) -> HandbookRule:
    """Retrieve a single handbook rule by its clause ID.

    Args:
        rule_id: The clause/rule identifier (e.g. "0.4", "4.1").
        rules: A list of HandbookRule objects.

    Returns:
        The matching HandbookRule.

    Raises:
        ValueError: If rule_id is empty.
        LookupError: If no rule with the given ID is found.
    """
    if not rule_id or not rule_id.strip():
        raise ValueError("rule_id must not be empty")

    for rule in rules:
        if rule.rule_id == rule_id:
            return rule

    raise LookupError(f"No handbook rule found with rule_id: {rule_id}")
