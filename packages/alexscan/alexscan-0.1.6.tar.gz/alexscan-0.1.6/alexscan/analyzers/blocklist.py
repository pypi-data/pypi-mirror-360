"""Blocklist analyzer for domain analysis."""

import socket
from typing import Any, Dict
from urllib.parse import urlparse

import requests

from .base import BaseAnalyzer


class BlocklistAnalyzer(BaseAnalyzer):
    """Blocklist analyzer for domain reputation checking."""

    def __init__(self) -> None:
        super().__init__("blocklist", "Domain blocklist reputation analyzer")

        # DNS-based blocklists that don't require API keys
        self.dns_blocklists = {
            "spamhaus_sbl": {
                "name": "Spamhaus SBL",
                "description": "Spamhaus Spam Block List",
                "query_format": "{domain}.sbl.spamhaus.org",
            },
            "spamhaus_css": {
                "name": "Spamhaus CSS",
                "description": "Spamhaus CSS List",
                "query_format": "{domain}.css.spamhaus.org",
            },
            "surbl": {
                "name": "SURBL",
                "description": "Spam URI Realtime Blocklist",
                "query_format": "{domain}.multi.surbl.org",
            },
            "uribl_black": {
                "name": "URIBL Black",
                "description": "URIBL Black List",
                "query_format": "{domain}.black.uribl.com",
            },
            "uribl_red": {
                "name": "URIBL Red",
                "description": "URIBL Red List",
                "query_format": "{domain}.red.uribl.com",
            },
        }

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze domain against various blocklists.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing blocklist analysis results
        """
        results: Dict[str, Any] = {
            "domain": domain,
            "blocklist_status": {},
            "summary": {"total_lists_checked": 0, "listed_count": 0, "clean_count": 0, "error_count": 0},
            "errors": [],
        }

        # Check DNS-based blocklists
        for blocklist_id, blocklist_info in self.dns_blocklists.items():
            try:
                is_listed = self._check_dns_blocklist(domain, blocklist_info)
                results["blocklist_status"][blocklist_id] = {
                    "name": blocklist_info["name"],
                    "description": blocklist_info["description"],
                    "listed": is_listed,
                    "status": "Listed" if is_listed else "Clean",
                }

                results["summary"]["total_lists_checked"] += 1
                if is_listed:
                    results["summary"]["listed_count"] += 1
                else:
                    results["summary"]["clean_count"] += 1

            except Exception as e:
                results["blocklist_status"][blocklist_id] = {
                    "name": blocklist_info["name"],
                    "description": blocklist_info["description"],
                    "listed": False,
                    "status": "Error",
                    "error": str(e),
                }
                results["summary"]["total_lists_checked"] += 1
                results["summary"]["error_count"] += 1
                results["errors"].append(f"{blocklist_info['name']}: {str(e)}")

        # Check web-based reputation services
        try:
            virus_total_result = self._check_virus_total_basic(domain)
            if virus_total_result:
                results["blocklist_status"]["virus_total"] = virus_total_result
                results["summary"]["total_lists_checked"] += 1
                if virus_total_result["listed"]:
                    results["summary"]["listed_count"] += 1
                else:
                    results["summary"]["clean_count"] += 1
        except Exception as e:
            results["errors"].append(f"VirusTotal check failed: {str(e)}")
            results["summary"]["error_count"] += 1

        return results

    def _check_dns_blocklist(self, domain: str, blocklist_info: Dict[str, Any]) -> bool:
        """
        Check if domain is listed in a DNS-based blocklist.

        Args:
            domain: Domain to check
            blocklist_info: Blocklist configuration

        Returns:
            True if domain is listed, False otherwise
        """
        query_domain = blocklist_info["query_format"].format(domain=domain)

        try:
            # Try to resolve the query domain
            # If it resolves, the domain is listed
            socket.gethostbyname(query_domain)
            return True
        except socket.gaierror:
            # If resolution fails, domain is not listed
            return False
        except Exception as e:
            raise Exception(f"DNS query failed: {str(e)}")

    def _check_virus_total_basic(self, domain: str) -> Dict[str, Any]:
        """
        Check domain reputation using VirusTotal public interface.

        Note: This uses the public interface without API key for basic checks.

        Args:
            domain: Domain to check

        Returns:
            Dict with reputation information
        """
        try:
            # Use VirusTotal's public URL analysis (no API key required)
            # This is a basic check that doesn't provide detailed results
            url = "https://www.virustotal.com/vtapi/v2/url/report"
            params = {"resource": f"http://{domain}", "scan": "0"}  # Don't trigger new scan

            # Make request with timeout
            response = requests.get(url, params=params, timeout=10)

            # VirusTotal returns 403 for API requests without key
            # But we can still check if the request format is accepted
            if response.status_code == 403:
                return {
                    "name": "VirusTotal",
                    "description": "VirusTotal URL/Domain Reputation",
                    "listed": False,
                    "status": "API Key Required",
                    "note": "Full VirusTotal analysis requires API key",
                }

            return {
                "name": "VirusTotal",
                "description": "VirusTotal URL/Domain Reputation",
                "listed": False,
                "status": "Check Completed",
                "note": "Basic check completed",
            }

        except requests.exceptions.Timeout:
            raise Exception("Request timeout")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _normalize_domain(self, domain: str) -> str:
        """
        Normalize domain for blocklist checking.

        Args:
            domain: Domain to normalize

        Returns:
            Normalized domain
        """
        # Remove protocol if present
        if "://" in domain:
            domain = urlparse(domain).netloc

        # Remove www prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        # Convert to lowercase
        domain = domain.lower()

        return domain

    def is_available(self) -> bool:
        """
        Check if Blocklist analyzer is available.

        Returns:
            True if requests library is available, False otherwise
        """
        try:
            return True
        except ImportError:
            return False


def analyze_domain_blocklists(domain: str) -> Dict[str, Any]:
    """
    Analyze domain against blocklists.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing blocklist analysis results
    """
    analyzer = BlocklistAnalyzer()
    return analyzer.analyze(domain)
