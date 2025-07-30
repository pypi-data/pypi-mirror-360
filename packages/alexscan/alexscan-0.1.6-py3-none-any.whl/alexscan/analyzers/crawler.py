"""Web crawler analyzer for domain analysis."""

import re
import time
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class CrawlerAnalyzer(BaseAnalyzer):
    """Web crawler analyzer using requests and BeautifulSoup."""

    def __init__(self, max_pages: int = 10, timeout: int = 10, max_depth: int = 2):
        super().__init__("crawler", "Web crawler for domain analysis")
        self.max_pages = max_pages
        self.timeout = timeout
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AlexScan Web Crawler 1.0 (Security Analysis Tool)"})

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Crawl a domain and analyze its web content.

        Args:
            domain: The domain to crawl

        Returns:
            Dict containing crawl results
        """
        results: Dict[str, Any] = {"domain": domain, "crawl_data": {}, "errors": []}

        try:
            crawl_data = self._crawl_domain(domain)
            results["crawl_data"] = crawl_data
        except Exception as e:
            results["errors"].append(f"Crawling failed: {str(e)}")

        return results

    def _crawl_domain(self, domain: str) -> Dict[str, Any]:
        """Crawl the domain and collect information."""
        # Try both HTTP and HTTPS
        base_urls = [f"https://{domain}", f"http://{domain}"]

        crawl_data = {
            "pages_crawled": 0,
            "total_links": 0,
            "internal_links": set(),
            "external_links": set(),
            "emails": set(),
            "open_directories": [],
            "page_content": [],
            "errors": [],
            "technologies": set(),
            "forms": [],
            "images": set(),
            "documents": set(),
        }

        visited_urls = set()
        urls_to_visit = []

        # Find the working base URL
        working_base_url = None
        for base_url in base_urls:
            try:
                response = self.session.get(base_url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    working_base_url = base_url
                    urls_to_visit.append((base_url, 0))  # (url, depth)
                    break
            except requests.RequestException:
                continue

        if not working_base_url:
            raise Exception("Could not connect to domain via HTTP or HTTPS")

        # Crawl pages
        while urls_to_visit and crawl_data["pages_crawled"] < self.max_pages:
            url, depth = urls_to_visit.pop(0)

            if url in visited_urls or depth > self.max_depth:
                continue

            try:
                page_data = self._crawl_page(url, domain, depth)
                if page_data:
                    visited_urls.add(url)
                    crawl_data["pages_crawled"] += 1
                    crawl_data["page_content"].append(page_data)

                    # Add internal links to crawl queue
                    if depth < self.max_depth:
                        for link in page_data["internal_links"]:
                            if link not in visited_urls:
                                urls_to_visit.append((link, depth + 1))

                    # Update aggregated data
                    crawl_data["internal_links"].update(page_data["internal_links"])
                    crawl_data["external_links"].update(page_data["external_links"])
                    crawl_data["emails"].update(page_data["emails"])
                    crawl_data["technologies"].update(page_data["technologies"])
                    crawl_data["forms"].extend(page_data["forms"])
                    crawl_data["images"].update(page_data["images"])
                    crawl_data["documents"].update(page_data["documents"])

            except Exception as e:
                crawl_data["errors"].append(f"Error crawling {url}: {str(e)}")

            # Rate limiting
            time.sleep(1)

        # Convert sets to lists for JSON serialization
        crawl_data["internal_links"] = list(crawl_data["internal_links"])
        crawl_data["external_links"] = list(crawl_data["external_links"])
        crawl_data["emails"] = list(crawl_data["emails"])
        crawl_data["technologies"] = list(crawl_data["technologies"])
        crawl_data["images"] = list(crawl_data["images"])
        crawl_data["documents"] = list(crawl_data["documents"])
        crawl_data["total_links"] = len(crawl_data["internal_links"]) + len(crawl_data["external_links"])

        # Detect open directories
        crawl_data["open_directories"] = self._detect_open_directories(crawl_data["internal_links"], domain)

        return crawl_data

    def _crawl_page(self, url: str, domain: str, depth: int) -> Optional[Dict[str, Any]]:
        """Crawl a single page and extract information."""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            # Only process HTML content
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            page_data = {
                "url": url,
                "title": self._get_page_title(soup),
                "status_code": response.status_code,
                "content_length": len(response.text),
                "depth": depth,
                "internal_links": set(),
                "external_links": set(),
                "emails": self._extract_emails(response.text),
                "technologies": self._detect_technologies(response),
                "forms": self._extract_forms(soup),
                "images": set(),
                "documents": set(),
                "meta_description": self._get_meta_description(soup),
                "headers": dict(response.headers),
                "text_content": self._extract_text_content(soup),
            }

            # Extract links
            links = self._extract_links(soup, url, domain)
            page_data["internal_links"] = links["internal"]
            page_data["external_links"] = links["external"]
            page_data["images"] = links["images"]
            page_data["documents"] = links["documents"]

            return page_data

        except requests.RequestException as e:
            raise Exception(f"HTTP error: {str(e)}")
        except Exception as e:
            raise Exception(f"Parsing error: {str(e)}")

    def _get_page_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""

    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        return meta_desc.get("content", "") if meta_desc else ""

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Limit length to avoid memory issues
        return text[:2000] if len(text) > 2000 else text

    def _extract_links(self, soup: BeautifulSoup, base_url: str, domain: str) -> Dict[str, Set[str]]:
        """Extract and categorize links from the page."""
        links = {"internal": set(), "external": set(), "images": set(), "documents": set()}

        # Extract all links
        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue

            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)

            if parsed_url.netloc and domain in parsed_url.netloc:
                links["internal"].add(absolute_url)
            elif parsed_url.netloc:
                links["external"].add(absolute_url)

        # Extract image links
        for img in soup.find_all("img", src=True):
            src = img["src"].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                links["images"].add(absolute_url)

        # Extract document links
        doc_extensions = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"}
        for link in soup.find_all("a", href=True):
            href = link["href"].strip().lower()
            if any(href.endswith(ext) for ext in doc_extensions):
                absolute_url = urljoin(base_url, link["href"])
                links["documents"].add(absolute_url)

        return links

    def _extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = set(re.findall(email_pattern, text))

        # Filter out common false positives
        filtered_emails = set()
        for email in emails:
            if not any(exclude in email.lower() for exclude in ["example.com", "test.com", "lorem"]):
                filtered_emails.add(email)

        return filtered_emails

    def _detect_technologies(self, response: requests.Response) -> Set[str]:
        """Detect web technologies used."""
        technologies = set()

        headers = response.headers

        # Server detection
        server = headers.get("server", "").lower()
        if "apache" in server:
            technologies.add("Apache")
        elif "nginx" in server:
            technologies.add("Nginx")
        elif "iis" in server:
            technologies.add("IIS")

        # Framework detection
        if "x-powered-by" in headers:
            powered_by = headers["x-powered-by"].lower()
            if "php" in powered_by:
                technologies.add("PHP")
            elif "asp.net" in powered_by:
                technologies.add("ASP.NET")
            elif "express" in powered_by:
                technologies.add("Express.js")

        # Content analysis
        content = response.text.lower()
        if "wordpress" in content or "wp-content" in content:
            technologies.add("WordPress")
        elif "drupal" in content:
            technologies.add("Drupal")
        elif "joomla" in content:
            technologies.add("Joomla")

        # JavaScript frameworks
        if "react" in content:
            technologies.add("React")
        elif "angular" in content:
            technologies.add("Angular")
        elif "vue" in content:
            technologies.add("Vue.js")

        return technologies

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []

        for form in soup.find_all("form"):
            form_data = {"action": form.get("action", ""), "method": form.get("method", "GET").upper(), "inputs": []}

            for input_tag in form.find_all(["input", "textarea", "select"]):
                input_data = {
                    "type": input_tag.get("type", "text"),
                    "name": input_tag.get("name", ""),
                    "required": input_tag.has_attr("required"),
                }
                form_data["inputs"].append(input_data)

            forms.append(form_data)

        return forms

    def _detect_open_directories(self, internal_links: List[str], domain: str) -> List[str]:
        """Detect potential open directories."""
        open_directories = []

        # Common directory patterns to check
        common_dirs = [
            "/admin/",
            "/uploads/",
            "/files/",
            "/docs/",
            "/backup/",
            "/config/",
            "/logs/",
            "/tmp/",
            "/cache/",
            "/assets/",
        ]

        for directory in common_dirs:
            test_url = f"https://{domain}{directory}"
            try:
                response = self.session.get(test_url, timeout=5, allow_redirects=False)
                if response.status_code == 200:
                    content = response.text.lower()
                    # Look for directory listing indicators
                    if any(indicator in content for indicator in ["index of", "directory listing", "parent directory"]):
                        open_directories.append(test_url)
            except requests.RequestException:
                continue

        return open_directories

    def is_available(self) -> bool:
        """
        Check if crawler analyzer is available.

        Returns:
            True if requests and BeautifulSoup are available
        """
        try:
            return True
        except ImportError:
            return False


def crawl_domain(domain: str, max_pages: int = 10, timeout: int = 10, max_depth: int = 2) -> Dict[str, Any]:
    """
    Crawl a domain and return structured data.

    Args:
        domain: The domain to crawl
        max_pages: Maximum number of pages to crawl
        timeout: Request timeout in seconds
        max_depth: Maximum crawl depth

    Returns:
        Dict containing crawl results
    """
    analyzer = CrawlerAnalyzer(max_pages=max_pages, timeout=timeout, max_depth=max_depth)
    return analyzer.analyze(domain)
