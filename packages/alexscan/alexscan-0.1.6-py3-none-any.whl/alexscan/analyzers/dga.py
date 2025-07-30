"""DGA (Domain Generation Algorithm) analyzer for domain analysis."""

import json
import math
import re
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from ..utils.cache_manager import CacheManager
from .base import BaseAnalyzer


class DGAAnalyzer(BaseAnalyzer):
    """DGA analyzer for detecting algorithmically generated domains."""

    def __init__(self, use_llm: bool = True, llm_timeout: int = 300) -> None:
        super().__init__("dga", "Domain Generation Algorithm detection analyzer")
        self.use_llm = use_llm
        self.llm_timeout = llm_timeout
        self.cache_manager = CacheManager()

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
        results: Dict[str, Any] = {"domain": domain, "dga_analysis": {}, "errors": []}

        try:
            # Normalize domain
            normalized_domain = self._normalize_domain(domain)

            # Extract features
            features = self._extract_features(normalized_domain)

            # Calculate DGA probability
            dga_probability = self._calculate_dga_probability(features)

            # Classify domain using traditional methods
            classification = self._classify_domain(dga_probability)
            traditional_confidence = self._calculate_confidence(dga_probability)

            # Enhanced classification with LLM if enabled
            llm_analysis = None
            if self.use_llm:
                llm_analysis = self._perform_llm_analysis(domain, features)

            # Combine traditional and LLM results
            final_classification, final_confidence = self._combine_analysis_results(
                classification, traditional_confidence, llm_analysis, dga_probability
            )

            results["dga_analysis"] = {
                "normalized_domain": normalized_domain,
                "features": features,
                "dga_probability": round(dga_probability, 3),
                "classification": final_classification,
                "confidence": final_confidence,
                "risk_level": self._get_risk_level(dga_probability),
                "traditional_analysis": {
                    "classification": classification,
                    "confidence": traditional_confidence,
                },
                "llm_analysis": llm_analysis,
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

        features: Dict[str, float] = {}

        # Length-based features
        features["domain_length"] = float(len(subdomain))
        features["total_length"] = float(len(domain))

        # Character entropy
        features["entropy"] = self._calculate_entropy(subdomain)

        # Character composition
        features["vowel_ratio"] = self._calculate_vowel_ratio(subdomain)
        features["consonant_ratio"] = 1.0 - features["vowel_ratio"]
        features["digit_ratio"] = self._calculate_digit_ratio(subdomain)

        # Dictionary word presence
        features["contains_dictionary_words"] = self._contains_dictionary_words(subdomain)
        features["dictionary_word_ratio"] = self._calculate_dictionary_word_ratio(subdomain)

        # Character patterns
        features["consecutive_consonants"] = float(self._max_consecutive_consonants(subdomain))
        features["consecutive_digits"] = float(self._max_consecutive_digits(subdomain))
        features["char_frequency_variance"] = self._calculate_char_frequency_variance(subdomain)

        # TLD legitimacy
        features["legitimate_tld"] = 1.0 if tld in self.legitimate_tlds else 0.0

        # Structural features
        features["hyphen_count"] = float(subdomain.count("-"))
        features["underscore_count"] = float(subdomain.count("_"))
        features["has_special_chars"] = 1.0 if re.search(r"[^a-z0-9\-_]", subdomain) else 0.0

        return features

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0

        char_counts: Dict[str, int] = {}
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

        char_counts: Dict[str, int] = {}
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

    def _perform_llm_analysis(self, domain: str, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform LLM-based DGA analysis.

        Args:
            domain: Domain to analyze
            features: Extracted features

        Returns:
            LLM analysis results
        """
        try:
            # Check cache first
            cached_result = self.cache_manager.get_cached_result(domain, "dga_llm")
            if cached_result:
                return cached_result

            # Load prompt template
            prompt_path = Path(__file__).parent.parent / "prompts" / "dga_prompt.txt"
            if not prompt_path.exists():
                return {"error": "DGA prompt template not found"}

            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Prepare domain parts
            parts = domain.split(".")
            subdomain = parts[0] if len(parts) > 1 else domain
            tld = parts[-1] if len(parts) > 1 else ""

            # Format prompt
            prompt = prompt_template.format(
                domain=domain,
                subdomain=subdomain,
                tld=tld,
                domain_length=int(features.get("domain_length", 0)),
                entropy=round(features.get("entropy", 0), 3),
                vowel_ratio=round(features.get("vowel_ratio", 0) * 100, 1),
                consonant_ratio=round(features.get("consonant_ratio", 0) * 100, 1),
                digit_ratio=round(features.get("digit_ratio", 0) * 100, 1),
                contains_dictionary_words="Yes" if features.get("contains_dictionary_words", 0) > 0 else "No",
                dictionary_word_ratio=round(features.get("dictionary_word_ratio", 0) * 100, 1),
                consecutive_consonants=int(features.get("consecutive_consonants", 0)),
                consecutive_digits=int(features.get("consecutive_digits", 0)),
                char_frequency_variance=round(features.get("char_frequency_variance", 0), 3),
                legitimate_tld="Yes" if features.get("legitimate_tld", 0) > 0 else "No",
            )

            # Call LLM (using the same approach as other analyzers)
            try:
                import ollama

                client = ollama.Client()

                response = client.chat(
                    model="gemma:2b",
                    messages=[{"role": "user", "content": prompt}],
                    options={"timeout": self.llm_timeout},
                )

                llm_response = response["message"]["content"]

                # Extract JSON from response
                json_start = llm_response.find("{")
                json_end = llm_response.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    llm_result = json.loads(json_str)

                    # Cache the result
                    self.cache_manager.set_cached_result(domain, "dga_llm", llm_result)

                    return llm_result
                else:
                    return {"error": "Invalid JSON response from LLM", "raw_response": llm_response}

            except ImportError:
                return {"error": "Ollama not available"}
            except Exception as e:
                return {"error": f"LLM analysis failed: {str(e)}"}

        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}

    def _combine_analysis_results(
        self,
        traditional_classification: str,
        traditional_confidence: str,
        llm_analysis: Dict[str, Any],
        dga_probability: float,
    ) -> tuple[str, str]:
        """
        Combine traditional and LLM analysis results.

        Args:
            traditional_classification: Traditional classification
            traditional_confidence: Traditional confidence
            llm_analysis: LLM analysis results
            dga_probability: DGA probability score

        Returns:
            Tuple of (final_classification, final_confidence)
        """
        if not llm_analysis or "error" in llm_analysis:
            # Fall back to traditional analysis
            return traditional_classification, traditional_confidence

        llm_classification = llm_analysis.get("classification", traditional_classification)
        llm_confidence = llm_analysis.get("confidence", 50)

        # Weight the results (LLM gets more weight for reasoning capability)
        llm_weight = 0.7
        traditional_weight = 0.3

        # Convert traditional confidence to numeric
        traditional_confidence_num = self._confidence_to_numeric(traditional_confidence)

        # Calculate weighted confidence
        weighted_confidence = (llm_confidence * llm_weight) + (traditional_confidence_num * traditional_weight)

        # Determine final classification
        if llm_classification == traditional_classification:
            # Both agree - use LLM classification with weighted confidence
            final_classification = llm_classification
        else:
            # Disagreement - prefer LLM but consider traditional
            if weighted_confidence > 70:
                final_classification = llm_classification
            elif weighted_confidence < 30:
                final_classification = traditional_classification
            else:
                # Middle ground - use more conservative classification
                final_classification = self._get_more_conservative_classification(
                    llm_classification, traditional_classification
                )

        return final_classification, self._numeric_to_confidence(weighted_confidence)

    def _confidence_to_numeric(self, confidence: str) -> float:
        """Convert confidence string to numeric value."""
        confidence_lower = confidence.lower()
        if "high" in confidence_lower:
            return 85.0
        elif "medium" in confidence_lower:
            return 65.0
        elif "low" in confidence_lower:
            return 45.0
        else:
            return 50.0

    def _numeric_to_confidence(self, confidence: float) -> str:
        """Convert numeric confidence to string."""
        if confidence >= 80:
            return "High"
        elif confidence >= 60:
            return "Medium"
        else:
            return "Low"

    def _get_more_conservative_classification(self, llm_class: str, traditional_class: str) -> str:
        """Get the more conservative classification when there's disagreement."""
        # Order from most to least conservative
        conservativeness_order = ["Likely Malicious", "Possibly Malicious", "Possibly Legitimate", "Likely Legitimate"]

        llm_index = conservativeness_order.index(llm_class) if llm_class in conservativeness_order else 2
        traditional_index = (
            conservativeness_order.index(traditional_class) if traditional_class in conservativeness_order else 2
        )

        # Return the more conservative (higher index) classification
        return conservativeness_order[max(llm_index, traditional_index)]

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
