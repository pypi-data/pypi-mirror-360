"""HTTP Headers analyzer for domain analysis (enhanced)."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

import requests

from .base import BaseAnalyzer


class HeadersAnalyzer(BaseAnalyzer):
    """HTTP Headers analyzer for security-relevant header analysis (multi-endpoint, weighted scoring)."""

    def __init__(self) -> None:
        super().__init__("headers", "HTTP response headers analyzer")
        self._endpoints = ["", "www.", "login."]  # Common subdomain prefixes to check
        self._paths = ["", "/login", "/admin"]  # Common paths to probe

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze HTTP response headers for a domain.

        Args:
            domain: The domain to analyze.

        Returns:
            Dict containing HTTP headers analysis results.
        """
        results: Dict[str, Any] = {
            "domain": domain,
            "headers_data": {},
            "errors": [],
        }

        # Aggregate data from multiple endpoints
        aggregated_headers: Dict[str, Any] = {
            "all_headers": {},
            "security_headers": {},
            "missing_headers": [],
            "security_score": 0,
            "total_security_headers": 0,
            "implemented_security_headers": 0,
        }
        try:
            futures = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                for sub in self._endpoints:
                    for path in self._paths:
                        full_domain = "{}{}{}".format(sub, domain, path)
                        futures.append(executor.submit(self._get_http_headers, full_domain))

                collected_headers = []
                for future in as_completed(futures):
                    headers = future.result()
                    if headers:
                        collected_headers.append(headers)

                if collected_headers:
                    # Merge all headers for analysis
                    for hdr in collected_headers:
                        aggregated_headers["all_headers"].update(hdr)

                    analyzed = self._analyze_security_headers(aggregated_headers["all_headers"])
                    aggregated_headers.update(analyzed)
                else:
                    results["errors"].append("No HTTP headers found across scanned endpoints")

        except Exception as e:
            results["errors"].append("HTTP headers analysis failed: {}".format(e))

        results["headers_data"] = aggregated_headers
        return results

    def _get_http_headers(self, domain: str, timeout: int = 10) -> Optional[Dict[str, str]]:
        """
        Fetch HTTP response headers for a domain, trying HTTPS first then HTTP.

        Args:
            domain: Domain to analyze.
            timeout: Request timeout in seconds.

        Returns:
            Dictionary of headers or None if failed.
        """
        for scheme in ("https", "http"):
            try:
                response = requests.get("{}://{}".format(scheme, domain), timeout=timeout, allow_redirects=True)
                if response.status_code < 400:
                    return dict(response.headers)
            except requests.exceptions.SSLError:
                continue  # Try HTTP if HTTPS fails
            except requests.RequestException:
                return None
        return None

    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze security-relevant HTTP headers with weighted scoring.

        Args:
            headers: Raw HTTP headers dictionary.

        Returns:
            Analyzed headers with security assessments.
        """
        security_headers = self._security_headers_spec()
        total = len(security_headers)
        implemented = 0
        weighted_score = 0
        total_weight = 0

        analyzed = {
            "all_headers": headers,
            "security_headers": {},
            "missing_headers": [],
            "security_score": 0,
            "total_security_headers": total,
            "implemented_security_headers": 0,
        }

        for name, meta in security_headers.items():
            weight = meta.get("weight", 1)
            total_weight += weight
            if name in headers:
                value = headers[name]
                assessment = self._assess_header_security(name, value)

                analyzed["security_headers"][name] = {
                    "value": value,
                    "description": meta["description"],
                    "category": meta["category"],
                    "assessment": assessment,
                    "recommendation": meta["recommendation"],
                }

                if assessment in ("Strong", "Good"):
                    implemented += 1
                    weighted_score += weight
            else:
                analyzed["missing_headers"].append(
                    {
                        "name": name,
                        "description": meta["description"],
                        "category": meta["category"],
                        "recommendation": meta["recommendation"],
                    }
                )

        if total_weight:
            analyzed["security_score"] = round((weighted_score / total_weight) * 100)
            analyzed["implemented_security_headers"] = implemented

        return analyzed

    def _assess_header_security(self, name: str, value: str) -> str:
        """
        Assess the security strength of a header value.

        Args:
            name: Name of the header.
            value: Value of the header.

        Returns:
            Security assessment: Missing, Weak, Good, Strong, or Recommended.
        """
        value = value.lower()

        if name == "Content-Security-Policy":
            if "default-src 'none'" in value or "default-src 'self'" in value:
                return "Strong"
            if "default-src" in value:
                return "Good"
            return "Weak"
        elif name == "Strict-Transport-Security":
            if "max-age=31536000" in value and "includesubdomains" in value:
                return "Strong"
            if "max-age=" in value:
                return "Good"
            return "Weak"
        elif name == "X-Content-Type-Options":
            return "Strong" if "nosniff" in value else "Weak"
        elif name == "X-Frame-Options":
            if "deny" in value:
                return "Strong"
            if "sameorigin" in value:
                return "Good"
            return "Weak"
        elif name == "X-XSS-Protection":
            if "1; mode=block" in value:
                return "Strong"
            if "1" in value:
                return "Good"
            return "Weak"
        elif name == "Referrer-Policy":
            if "no-referrer" in value or "strict-origin" in value:
                return "Strong"
            if "origin" in value or "origin-when-cross-origin" in value:
                return "Good"
            return "Weak"
        elif name == "Permissions-Policy":
            if "geolocation=(), microphone=(), camera=()" in value:
                return "Strong"
            if "geolocation=" in value or "microphone=" in value:
                return "Good"
            return "Weak"
        elif name == "Server":
            return "Good" if value in ("", "nginx", "apache", "cloudflare") else "Weak"
        elif name == "X-Powered-By":
            return "Weak"
        elif name == "Cache-Control":
            if "no-cache" in value or "no-store" in value:
                return "Strong"
            if "max-age=" in value:
                return "Good"
            return "Weak"
        return "Recommended"

    def _security_headers_spec(self) -> Dict[str, Dict[str, Any]]:
        """
        Specification of security-relevant headers with weights.
        """
        return {
            "Content-Security-Policy": {
                "description": "Content Security Policy",
                "category": "Security",
                "recommendation": "Should be implemented to prevent XSS attacks",
                "weight": 3,
            },
            "Strict-Transport-Security": {
                "description": "HTTP Strict Transport Security",
                "category": "Security",
                "recommendation": "Should be implemented to enforce HTTPS",
                "weight": 3,
            },
            "X-Content-Type-Options": {
                "description": "X-Content-Type-Options",
                "category": "Security",
                "recommendation": "Should be set to 'nosniff' to prevent MIME type sniffing",
                "weight": 2,
            },
            "X-Frame-Options": {
                "description": "X-Frame-Options",
                "category": "Security",
                "recommendation": "Should be implemented to prevent clickjacking",
                "weight": 2,
            },
            "X-XSS-Protection": {
                "description": "X-XSS-Protection",
                "category": "Security",
                "recommendation": "Should be set to '1; mode=block' for XSS protection",
                "weight": 2,
            },
            "Referrer-Policy": {
                "description": "Referrer Policy",
                "category": "Privacy",
                "recommendation": "Should be implemented to control referrer information",
                "weight": 1,
            },
            "Permissions-Policy": {
                "description": "Permissions Policy",
                "category": "Privacy",
                "recommendation": "Should be implemented to control browser features",
                "weight": 1,
            },
            "Cache-Control": {
                "description": "Cache Control",
                "category": "Performance",
                "recommendation": "Should be configured appropriately for content type",
                "weight": 1,
            },
            "Server": {
                "description": "Server Information",
                "category": "Information Disclosure",
                "recommendation": "Should be hidden or generic to prevent information disclosure",
                "weight": 1,
            },
            "X-Powered-By": {
                "description": "X-Powered-By",
                "category": "Information Disclosure",
                "recommendation": "Should be removed to prevent technology disclosure",
                "weight": 1,
            },
        }

    def is_available(self) -> bool:
        """
        Check if HTTP headers analyzer is available.

        Returns:
            True as requests is a required dependency.
        """
        return True
