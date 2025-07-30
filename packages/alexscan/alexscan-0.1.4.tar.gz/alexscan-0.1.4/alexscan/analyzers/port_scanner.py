"""Port scanning and vulnerability detection analyzer for domain analysis."""

import re
import socket
import ssl
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class PortScannerAnalyzer(BaseAnalyzer):
    """Port scanner and vulnerability detection analyzer using Python packages only."""

    def __init__(self) -> None:
        super().__init__("port_scanner", "Port scanning and vulnerability detection analyzer")
        self.common_ports = [
            21,
            22,
            23,
            25,
            53,
            80,
            110,
            143,
            443,
            993,
            995,  # Common services
            8080,
            8443,  # Alternative web ports
            3306,
            5432,
            6379,
            27017,  # Database ports
            3389,
            5900,  # Remote access
            161,
            162,  # SNMP
            389,
            636,  # LDAP
            1433,
            1434,
            1521,  # Database ports
            69,
            115,  # File transfer
            123,  # NTP
            137,
            138,
            139,
            445,  # NetBIOS/SMB
        ]
        self.common_ports = list(set(self.common_ports))  # Remove duplicates
        self.timeout = 3
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Perform port scanning and vulnerability detection on a domain.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing port scan and vulnerability analysis results
        """
        results: Dict[str, Any] = {
            "domain": domain,
            "scan_summary": {},
            "open_ports": [],
            "vulnerabilities": [],
            "recommendations": [],
            "errors": [],
        }

        try:
            # Resolve domain to IP
            ip_address = self._resolve_domain(domain)
            if not ip_address:
                results["errors"].append(f"Could not resolve domain {domain} to IP address")
                return results

            results["ip_address"] = ip_address

            # Perform port scan
            open_ports = self._scan_ports(ip_address)
            results["open_ports"] = open_ports

            # Analyze each open port for vulnerabilities
            vulnerabilities = []
            recommendations = []

            for port_info in open_ports:
                port_vulns, port_recs = self._analyze_port_vulnerabilities(port_info)
                vulnerabilities.extend(port_vulns)
                recommendations.extend(port_recs)

            results["vulnerabilities"] = vulnerabilities
            results["recommendations"] = list(set(recommendations))  # Remove duplicates

            # Generate scan summary
            results["scan_summary"] = {
                "total_ports_scanned": len(self.common_ports),
                "open_ports_count": len(open_ports),
                "vulnerabilities_found": len(vulnerabilities),
                "high_risk_vulnerabilities": len([v for v in vulnerabilities if v.get("severity") == "High"]),
                "medium_risk_vulnerabilities": len([v for v in vulnerabilities if v.get("severity") == "Medium"]),
                "low_risk_vulnerabilities": len([v for v in vulnerabilities if v.get("severity") == "Low"]),
            }

        except Exception as e:
            results["errors"].append(f"Port scanning failed: {str(e)}")

        return results

    def _resolve_domain(self, domain: str) -> Optional[str]:
        """
        Resolve domain to IP address.

        Args:
            domain: Domain to resolve

        Returns:
            IP address or None if resolution fails
        """
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except socket.gaierror:
            return None

    def _scan_ports(self, ip_address: str) -> List[Dict[str, Any]]:
        """
        Scan common ports on the target IP.

        Args:
            ip_address: IP address to scan

        Returns:
            List of open ports with service information
        """
        open_ports = []

        for port in self.common_ports:
            try:
                # Create socket with timeout
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)

                result = sock.connect_ex((ip_address, port))
                sock.close()

                if result == 0:
                    # Port is open, get service information
                    service_info = self._get_service_info(ip_address, port)
                    open_ports.append(service_info)

            except Exception:
                # Continue scanning other ports
                continue

        return open_ports

    def _get_service_info(self, ip_address: str, port: int) -> Dict[str, Any]:
        """
        Get service information for an open port.

        Args:
            ip_address: IP address
            port: Port number

        Returns:
            Service information dictionary
        """
        service_info = {
            "port": port,
            "service": self._get_service_name(port),
            "banner": "",
            "version": "",
            "protocol": "tcp",
            "ssl_enabled": False,
        }

        # Try to get banner and version
        try:
            if port in [443, 993, 995, 8443]:
                # SSL/TLS ports
                service_info["ssl_enabled"] = True
                banner, version = self._get_ssl_service_info(ip_address, port)
            else:
                banner, version = self._get_tcp_service_info(ip_address, port)

            service_info["banner"] = banner
            service_info["version"] = version

        except Exception:
            pass

        return service_info

    def _get_tcp_service_info(self, ip_address: str, port: int) -> tuple[str, str]:
        """
        Get TCP service banner and version.

        Args:
            ip_address: IP address
            port: Port number

        Returns:
            Tuple of (banner, version)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((ip_address, port))

            # Send probes based on service
            if port == 80:
                probe = b"GET / HTTP/1.1\r\nHost: " + ip_address.encode() + b"\r\n\r\n"
            elif port == 22:
                probe = b"SSH-2.0-OpenSSH_8.0\r\n"
            elif port == 21:
                probe = b"USER anonymous\r\n"
            else:
                probe = b"\r\n"

            sock.send(probe)

            # Try to receive banner
            try:
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                version = self._extract_version_from_banner(banner)
                sock.close()
                return banner, version
            except Exception:
                sock.close()
                return "", ""

        except Exception:
            return "", ""

    def _get_ssl_service_info(self, ip_address: str, port: int) -> tuple[str, str]:
        """
        Get SSL/TLS service banner and version.

        Args:
            ip_address: IP address
            port: Port number

        Returns:
            Tuple of (banner, version)
        """
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((ip_address, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=ip_address) as ssock:
                    # Get SSL certificate info
                    cert = ssock.getpeercert()
                    if cert:
                        # Try to get HTTP response if it's HTTPS
                        if port in [443, 8443]:
                            try:
                                ssock.send(b"GET / HTTP/1.1\r\nHost: " + ip_address.encode() + b"\r\n\r\n")
                                response = ssock.recv(1024).decode("utf-8", errors="ignore")
                                version = self._extract_version_from_banner(response)
                                return response, version
                            except Exception:
                                pass

                        # Extract version from certificate
                        try:
                            subject_dict = {}
                            for item in cert["subject"]:
                                if isinstance(item, tuple) and len(item) > 0:
                                    if isinstance(item[0], tuple) and len(item[0]) > 0:
                                        key = item[0][0]
                                        value = item[0][1]
                                        if isinstance(key, str) and isinstance(value, str):
                                            subject_dict[key] = value
                            version = subject_dict.get("commonName", "")
                            return f"SSL Certificate: {subject_dict}", version
                        except (KeyError, TypeError, IndexError):
                            return "SSL Certificate detected", ""

        except Exception:
            pass

        return "", ""

    def _get_service_name(self, port: int) -> str:
        """
        Get service name for common ports.

        Args:
            port: Port number

        Returns:
            Service name
        """
        service_map = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            3389: "RDP",
            5900: "VNC",
            161: "SNMP",
            162: "SNMP-Trap",
            389: "LDAP",
            636: "LDAPS",
            1433: "MSSQL",
            1434: "MSSQL-UDP",
            1521: "Oracle",
            69: "TFTP",
            115: "SFTP",
            123: "NTP",
            137: "NetBIOS-NS",
            138: "NetBIOS-DGM",
            139: "NetBIOS-SSN",
            445: "SMB",
        }

        return service_map.get(port, f"Unknown-{port}")

    def _extract_version_from_banner(self, banner: str) -> str:
        """
        Extract version information from service banner.

        Args:
            banner: Service banner

        Returns:
            Version string or empty string
        """
        # Common version patterns
        version_patterns = [
            r"(\d+\.\d+\.\d+)",  # x.x.x
            r"(\d+\.\d+)",  # x.x
            r"version[:\s]+([^\s]+)",  # version: x.x.x
            r"v([\d\.]+)",  # vx.x.x
            r"([A-Za-z]+)/(\d+\.\d+)",  # Server/x.x
            r"OpenSSH_(\d+\.\d+)",  # OpenSSH_x.x
        ]

        for pattern in version_patterns:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                # Only return if the match contains a digit
                value = match.group(1)
                if any(char.isdigit() for char in value):
                    if len(match.groups()) > 1:
                        return f"{match.group(1)} {match.group(2)}"
                    return value

        return ""

    def _analyze_port_vulnerabilities(self, port_info: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Analyze a port for potential vulnerabilities.

        Args:
            port_info: Port information dictionary

        Returns:
            Tuple of (vulnerabilities, recommendations)
        """
        vulnerabilities = []
        recommendations = []

        port = port_info["port"]
        service = port_info["service"]
        port_info["banner"]
        version = port_info["version"]
        ssl_enabled = port_info.get("ssl_enabled", False)

        # Check for common vulnerable services
        if service == "Telnet" and port == 23:
            vulnerabilities.append(
                {
                    "type": "Insecure Protocol",
                    "description": "Telnet service detected - transmits data in plaintext",
                    "severity": "High",
                    "port": port,
                    "service": service,
                    "cve_references": ["CVE-1999-0001"],
                }
            )
            recommendations.append("Disable Telnet and use SSH instead for secure remote access")

        elif service == "FTP" and port == 21:
            vulnerabilities.append(
                {
                    "type": "Insecure Protocol",
                    "description": "FTP service detected - transmits data in plaintext",
                    "severity": "Medium",
                    "port": port,
                    "service": service,
                    "cve_references": ["CVE-1999-0002"],
                }
            )
            recommendations.append("Use SFTP or FTPS instead of plain FTP for secure file transfer")

        elif service == "HTTP" and port == 80:
            vulnerabilities.append(
                {
                    "type": "Insecure Protocol",
                    "description": "HTTP service detected - transmits data in plaintext",
                    "severity": "Medium",
                    "port": port,
                    "service": service,
                }
            )
            recommendations.append("Redirect HTTP to HTTPS to encrypt all web traffic")

        elif service == "SNMP" and port in [161, 162]:
            vulnerabilities.append(
                {
                    "type": "Network Service",
                    "description": "SNMP service detected - may expose system information",
                    "severity": "Low",
                    "port": port,
                    "service": service,
                }
            )
            recommendations.append("Configure SNMP with strong community strings and restrict access")

        elif service == "RDP" and port == 3389:
            vulnerabilities.append(
                {
                    "type": "Remote Access",
                    "description": "RDP service detected - ensure strong authentication is configured",
                    "severity": "Medium",
                    "port": port,
                    "service": service,
                }
            )
            recommendations.append("Enable Network Level Authentication (NLA) and use strong passwords")

        elif service == "VNC" and port == 5900:
            vulnerabilities.append(
                {
                    "type": "Remote Access",
                    "description": "VNC service detected - may be vulnerable to brute force attacks",
                    "severity": "Medium",
                    "port": port,
                    "service": service,
                }
            )
            recommendations.append("Use VNC over SSH tunnel or implement strong authentication")

        # Check for database services
        elif service in ["MySQL", "PostgreSQL", "MongoDB", "MSSQL", "Oracle"]:
            vulnerabilities.append(
                {
                    "type": "Database Service",
                    "description": f"{service} database service detected - ensure proper access controls",
                    "severity": "High",
                    "port": port,
                    "service": service,
                }
            )
            recommendations.append(f"Restrict {service} access to trusted IPs and use strong authentication")

        # Check for outdated versions and known vulnerabilities
        if version:
            # Check against known vulnerable versions
            vulns = self._check_known_vulnerabilities(service, version)
            vulnerabilities.extend(vulns)

            # Check for outdated versions
            if self._check_outdated_versions(service, version):
                vulnerabilities.append(
                    {
                        "type": "Outdated Software",
                        "description": f"{service} version {version} may be outdated",
                        "severity": "Medium",
                        "port": port,
                        "service": service,
                        "version": version,
                    }
                )
                recommendations.append(f"Update {service} to the latest stable version")

            # Search for vulnerabilities online
            online_vulns = self._search_vulnerabilities_online(service, version)
            vulnerabilities.extend(online_vulns)

        # Check SSL/TLS configuration for HTTPS
        if ssl_enabled and port in [443, 8443]:
            ssl_vulns = self._check_ssl_vulnerabilities(port_info)
            vulnerabilities.extend(ssl_vulns)

        return vulnerabilities, recommendations

    def _search_vulnerabilities_online(self, service: str, version: str) -> List[Dict[str, Any]]:
        """
        Search for vulnerabilities online using web scraping.

        Args:
            service: Service name
            version: Version string

        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []

        try:
            # Search CVE Details
            cve_vulns = self._search_cve_details(service, version)
            vulnerabilities.extend(cve_vulns)

            # Search Exploit-DB
            exploit_vulns = self._search_exploit_db(service, version)
            vulnerabilities.extend(exploit_vulns)

        except Exception:
            # Silently fail - online search is optional
            pass

        return vulnerabilities

    def _search_cve_details(self, service: str, version: str) -> List[Dict[str, Any]]:
        """
        Search CVE Details website for vulnerabilities.

        Args:
            service: Service name
            version: Version string

        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []

        try:
            # Search query for CVE Details
            search_query = f"{service} {version}"
            encoded_query = quote_plus(search_query)
            url = f"https://www.cvedetails.com/cve/search.php?q={encoded_query}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Look for CVE entries in the search results
                cve_links = soup.find_all("a", href=re.compile(r"/cve/CVE-\d{4}-\d+/"))

                for link in cve_links[:3]:  # Limit to first 3 results
                    cve_id = link.text.strip()
                    if cve_id.startswith("CVE-"):
                        # Get CVE details
                        cve_url = f"https://www.cvedetails.com{link['href']}"
                        cve_details = self._get_cve_details(cve_url)

                        if cve_details:
                            vulnerabilities.append(
                                {
                                    "type": "Online CVE",
                                    "description": cve_details.get(
                                        "description", f"Vulnerability in {service} {version}"
                                    ),
                                    "severity": cve_details.get("severity", "Medium"),
                                    "service": service,
                                    "version": version,
                                    "cve_references": [cve_id],
                                    "source": "CVE Details",
                                }
                            )

        except Exception:
            pass

        return vulnerabilities

    def _get_cve_details(self, cve_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a CVE.

        Args:
            cve_url: URL to the CVE details page

        Returns:
            Dictionary with CVE details or None
        """
        try:
            response = self.session.get(cve_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Extract description
                description_elem = soup.find("div", class_="cvedetailssummary")
                description = description_elem.get_text().strip() if description_elem else ""

                # Extract severity
                severity = "Medium"  # Default
                severity_elem = soup.find("span", class_="cvssbox")
                if severity_elem:
                    severity_text = severity_elem.get_text().strip()
                    if "High" in severity_text:
                        severity = "High"
                    elif "Low" in severity_text:
                        severity = "Low"

                return {"description": description, "severity": severity}

        except Exception:
            pass

        return None

    def _search_exploit_db(self, service: str, version: str) -> List[Dict[str, Any]]:
        """
        Search Exploit-DB for vulnerabilities.

        Args:
            service: Service name
            version: Version string

        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []

        try:
            # Search query for Exploit-DB
            search_query = f"{service} {version}"
            encoded_query = quote_plus(search_query)
            url = f"https://www.exploit-db.com/search?q={encoded_query}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Look for exploit entries
                exploit_rows = soup.find_all("tr", class_="exploit-row")

                for row in exploit_rows[:2]:  # Limit to first 2 results
                    title_elem = row.find("td", class_="description")
                    if title_elem:
                        title = title_elem.get_text().strip()

                        vulnerabilities.append(
                            {
                                "type": "Online Exploit",
                                "description": f"Exploit available: {title}",
                                "severity": "High",
                                "service": service,
                                "version": version,
                                "source": "Exploit-DB",
                            }
                        )

        except Exception:
            pass

        return vulnerabilities

    def _check_known_vulnerabilities(self, service: str, version: str) -> List[Dict[str, Any]]:
        """
        Check for known vulnerabilities in service versions.

        Args:
            service: Service name
            version: Version string

        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []

        # Known vulnerable versions (basic examples)
        vulnerable_versions = {
            "OpenSSH": {
                "5.0": ["CVE-2010-5107", "CVE-2011-0538"],
                "6.0": ["CVE-2014-1692", "CVE-2014-2532"],
                "7.0": ["CVE-2016-6210", "CVE-2016-6515"],
            },
            "Apache": {
                "2.4.49": ["CVE-2021-41773", "CVE-2021-42013"],
                "2.4.50": ["CVE-2021-41773", "CVE-2021-42013"],
            },
            "Nginx": {
                "1.16.0": ["CVE-2019-20372"],
                "1.17.0": ["CVE-2019-20372"],
            },
        }

        # Check if service and version are in vulnerable list
        if service in vulnerable_versions:
            for vuln_version, cves in vulnerable_versions[service].items():
                if version.startswith(vuln_version):
                    for cve in cves:
                        vulnerabilities.append(
                            {
                                "type": "Known Vulnerability",
                                "description": f"{service} version {version} has known vulnerability {cve}",
                                "severity": "High",
                                "service": service,
                                "version": version,
                                "cve_references": [cve],
                            }
                        )

        return vulnerabilities

    def _check_outdated_versions(self, service: str, version: str) -> bool:
        """
        Basic check for potentially outdated versions.

        Args:
            service: Service name
            version: Version string

        Returns:
            True if version might be outdated
        """
        try:
            # Simple version comparison
            version_parts = version.split(".")
            if len(version_parts) >= 2:
                major = int(version_parts[0])
                int(version_parts[1])

                # Basic outdated version checks
                if service == "SSH" and major < 7:
                    return True
                elif service == "MySQL" and major < 8:
                    return True
                elif service == "PostgreSQL" and major < 12:
                    return True
                elif service == "MongoDB" and major < 4:
                    return True
                elif service == "Apache" and major < 2:
                    return True
                elif service == "Nginx" and major < 1:
                    return True

        except (ValueError, IndexError):
            pass

        return False

    def _check_ssl_vulnerabilities(self, port_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for SSL/TLS vulnerabilities.

        Args:
            port_info: Port information dictionary

        Returns:
            List of SSL/TLS vulnerabilities
        """
        vulnerabilities = []

        # Basic SSL/TLS checks
        if not port_info.get("ssl_enabled", False):
            vulnerabilities.append(
                {
                    "type": "SSL/TLS Configuration",
                    "description": "Service should use SSL/TLS encryption",
                    "severity": "Medium",
                    "port": port_info["port"],
                    "service": port_info["service"],
                }
            )

        return vulnerabilities

    def is_available(self) -> bool:
        """
        Check if port scanner is available.

        Returns:
            True if socket operations are available
        """
        try:
            # Test basic socket functionality
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.close()
            return True
        except Exception:
            return False


def analyze_port_scan(domain: str) -> Dict[str, Any]:
    """
    Analyze ports and vulnerabilities for a domain.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing port scan and vulnerability analysis results
    """
    analyzer = PortScannerAnalyzer()
    return analyzer.analyze(domain)
