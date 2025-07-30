"""Domain Safety Rating Algorithm for AlexScan."""

from typing import Any, Dict, Tuple


class SafetyRatingCalculator:
    """Calculate domain safety rating based on analyzer results."""

    def __init__(self):
        self.rating_thresholds = {
            "safe": (70, 100),
            "likely_unsafe": (50, 70),
            "likely_malicious": (30, 50),
            "unsafe": (0, 30),
        }

    def calculate_analyzer_score(self, analyzer_name: str, analyzer_results: Dict[str, Any]) -> float:
        """
        Calculate safety score for a specific analyzer.

        Args:
            analyzer_name: Name of the analyzer
            analyzer_results: Results from the analyzer

        Returns:
            Safety score between 0-10
        """
        if not analyzer_results or analyzer_results.get("errors"):
            return 0.0

        if analyzer_name == "dns":
            return self._calculate_dns_score(analyzer_results)
        elif analyzer_name == "whois":
            return self._calculate_whois_score(analyzer_results)
        elif analyzer_name == "ssl":
            return self._calculate_ssl_score(analyzer_results)
        elif analyzer_name == "blocklist":
            return self._calculate_blocklist_score(analyzer_results)
        elif analyzer_name == "whitelist":
            return self._calculate_whitelist_score(analyzer_results)
        elif analyzer_name == "dga":
            return self._calculate_dga_score(analyzer_results)
        elif analyzer_name == "headers":
            return self._calculate_headers_score(analyzer_results)
        elif analyzer_name == "ports":
            return self._calculate_ports_score(analyzer_results)
        else:
            return 5.0  # Default neutral score

    def _calculate_dns_score(self, results: Dict[str, Any]) -> float:
        """Calculate DNS safety score."""
        score = 8.0

        try:
            records = results.get("records", {})

            # Check for essential records
            if "A" in records and records["A"].get("values"):
                score += 1.0

            if "MX" in records and records["MX"].get("values"):
                score += 0.5

            if "NS" in records and records["NS"].get("values"):
                score += 0.5

            # Check for security records
            if "TXT" in records:
                txt_values = records["TXT"].get("values", [])
                for txt in txt_values:
                    if "spf" in txt.lower():
                        score += 1.0
                        break
                    if "dmarc" in txt.lower():
                        score += 1.0
                        break

            # Check for IPv6 support
            if "AAAA" in records and records["AAAA"].get("values"):
                score += 0.5

            # Reduced penalty for errors
            if results.get("errors"):
                score -= 1.0  # Reduced from 2.0 to 1.0

        except Exception:
            score = 5.0  # Increased minimum score from 0.0 to 5.0

        return max(0.0, min(10.0, score))

    def _calculate_whois_score(self, results: Dict[str, Any]) -> float:
        """Calculate WHOIS safety score."""
        score = 5.0  # Base score

        try:
            whois_data = results.get("whois_data", {})

            # Check domain age (older domains are generally safer)
            creation_date = whois_data.get("creation_date")
            if creation_date:
                # Simple heuristic: domains older than 1 year get bonus
                import datetime

                try:
                    if isinstance(creation_date, str):
                        # Parse date string
                        if "T" in creation_date:
                            creation_date = creation_date.split("T")[0]
                        creation_dt = datetime.datetime.strptime(creation_date, "%Y-%m-%d")
                        age_days = (datetime.datetime.now() - creation_dt).days
                        if age_days > 365:
                            score += 2.0
                        elif age_days > 30:
                            score += 1.0
                    else:
                        score += 1.0
                except Exception:
                    pass

            # Check for legitimate registrar
            registrar = whois_data.get("registrar", "").lower()
            legitimate_registrars = [
                "godaddy",
                "namecheap",
                "google",
                "cloudflare",
                "markmonitor",
            ]
            if any(legit in registrar for legit in legitimate_registrars):
                score += 1.0

            # Check for organization info
            if whois_data.get("organization"):
                score += 0.5

            # Check for privacy protection
            if whois_data.get("status"):
                statuses = whois_data["status"]
                if isinstance(statuses, list):
                    statuses = [str(s) for s in statuses]
                else:
                    statuses = [str(statuses)]

                if any("clientdeleteprohibited" in s.lower() for s in statuses):
                    score += 1.0

        except Exception:
            score = 0.0

        return max(0.0, min(10.0, score))

    def _calculate_ssl_score(self, results: Dict[str, Any]) -> float:
        """Calculate SSL safety score."""
        score = 5.0  # Increased base score from 0.0 to 5.0

        try:
            ssl_data = results.get("ssl_data", {})

            # Check if certificate exists and is valid
            if ssl_data.get("is_expired") is False:
                score += 2.0  # Reduced from 3.0 to 2.0

            # Check certificate expiration (more days = better)
            days_until_expiry = ssl_data.get("days_until_expiry", 0)
            if days_until_expiry > 30:
                score += 1.5  # Reduced from 2.0 to 1.5
            elif days_until_expiry > 7:
                score += 1.0

            # Check for strong issuer
            issuer = ssl_data.get("issuer", "").lower()
            strong_issuers = [
                "digicert",
                "letsencrypt",
                "google",
                "amazon",
                "cloudflare",
            ]
            if any(strong in issuer for strong in strong_issuers):
                score += 1.0

            # Reduced penalty for wildcard certificate
            subject = ssl_data.get("subject", "")
            if "*" in subject:
                score -= 0.25  # Reduced from 0.5 to 0.25

            # Check for strong cipher
            cipher_bits = ssl_data.get("cipher_bits", 0)
            if cipher_bits >= 256:
                score += 1.0
            elif cipher_bits >= 128:
                score += 0.5

        except Exception:
            score = 3.0  # Increased minimum score from 0.0 to 3.0

        return max(0.0, min(10.0, score))

    def _calculate_blocklist_score(self, results: Dict[str, Any]) -> float:
        """Calculate blocklist safety score."""
        score = 10.0  # Start at 10, subtract for listings

        try:
            summary = results.get("summary", {})
            total_lists = summary.get("total_lists_checked", 0)
            listed_count = summary.get("listed_count", 0)

            if total_lists > 0:
                # Calculate percentage of lists that flagged the domain
                listing_percentage = (listed_count / total_lists) * 100

                # Penalize based on listing percentage
                if listing_percentage > 50:
                    score -= 8.0  # Major penalty
                elif listing_percentage > 25:
                    score -= 5.0  # Significant penalty
                elif listing_percentage > 10:
                    score -= 3.0  # Moderate penalty
                elif listing_percentage > 0:
                    score -= 1.0  # Minor penalty

        except Exception:
            score = 0.0

        return max(0.0, min(10.0, score))

    def _calculate_whitelist_score(self, results: Dict[str, Any]) -> float:
        """Calculate whitelist safety score."""
        score = 5.0  # Base neutral score

        try:
            summary = results.get("summary", {})
            total_lists = summary.get("total_lists_checked", 0)
            whitelisted_count = summary.get("whitelisted_count", 0)

            if total_lists > 0:
                # Calculate percentage of lists that whitelisted the domain
                whitelist_percentage = (whitelisted_count / total_lists) * 100

                # Reward based on whitelist percentage
                if whitelist_percentage > 80:
                    score += 4.0  # Major bonus
                elif whitelist_percentage > 50:
                    score += 2.0  # Significant bonus
                elif whitelist_percentage > 25:
                    score += 1.0  # Moderate bonus

        except Exception:
            score = 0.0

        return max(0.0, min(10.0, score))

    def _calculate_dga_score(self, results: Dict[str, Any]) -> float:
        """Calculate DGA safety score."""
        score = 5.0  # Base neutral score

        try:
            dga_analysis = results.get("dga_analysis", {})
            classification = dga_analysis.get("classification", "").lower()
            dga_probability = dga_analysis.get("dga_probability", 0.5)

            # Adjust score based on classification (reduced penalties)
            if "legitimate" in classification:
                score += 2.0  # Reduced from 3.0
            elif "possibly legitimate" in classification:
                score += 0.5  # Reduced from 1.0
            elif "possibly malicious" in classification:
                score -= 1.0  # Reduced from 2.0
            elif "malicious" in classification:
                score -= 2.0  # Reduced from 5.0

            # Adjust score based on DGA probability (reduced penalties)
            if dga_probability < 0.2:
                score += 0.5  # Reduced from 1.0
            elif dga_probability > 0.8:
                score -= 1.5  # Reduced from 3.0
            elif dga_probability > 0.6:
                score -= 0.5  # Reduced from 1.0

        except Exception:
            score = 0.0

        return max(0.0, min(10.0, score))

    def _calculate_headers_score(self, results: Dict[str, Any]) -> float:
        """Calculate HTTP headers safety score."""
        score = 10.0

        try:
            headers_data = results.get("headers_data", {})
            security_score = headers_data.get("security_score", 0)

            # Convert percentage to 0-10 scale with more lenient scaling
            score = (security_score / 100) * 8.0  # Reduced from 10.0 to 8.0 to be more lenient

            # Bonus for having any security headers
            implemented = headers_data.get("implemented_security_headers", 0)
            if implemented > 0:
                score += 1.0  # Increased from 0.5 to 1.0

            # Reduced penalty for missing critical headers
            missing_headers = headers_data.get("missing_headers", [])
            critical_headers = ["Content-Security-Policy", "Strict-Transport-Security"]
            for header in critical_headers:
                if any(h.get("name") == header for h in missing_headers):
                    score -= 0.5  # Reduced from 1.0 to 0.5

        except Exception:
            score = 4.0  # Increased minimum score from 0.0 to 4.0

        return max(0.0, min(10.0, score))

    def _calculate_ports_score(self, results: Dict[str, Any]) -> float:
        """Calculate port scanning safety score."""
        score = 10.0  # Start at 10, subtract for vulnerabilities

        try:
            open_ports = results.get("open_ports", [])
            vulnerabilities = results.get("vulnerabilities", [])

            # Penalty for too many open ports
            if len(open_ports) > 5:
                score -= 2.0
            elif len(open_ports) > 2:
                score -= 1.0

            # Penalty for specific dangerous ports
            dangerous_ports = [21, 23, 3389, 5900]  # FTP, Telnet, RDP, VNC
            for port_info in open_ports:
                port = port_info.get("port", 0)
                if port in dangerous_ports:
                    score -= 2.0

            # Penalty for vulnerabilities
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "Medium").lower()
                if severity == "high":
                    score -= 3.0
                elif severity == "medium":
                    score -= 2.0
                elif severity == "low":
                    score -= 1.0

        except Exception:
            score = 0.0

        return max(0.0, min(10.0, score))

    def calculate_overall_rating(self, analyzer_results: Dict[str, Any]) -> Tuple[float, str, Dict[str, float]]:
        """
        Calculate overall domain safety rating.

        Args:
            analyzer_results: Dictionary of analyzer results

        Returns:
            Tuple of (overall_score, classification, component_scores)
        """
        component_scores = {}
        total_score = 0.0
        analyzer_count = 0

        # Define analyzers to exclude from safety rating calculation
        excluded_analyzers = {"crawler", "screenshot", "llm_summary", "hierarchical_classification"}

        # Calculate scores for each analyzer
        for analyzer_name, results in analyzer_results.items():
            if analyzer_name.endswith("_results") and results:
                base_name = analyzer_name.replace("_results", "")

                # Skip excluded analyzers (not security analyzers)
                if base_name in excluded_analyzers:
                    continue

                score = self.calculate_analyzer_score(base_name, results)
                component_scores[base_name] = score
                total_score += score
                analyzer_count += 1

        # Calculate overall score
        if analyzer_count > 0:
            overall_score = total_score / analyzer_count
        else:
            overall_score = 0.0

        # Determine classification
        classification = self._get_classification(overall_score)

        return overall_score, classification, component_scores

    def _get_classification(self, score: float) -> str:
        """
        Get classification based on safety score.

        Args:
            score: Safety score between 0-10

        Returns:
            Classification string
        """
        # Convert 0-10 scale to 0-100 scale for threshold comparison
        percentage_score = (score / 10) * 100

        if percentage_score >= 70:
            return "✅ Safe"
        elif percentage_score >= 50:
            return "⚠️ Likely Unsafe"
        elif percentage_score >= 30:
            return "❌ Likely Malicious"
        else:
            return "❌ Unsafe (high risk)"


def calculate_domain_safety_rating(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate domain safety rating from analyzer results.

    Args:
        analyzer_results: Dictionary of analyzer results

    Returns:
        Dictionary containing safety rating information
    """
    calculator = SafetyRatingCalculator()
    overall_score, classification, component_scores = calculator.calculate_overall_rating(analyzer_results)

    return {
        "overall_score": round(overall_score, 2),
        "classification": classification,
        "component_scores": {k: round(v, 2) for k, v in component_scores.items()},
        "percentage_score": round((overall_score / 10) * 100, 1),
        "analyzer_count": len(component_scores),
    }
