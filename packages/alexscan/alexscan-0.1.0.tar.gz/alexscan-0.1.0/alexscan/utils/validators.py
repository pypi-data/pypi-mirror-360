import re


def is_valid_domain(domain: str) -> bool:
    """
    Validate if a string is a valid domain name.

    Args:
        domain: The domain string to validate

    Returns:
        True if domain is valid, False otherwise
    """
    if not domain or len(domain) > 253:
        return False

    # Remove trailing dot if present
    if domain.endswith("."):
        domain = domain[:-1]

    # Check for valid characters and format
    pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"

    if not re.match(pattern, domain):
        return False

    # Check each label length
    labels = domain.split(".")
    for label in labels:
        if not label or len(label) > 63:
            return False

    return True
