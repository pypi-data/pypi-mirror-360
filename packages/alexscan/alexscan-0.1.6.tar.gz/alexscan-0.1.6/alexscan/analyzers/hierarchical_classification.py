"""Hierarchical Domain Classification analyzer for domain analysis."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class HierarchicalClassificationAnalyzer(BaseAnalyzer):
    """Hierarchical domain classification analyzer using LLM-powered reasoning."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma:2b"):
        super().__init__("hierarchical_classification", "Hierarchical domain classification based on HTML content")
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = 60  # seconds - increased for LLM processing
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AlexScan Classification Tool 1.0"})

        # Load the classification taxonomy
        self.taxonomy = self._load_taxonomy()

        # Load the classification prompt
        self.classification_prompt = self._load_classification_prompt()

    def _load_taxonomy(self) -> Dict[str, List[str]]:
        """Load the hierarchical classification taxonomy."""
        return {
            "News/Media": [
                "General News",
                "Politics & Government",
                "Technology News",
                "Entertainment & Celebrities",
                "Sports News",
                "Financial & Business News",
                "Science & Environment",
                "Local/Regional News",
                "Opinion/Editorial",
            ],
            "Social Media & Communities": [
                "Social Networks (Facebook, Twitter)",
                "Forums & Message Boards (Reddit, 4chan)",
                "Dating Sites & Apps",
                "Gaming Communities",
                "Professional Networks (LinkedIn)",
                "Hobbyist Groups (Photography, Gardening, etc.)",
                "File Sharing & Collaboration",
            ],
            "E-commerce & Shopping": [
                "General Retail (Amazon, eBay)",
                "Electronics & Gadgets",
                "Fashion & Apparel",
                "Food & Grocery Delivery",
                "Health & Beauty Products",
                "Automotive Parts & Accessories",
                "Luxury Goods",
                "Online Marketplaces",
            ],
            "Adult Content": [
                "Adult Entertainment Streaming",
                "Erotic Literature",
                "Adult Social Networks",
                "Webcam Services",
                "Pornographic Image Galleries",
                "Adult Novelty Stores",
            ],
            "Gambling": [
                "Online Casinos",
                "Sports Betting",
                "Poker Sites",
                "Lottery & Sweepstakes",
                "Horse Racing Betting",
                "Fantasy Sports",
            ],
            "Technology": [
                "Developer Tools & Resources",
                "IT Services & Consulting",
                "SaaS Platforms",
                "Open Source Projects",
                "Cloud Infrastructure",
                "AI/ML Platforms",
                "Cybersecurity Blogs",
            ],
            "Blogs & Personal Websites": [
                "Lifestyle Blogs",
                "Travel Journals",
                "Photography Portfolios",
                "Developer/Technical Blogs",
                "Personal Resumes & Pages",
                "Writers/Authors",
            ],
            "Education & Reference": [
                "Universities & Colleges",
                "Online Learning Platforms (Coursera, Udemy)",
                "K-12 Resources",
                "Libraries & Archives",
                "Research Journals",
                "Government Educational Portals",
            ],
            "Government & Law": [
                "Federal Government Portals",
                "Local/Municipal Government Sites",
                "Legal Reference Sites",
                "Military & Defense",
                "Public Health Portals",
            ],
            "Finance & Business": [
                "Online Banking",
                "Investment Platforms",
                "Cryptocurrency Exchanges",
                "Corporate Websites",
                "Small Business Sites",
                "Accounting & Tax Services",
            ],
            "Other/Miscellaneous": [
                "Parked Domains",
                "Content Delivery Networks",
                "Search Engines",
                "Internet Infrastructure",
            ],
        }

    def _load_classification_prompt(self) -> str:
        """Load the classification prompt template."""
        prompt_file = Path(__file__).parent.parent / "prompts" / "hierarchical_classification_prompt.txt"
        try:
            if prompt_file.exists():
                return prompt_file.read_text(encoding="utf-8")
            else:
                # Fallback to default prompt
                return self._get_default_classification_prompt()
        except Exception:
            return self._get_default_classification_prompt()

    def _get_default_classification_prompt(self) -> str:
        """Get the default classification prompt."""
        return """You are a domain classification expert. Analyze the provided HTML content and metadata to classify the domain into exactly one primary category and one subcategory from the given taxonomy.

**CLASSIFICATION REQUIREMENTS:**
- Classify based ONLY on the homepage HTML content and metadata provided
- Choose exactly ONE primary category and ONE subcategory from the taxonomy
- Provide a confidence score (0-100) for your classification
- If confidence < 50%, classify as "Uncategorized"
- Provide clear evidence explaining your classification decision

**TAXONOMY:**
{taxonomy}

**DOMAIN:** {domain}

**HTML CONTENT:**
{html_content}

**METADATA:**
- Title: {title}
- Meta Description: {meta_description}
- Meta Keywords: {meta_keywords}
- Platform Markers: {platform_markers}
- Outbound Links: {outbound_links}

**OUTPUT FORMAT (JSON only):**
{{
    "primary_category": "Category Name",
    "subcategory": "Subcategory Name",
    "confidence": 85,
    "evidence": "Clear explanation of classification based on content analysis"
}}

If confidence < 50%, use:
{{
    "primary_category": "Uncategorized",
    "subcategory": "Uncategorized",
    "confidence": 45,
    "evidence": "Insufficient evidence for confident classification"
}}

Provide only the JSON response:"""

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze a domain and classify it hierarchically.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing classification results
        """
        results: Dict[str, Any] = {"domain": domain, "classification": {}, "errors": []}

        try:
            # Fetch HTML content
            html_content = self._fetch_html_content(domain)
            if not html_content:
                results["errors"].append("Could not fetch HTML content")
                return results

            # Extract metadata and signals
            metadata = self._extract_metadata(html_content)

            # Perform LLM classification
            classification = self._classify_with_llm(domain, html_content, metadata)

            results["classification"] = classification

        except Exception as e:
            results["errors"].append(f"Classification failed: {str(e)}")

        return results

    def _fetch_html_content(self, domain: str) -> Optional[str]:
        """Fetch the HTML content of the domain homepage."""
        urls_to_try = [f"https://{domain}", f"http://{domain}"]

        for url in urls_to_try:
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type:
                        return response.text
            except (requests.RequestException, Exception):
                continue

        return None

    def _extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract metadata and signals from HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc.get("content", "") if meta_desc else ""

        # Extract meta keywords
        meta_keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        meta_keywords = meta_keywords_tag.get("content", "") if meta_keywords_tag else ""

        # Extract visible text content
        for script in soup(["script", "style"]):
            script.decompose()
        text_content = soup.get_text()
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = " ".join(chunk for chunk in chunks if chunk)

        # Detect platform markers
        platform_markers = self._detect_platform_markers(html_content, soup)

        # Extract outbound links
        outbound_links = self._extract_outbound_links(soup)

        return {
            "title": title,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "text_content": text_content[:2000],  # Limit length
            "platform_markers": platform_markers,
            "outbound_links": outbound_links,
        }

    def _detect_platform_markers(self, html_content: str, soup: BeautifulSoup) -> List[str]:
        """Detect common platform markers in the HTML."""
        markers = []

        # Common platform indicators
        platform_patterns = {
            "WordPress": [r"wp-content", r"wp-includes", r"wordpress", r"wp-json"],
            "Shopify": [r"shopify", r"myshopify", r"cdn\.shopify"],
            "Wix": [r"wix", r"wixsite"],
            "Squarespace": [r"squarespace"],
            "Drupal": [r"drupal"],
            "Joomla": [r"joomla"],
            "Magento": [r"magento"],
            "WooCommerce": [r"woocommerce"],
            "React": [r"react", r"reactjs"],
            "Angular": [r"angular"],
            "Vue": [r"vue"],
            "Bootstrap": [r"bootstrap"],
            "jQuery": [r"jquery"],
            "Google Analytics": [r"google-analytics", r"gtag", r"ga\("],
            "Facebook Pixel": [r"facebook", r"fbq"],
            "Cloudflare": [r"cloudflare"],
            "AWS": [r"amazonaws", r"aws"],
            "Google Cloud": [r"googleapis", r"gstatic"],
            "Azure": [r"azure", r"microsoft"],
        }

        for platform, patterns in platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    markers.append(platform)
                    break

        return list(set(markers))  # Remove duplicates

    def _extract_outbound_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract outbound links from the page."""
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href.startswith(("http://", "https://")):
                links.append(href)
        return links[:20]  # Limit to first 20 links

    def _classify_with_llm(self, domain: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to classify the domain."""
        try:
            # Format taxonomy for prompt
            taxonomy_text = "\n".join(
                [
                    f"{i+1}️⃣ {category}\n" + "\n".join([f"  - {sub}" for sub in subcategories])
                    for i, (category, subcategories) in enumerate(self.taxonomy.items())
                ]
            )

            # Create prompt
            prompt = self.classification_prompt.format(
                taxonomy=taxonomy_text,
                domain=domain,
                html_content=html_content[:3000],  # Limit HTML content length
                title=metadata.get("title", ""),
                meta_description=metadata.get("meta_description", ""),
                meta_keywords=metadata.get("meta_keywords", ""),
                platform_markers=", ".join(metadata.get("platform_markers", [])),
                outbound_links=", ".join(metadata.get("outbound_links", [])[:10]),
            )

            # Send to LLM
            response = self._send_to_ollama(prompt)

            # Parse response
            classification = self._parse_classification_response(response)

            return classification

        except Exception as e:
            # Fallback classification
            return {
                "primary_category": "Uncategorized",
                "subcategory": "Uncategorized",
                "confidence": 0,
                "evidence": f"Classification failed: {str(e)}",
            }

    def _send_to_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama LLM service."""
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "top_p": 0.9},  # Low temperature for consistent classification
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate", json=data, timeout=300  # 5 minutes for LLM generation
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except requests.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}")

    def _parse_classification_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM classification response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                classification = json.loads(json_str)

                # Validate required fields
                required_fields = ["primary_category", "subcategory", "confidence", "evidence"]
                if all(field in classification for field in required_fields):
                    # Ensure confidence is a number
                    confidence = classification.get("confidence", 0)
                    if isinstance(confidence, str):
                        try:
                            confidence = int(confidence)
                        except ValueError:
                            confidence = 0

                    # Ensure confidence is within bounds
                    confidence = max(0, min(100, confidence))

                    return {
                        "primary_category": classification.get("primary_category", "Uncategorized"),
                        "subcategory": classification.get("subcategory", "Uncategorized"),
                        "confidence": confidence,
                        "evidence": classification.get("evidence", "No evidence provided"),
                    }

            # Fallback if JSON parsing fails
            return {
                "primary_category": "Uncategorized",
                "subcategory": "Uncategorized",
                "confidence": 0,
                "evidence": f"Failed to parse LLM response: {response[:200]}",
            }

        except (json.JSONDecodeError, Exception) as e:
            return {
                "primary_category": "Uncategorized",
                "subcategory": "Uncategorized",
                "confidence": 0,
                "evidence": f"Response parsing error: {str(e)}",
            }

    def is_available(self) -> bool:
        """Check if the analyzer is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            return response.status_code == 200
        except (requests.RequestException, Exception):
            return False

    def get_taxonomy(self) -> Dict[str, List[str]]:
        """Get the current classification taxonomy."""
        return self.taxonomy.copy()

    def update_taxonomy(self, new_taxonomy: Dict[str, List[str]]) -> None:
        """Update the classification taxonomy."""
        self.taxonomy = new_taxonomy.copy()


def classify_domain_hierarchically(
    domain: str, ollama_url: str = "http://localhost:11434", model: str = "gemma:2b"
) -> Dict[str, Any]:
    """
    Convenience function to classify a domain hierarchically.

    Args:
        domain: The domain to classify
        ollama_url: Ollama service URL
        model: LLM model to use

    Returns:
        Dict containing classification results
    """
    analyzer = HierarchicalClassificationAnalyzer(ollama_url=ollama_url, model=model)
    return analyzer.analyze(domain)
