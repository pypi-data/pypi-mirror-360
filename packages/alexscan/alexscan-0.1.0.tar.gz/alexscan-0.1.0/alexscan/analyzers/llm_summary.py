"""LLM-based summarization analyzer for domain analysis results."""

import subprocess
import time
from typing import Any, Dict, Optional

import requests

from .base import BaseAnalyzer


class LLMSummaryAnalyzer(BaseAnalyzer):
    """LLM-based summarization analyzer using Ollama."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma:2b"):
        super().__init__("llm_summary", "LLM-based summarization of domain analysis results")
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = 30  # seconds

    def analyze(self, domain: str, analyzer_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an LLM-based summary of domain analysis results.

        Args:
            domain: The domain being analyzed
            analyzer_results: Results from other analyzers to summarize

        Returns:
            Dict containing LLM summary results
        """
        results = {"domain": domain, "llm_summary": {}, "errors": []}

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
                summary_text = self._generate_summary(domain, analyzer_results)
                results["llm_summary"] = {
                    "domain": domain,
                    "summary": summary_text,
                    "model_used": self.model,
                    "analyzers_summarized": list(analyzer_results.keys()),
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
                f"{self.ollama_url}/api/pull", json=pull_data, timeout=60  # Longer timeout for model pulling
            )
            return response.status_code == 200

        except requests.RequestException:
            return False

    def _is_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def _is_ollama_container_running(self) -> bool:
        """Check if Ollama container is already running."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "ancestor=ollama/ollama:latest", "--format", "{{.ID}}"],
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
                ["docker", "ps", "-a", "--filter", "ancestor=ollama/ollama:latest", "--format", "{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if existing_result.returncode == 0 and existing_result.stdout.strip():
                container_id = existing_result.stdout.strip().split("\n")[0]
                start_result = subprocess.run(
                    ["docker", "start", container_id], capture_output=True, text=True, timeout=30
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

    def _generate_summary(self, domain: str, analyzer_results: Dict[str, Any]) -> str:
        """Generate a summary using the LLM."""
        # Format the analyzer results for the LLM
        formatted_results = self._format_results_for_llm(domain, analyzer_results)

        # Create the prompt
        prompt = self._create_summary_prompt(domain, formatted_results)

        # Send to Ollama
        response = self._send_to_ollama(prompt)

        return response.strip()

    def _format_results_for_llm(self, domain: str, analyzer_results: Dict[str, Any]) -> str:
        """Format analyzer results into a readable format for the LLM."""
        formatted_text = f"Domain Analysis Results for {domain}:\n\n"

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
            key_fields = ["issuer", "valid_from", "valid_to", "is_expired", "days_until_expiry"]
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

        return formatted_text

    def _create_summary_prompt(self, domain: str, formatted_results: str) -> str:
        """Create a prompt for the LLM to generate a summary."""
        prompt = f"""
As an analyst, generate a comprehensive and actionable summary of the domain analysis results provided below.
Your response should thoroughly identify and explain the most relevant insights from the analysis. Highlight any indicators of compromise, anomalies, suspicious behaviors, or security risks that require immediate or long-term attention.
Provide detailed context for each finding so that it is meaningful and useful for decision-making by other analysts or stakeholders. Clearly describe why each issue is significant and how it might impact the security posture.
Where appropriate, suggest potential remediation steps, further investigation areas, or follow-up actions.
Additionally, classify the domain based on your analysis as one of the following: **Malicious**, **Likely Malicious**, **Likely Safe**, or **Safe**. Justify your classification with supporting evidence from the findings.

Where applicable, include:
- A confidence score (0-100%) for the classification.
- Suggested priority level for investigation (High, Medium, Low).
- Potential impact level if the domain is determined to be malicious.
- Recommendations for further automated scans or analyst review.

Maintain a professional tone appropriate for a security analyst audience.
Avoid unnecessary simplification, but ensure clarity and precision in the language.
The summary should be verbose and well-structured. Provide an in-depth narrative of the results rather than limiting it to just a few sentences.

{formatted_results}

Summary: <place summary here>
Analysis: <place analysis here>
Classification: <place classification here>
Final Conclusion: <place final conclusion here>
"""

        return prompt

    def _send_to_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and get response."""
        try:
            data = {"model": self.model, "prompt": prompt, "stream": False}

            response = requests.post(f"{self.ollama_url}/api/generate", json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Failed to generate summary")
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


def generate_llm_summary(domain: str, analyzer_results: Dict[str, Any], model: str = "gemma:2b") -> Dict[str, Any]:
    """
    Generate an LLM-based summary of domain analysis results.

    Args:
        domain: The domain being analyzed
        analyzer_results: Results from other analyzers
        model: The LLM model to use

    Returns:
        Dict containing LLM summary results
    """
    analyzer = LLMSummaryAnalyzer(model=model)
    return analyzer.analyze(domain, analyzer_results)
