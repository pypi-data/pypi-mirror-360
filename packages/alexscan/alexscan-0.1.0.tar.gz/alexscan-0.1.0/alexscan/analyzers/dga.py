"""DGA (Domain Generation Algorithm) analyzer for domain analysis."""

import math
import re
from typing import Any, Dict
from urllib.parse import urlparse

from .base import BaseAnalyzer


class DGAAnalyzer(BaseAnalyzer):
    """DGA analyzer for detecting algorithmically generated domains."""

    def __init__(self):
        super().__init__("dga", "Domain Generation Algorithm detection analyzer")

        # Common legitimate TLDs (higher weight for legitimacy)
        self.legitimate_tlds = {
            "com",
            "org",
            "net",
            "edu",
            "gov",
            "mil",
            "int",
            "co",
            "io",
            "ai",
            "uk",
            "de",
            "fr",
            "jp",
            "au",
            "ca",
            "br",
            "ru",
            "in",
            "cn",
        }

        # Common English words that appear in legitimate domains
        self.common_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "man",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "its",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
            "web",
            "app",
            "api",
            "dev",
            "test",
            "demo",
            "blog",
            "news",
            "mail",
            "shop",
            "store",
            "site",
            "page",
        }

    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze domain for DGA characteristics.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing DGA analysis results
        """
        results = {"domain": domain, "dga_analysis": {}, "errors": []}

        try:
            # Normalize domain
            normalized_domain = self._normalize_domain(domain)

            # Extract features
            features = self._extract_features(normalized_domain)

            # Calculate DGA probability
            dga_probability = self._calculate_dga_probability(features)

            # Classify domain
            classification = self._classify_domain(dga_probability)

            results["dga_analysis"] = {
                "normalized_domain": normalized_domain,
                "features": features,
                "dga_probability": round(dga_probability, 3),
                "classification": classification,
                "confidence": self._calculate_confidence(dga_probability),
                "risk_level": self._get_risk_level(dga_probability),
            }

        except Exception as e:
            results["errors"].append(f"DGA analysis failed: {str(e)}")

        return results

    def _normalize_domain(self, domain: str) -> str:
        """
        Normalize domain for analysis.

        Args:
            domain: Domain to normalize

        Returns:
            Normalized domain
        """
        # Remove protocol if present
        if "://" in domain:
            domain = urlparse(domain).netloc

        # Remove www prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        # Convert to lowercase
        domain = domain.lower()

        return domain

    def _extract_features(self, domain: str) -> Dict[str, float]:
        """
        Extract features for DGA detection.

        Args:
            domain: Domain to analyze

        Returns:
            Dict of extracted features
        """
        # Split domain into parts
        parts = domain.split(".")
        if len(parts) < 2:
            raise ValueError("Invalid domain format")

        subdomain = parts[0]
        tld = parts[-1]

        features = {}

        # Length-based features
        features["domain_length"] = len(subdomain)
        features["total_length"] = len(domain)

        # Character entropy
        features["entropy"] = self._calculate_entropy(subdomain)

        # Character composition
        features["vowel_ratio"] = self._calculate_vowel_ratio(subdomain)
        features["consonant_ratio"] = 1 - features["vowel_ratio"]
        features["digit_ratio"] = self._calculate_digit_ratio(subdomain)

        # Dictionary word presence
        features["contains_dictionary_words"] = self._contains_dictionary_words(subdomain)
        features["dictionary_word_ratio"] = self._calculate_dictionary_word_ratio(subdomain)

        # Character patterns
        features["consecutive_consonants"] = self._max_consecutive_consonants(subdomain)
        features["consecutive_digits"] = self._max_consecutive_digits(subdomain)
        features["char_frequency_variance"] = self._calculate_char_frequency_variance(subdomain)

        # TLD legitimacy
        features["legitimate_tld"] = 1.0 if tld in self.legitimate_tlds else 0.0

        # Structural features
        features["hyphen_count"] = subdomain.count("-")
        features["underscore_count"] = subdomain.count("_")
        features["has_special_chars"] = 1.0 if re.search(r"[^a-z0-9\-_]", subdomain) else 0.0

        return features

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0

        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        entropy = 0.0
        text_length = len(text)

        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _calculate_vowel_ratio(self, text: str) -> float:
        """Calculate ratio of vowels to total characters."""
        if not text:
            return 0.0

        vowels = "aeiou"
        vowel_count = sum(1 for char in text.lower() if char in vowels)
        return vowel_count / len(text)

    def _calculate_digit_ratio(self, text: str) -> float:
        """Calculate ratio of digits to total characters."""
        if not text:
            return 0.0

        digit_count = sum(1 for char in text if char.isdigit())
        return digit_count / len(text)

    def _contains_dictionary_words(self, text: str) -> float:
        """Check if text contains common dictionary words."""
        text_lower = text.lower()
        for word in self.common_words:
            if word in text_lower and len(word) >= 3:
                return 1.0
        return 0.0

    def _calculate_dictionary_word_ratio(self, text: str) -> float:
        """Calculate ratio of characters that are part of dictionary words."""
        if not text:
            return 0.0

        text_lower = text.lower()
        covered_chars = 0

        for word in self.common_words:
            if word in text_lower and len(word) >= 3:
                covered_chars += len(word)

        return min(covered_chars / len(text), 1.0)

    def _max_consecutive_consonants(self, text: str) -> int:
        """Find maximum consecutive consonants."""
        vowels = "aeiou"
        max_consecutive = 0
        current_consecutive = 0

        for char in text.lower():
            if char.isalpha() and char not in vowels:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _max_consecutive_digits(self, text: str) -> int:
        """Find maximum consecutive digits."""
        max_consecutive = 0
        current_consecutive = 0

        for char in text:
            if char.isdigit():
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        return max_consecutive

    def _calculate_char_frequency_variance(self, text: str) -> float:
        """Calculate variance in character frequencies."""
        if not text:
            return 0.0

        char_counts = {}
        for char in text.lower():
            char_counts[char] = char_counts.get(char, 0) + 1

        frequencies = list(char_counts.values())
        if len(frequencies) <= 1:
            return 0.0

        mean_freq = sum(frequencies) / len(frequencies)
        variance = sum((freq - mean_freq) ** 2 for freq in frequencies) / len(frequencies)

        return variance

    def _calculate_dga_probability(self, features: Dict[str, float]) -> float:
        """
        Calculate probability that domain is DGA-generated using a simple scoring model.

        Args:
            features: Extracted features

        Returns:
            Probability score between 0 and 1
        """
        score = 0.0

        # Length-based scoring (very long or very short domains are suspicious)
        length = features["domain_length"]
        if length < 5:
            score += 0.3
        elif length > 20:
            score += 0.4
        elif 8 <= length <= 12:
            score -= 0.1  # Typical legitimate length

        # Entropy scoring (high entropy suggests randomness)
        entropy = features["entropy"]
        if entropy > 3.5:
            score += 0.3
        elif entropy < 2.0:
            score += 0.2  # Very low entropy also suspicious
        elif 2.5 <= entropy <= 3.0:
            score -= 0.1  # Normal entropy range

        # Vowel ratio scoring
        vowel_ratio = features["vowel_ratio"]
        if vowel_ratio < 0.1 or vowel_ratio > 0.6:
            score += 0.2
        elif 0.2 <= vowel_ratio <= 0.4:
            score -= 0.1

        # Dictionary words scoring
        if features["contains_dictionary_words"] > 0:
            score -= 0.3
        if features["dictionary_word_ratio"] > 0.5:
            score -= 0.2

        # Consecutive characters scoring
        if features["consecutive_consonants"] > 5:
            score += 0.3
        if features["consecutive_digits"] > 3:
            score += 0.2

        # Digit ratio scoring
        digit_ratio = features["digit_ratio"]
        if digit_ratio > 0.3:
            score += 0.2
        elif digit_ratio > 0.5:
            score += 0.4

        # TLD scoring
        if features["legitimate_tld"] > 0:
            score -= 0.1
        else:
            score += 0.1

        # Character frequency variance
        if features["char_frequency_variance"] > 2.0:
            score += 0.1
        elif features["char_frequency_variance"] < 0.5:
            score += 0.1

        # Special characters
        if features["has_special_chars"] > 0:
            score += 0.1

        # Normalize score to 0-1 range
        probability = max(0.0, min(1.0, score))

        return probability

    def _classify_domain(self, probability: float) -> str:
        """
        Classify domain based on DGA probability.

        Args:
            probability: DGA probability score

        Returns:
            Classification string
        """
        if probability >= 0.7:
            return "Likely DGA"
        elif probability >= 0.4:
            return "Suspicious"
        elif probability >= 0.2:
            return "Possibly Legitimate"
        else:
            return "Likely Legitimate"

    def _calculate_confidence(self, probability: float) -> str:
        """
        Calculate confidence level based on probability.

        Args:
            probability: DGA probability score

        Returns:
            Confidence level string
        """
        if probability >= 0.8 or probability <= 0.2:
            return "High"
        elif probability >= 0.6 or probability <= 0.4:
            return "Medium"
        else:
            return "Low"

    def _get_risk_level(self, probability: float) -> str:
        """
        Get risk level based on probability.

        Args:
            probability: DGA probability score

        Returns:
            Risk level string
        """
        if probability >= 0.7:
            return "High"
        elif probability >= 0.4:
            return "Medium"
        else:
            return "Low"

    def is_available(self) -> bool:
        """
        Check if DGA analyzer is available.

        Returns:
            True as this analyzer uses built-in Python libraries
        """
        return True


def analyze_domain_dga(domain: str) -> Dict[str, Any]:
    """
    Analyze domain for DGA characteristics.

    Args:
        domain: The domain to analyze

    Returns:
        Dict containing DGA analysis results
    """
    analyzer = DGAAnalyzer()
    return analyzer.analyze(domain)
