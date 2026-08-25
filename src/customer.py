"""
Customer lookup utilities for Kalam CX.

This module implements the Customer Lookup component described in
docs/System_Architecture.md. It uses a customer ID to find the matching
customer record within an already-loaded list of customer dictionaries and
converts it into the CustomerData model.

It does NOT load files from disk (that is the responsibility of
src.loader), and it does NOT perform AI logic, sentiment analysis,
categorization, handbook retrieval, transcript parsing, validation, safety
checks, decision logic, or database logic.
"""

from typing import List, Optional

from src.schemas import CustomerData


def get_customer(
    customer_id: Optional[str],
    customers: List[dict],
) -> Optional[CustomerData]:
    """Look up a customer by ID from a list of customer records.

    Args:
        customer_id: The unique identifier of the customer to find.
            May be None for non-interaction calls.
        customers: A list of customer dictionaries (already loaded), each
            expected to contain a "customer_id" key along with the other
            fields required by the CustomerData model.

    Returns:
        A CustomerData object built from the matching customer dictionary,
        or None if customer_id is None.

    Raises:
        TypeError: If customer_id is not a string or None.
        ValueError: If customer_id is empty or whitespace-only.
        LookupError: If no customer with a matching customer_id is found.
    """
    if customer_id is None:
        return None

    if not isinstance(customer_id, str):
        raise TypeError("customer_id must be a string")

    if not customer_id.strip():
        raise ValueError("customer_id must not be empty or whitespace-only")

    for customer in customers:
        if customer.get("customer_id") == customer_id:
            return CustomerData(**customer)

    raise LookupError(f"No customer found with customer_id: {customer_id}")


def detect_repeat_contact(
    customer: Optional[CustomerData],
    transcript_lower: str,
) -> Optional[dict]:
    """Detect whether a customer has previous open tickets related to
    the same issue (repeat contact).

    Args:
        customer: CustomerData object or None.
        transcript_lower: Lowercased transcript text.

    Returns:
        A dict with repeat-contact info if a repeat contact is detected,
        else None. Example: {"ticket": "T-8801", "issue": "home internet keeps dropping"}
    """
    if customer is None:
        return None

    for ticket in customer.open_tickets:
        issue = ticket.get("issue", "").lower()
        if issue and issue in transcript_lower:
            return ticket

    return None


def get_customer_context(
    customer: Optional[CustomerData],
) -> dict:
    """Build a context dict summarizing a customer's relevant attributes.

    Args:
        customer: CustomerData object or None.

    Returns:
        A dict with keys: client, tier, is_priority_tier, has_open_tickets,
        repeat_contact.
    """
    if customer is None:
        return {
            "client": "unknown",
            "tier": "unknown",
            "is_priority_tier": False,
            "has_open_tickets": False,
            "repeat_contact": False,
        }

    return {
        "client": customer.client,
        "tier": customer.tier,
        "is_priority_tier": customer.is_priority_tier,
        "has_open_tickets": customer.has_open_tickets,
        "open_tickets": customer.open_tickets,
        "repeat_contact": customer.has_open_tickets,
    }
