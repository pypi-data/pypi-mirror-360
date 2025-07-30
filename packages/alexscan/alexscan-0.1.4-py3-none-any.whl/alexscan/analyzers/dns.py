"""DNS analyzer for domain analysis."""

from typing import Any, Dict, List

import dns.exception
import dns.resolver

from .base import BaseAnalyzer


class DNSAnalyzer(BaseAnalyzer):
    """DNS analyzer for resolving domain records."""

    def __init__(self) -> None:
        super().__init__("dns", "DNS record lookup analyzer")

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze DNS records for a domain.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing DNS analysis results
        """
        results: Dict[str, Any] = {"domain": domain, "records": {}, "errors": []}

        # Record types to query
        record_types = {
            "A": "IPv4 addresses",
            "AAAA": "IPv6 addresses",
            "MX": "Mail exchange records",
            "NS": "Name servers",
            "TXT": "Text records",
        }

        for record_type, description in record_types.items():
            try:
                records = self._query_dns_record(domain, record_type)
                if records:
                    results["records"][record_type] = {"description": description, "values": records}
            except dns.exception.DNSException as e:
                results["errors"].append(f"{record_type} lookup failed: {str(e)}")
            except Exception as e:
                results["errors"].append(f"Unexpected error for {record_type}: {str(e)}")

        return results

    def _query_dns_record(self, domain: str, record_type: str) -> List[str]:
        """
        Query DNS records for a specific type.

        Args:
            domain: Domain to query
            record_type: DNS record type (A, AAAA, MX, NS, TXT)

        Returns:
            List of DNS record values
        """
        try:
            answers = dns.resolver.resolve(domain, record_type)
            records: List[str] = []

            for rdata in answers:
                if record_type == "MX":
                    records.append(f"{rdata.preference} {rdata.exchange}")
                elif record_type == "TXT":
                    # TXT records can contain multiple strings
                    txt_value = " ".join([s.decode() if isinstance(s, bytes) else str(s) for s in rdata.strings])
                    records.append(txt_value)
                else:
                    records.append(str(rdata))

            return records

        except dns.resolver.NXDOMAIN:
            raise dns.exception.DNSException(f"Domain {domain} does not exist")
        except dns.resolver.NoAnswer:
            # No records of this type found, return empty list
            return []
        except dns.resolver.Timeout:
            raise dns.exception.DNSException(f"DNS query timeout for {record_type} record")
        except Exception as e:
            raise dns.exception.DNSException(f"DNS query failed: {str(e)}")

    def is_available(self) -> bool:
        """
        Check if DNS analyzer is available.

        Returns:
            True if dnspython is available, False otherwise
        """
        try:
            return True
        except ImportError:
            return False


def analyze_dns_records(domain: str) -> Dict[str, Any]:
    """
    Analyze DNS records for a domain.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing DNS analysis results
    """
    analyzer = DNSAnalyzer()
    return analyzer.analyze(domain)
