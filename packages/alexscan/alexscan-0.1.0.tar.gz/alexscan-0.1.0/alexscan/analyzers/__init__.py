"""
Analyzer modules for domain analysis.

This package provides a modular architecture for domain analysis.
Analyzers can be added here to support different types of domain analysis
such as DNS, WHOIS, SSL, and blocklist checking.
"""

from .base import BaseAnalyzer
from .dns import DNSAnalyzer

__all__ = ["BaseAnalyzer", "DNSAnalyzer"]
