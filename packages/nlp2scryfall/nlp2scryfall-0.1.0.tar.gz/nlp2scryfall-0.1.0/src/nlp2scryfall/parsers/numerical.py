"""
Parsers for numerical card properties: power/toughness, mana cost, and price.
"""

import re
from typing import Optional

from .core import BaseParser


class PowerToughnessParser(BaseParser):
    """Parser for power/toughness queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"power\s*[=<>]\s*(\d+)", "power"),
            (r"power\s+(\d+)", "power"),
            (r"p\s*[=<>]\s*(\d+)", "power"),
            (r"toughness\s*[=<>]\s*(\d+)", "toughness"),
            (r"toughness\s+(\d+)", "toughness"),
            (r"t\s*[=<>]\s*(\d+)", "toughness"),
            (r"(\d+)/\s*(\d+)", "power_toughness"),
            (r"(\d+)\s*/\s*(\d+)", "power_toughness"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse power/toughness queries into Scryfall syntax.

        This method handles various power/toughness query formats including
        explicit power/toughness mentions, abbreviated forms, and X/Y notation.
        It supports comparison operators and exact matches.

        Args:
            query: Natural language query string containing power/toughness information

        Returns:
            Scryfall power/toughness syntax string or None if no match found

        Examples:
            >>> parser = PowerToughnessParser()
            >>> parser.parse("power 5")
            "pow=5"
            >>> parser.parse("toughness >= 3")
            "tou>=3"
            >>> parser.parse("5/5 creatures")
            "pow=5 tou=5"
            >>> parser.parse("p>3 t<6")
            "pow>3 tou<6"

        Power/Toughness Syntax:
            - Power: pow=5, pow>3, pow<=7
            - Toughness: tou=5, tou>3, tou<=7
            - Combined: pow=5 tou=5 (for 5/5)

        Notes:
            - Supports comparison operators: =, >, <, >=, <=
            - Handles both full words and abbreviations (power/p, toughness/t)
            - X/Y notation is converted to separate power and toughness constraints
            - Multiple constraints can be combined in a single query
        """
        query_lower = query.lower()
        components = []

        # Handle X/Y notation first
        pt_match = re.search(r"(\d+)\s*/\s*(\d+)", query_lower)
        if pt_match:
            power, toughness = pt_match.groups()
            components.extend([f"pow={power}", f"tou={toughness}"])

        # Handle explicit power mentions (more specific patterns first)
        power_patterns = [
            (r"power\s+(\d+)\s+or\s+more", "pow>="),
            (r"power\s+(\d+)\s+or\s+less", "pow<="),
            (r"power\s*(?:greater than|more than|over|above)\s*(\d+)", "pow>"),
            (r"power\s*(?:less than|under|below)\s*(\d+)", "pow<"),
            (r"power\s*(?:equal to|exactly)\s*(\d+)", "pow="),
            (r"power\s*([=<>]+)\s*(\d+)", "pow"),
            (r"p\s*([=<>]+)\s*(\d+)", "pow"),
            (r"power\s+(\d+)", "pow"),
            (r"p\s+(\d+)", "pow"),
        ]

        for pattern, prefix in power_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if len(match.groups()) == 2:
                    op, value = match.groups()
                    components.append(f"{prefix}{op}{value}")
                else:
                    value = match.group(1)
                    if prefix.endswith((">", "<", "=")):
                        components.append(f"{prefix}{value}")
                    else:
                        components.append(f"{prefix}={value}")
                break  # Only use the first match

        # Handle explicit toughness mentions (more specific patterns first)
        toughness_patterns = [
            (r"toughness\s+(\d+)\s+or\s+more", "tou>="),
            (r"toughness\s+(\d+)\s+or\s+less", "tou<="),
            (r"toughness\s*(?:greater than|more than|over|above)\s*(\d+)", "tou>"),
            (r"toughness\s*(?:less than|under|below)\s*(\d+)", "tou<"),
            (r"toughness\s*(?:equal to|exactly)\s*(\d+)", "tou="),
            (r"toughness\s*([=<>]+)\s*(\d+)", "tou"),
            (r"t\s*([=<>]+)\s*(\d+)", "tou"),
            (r"toughness\s+(\d+)", "tou"),
            (r"t\s+(\d+)", "tou"),
        ]

        for pattern, prefix in toughness_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if len(match.groups()) == 2:
                    op, value = match.groups()
                    components.append(f"{prefix}{op}{value}")
                else:
                    value = match.group(1)
                    if prefix.endswith((">", "<", "=")):
                        components.append(f"{prefix}{value}")
                    else:
                        components.append(f"{prefix}={value}")
                break  # Only use the first match

        return " ".join(components) if components else None


class ManaCostParser(BaseParser):
    """Parser for mana cost queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"cmc\s*[=<>]\s*(\d+)", "cmc"),
            (r"mana\s+cost\s*[=<>]\s*(\d+)", "cmc"),
            (r"converted\s+mana\s+cost\s*[=<>]\s*(\d+)", "cmc"),
            (r"(\d+)\s+mana", "cmc"),
            (r"(\d+)\s+cmc", "cmc"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse mana cost queries into Scryfall syntax.

        This method handles various mana cost query formats including
        CMC (Converted Mana Cost) mentions, explicit mana cost references,
        and numerical mana values. It supports comparison operators.

        Args:
            query: Natural language query string containing mana cost information

        Returns:
            Scryfall mana cost syntax string or None if no match found

        Examples:
            >>> parser = ManaCostParser()
            >>> parser.parse("cmc 3")
            "cmc=3"
            >>> parser.parse("mana cost >= 5")
            "cmc>=5"
            >>> parser.parse("3 mana spells")
            "cmc=3"
            >>> parser.parse("converted mana cost < 2")
            "cmc<2"

        Mana Cost Syntax:
            - CMC: cmc=3, cmc>2, cmc<=6
            - Supports all comparison operators: =, >, <, >=, <=

        Notes:
            - CMC (Converted Mana Cost) is the primary way to search mana costs
            - Handles various phrasings: "cmc", "mana cost", "converted mana cost"
            - Supports both explicit operators and implicit equality
            - Avoids conflicts with price queries by being more specific
        """
        query_lower = query.lower()

        # Handle CMC patterns
        cmc_patterns = [
            (
                r"(?:mana cost|converted mana cost)\s*(?:greater than|more than|over|above)\s*(\d+)",
                "cmc>",
            ),
            (
                r"(?:mana cost|converted mana cost)\s*(?:less than|under|below)\s*(\d+)",
                "cmc<",
            ),
            (
                r"(?:mana cost|converted mana cost)\s*(?:equal to|exactly)\s*(\d+)",
                "cmc=",
            ),
            (r"(?:mana cost|converted mana cost)\s+(\d+)\s+or\s+more", "cmc>="),
            (r"(?:mana cost|converted mana cost)\s+(\d+)\s+or\s+less", "cmc<="),
            (
                r"(?:costs?|costing)\s*(?:greater than|more than|over|above)\s*(\d+)",
                "cmc>",
            ),
            (r"(?:costs?|costing)\s*(?:less than|under|below)\s*(\d+)", "cmc<"),
            (r"(?:costs?|costing)\s*(?:equal to|exactly)\s*(\d+)", "cmc="),
            (r"(?:costs?|costing)\s+(\d+)\s+or\s+more", "cmc>="),
            (r"(?:costs?|costing)\s+(\d+)\s+or\s+less", "cmc<="),
            (r"(\d+)\s+mana\s+or\s+less", "cmc<="),
            (r"(\d+)\s+mana\s+or\s+more", "cmc>="),
            (r"cmc\s*([=<>]+)\s*(\d+)", "cmc"),
            (r"mana\s+cost\s*([=<>]+)\s*(\d+)", "cmc"),
            (r"converted\s+mana\s+cost\s*([=<>]+)\s*(\d+)", "cmc"),
            (r"(\d+)\s+mana", "cmc"),
            (r"(\d+)\s+cmc", "cmc"),
        ]

        for pattern, prefix in cmc_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if len(match.groups()) == 2:
                    op, value = match.groups()
                    return f"{prefix}{op}{value}"
                else:
                    value = match.group(1)
                    if prefix.endswith((">", "<", "=")):
                        return f"{prefix}{value}"
                    else:
                        return f"{prefix}={value}"

        return None


class PriceParser(BaseParser):
    """Parser for price-related queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"price\s*[=<>]\s*\$?(\d+(?:\.\d+)?)", "price"),
            (r"\$(\d+(?:\.\d+)?)", "price"),
            (r"(\d+(?:\.\d+)?)\s+dollars?", "price"),
            (r"(\d+(?:\.\d+)?)\s+bucks?", "price"),
            (r"cheap", "cheap"),
            (r"expensive", "expensive"),
            (r"budget", "budget"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse price-related queries into Scryfall syntax.

        This method handles various price query formats including
        explicit price mentions, dollar amounts, and qualitative terms.
        It supports comparison operators and relative price indicators.

        Args:
            query: Natural language query string containing price information

        Returns:
            Scryfall price syntax string or None if no match found

        Examples:
            >>> parser = PriceParser()
            >>> parser.parse("price < $5")
            "usd<5"
            >>> parser.parse("$10 cards")
            "usd=10"
            >>> parser.parse("cheap cards")
            "usd<5"
            >>> parser.parse("expensive cards")
            "usd>20"
            >>> parser.parse("budget deck")
            "usd<50"

        Price Syntax:
            - USD: usd=10, usd>5, usd<=20
            - Qualitative: usd<5 (cheap), usd>20 (expensive), usd<50 (budget)
            - Supports all comparison operators: =, >, <, >=, <=

        Notes:
            - Uses USD as the default currency
            - Handles dollar signs and various price phrasings
            - Qualitative terms are mapped to reasonable price ranges
            - Avoids conflicts with mana cost queries by being more specific
        """
        query_lower = query.lower()

        # Handle explicit price patterns first (more specific)
        price_patterns = [
            (
                r"price\s*(?:greater than|more than|over|above)\s*\$?(\d+(?:\.\d+)?)",
                "usd>",
            ),
            (r"price\s*(?:less than|under|below)\s*\$?(\d+(?:\.\d+)?)", "usd<"),
            (r"price\s*(?:equal to|exactly)\s*\$?(\d+(?:\.\d+)?)", "usd="),
            (r"\$(\d+(?:\.\d+)?)\s+or\s+more", "usd>="),
            (r"\$(\d+(?:\.\d+)?)\s+or\s+less", "usd<="),
            (r"under\s+\$(\d+(?:\.\d+)?)", "usd<"),
            (r"over\s+\$(\d+(?:\.\d+)?)", "usd>"),
            (r"price\s*([=<>]+)\s*\$?(\d+(?:\.\d+)?)", "usd"),
            (r"\$(\d+(?:\.\d+)?)", "usd"),
            (r"(\d+(?:\.\d+)?)\s+dollars?", "usd"),
            (r"(\d+(?:\.\d+)?)\s+bucks?", "usd"),
        ]

        for pattern, prefix in price_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if len(match.groups()) == 2:
                    op, value = match.groups()
                    return f"{prefix}{op}{value}"
                else:
                    value = match.group(1)
                    if prefix.endswith((">", "<", "=")):
                        return f"{prefix}{value}"
                    else:
                        return f"{prefix}={value}"

        # Handle qualitative price terms only if no explicit price found
        if "cheap" in query_lower:
            return "usd<5"
        elif "expensive" in query_lower:
            return "usd>20"
        elif "budget" in query_lower:
            return "usd<50"

        return None
