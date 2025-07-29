import logging
import re
from datetime import datetime

from bs4 import BeautifulSoup, Tag


def _sanitize_selector(sel: str) -> str:
    """Convert class names containing dots (e.g. '.my-1.5') into attribute selectors.

    BeautifulSoup's CSS engine cannot parse class names that themselves contain
    dots because '.' is the class separator. Replace occurrences like
    '.my-1.5' with '[class~="my-1.5"]'.
    """
    return re.sub(
        r"\.([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)",
        lambda m: f'[class~="{m.group(1)}"]',
        sel,
    )


def _month_name_to_number(month_name: str) -> str | None:
    """Convert full month name to number."""
    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
    }
    return months.get(month_name.lower())


def _month_abbr_to_number(month_abbr: str) -> str | None:
    """Convert abbreviated month name to number."""
    months = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }
    return months.get(month_abbr.lower())


def _standardize_date(date_str: str) -> str | None:
    """Standardize date to YYYY-MM-DD format."""
    if not date_str:
        return None

    current_year = datetime.now().year

    try:
        # Already ISO format
        if re.match(r"^\d{4}-\d{2}-\d{2}", date_str):
            return date_str.split("T")[0]

        # YYYY-MM-DD HH:MM:SS
        if re.match(r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}", date_str):
            return date_str.split(" ")[0]

        # MM-DD format
        if re.match(r"^\d{2}-\d{2}$", date_str):
            month, day = date_str.split("-")
            return f"{current_year}-{month}-{day}"

        # M-DD format
        if re.match(r"^\d{1,2}-\d{1,2}$", date_str):
            month, day = date_str.split("-")
            return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"

        # MM/DD/YYYY format
        if re.match(r"^\d{1,2}/\d{1,2}/\d{4}", date_str):
            parts = date_str.split("/")
            month, day, year = parts[0], parts[1], parts[2]
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Month DD, YYYY format
        month_match = re.match(r"(\w+)\s+(\d{1,2}),\s+(\d{4})", date_str)
        if month_match:
            month_name, day, year = month_match.groups()
            month_num = _month_name_to_number(month_name)
            if month_num:
                return f"{year}-{month_num.zfill(2)}-{day.zfill(2)}"

        # DD Month YYYY format
        day_month_match = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_str)
        if day_month_match:
            day, month_name, year = day_month_match.groups()
            month_num = _month_name_to_number(month_name)
            if month_num:
                return f"{year}-{month_num.zfill(2)}-{day.zfill(2)}"

        # Mon DD, YYYY format
        short_month_match = re.match(r"(\w{3})\s+(\d{1,2}),\s+(\d{4})", date_str)
        if short_month_match:
            month_abbr, day, year = short_month_match.groups()
            month_num = _month_abbr_to_number(month_abbr)
            if month_num:
                return f"{year}-{month_num.zfill(2)}-{day.zfill(2)}"

        return date_str

    except Exception:
        return date_str


def _is_valid_date_text(text: str) -> bool:
    """Check if text looks like a valid date."""
    if not text or len(text) < 2:
        return False

    date_patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{2}-\d{2}\b",
        r"\b\d{1,2}-\d{1,2}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        r"\b\d{1,2}\s+\w+\s+\d{4}\b",
        r"\b\w+\s+\d{1,2},\s+\d{4}\b",
        r"\b\w{3}\s+\d{1,2},\s+\d{4}\b",
        r"\b\d{4}\b",
    ]

    return any(re.search(pattern, text) for pattern in date_patterns)


def _extract_date_from_text(text: str) -> str | None:
    """Extract date from text using regex patterns."""
    if not text:
        return None

    date_patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",  # 2024-01-15
        r"\b\d{2}-\d{2}\b",  # 06-17
        r"\b\d{1,2}-\d{1,2}\b",  # 6-17
        r"\b\d{2}/\d{2}/\d{4}\b",  # 01/15/2024
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # 1/15/2024
        r"\b\d{1,2}\s+\w+\s+\d{4}\b",  # 15 January 2024
        r"\b\w+\s+\d{1,2},\s+\d{4}\b",  # January 15, 2024
        r"\b\w{3}\s+\d{1,2},\s+\d{4}\b",  # Jan 15, 2024
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            found_date = match.group(0)
            return _standardize_date(found_date)

    return None


def extract_publication_date(
    container: BeautifulSoup | Tag,
    date_selectors: list[str],
) -> str | None:
    """Extract publication date from container element."""
    if not container or not date_selectors:
        return None

    # Try each date selector
    for selector in date_selectors:
        current_selector = selector
        date_elements = container.select("")  # Initialize with empty result

        for attempt in range(2):  # at most one sanitized retry
            try:
                date_elements = container.select(current_selector)
                break  # success
            except Exception as exc:
                logging.debug("Date selector '%s' raised %s", current_selector, exc)
                if attempt == 0:
                    # Try sanitized version once
                    current_selector = _sanitize_selector(selector)
                    if current_selector != selector:
                        logging.debug(
                            "Retrying date selector with sanitized version '%s'",
                            current_selector,
                        )
                        continue
                # If we reach here, both attempts failed
                date_elements = container.select("")  # Empty result
                break

        if not date_elements:
            # Try fallback selectors
            general_selectors = [
                "time",
                "[datetime]",
                ".date",
                ".published",
                ".created",
            ]
            for gen_sel in general_selectors:
                date_elements = container.select(gen_sel)
                if date_elements:
                    break

        for date_element in date_elements:
            # Check datetime attribute
            datetime_attr = date_element.get("datetime")
            if datetime_attr:
                return _standardize_date(str(datetime_attr))

            # Check element text
            date_text = date_element.get_text(strip=True)
            if date_text and _is_valid_date_text(date_text):
                return _standardize_date(date_text)

            # For time elements
            if date_element.name == "time" and date_text:
                return _standardize_date(date_text)

    # Fallback: search container text for date patterns
    return _extract_date_from_text(container.get_text())
