"""WHOIS analyzer for domain analysis."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import whois

from .base import BaseAnalyzer


class WHOISAnalyzer(BaseAnalyzer):
    """WHOIS analyzer for domain registration information."""

    def __init__(self) -> None:
        super().__init__("whois", "WHOIS domain registration analyzer")

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze WHOIS information for a domain.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing WHOIS analysis results
        """
        results: Dict[str, Any] = {"domain": domain, "whois_data": {}, "errors": []}

        try:
            whois_data = self._query_whois(domain)

            if whois_data:
                # Extract key information
                parsed_data = self._parse_whois_data(whois_data)
                results["whois_data"] = parsed_data
            else:
                results["errors"].append("No WHOIS data available for domain")

        except Exception as e:
            results["errors"].append(f"WHOIS lookup failed: {str(e)}")

        return results

    def _query_whois(self, domain: str) -> Optional[whois.WhoisEntry]:
        """
        Query WHOIS information for a domain.

        Args:
            domain: Domain to query

        Returns:
            WHOIS entry object or None if failed
        """
        try:
            return whois.whois(domain)
        except whois.parser.PywhoisError as e:
            raise Exception(f"WHOIS query failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during WHOIS lookup: {str(e)}")

    def _parse_whois_data(self, whois_data: whois.WhoisEntry) -> Dict[str, Any]:
        """
        Parse WHOIS data into structured format.

        Args:
            whois_data: Raw WHOIS data

        Returns:
            Structured WHOIS information
        """
        parsed: Dict[str, Any] = {}

        # Registrar information
        if hasattr(whois_data, "registrar") and whois_data.registrar:
            parsed["registrar"] = self._format_field(whois_data.registrar)

        # Creation date
        if hasattr(whois_data, "creation_date") and whois_data.creation_date:
            parsed["creation_date"] = self._format_date(whois_data.creation_date)

        # Expiry date
        if hasattr(whois_data, "expiration_date") and whois_data.expiration_date:
            parsed["expiry_date"] = self._format_date(whois_data.expiration_date)

        # Updated date
        if hasattr(whois_data, "updated_date") and whois_data.updated_date:
            parsed["updated_date"] = self._format_date(whois_data.updated_date)

        # Name servers
        if hasattr(whois_data, "name_servers") and whois_data.name_servers:
            parsed["name_servers"] = self._format_name_servers(whois_data.name_servers)

        # Status
        if hasattr(whois_data, "status") and whois_data.status:
            parsed["status"] = self._format_field(whois_data.status)

        # Registrant organization
        if hasattr(whois_data, "org") and whois_data.org:
            parsed["organization"] = self._format_field(whois_data.org)

        # Country
        if hasattr(whois_data, "country") and whois_data.country:
            parsed["country"] = self._format_field(whois_data.country)

        return parsed

    def _format_field(self, field: Any) -> str:
        """Format a WHOIS field value."""
        if isinstance(field, list):
            return field[0] if field else ""
        return str(field) if field else ""

    def _format_date(self, date_field: Any) -> str:
        """Format a date field from WHOIS data."""
        if isinstance(date_field, list):
            date_field = date_field[0] if date_field else None

        if isinstance(date_field, datetime):
            return date_field.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date_field, str):
            return date_field

        return ""

    def _format_name_servers(self, name_servers: Any) -> List[str]:
        """Format name servers from WHOIS data."""
        if not name_servers:
            return []

        if isinstance(name_servers, list):
            return [ns.lower() for ns in name_servers if ns]

        return [name_servers.lower()]

    def is_available(self) -> bool:
        """
        Check if WHOIS analyzer is available.

        Returns:
            True if python-whois is available, False otherwise
        """
        try:
            return True
        except ImportError:
            return False


def analyze_whois_records(domain: str) -> Dict[str, Any]:
    """
    Analyze WHOIS records for a domain.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing WHOIS analysis results
    """
    analyzer = WHOISAnalyzer()
    return analyzer.analyze(domain)
