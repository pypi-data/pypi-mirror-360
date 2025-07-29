"""
Main translator module for converting natural language to Scryfall syntax.

This module provides the primary interface for translating natural language
queries into Scryfall search syntax. The Translator class orchestrates
multiple specialized parsers to handle different aspects of Magic: The
Gathering card properties.

Key features:
- Natural language query processing
- Multi-parser coordination
- Query normalization and preprocessing
- Order-independent component matching
- Conflict resolution between parsers

The translator processes queries through a carefully ordered sequence of
parsers to avoid conflicts and ensure accurate results. It handles:
- Color and type parsing
- Set recognition with dynamic API integration
- Power/toughness and mana cost comparisons
- Text-based searches
- Format and rarity queries
- Ordering and special properties

Example usage:
    translator = Translator(cache_data=True)
    result = translator.translate("red dragons from dominaria")
    # Returns: "c>=r t:dragon s:dom"
"""

import re
from typing import List

from .parsers import (
    ArtistParser,
    CardPropertyParser,
    CollectorNumberParser,
    ColorParser,
    DateParser,
    FormatParser,
    FunctionParser,
    ManaCostParser,
    OrderParser,
    PowerToughnessParser,
    PriceParser,
    RarityParser,
    SetParser,
    SpellParser,
    TextParser,
    TypeParser,
)
from .scryfall_api import ScryfallAPI


class Translator:
    """
    Main translator class for converting natural language queries to Scryfall syntax.
    """

    def __init__(self, cache_data: bool = True):
        """
        Initialize the translator.

        Args:
            cache_data: Whether to cache Scryfall API data for better performance
        """
        self.api = ScryfallAPI(cache_data=cache_data)

        # Initialize all parsers
        self.parsers = {
            "color": ColorParser(),
            "type": TypeParser(),
            "set": SetParser(self.api),
            "power_toughness": PowerToughnessParser(),
            "mana_cost": ManaCostParser(),
            "rarity": RarityParser(),
            "text": TextParser(),
            "format": FormatParser(),
            "artist": ArtistParser(),
            "collector_number": CollectorNumberParser(),
            "date": DateParser(),
            "price": PriceParser(),
            "spell": SpellParser(),
            "function": FunctionParser(),
            "order": OrderParser(),
            "card_property": CardPropertyParser(),
        }

        # Common patterns for natural language
        self.patterns = {
            "find": r"\b(find|show|get|search for|look for)\b",
            "all": r"\ball\b",
            "with": r"\bwith\b",
            "that": r"\bthat\b",
            "from": r"\bfrom\b",
            "in": r"\bin\b",
            "costs": r"\b(costs?|costing)\b",
            "greater_than": r"\b(greater than|more than|over|above)\b",
            "less_than": r"\b(less than|under|below)\b",
            "equal_to": r"\b(equal to|exactly)\b",
            "and": r"\band\b",
            "or": r"\bor\b",
        }

    def translate(self, query: str) -> str:
        """
        Translate a natural language query to Scryfall syntax.

        This method processes natural language queries through multiple specialized
        parsers to generate Scryfall search syntax. The parsers are executed in
        a specific order to avoid conflicts and ensure accurate results.

        Args:
            query: Natural language query string. Can include multiple components
                   in any order (e.g., "red dragons from dominaria" or
                   "from dominaria red dragons" both work).

        Returns:
            Scryfall search syntax string. Returns empty string for empty/null queries.

        Examples:
            >>> translator = Translator()
            >>> translator.translate("red dragons")
            "c>=r t:dragon"
            >>> translator.translate("mono blue creatures from dominaria")
            "c=u t:creature s:dom"
            >>> translator.translate("green lands with power 5 or more")
            "t:land id>=g pow>=5"
            >>> translator.translate("the most recent 3 sets")
            "s:woe s:mat s:mom"

        Notes:
            - Color queries use 'c>=' for general colors, 'c=' for mono colors
            - Land queries automatically use 'id>=' for color identity
            - Set names are dynamically fetched from Scryfall API
            - Query components can appear in any order
            - Case insensitive processing
            - Filler words like "find", "show", "get" are ignored
        """
        if not query or not query.strip():
            return ""

        # Store original query for case-sensitive parsers
        original_query = query

        # Normalize the query
        query = self._normalize_query(query)

        # Parse different components
        components = []

        # Parse ordering first (to avoid conflicts with other parsers)
        order_result = self.parsers["order"].parse(query)
        if order_result:
            components.append(order_result)

        # Parse types
        type_result = self.parsers["type"].parse(query)
        if type_result:
            components.append(type_result)

        # Parse colors
        color_result = self.parsers["color"].parse(query)
        if color_result:
            components.append(color_result)

        # Parse functions (community tags)
        function_result = self.parsers["function"].parse(query)
        if function_result:
            components.append(function_result)

        # Parse spells
        spell_result = self.parsers["spell"].parse(query)
        if spell_result:
            components.append(spell_result)

        # Parse sets
        set_result = self.parsers["set"].parse(query)
        if set_result:
            components.append(set_result)

        # Parse power/toughness
        pt_result = self.parsers["power_toughness"].parse(query)
        if pt_result:
            components.append(pt_result)

        # Parse mana cost
        mana_result = self.parsers["mana_cost"].parse(query)
        if mana_result:
            components.append(mana_result)

        # Parse rarity
        rarity_result = self.parsers["rarity"].parse(query)
        if rarity_result:
            components.append(rarity_result)

        # Parse format
        format_result = self.parsers["format"].parse(query)
        if format_result:
            components.append(format_result)

        # Parse artist (use original query to preserve case)
        artist_result = self.parsers["artist"].parse(original_query)
        if artist_result:
            components.append(artist_result)

        # Parse collector number
        collector_result = self.parsers["collector_number"].parse(query)
        if collector_result:
            components.append(collector_result)

        # Parse date
        date_result = self.parsers["date"].parse(query)
        if date_result:
            components.append(date_result)

        # Parse price
        price_result = self.parsers["price"].parse(query)
        if price_result:
            components.append(price_result)

        # Parse text last (to avoid conflicts with other parsers)
        text_result = self.parsers["text"].parse(query)
        if text_result:
            components.append(text_result)

        # Parse card properties
        property_result = self.parsers["card_property"].parse(query)
        if property_result:
            components.append(property_result)

        # Combine all components
        result = " ".join(components)

        return result.strip()

    def _normalize_query(self, query: str) -> str:
        """
        Normalize the query by removing extra whitespace and converting to lowercase.

        Args:
            query: Raw query string

        Returns:
            Normalized query string
        """
        # Convert to lowercase
        query = query.lower()

        # Remove extra whitespace
        query = re.sub(r"\s+", " ", query)

        # Remove common filler words that don't affect meaning
        filler_words = [
            "please",
            "can you",
            "could you",
            "would you",
            "i want",
            "i need",
            "i would like",
            "i am looking for",
            "i am searching for",
        ]

        for word in filler_words:
            query = query.replace(word, "").strip()

        return query.strip()

    def get_supported_features(self) -> List[str]:
        """
        Get a list of supported features/query types.

        Returns:
            List of supported feature names
        """
        return list(self.parsers.keys())
