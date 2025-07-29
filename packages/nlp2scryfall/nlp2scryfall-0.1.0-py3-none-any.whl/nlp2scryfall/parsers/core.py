"""
Core parser functionality and base classes.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseParser(ABC):
    """Base class for all parsers."""

    @abstractmethod
    def parse(self, query: str) -> Optional[str]:
        """
        Parse the query and return Scryfall syntax.

        Args:
            query: Natural language query

        Returns:
            Scryfall syntax string or None if no match
        """
        pass
