"""LLM-based summarization analyzer for domain analysis results."""

import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .base import BaseAnalyzer


class LLMSummaryAnalyzer(BaseAnalyzer):
    """LLM-based summarization analyzer using Ollama."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma:2b"):
        super().__init__("llm_summary", "LLM-based summarization of domain analysis results")
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = 300  # seconds

        # Load all prompt templates from the prompts folder
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        """Load all prompt templates from the prompts folder."""
        prompts = {}
        prompts_dir = Path(__file__).parent.parent / "prompts"

        prompt_files = {
            "classification": "classification_prompt.txt",
            "confidence": "confidence_prompt.txt",
            "summary": "summary_prompt.txt",
            "analysis": "analysis_prompt.txt",
            "justification": "justification_prompt.txt",
            "conclusion": "conclusion_prompt.txt",
        }

        for prompt_type, filename in prompt_files.items():
            prompt_file = prompts_dir / filename
            try:
                if prompt_file.exists():
                    prompts[prompt_type] = prompt_file.read_text(encoding="utf-8")
                else:
                    # Fallback to empty string if file doesn't exist
                    prompts[prompt_type] = ""
            except Exception:
                # Fallback to empty string if there's an error reading the file
                prompts[prompt_type] = ""

        return prompts

    def analyze(
        self,
        domain: str,
        analyzer_results: Optional[Dict[str, Any]] = None,
        website_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an LLM-based summary of domain analysis results.

        Args:
            domain: The domain being analyzed
            analyzer_results: Results from other analyzers to summarize
            website_content: Optional website text content to include in analysis

        Returns:
            Dict containing LLM summary results
        """
        results: Dict[str, Any] = {"domain": domain, "llm_summary": {}, "errors": []}

        try:
            # Check if Ollama is available, attempt to start if not
            if not self._is_ollama_available():
                if not self._attempt_start_ollama():
                    results["errors"].append(
                        "Ollama service is not available and could not be started automatically. Please ensure Docker is installed and running."
                    )
                    return results

            # Ensure model is available
            if not self._ensure_model_available():
                results["errors"].append(f"Model '{self.model}' is not available. Please pull the model first.")
                return results

            # Generate summary
            if analyzer_results:
                # Check if domain is whitelisted before fetching website content
                is_whitelisted = False
                if "whitelist_results" in analyzer_results:
                    whitelist_data = analyzer_results["whitelist_results"]
                    summary = whitelist_data.get("summary", {})
                    whitelisted_count = summary.get("whitelisted_count", 0)
                    total_lists = summary.get("total_lists_checked", 0)
                    # Consider whitelisted if majority of lists whitelist it
                    is_whitelisted = whitelisted_count > 0 and whitelisted_count >= total_lists / 2

                # Only fetch website content if not whitelisted
                if website_content is None:
                    if is_whitelisted:
                        website_content = ""  # Empty content for whitelisted domains
                    else:
                        website_content = self._fetch_website_content(domain)
                elif is_whitelisted:
                    website_content = ""  # Empty content for whitelisted domains

                llm_response = self._generate_summary(domain, analyzer_results, website_content)
                parsed_response = llm_response  # _generate_summary now returns parsed dict directly

                results["llm_summary"] = {
                    "domain": domain,
                    "summary": parsed_response.get("summary", ""),
                    "analysis": parsed_response.get("analysis", ""),
                    "classification": parsed_response.get("classification", "Unknown"),
                    "confidence_score": parsed_response.get("confidence_score", 0.0),
                    "justification": parsed_response.get("justification", ""),
                    "conclusion": parsed_response.get("conclusion", ""),
                    "model_used": self.model,
                    "analyzers_summarized": list(analyzer_results.keys()),
                    "website_content_analyzed": website_content is not None and len(website_content) > 0,
                }
            else:
                results["errors"].append("No analyzer results provided for summarization.")

        except Exception as e:
            results["errors"].append(f"LLM summary generation failed: {str(e)}")

        return results

    def _is_ollama_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _ensure_model_available(self) -> bool:
        """Ensure the specified model is available, try to pull if not."""
        try:
            # Check if model is already available
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                # Check for exact match or base name match
                if self.model in model_names or any(name.startswith(self.model.split(":")[0]) for name in model_names):
                    return True

            # Try to pull the model
            pull_data = {"name": self.model}
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json=pull_data,
                timeout=60,  # Longer timeout for model pulling
            )
            return response.status_code == 200

        except requests.RequestException:
            return False

    def _is_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False

    def _is_ollama_container_running(self) -> bool:
        """Check if Ollama container is already running."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "ancestor=ollama/ollama:latest",
                    "--format",
                    "{{.ID}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _start_ollama_container(self) -> bool:
        """Start Ollama container using Docker."""
        try:
            # First, try to start an existing stopped container
            existing_result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    "ancestor=ollama/ollama:latest",
                    "--format",
                    "{{.ID}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if existing_result.returncode == 0 and existing_result.stdout.strip():
                container_id = existing_result.stdout.strip().split("\n")[0]
                start_result = subprocess.run(
                    ["docker", "start", container_id],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if start_result.returncode == 0:
                    return True

            # If no existing container or start failed, create a new one
            result = subprocess.run(
                ["docker", "run", "-d", "-p", "11434:11434", "ollama/ollama:latest"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _wait_for_ollama_ready(self, max_wait_seconds: int = 30) -> bool:
        """Wait for Ollama to be ready to accept requests."""
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            if self._is_ollama_available():
                return True
            time.sleep(2)
        return False

    def _attempt_start_ollama(self) -> bool:
        """Attempt to start Ollama if it's not running."""
        # Check if Docker is available
        if not self._is_docker_available():
            return False

        # Check if Ollama container is already running
        if self._is_ollama_container_running():
            # Container is running but maybe not ready yet
            return self._wait_for_ollama_ready(15)

        # Try to start Ollama container
        if not self._start_ollama_container():
            return False

        # Wait for Ollama to be ready
        if not self._wait_for_ollama_ready(30):
            return False

        # Try to ensure the model is available
        self._ensure_model_available()
        return True

    def _fetch_website_content(self, domain: str) -> str:
        """Fetch website content for analysis."""
        try:
            # Try both HTTP and HTTPS
            for protocol in ["https", "http"]:
                try:
                    url = f"{protocol}://{domain}"
                    response = requests.get(url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        # Extract text content (simple extraction)
                        content = response.text
                        # Remove HTML tags for cleaner content
                        content = re.sub(r"<[^>]+>", " ", content)
                        # Clean up whitespace
                        content = re.sub(r"\s+", " ", content).strip()
                        # Limit content length to avoid token limits
                        return content[:2000] if len(content) > 2000 else content
                except requests.RequestException:
                    continue
            return ""
        except Exception:
            return ""

    def _parse_simple_response(self, response: str) -> str:
        """Parse a simple text response from LLM."""
        # Clean up the response
        response = response.strip()

        # Remove common prefixes that LLMs sometimes add
        prefixes_to_remove = [
            "Classification:",
            "Confidence:",
            "Summary:",
            "Analysis:",
            "Justification:",
            "Conclusion:",
            "Response:",
            "Answer:",
        ]

        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix) :].strip()  # noqa
                break

        return response

    def _parse_classification_response(self, response: str) -> str:
        """Parse classification response and validate it."""
        classification = self._parse_simple_response(response)

        # Valid classifications
        valid_classifications = ["Safe", "Likely Safe", "Likely Malicious", "Malicious"]

        # Try exact match first
        if classification in valid_classifications:
            return classification

        # Try case-insensitive match
        for valid_cls in valid_classifications:
            if classification.lower() == valid_cls.lower():
                return valid_cls

        # Try partial match (look for keywords in the response)
        response_lower = response.lower()
        if "malicious" in response_lower:
            if "likely" in response_lower:
                return "Likely Malicious"
            else:
                return "Malicious"
        elif "safe" in response_lower:
            if "likely" in response_lower:
                return "Likely Safe"
            else:
                return "Safe"

        # Default to Safe for legitimate domains if no clear classification
        if "legitimate" in response_lower or "normal" in response_lower or "standard" in response_lower:
            return "Safe"

        return "Unknown"

    def _parse_confidence_response(self, response: str) -> float:
        """Parse confidence response and convert to 0-1 scale."""
        confidence_text = self._parse_simple_response(response)

        try:
            # Extract number from text
            import re

            match = re.search(r"\d+(?:\.\d+)?", confidence_text)
            if match:
                confidence = float(match.group())
                # If it's a percentage (0-100), convert to 0-1 scale
                if confidence > 1:
                    return confidence / 100.0
                else:
                    return confidence
        except (ValueError, AttributeError):
            pass

        return 0.0

    def _generate_summary(
        self, domain: str, analyzer_results: Dict[str, Any], website_content: str = ""
    ) -> Dict[str, Any]:
        """Generate a summary using multiple separate LLM prompts with risk assessment focus."""
        # Format the analyzer results for the LLM
        formatted_results = self._format_results_for_llm(domain, analyzer_results, website_content)

        result = {
            "summary": "",
            "analysis": "",
            "classification": "Unknown",
            "confidence_score": 0.0,
            "justification": "",
            "conclusion": "",
            "risk_score": 0.0,
            "risk_level": "Unknown",
        }

        try:
            # 1. Get classification with risk assessment
            classification_prompt = self._create_classification_prompt(domain, formatted_results)
            classification_response = self._send_to_ollama(classification_prompt)
            classification_data = self._parse_risk_assessment_response(classification_response)
            result["classification"] = classification_data.get("classification", "Unknown")
            result["risk_score"] = classification_data.get("risk_score", 0.0)
            result["risk_level"] = classification_data.get("risk_level", "Unknown")

            # 2. Get confidence score
            confidence_prompt = self._create_confidence_prompt(
                domain, formatted_results, result["classification"], result["risk_score"]
            )
            confidence_response = self._send_to_ollama(confidence_prompt)
            confidence_score = self._parse_confidence_response(confidence_response)
            result["confidence_score"] = confidence_score

            # 3. Get summary
            summary_prompt = self._create_summary_prompt(domain, formatted_results)
            summary_response = self._send_to_ollama(summary_prompt)
            result["summary"] = self._parse_simple_response(summary_response)

            # 4. Get detailed analysis
            analysis_prompt = self._create_analysis_prompt(domain, formatted_results)
            analysis_response = self._send_to_ollama(analysis_prompt)
            result["analysis"] = self._parse_simple_response(analysis_response)

            # 5. Get justification
            justification_prompt = self._create_justification_prompt(
                domain, formatted_results, result["classification"], result["risk_score"]
            )
            justification_response = self._send_to_ollama(justification_prompt)
            result["justification"] = self._parse_simple_response(justification_response)

            # 6. Get conclusion
            conclusion_prompt = self._create_conclusion_prompt(
                domain, formatted_results, result["classification"], result["risk_score"]
            )
            conclusion_response = self._send_to_ollama(conclusion_prompt)
            result["conclusion"] = self._parse_simple_response(conclusion_response)

        except Exception as e:
            result["summary"] = f"Error generating summary: {str(e)}"

        return result

    def _format_results_for_llm(self, domain: str, analyzer_results: Dict[str, Any], website_content: str = "") -> str:
        """Format analyzer results into a readable format for the LLM."""
        formatted_text = f"Domain Analysis Results for {domain}:\n\n"

        # Add safety rating information
        try:
            from .safety_rating import calculate_domain_safety_rating

            safety_rating = calculate_domain_safety_rating(analyzer_results)
            formatted_text += "SAFETY RATING:\n"
            formatted_text += (
                f"Overall Safety Score: {safety_rating['overall_score']}/10 ({safety_rating['percentage_score']}%)\n"
            )
            formatted_text += f"Classification: {safety_rating['classification']}\n"
            formatted_text += "Component Scores:\n"
            for analyzer, score in safety_rating["component_scores"].items():
                formatted_text += f"  {analyzer}: {score}/10\n"
            formatted_text += "\n"
        except Exception:
            pass  # Continue without safety rating if there's an error

        # DNS Results
        if "dns_results" in analyzer_results:
            dns_data = analyzer_results["dns_results"]
            formatted_text += "DNS Analysis:\n"
            records = dns_data.get("records", {})
            for record_type, record_info in records.items():
                values = record_info.get("values", [])
                if values:
                    formatted_text += f"  {record_type}: {', '.join(values[:3])}\n"
            if dns_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(dns_data['errors'])}\n"
            formatted_text += "\n"

        # WHOIS Results
        if "whois_results" in analyzer_results:
            whois_data = analyzer_results["whois_results"]
            formatted_text += "WHOIS Analysis:\n"
            whois_info = whois_data.get("whois_data", {})
            for field, value in whois_info.items():
                if field == "name_servers" and isinstance(value, list):
                    formatted_text += f"  {field}: {', '.join(value[:2])}\n"
                elif value:
                    formatted_text += f"  {field}: {str(value)[:100]}\n"
            if whois_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(whois_data['errors'])}\n"
            formatted_text += "\n"

        # SSL Results
        if "ssl_results" in analyzer_results:
            ssl_data = analyzer_results["ssl_results"]
            formatted_text += "SSL Analysis:\n"
            ssl_info = ssl_data.get("ssl_data", {})
            key_fields = [
                "issuer",
                "valid_from",
                "valid_to",
                "is_expired",
                "days_until_expiry",
            ]
            for field in key_fields:
                if field in ssl_info:
                    formatted_text += f"  {field}: {ssl_info[field]}\n"
            if ssl_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(ssl_data['errors'])}\n"
            formatted_text += "\n"

        # Blocklist Results
        if "blocklist_results" in analyzer_results:
            blocklist_data = analyzer_results["blocklist_results"]
            formatted_text += "Blocklist Analysis:\n"
            summary = blocklist_data.get("summary", {})
            formatted_text += f"  Lists checked: {summary.get('total_lists_checked', 0)}\n"
            formatted_text += f"  Listed: {summary.get('listed_count', 0)}\n"
            formatted_text += f"  Clean: {summary.get('clean_count', 0)}\n"
            if blocklist_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(blocklist_data['errors'])}\n"
            formatted_text += "\n"

        # Whitelist Results
        if "whitelist_results" in analyzer_results:
            whitelist_data = analyzer_results["whitelist_results"]
            formatted_text += "Whitelist Analysis:\n"
            summary = whitelist_data.get("summary", {})
            formatted_text += f"  Lists checked: {summary.get('total_lists_checked', 0)}\n"
            formatted_text += f"  Whitelisted: {summary.get('whitelisted_count', 0)}\n"
            formatted_text += f"  Not whitelisted: {summary.get('not_whitelisted_count', 0)}\n"
            whitelist_status = whitelist_data.get("whitelist_status", {})
            if whitelist_status:
                whitelisted_sources = [
                    data.get("name", source) for source, data in whitelist_status.items() if data.get("whitelisted")
                ]
                if whitelisted_sources:
                    formatted_text += f"  Whitelisted by: {', '.join(whitelisted_sources)}\n"
            if whitelist_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(whitelist_data['errors'])}\n"
            formatted_text += "\n"

        # DGA Results
        if "dga_results" in analyzer_results:
            dga_data = analyzer_results["dga_results"]
            formatted_text += "DGA Analysis:\n"
            dga_info = dga_data.get("dga_analysis", {})
            formatted_text += f"  Classification: {dga_info.get('classification', 'Unknown')}\n"
            formatted_text += f"  DGA Probability: {dga_info.get('dga_probability', 0)}\n"
            formatted_text += f"  Risk Level: {dga_info.get('risk_level', 'Unknown')}\n"
            if dga_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(dga_data['errors'])}\n"
            formatted_text += "\n"

        # HTTP Headers Results
        if "headers_results" in analyzer_results:
            headers_data = analyzer_results["headers_results"]
            formatted_text += "HTTP Headers Analysis:\n"
            headers_info = headers_data.get("headers_data", {})
            security_score = headers_info.get("security_score", 0)
            implemented = headers_info.get("implemented_security_headers", 0)
            total = headers_info.get("total_security_headers", 0)
            formatted_text += f"  Security Score: {security_score}% ({implemented}/{total} headers implemented)\n"

            security_headers = headers_info.get("security_headers", {})
            if security_headers:
                formatted_text += "  Implemented security headers:\n"
                for header_name, header_info in security_headers.items():
                    assessment = header_info.get("assessment", "Unknown")
                    formatted_text += f"    {header_name}: {assessment}\n"

            missing_headers = headers_info.get("missing_headers", [])
            if missing_headers:
                missing_names = [h.get("name", "") for h in missing_headers]
                formatted_text += f"  Missing security headers: {', '.join(missing_names)}\n"

            if headers_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(headers_data['errors'])}\n"
            formatted_text += "\n"

        # Crawler Results
        if "crawler_results" in analyzer_results:
            crawler_data = analyzer_results["crawler_results"]
            formatted_text += "Web Crawler Analysis:\n"
            crawler_info = crawler_data.get("crawler_data", {})
            success = crawler_info.get("success", False)
            if success:
                formatted_text += "  Status: Successfully crawled\n"
                formatted_text += f"  URL: {crawler_info.get('url_used', 'N/A')}\n"
                formatted_text += f"  Status code: {crawler_info.get('status_code', 'N/A')}\n"
                formatted_text += f"  Content length: {crawler_info.get('content_length', 0)} characters\n"
                formatted_text += f"  Title: {crawler_info.get('title', 'N/A')}\n"
                formatted_text += f"  Meta description: {crawler_info.get('meta_description', 'N/A')[:100]}...\n"
            else:
                formatted_text += "  Status: Failed to crawl\n"
                formatted_text += f"  Error: {crawler_info.get('error', 'Unknown error')}\n"
            if crawler_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(crawler_data['errors'])}\n"
            formatted_text += "\n"

        # Port Scanning Results
        if "ports_results" in analyzer_results:
            ports_data = analyzer_results["ports_results"]
            formatted_text += "Port Scanning Analysis:\n"

            # IP Address
            ip_address = ports_data.get("ip_address", "")
            if ip_address:
                formatted_text += f"  IP Address: {ip_address}\n"

            # Scan Summary
            scan_summary = ports_data.get("scan_summary", {})
            if scan_summary:
                formatted_text += f"  Total Ports Scanned: {scan_summary.get('total_ports_scanned', 0)}\n"
                formatted_text += f"  Open Ports Found: {scan_summary.get('open_ports_count', 0)}\n"
                formatted_text += f"  Vulnerabilities Found: {scan_summary.get('vulnerabilities_found', 0)}\n"

            # Open Ports
            open_ports = ports_data.get("open_ports", [])
            if open_ports:
                formatted_text += "  Open Ports:\n"
                for port_info in open_ports:
                    port = port_info.get("port", "")
                    service = port_info.get("service", "")
                    version = port_info.get("version", "")
                    ssl = "SSL" if port_info.get("ssl_enabled") else "No SSL"
                    formatted_text += f"    Port {port}: {service} {version} ({ssl})\n"

            # Vulnerabilities
            vulnerabilities = ports_data.get("vulnerabilities", [])
            if vulnerabilities:
                formatted_text += "  Vulnerabilities:\n"
                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "")
                    vuln_type = vuln.get("type", "")
                    port = vuln.get("port", "")
                    description = vuln.get("description", "")
                    formatted_text += f"    {severity} - {vuln_type} (Port {port}): {description}\n"

            if ports_data.get("errors"):
                formatted_text += f"  Errors: {', '.join(ports_data['errors'])}\n"
            formatted_text += "\n"

        # Website Content
        if website_content:
            formatted_text += "Website Content:\n"
            formatted_text += f"  Content length: {len(website_content)} characters\n"
            formatted_text += f"  Content preview: {website_content[:500]}...\n"
            formatted_text += "\n"

        return formatted_text

    def _create_classification_prompt(self, domain: str, formatted_results: str) -> str:
        """Create a prompt to get just the security classification."""
        prompt_template = self.prompts.get("classification", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """As a cybersecurity analyst, you must classify the security risk of the domain "{domain}" based on the technical analysis results below.

Consider these security indicators:
- DNS configuration and anomalies
- SSL certificate validity and issues
- WHOIS registration information
- Blocklist presence (if any)
- Domain generation algorithm (DGA) patterns
- Website content analysis

Domain Analysis Data:
{formatted_results}

You MUST choose EXACTLY ONE classification from the list below. Do not provide explanations or caveats:

Safe
Likely Safe
Likely Malicious
Malicious

Your classification:"""

        return prompt_template.format(domain=domain, formatted_results=formatted_results)

    def _create_confidence_prompt(
        self, domain: str, formatted_results: str, classification: str, risk_score: float
    ) -> str:
        """Create a prompt to get confidence score."""
        prompt_template = self.prompts.get("confidence", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """You classified the domain "{domain}" as "{classification}" with a risk score of {risk_score:.2f}.

Based on the technical analysis data below, rate your confidence in this classification.

Domain Analysis Data:
{formatted_results}

Provide ONLY a number between 0 and 100 (where 100 = completely confident, 0 = not confident at all).

Your confidence score:"""

        return prompt_template.format(
            domain=domain,
            formatted_results=formatted_results,
            classification=classification,
            risk_score=risk_score,
        )

    def _create_summary_prompt(self, domain: str, formatted_results: str) -> str:
        """Create a prompt to get a concise summary."""
        prompt_template = self.prompts.get("summary", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """As a cybersecurity analyst, provide a concise overview of the key findings and security implications for this domain.

Domain Analysis Data:
{formatted_results}

Write 2-3 sentences highlighting the most important security findings.

Summary:"""

        return prompt_template.format(domain=domain, formatted_results=formatted_results)

    def _create_analysis_prompt(self, domain: str, formatted_results: str) -> str:
        """Create a prompt to get detailed analysis."""
        prompt_template = self.prompts.get("analysis", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """As a cybersecurity analyst, provide a detailed analysis of each component (DNS, WHOIS, SSL, Blocklist, DGA, Website Content).

Domain Analysis Data:
{formatted_results}

Explain the specific findings, anomalies, and their significance for security assessment. Be thorough and technical.

Analysis:"""

        return prompt_template.format(domain=domain, formatted_results=formatted_results)

    def _create_justification_prompt(
        self, domain: str, formatted_results: str, classification: str, risk_score: float
    ) -> str:
        """Create a prompt to get classification justification."""
        prompt_template = self.prompts.get("justification", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """As a cybersecurity analyst, you classified the domain "{domain}" as "{classification}" with a risk score of {risk_score:.2f}.

Domain Analysis Data:
{formatted_results}

Provide detailed justification for this classification with specific evidence from the analysis results.

Justification:"""

        return prompt_template.format(
            domain=domain,
            formatted_results=formatted_results,
            classification=classification,
            risk_score=risk_score,
        )

    def _create_conclusion_prompt(
        self, domain: str, formatted_results: str, classification: str, risk_score: float
    ) -> str:
        """Create a prompt to get actionable conclusions."""
        prompt_template = self.prompts.get("conclusion", "")
        if not prompt_template:
            # Fallback to hardcoded prompt if template is not available
            prompt_template = """As a cybersecurity analyst, you classified the domain "{domain}" as "{classification}" with a risk score of {risk_score:.2f}.

Domain Analysis Data:
{formatted_results}

Provide actionable recommendations, priority level (High/Medium/Low), and suggested next steps for security teams.

Conclusion:"""

        return prompt_template.format(
            domain=domain,
            formatted_results=formatted_results,
            classification=classification,
            risk_score=risk_score,
        )

    def _send_to_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response."""
        try:
            data = {"model": self.model, "prompt": prompt, "stream": False}

            response = requests.post(f"{self.ollama_url}/api/generate", json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                return str(result.get("response", "Failed to generate summary"))
            else:
                return f"Error: Ollama API returned status {response.status_code}"

        except requests.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"

    def is_available(self) -> bool:
        """
        Check if LLM summary analyzer is available.

        Returns:
            True if Ollama is available and model can be loaded
        """
        return self._is_ollama_available()

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name", "").startswith(self.model):
                        return {
                            "name": model.get("name"),
                            "size": model.get("size", 0),
                            "digest": model.get("digest"),
                            "modified_at": model.get("modified_at"),
                        }
        except requests.RequestException:
            pass
        return {}

    def _build_summary_context(self, domain: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for LLM summary prompt."""
        context = {"domain": domain}
        # Add HTTP headers summary if available
        headers = results.get("headers", {}).get("headers_data", {})
        if headers:
            context["headers_summary"] = self._summarize_headers(headers)
        else:
            context["headers_summary"] = "No HTTP headers data found."
        return context

    def _summarize_headers(self, headers_data: dict) -> str:
        """Summarize key HTTP header findings for LLM prompt."""
        lines = []
        score = headers_data.get("security_score", 0)
        implemented = headers_data.get("implemented_security_headers", 0)
        total = headers_data.get("total_security_headers", 0)
        lines.append(f"Security Score: {score}% ({implemented}/{total} headers implemented)")
        security_headers = headers_data.get("security_headers", {})
        if security_headers:
            lines.append("Implemented security headers:")
            for name, info in security_headers.items():
                lines.append(f"- {name}: {info.get('assessment', 'Unknown')} ({info.get('value', '')})")
        missing_headers = headers_data.get("missing_headers", [])
        if missing_headers:
            lines.append(f"Missing security headers: {', '.join(h.get('name', '') for h in missing_headers)}")
        return "\n".join(lines)

    def _parse_risk_assessment_response(self, response: str) -> Dict[str, Any]:
        """
        Parse risk assessment response from the new risk-based classification prompt.

        Expected format:
        1. Component Risk Scores (DNS: X, WHOIS: X, SSL: X, Reputation: X, DGA: X, Headers: X, Content: X, Port: X)
        2. Base Risk Score: X.X
        3. Whitelist Adjustment: X% (if applicable)
        4. Final Risk Score: X.X
        5. Risk Level: [Safe/Likely Safe/Likely Malicious/Malicious]
        6. Classification: [Single word classification]
        """
        result = {
            "classification": "Unknown",
            "risk_score": 0.0,
            "risk_level": "Unknown",
            "component_scores": {},
            "base_risk_score": 0.0,
            "whitelist_adjustment": 0.0,
        }

        try:
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()

                # Parse component risk scores
                if "Component Risk Scores" in line:
                    # Extract scores from line like "Component Risk Scores (DNS: 2, WHOIS: 1, SSL: 3, ...)"
                    import re

                    score_matches = re.findall(r"(\w+):\s*(\d+)", line)
                    for component, score in score_matches:
                        result["component_scores"][component] = int(score)

                # Parse base risk score
                elif "Base Risk Score:" in line:
                    score_match = re.search(r"Base Risk Score:\s*([\d.]+)", line)
                    if score_match:
                        result["base_risk_score"] = float(score_match.group(1))

                # Parse whitelist adjustment
                elif "Whitelist Adjustment:" in line:
                    adj_match = re.search(r"Whitelist Adjustment:\s*([\d.]+)%", line)
                    if adj_match:
                        result["whitelist_adjustment"] = float(adj_match.group(1))

                # Parse final risk score
                elif "Final Risk Score:" in line:
                    score_match = re.search(r"Final Risk Score:\s*([\d.]+)", line)
                    if score_match:
                        result["risk_score"] = float(score_match.group(1))

                # Parse risk level
                elif "Risk Level:" in line:
                    level_match = re.search(r"Risk Level:\s*(\w+)", line)
                    if level_match:
                        result["risk_level"] = level_match.group(1)

                # Parse classification
                elif "Classification:" in line:
                    class_match = re.search(r"Classification:\s*(\w+)", line)
                    if class_match:
                        result["classification"] = class_match.group(1)

            # If we couldn't parse the structured format, try to extract from the text
            if result["classification"] == "Unknown":
                # Look for classification keywords in the response
                response_lower = response.lower()
                if "safe" in response_lower:
                    result["classification"] = "Safe"
                elif "malicious" in response_lower:
                    result["classification"] = "Malicious"
                elif "likely safe" in response_lower:
                    result["classification"] = "Likely Safe"
                elif "likely malicious" in response_lower:
                    result["classification"] = "Likely Malicious"

                # Try to extract a risk score from the text
                score_match = re.search(r"(\d+\.?\d*)/10", response)
                if score_match:
                    result["risk_score"] = float(score_match.group(1))

                # Determine risk level based on score
                if result["risk_score"] > 0:
                    if result["risk_score"] <= 3:
                        result["risk_level"] = "Low"
                    elif result["risk_score"] <= 6:
                        result["risk_level"] = "Medium"
                    elif result["risk_score"] <= 8:
                        result["risk_level"] = "High"
                    else:
                        result["risk_level"] = "Critical"

        except Exception:
            # Fallback to simple classification parsing
            result["classification"] = self._parse_classification_response(response)

        return result


def generate_llm_summary(
    domain: str,
    analyzer_results: Dict[str, Any],
    model: str = "gemma:2b",
    website_content: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an LLM-based summary of domain analysis results.

    Args:
        domain: The domain being analyzed
        analyzer_results: Results from other analyzers
        model: The LLM model to use
        website_content: Optional website text content to include in analysis

    Returns:
        Dict containing LLM summary results
    """
    analyzer = LLMSummaryAnalyzer(model=model)
    return analyzer.analyze(domain, analyzer_results, website_content)
