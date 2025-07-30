"""Date extraction utilities for html2rss_ai."""

import logging
import re
from datetime import datetime, timezone

from bs4 import Tag


def extract_publication_date(
    container: Tag,
    date_selectors: list[str],
) -> str | None:
    """
    Extract publication date from a container element using various selectors.

    Args:
        container: BeautifulSoup Tag containing the article
        date_selectors: List of CSS selectors to try for finding dates

    Returns:
        ISO formatted date string if found, None otherwise
    """
    if not container:
        return None

    # Try each date selector
    for selector in date_selectors:
        try:
            elements = container.select(selector)
            for element in elements:
                date_str = _extract_date_from_element(element)
                if date_str:
                    return date_str
        except Exception as e:
            logging.debug(f"Error processing selector '{selector}': {e}")
            continue

    # Fallback: search for common date patterns in text
    return _extract_date_from_text(container.get_text())


def _extract_date_from_element(element: Tag) -> str | None:
    """Extract date from a single HTML element."""
    # Check for datetime attribute first
    if element.name == "time" and element.get("datetime"):
        datetime_attr = element.get("datetime")
        if isinstance(datetime_attr, str):
            return _normalize_date(datetime_attr)

    # Check for data attributes
    for attr in ["data-date", "data-published", "data-timestamp"]:
        attr_value = element.get(attr)
        if attr_value and isinstance(attr_value, str):
            return _normalize_date(attr_value)

    # Extract from element text
    text = element.get_text(strip=True)
    return _extract_date_from_text(text)


def _extract_date_from_text(text: str) -> str | None:
    """Extract date from text using regex patterns."""
    if not text:
        return None

    # Common date patterns
    patterns = [
        # ISO format: 2024-01-15
        r"(\d{4}-\d{2}-\d{2})",
        # US format: January 15, 2024 or Jan 15, 2024
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        # European format: 15 January 2024
        r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        # Slash format: 01/15/2024 or 15/01/2024
        r"(\d{1,2}/\d{1,2}/\d{4})",
        # Dot format: 15.01.2024
        r"(\d{1,2}\.\d{1,2}\.\d{4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _normalize_date(match.group(1))

    return None


def _normalize_date(date_str: str) -> str | None:
    """Normalize various date formats to ISO format."""
    if not date_str:
        return None

    # Remove extra whitespace
    date_str = date_str.strip()

    # Try to parse various formats
    formats = [
        "%Y-%m-%d",  # 2024-01-15
        "%Y-%m-%dT%H:%M:%S",  # 2024-01-15T10:30:00
        "%Y-%m-%dT%H:%M:%SZ",  # 2024-01-15T10:30:00Z
        "%B %d, %Y",  # January 15, 2024
        "%b %d, %Y",  # Jan 15, 2024
        "%d %B %Y",  # 15 January 2024
        "%d %b %Y",  # 15 Jan 2024
        "%m/%d/%Y",  # 01/15/2024
        "%d/%m/%Y",  # 15/01/2024
        "%d.%m.%Y",  # 15.01.2024
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Return original if no format matches
    return date_str
