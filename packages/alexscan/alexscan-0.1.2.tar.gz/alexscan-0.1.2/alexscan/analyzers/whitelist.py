"""Whitelist analyzer for domain reputation checking against trusted sources."""

import csv
import io
import zipfile
from typing import Any, Dict
from urllib.parse import urlparse

import requests

from .base import BaseAnalyzer


class WhitelistAnalyzer(BaseAnalyzer):
    """Analyzer for checking domains against trusted whitelist sources."""

    def __init__(self, timeout: int = 10):
        super().__init__("whitelist", "Check domain against trusted whitelist sources")
        self.timeout = timeout
        self.whitelist_sources = {
            "cisco_umbrella": {
                "name": "Cisco Umbrella Top 1M",
                "url": "https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip",
                "description": "Cisco Umbrella's top 1 million most popular domains",
                "format": "zip_csv",
                "domain_column": 1,
            },
            "majestic_million": {
                "name": "Majestic Million",
                "url": "https://downloads.majestic.com/majestic_million.csv",
                "description": "Majestic's top 1 million domains by backlink count",
                "format": "csv",
                "domain_column": 2,
            },
            "tranco": {
                "name": "Tranco List",
                "url": "https://tranco-list.eu/top-1m.csv.zip",
                "description": "Research-oriented top sites ranking",
                "format": "zip_csv",
                "domain_column": 1,
            },
        }

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze domain against whitelist sources.

        Args:
            domain: Domain to check

        Returns:
            Dictionary containing whitelist analysis results
        """
        # Normalize domain
        normalized_domain = self._normalize_domain(domain)

        whitelist_status = {}
        summary = {
            "total_lists_checked": 0,
            "whitelisted_count": 0,
            "not_whitelisted_count": 0,
            "error_count": 0,
        }

        for source_id, source_info in self.whitelist_sources.items():
            try:
                result = self._check_whitelist_source(normalized_domain, source_id, source_info)
                whitelist_status[source_id] = result
                summary["total_lists_checked"] += 1

                if result.get("whitelisted"):
                    summary["whitelisted_count"] += 1
                elif result.get("error"):
                    summary["error_count"] += 1
                else:
                    summary["not_whitelisted_count"] += 1

            except Exception as e:
                whitelist_status[source_id] = {
                    "name": source_info["name"],
                    "whitelisted": False,
                    "error": str(e),
                    "description": source_info["description"],
                }
                summary["error_count"] += 1

        return {
            "domain": domain,
            "normalized_domain": normalized_domain,
            "whitelist_status": whitelist_status,
            "summary": summary,
        }

    def _check_whitelist_source(self, domain: str, source_id: str, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check domain against a specific whitelist source."""
        try:
            domains_list = self._fetch_whitelist_domains(source_info)
            whitelisted = domain in domains_list

            result = {
                "name": source_info["name"],
                "whitelisted": whitelisted,
                "description": source_info["description"],
                "source_url": source_info["url"],
            }

            if whitelisted:
                result["details"] = f"Domain found in {source_info['name']} trusted domains list"

            return result

        except Exception as e:
            return {
                "name": source_info["name"],
                "whitelisted": False,
                "error": str(e),
                "description": source_info["description"],
                "source_url": source_info["url"],
            }

    def _fetch_whitelist_domains(self, source_info: Dict[str, Any]) -> set:
        """Fetch domains from whitelist source."""
        url = source_info["url"]
        format_type = source_info["format"]
        domain_column = source_info["domain_column"]

        response = requests.get(url, timeout=self.timeout, stream=True)
        response.raise_for_status()

        domains = set()

        if format_type == "zip_csv":
            # Handle ZIP files containing CSV
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Get first CSV file in ZIP
                csv_files = [f for f in zip_file.namelist() if f.endswith(".csv")]
                if not csv_files:
                    raise ValueError("No CSV file found in ZIP archive")

                with zip_file.open(csv_files[0]) as csv_file:
                    content = csv_file.read().decode("utf-8")
                    reader = csv.reader(io.StringIO(content))

                    for row in reader:
                        if len(row) > domain_column:
                            domain = row[domain_column].strip().lower()
                            if domain and self._is_valid_domain_format(domain):
                                domains.add(domain)

        elif format_type == "csv":
            # Handle direct CSV files
            content = response.text
            reader = csv.reader(io.StringIO(content))

            for row in reader:
                if len(row) > domain_column:
                    domain = row[domain_column].strip().lower()
                    if domain and self._is_valid_domain_format(domain):
                        domains.add(domain)

        return domains

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for comparison."""
        # Remove protocol if present
        if "://" in domain:
            domain = urlparse(domain).netloc

        # Remove www prefix
        if domain.startswith("www."):
            domain = domain[4:]

        # Convert to lowercase
        domain = domain.lower().strip()

        # Remove trailing dot
        if domain.endswith("."):
            domain = domain[:-1]

        return domain

    def _is_valid_domain_format(self, domain: str) -> bool:
        """Basic validation of domain format."""
        if not domain or "." not in domain:
            return False

        # Skip entries that look like IPs or invalid formats
        if domain.replace(".", "").isdigit():
            return False

        # Skip entries with spaces or other invalid characters
        if " " in domain or "\t" in domain:
            return False

        return True

    def is_available(self) -> bool:
        """Check if whitelist analyzer is available."""
        try:
            # Test if we can make HTTP requests
            requests.get("https://httpbin.org/status/200", timeout=5)
            return True
        except Exception:
            return False


def analyze_domain_whitelists(domain: str) -> Dict[str, Any]:
    """
    Standalone function to analyze domain against whitelists.

    Args:
        domain: Domain to analyze

    Returns:
        Whitelist analysis results
    """
    analyzer = WhitelistAnalyzer()
    return analyzer.analyze(domain)
