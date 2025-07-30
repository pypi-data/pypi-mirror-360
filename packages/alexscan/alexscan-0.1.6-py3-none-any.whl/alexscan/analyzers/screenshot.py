"""Screenshot analyzer for domain analysis."""

import base64
import os
import time
from pathlib import Path
from typing import Any, Dict

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base import BaseAnalyzer


class ScreenshotAnalyzer(BaseAnalyzer):
    """Screenshot analyzer for capturing homepage screenshots of domains."""

    def __init__(
        self, output_dir: str = "reports", timeout: int = 30, disable_js: bool = False, embed_base64: bool = True
    ):
        super().__init__("screenshot", "Homepage screenshot capture analyzer")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timeout = timeout
        self.disable_js = disable_js
        self.embed_base64 = embed_base64
        self.driver = None

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Capture a screenshot of the domain's homepage.

        Args:
            domain: The domain to capture

        Returns:
            Dict containing screenshot analysis results
        """
        results: Dict[str, Any] = {"domain": domain, "screenshot_data": {}, "errors": []}

        try:
            # Create domain-specific output directory
            domain_dir = self.output_dir / domain
            domain_dir.mkdir(exist_ok=True)

            screenshot_path = domain_dir / "homepage.png"

            # Try to capture screenshot
            success, url_used, error = self._capture_screenshot(domain, screenshot_path)

            if success:
                # Get file size
                file_size = os.path.getsize(screenshot_path)

                # Convert to base64 if requested
                base64_data = None
                if self.embed_base64:
                    try:
                        base64_data = self._convert_to_base64(screenshot_path)
                    except Exception as e:
                        results["errors"].append(f"Failed to convert screenshot to base64: {str(e)}")

                results["screenshot_data"] = {
                    "screenshot_path": str(screenshot_path),
                    "url_used": url_used,
                    "file_size": file_size,
                    "timestamp": time.time(),
                    "success": True,
                    "timeout": self.timeout,
                    "javascript_disabled": self.disable_js,
                    "base64_data": base64_data,
                    "embed_base64": self.embed_base64,
                }
            else:
                results["errors"].append(f"Screenshot capture failed: {error}")
                results["screenshot_data"] = {
                    "success": False,
                    "error": error,
                    "timeout": self.timeout,
                    "javascript_disabled": self.disable_js,
                    "embed_base64": self.embed_base64,
                }

        except Exception as e:
            results["errors"].append(f"Screenshot analysis failed: {str(e)}")
            results["screenshot_data"] = {"success": False, "error": str(e), "embed_base64": self.embed_base64}

        return results

    def _convert_to_base64(self, screenshot_path: Path) -> str:
        """
        Convert screenshot file to base64 data.

        Args:
            screenshot_path: Path to the screenshot file

        Returns:
            Base64 encoded string of the image
        """
        with open(screenshot_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded_string}"

    def _capture_screenshot(self, domain: str, screenshot_path: Path) -> tuple[bool, str, str]:
        """
        Capture a screenshot of the domain's homepage.

        Args:
            domain: Domain to capture
            screenshot_path: Path to save the screenshot

        Returns:
            Tuple of (success, url_used, error_message)
        """
        driver = None
        try:
            # Setup Chrome options
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            # Disable JavaScript if requested
            if self.disable_js:
                chrome_options.add_argument("--disable-javascript")

            # Try to use system Chrome or Chromium
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]

            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break

            if chrome_binary:
                chrome_options.binary_location = chrome_binary

            # Create WebDriver
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except WebDriverException as e:
                # Try with explicit service if direct creation fails
                try:
                    service = ChromeService()
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                except WebDriverException:
                    return False, "", f"Failed to create Chrome WebDriver: {str(e)}"

            # Set timeouts
            driver.set_page_load_timeout(self.timeout)
            driver.implicitly_wait(10)

            # Try HTTPS first, then HTTP
            protocols = ["https", "http"]
            last_error = ""

            for protocol in protocols:
                url = f"{protocol}://{domain}"
                try:
                    driver.get(url)

                    # Wait for page to load
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    except TimeoutException:
                        # Continue even if body not found, page might still be usable
                        pass

                    # Additional wait for dynamic content
                    time.sleep(2)

                    # Take screenshot
                    success = driver.save_screenshot(str(screenshot_path))

                    if success and screenshot_path.exists():
                        return True, url, ""
                    else:
                        last_error = f"Failed to save screenshot for {url}"

                except TimeoutException:
                    last_error = f"Timeout loading {url}"
                    continue
                except WebDriverException as e:
                    last_error = f"WebDriver error for {url}: {str(e)}"
                    continue

            return False, "", last_error

        except Exception as e:
            return False, "", str(e)
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def is_available(self) -> bool:
        """
        Check if screenshot analyzer is available.

        Returns:
            True if Selenium and Chrome are available, False otherwise
        """
        try:
            # Check if Chrome/Chromium is available
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]

            chrome_available = any(os.path.exists(path) for path in chrome_paths)

            if not chrome_available:
                return False

            # Try to create a simple Chrome driver instance
            try:
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")

                # Test driver creation
                driver = webdriver.Chrome(options=chrome_options)
                driver.quit()
                return True
            except WebDriverException:
                return False

        except ImportError:
            return False


def analyze_domain_screenshot(
    domain: str, output_dir: str = "reports", timeout: int = 30, disable_js: bool = False, embed_base64: bool = True
) -> Dict[str, Any]:
    """
    Capture a screenshot of a domain's homepage.

    Args:
        domain: Domain to capture
        output_dir: Directory to save screenshot
        timeout: Timeout in seconds
        disable_js: Whether to disable JavaScript
        embed_base64: Whether to include base64 encoded image data

    Returns:
        Screenshot analysis results
    """
    analyzer = ScreenshotAnalyzer(
        output_dir=output_dir, timeout=timeout, disable_js=disable_js, embed_base64=embed_base64
    )
    return analyzer.analyze(domain)
