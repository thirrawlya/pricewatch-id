import re


def parse_price(value):
    """Parse Indonesian price string into integer rupiah value."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.lower()
    text = text.replace("rp", "")
    text = text.replace("idr", "")
    text = text.replace(" ", "")
    text = re.sub(r"[^0-9.,]", "", text)

    if not text:
        return None

    # Remove thousand separators and normalize decimal separators.
    if "." in text and "," in text:
        text = text.replace(".", "")
        text = text.replace(",", ".")
    else:
        text = re.sub(r"[^0-9]", "", text)

    if not text:
        return None

    try:
        return int(float(text))
    except ValueError:
        return None


def parse_rating(value):
    """Parse rating string into float rating value."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = re.sub(r"[^0-9,\.]", "", text)
    if not text:
        return None

    text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def parse_sold(value):
    """Parse sold count string into integer quantity."""
    if value is None:
        return None

    text = str(value).strip().lower()
    if not text:
        return None

    text = text.replace("terjual", "")
    text = text.replace("+", "")
    text = text.strip()

    if not text:
        return None

    # Handle thousands shorthand like "2 rb" or "2rb".
    match = re.search(r"([0-9.,]+)\s*(rb|ribu)", text)
    if match:
        raw_number = match.group(1)
        raw_number = raw_number.replace(".", "").replace(",", ".")
        try:
            return int(float(raw_number) * 1000)
        except ValueError:
            return None

    # Handle normal numeric values.
    sanitized = re.sub(r"[^0-9]", "", text)
    if not sanitized:
        return None

    try:
        return int(sanitized)
    except ValueError:
        return None
