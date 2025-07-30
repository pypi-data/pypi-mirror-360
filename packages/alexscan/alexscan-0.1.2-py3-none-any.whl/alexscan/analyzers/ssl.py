"""SSL/TLS analyzer for domain analysis."""

import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .base import BaseAnalyzer


class SSLAnalyzer(BaseAnalyzer):
    """SSL/TLS analyzer for domain certificate information."""

    def __init__(self) -> None:
        super().__init__("ssl", "SSL/TLS certificate analyzer")

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze SSL certificate information for a domain.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing SSL analysis results
        """
        results: Dict[str, Any] = {"domain": domain, "ssl_data": {}, "errors": []}

        try:
            cert_info = self._get_ssl_certificate(domain)

            if cert_info:
                parsed_data = self._parse_certificate_data(cert_info)
                results["ssl_data"] = parsed_data
            else:
                results["errors"].append("No SSL certificate found for domain")

        except Exception as e:
            results["errors"].append(f"SSL analysis failed: {str(e)}")

        return results

    def _get_ssl_certificate(self, domain: str, port: int = 443, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get SSL certificate for a domain.

        Args:
            domain: Domain to analyze
            port: HTTPS port (default 443)
            timeout: Connection timeout in seconds

        Returns:
            Certificate information dictionary or None
        """
        try:
            # Create SSL context
            context = ssl.create_default_context()

            # Create socket connection
            with socket.create_connection((domain, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    # Get certificate in DER format
                    cert_der = ssock.getpeercert(binary_form=True)
                    # Get certificate in parsed format
                    cert_dict = ssock.getpeercert()

                    return {
                        "cert_dict": cert_dict,
                        "cert_der": cert_der,
                        "cipher": ssock.cipher(),
                        "version": ssock.version(),
                    }

        except socket.gaierror:
            raise Exception(f"Domain {domain} could not be resolved")
        except socket.timeout:
            raise Exception(f"Connection to {domain}:{port} timed out")
        except ssl.SSLError as e:
            raise Exception(f"SSL error: {str(e)}")
        except ConnectionRefusedError:
            raise Exception(f"Connection refused to {domain}:{port}")
        except Exception as e:
            raise Exception(f"Certificate retrieval failed: {str(e)}")

    def _parse_certificate_data(self, cert_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse SSL certificate data into structured format.

        Args:
            cert_info: Raw certificate information

        Returns:
            Structured SSL certificate information
        """
        cert_dict = cert_info["cert_dict"]
        parsed: Dict[str, Any] = {}

        # Basic certificate info
        if "subject" in cert_dict:
            parsed["subject"] = self._format_certificate_name(cert_dict["subject"])

        if "issuer" in cert_dict:
            parsed["issuer"] = self._format_certificate_name(cert_dict["issuer"])

        # Serial number
        if "serialNumber" in cert_dict:
            parsed["serial_number"] = cert_dict["serialNumber"]

        # Version
        if "version" in cert_dict:
            parsed["version"] = cert_dict["version"]

        # Validity period
        if "notBefore" in cert_dict:
            parsed["valid_from"] = self._parse_certificate_date(cert_dict["notBefore"])

        if "notAfter" in cert_dict:
            parsed["valid_to"] = self._parse_certificate_date(cert_dict["notAfter"])
            # Check if certificate is expired
            parsed["is_expired"] = self._is_certificate_expired(cert_dict["notAfter"])
            parsed["days_until_expiry"] = self._days_until_expiry(cert_dict["notAfter"])

        # Subject Alternative Names
        if "subjectAltName" in cert_dict:
            san_list = cert_dict["subjectAltName"]
            if isinstance(san_list, (list, tuple)):
                parsed["subject_alt_names"] = [
                    name[1] for name in san_list if isinstance(name, (tuple, list)) and len(name) > 1
                ]

        # Signature algorithm
        if "signatureAlgorithm" in cert_dict:
            parsed["signature_algorithm"] = cert_dict["signatureAlgorithm"]

        # SSL/TLS protocol information
        if cert_info.get("version"):
            parsed["protocol_version"] = str(cert_info["version"])

        if cert_info.get("cipher"):
            cipher_info = cert_info["cipher"]
            if cipher_info and isinstance(cipher_info, (tuple, list)) and len(cipher_info) >= 3:
                parsed["cipher_suite"] = str(cipher_info[0])
                parsed["cipher_version"] = str(cipher_info[1])
                parsed["cipher_bits"] = int(cipher_info[2])

        return parsed

    def _format_certificate_name(self, name_tuple: Any) -> str:
        """Format certificate name from tuple format."""
        if not name_tuple:
            return ""

        name_parts = []
        for name_list in name_tuple:
            for name_part in name_list:
                if len(name_part) == 2:
                    name_parts.append(f"{name_part[0]}={name_part[1]}")

        return ", ".join(name_parts)

    def _parse_certificate_date(self, date_str: str) -> str:
        """Parse certificate date string to readable format."""
        try:
            # Certificate dates are in format 'Nov  1 00:00:00 2025 GMT'
            dt = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            return date_str

    def _is_certificate_expired(self, expiry_date: str) -> bool:
        """Check if certificate is expired."""
        try:
            expiry_dt = datetime.strptime(expiry_date, "%b %d %H:%M:%S %Y %Z")
            expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return now > expiry_dt
        except ValueError:
            return False

    def _days_until_expiry(self, expiry_date: str) -> int:
        """Calculate days until certificate expires."""
        try:
            expiry_dt = datetime.strptime(expiry_date, "%b %d %H:%M:%S %Y %Z")
            expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = expiry_dt - now
            return max(0, delta.days)
        except ValueError:
            return 0

    def is_available(self) -> bool:
        """
        Check if SSL analyzer is available.

        Returns:
            True as ssl and socket are built-in modules
        """
        return True


def analyze_ssl_certificate(domain: str) -> Dict[str, Any]:
    """
    Analyze SSL certificate for a domain.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing SSL analysis results
    """
    analyzer = SSLAnalyzer()
    return analyzer.analyze(domain)
