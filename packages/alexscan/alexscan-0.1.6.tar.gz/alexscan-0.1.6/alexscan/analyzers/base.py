from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAnalyzer(ABC):
    """Base class for all domain analyzers."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Analyze a domain and return results.

        Args:
            domain: The domain to analyze

        Returns:
            Dict containing analysis results
        """

    def is_available(self) -> bool:
        """
        Check if the analyzer is available for use.

        Returns:
            True if analyzer can be used, False otherwise
        """
        return True

    def get_info(self) -> Dict[str, str]:
        """
        Get information about the analyzer.

        Returns:
            Dict containing analyzer metadata
        """
        return {"name": self.name, "description": self.description, "available": str(self.is_available())}
