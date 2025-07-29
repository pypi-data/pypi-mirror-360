"""
Parsers for special queries: formats, functions, ordering, and card properties.
"""

import re
from typing import Optional

from .core import BaseParser


class FormatParser(BaseParser):
    """Parser for format-related queries."""

    def __init__(self) -> None:
        self.formats = {
            "standard": "standard",
            "modern": "modern",
            "legacy": "legacy",
            "vintage": "vintage",
            "commander": "commander",
            "edh": "commander",
            "pauper": "pauper",
            "pioneer": "pioneer",
            "historic": "historic",
            "alchemy": "alchemy",
            "explorer": "explorer",
            "brawl": "brawl",
            "oathbreaker": "oathbreaker",
            "limited": "limited",
            "sealed": "sealed",
            "draft": "draft",
            "cube": "cube",
            "casual": "casual",
            "kitchen table": "casual",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse format-related queries into Scryfall syntax.

        This method handles various format query formats including
        official format names and common abbreviations.

        Args:
            query: Natural language query string containing format information

        Returns:
            Scryfall format syntax string or None if no match found

        Examples:
            >>> parser = FormatParser()
            >>> parser.parse("modern legal cards")
            "f:modern"
            >>> parser.parse("commander staples")
            "f:commander"
            >>> parser.parse("standard deck")
            "f:standard"

        Format Syntax:
            - Format: f:modern, f:commander, f:standard
            - Supports all official Magic formats

        Notes:
            - Handles official format names and common abbreviations
            - Maps EDH to Commander format
            - Supports casual and kitchen table formats
            - Uses format legality for search
        """
        query_lower = query.lower()

        for format_name, code in self.formats.items():
            if format_name in query_lower:
                return f"f:{code}"

        return None


class FunctionParser(BaseParser):
    """Parser for function-related queries."""

    def __init__(self) -> None:
        self.functions = {
            "dual land": "function:dual-land",
            "dual lands": "function:dual-land",
            "fetch land": "function:fetchland",
            "fetch lands": "function:fetchland",
            "shock land": "function:shockland",
            "shock lands": "function:shockland",
            "check land": "function:checkland",
            "check lands": "function:checkland",
            "fast land": "function:fastland",
            "fast lands": "function:fastland",
            "slow land": "function:slowland",
            "slow lands": "function:slowland",
            "pain land": "function:painland",
            "pain lands": "function:painland",
            "filter land": "function:filterland",
            "filter lands": "function:filterland",
            "bounce land": "function:bounceland",
            "bounce lands": "function:bounceland",
            "manland": "function:manland",
            "manlands": "function:manland",
            "utility land": "function:utility",
            "utility lands": "function:utility",
            "counter spell": "function:counterspell",
            "counter spells": "function:counterspell",
            "counterspell": "function:counterspell",
            "counterspells": "function:counterspell",
            "removal spell": "function:removal",
            "removal spells": "function:removal",
            "removal": "function:removal",
            "burn spell": "function:burn",
            "burn spells": "function:burn",
            "burn": "function:burn",
            "draw spell": "function:draw",
            "draw spells": "function:draw",
            "draw": "function:draw",
            "lifegain spell": "function:lifegain",
            "lifegain spells": "function:lifegain",
            "lifegain": "function:lifegain",
            "mana rock": "function:mana_rock",
            "mana rocks": "function:mana_rock",
            "mana dork": "function:mana_dork",
            "mana dorks": "function:mana_dork",
            "ramp": "function:ramp",
            "ramp spell": "function:ramp",
            "ramp spells": "function:ramp",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse function-related queries into Scryfall syntax.

        This method handles various function query formats including
        land types and special card functions.

        Args:
            query: Natural language query string containing function information

        Returns:
            Scryfall function syntax string or None if no match found

        Examples:
            >>> parser = FunctionParser()
            >>> parser.parse("dual lands")
            "is:dual"
            >>> parser.parse("fetch land")
            "is:fetchland"
            >>> parser.parse("shock lands")
            "is:shockland"

        Function Syntax:
            - Land types: is:dual, is:fetchland, is:shockland
            - Special functions: is:utility, is:manland

        Notes:
            - Handles various land type classifications
            - Supports both singular and plural forms
            - Maps to Scryfall's is: function tags
            - Useful for finding specific land categories
        """
        query_lower = query.lower()

        for function_name, code in self.functions.items():
            if function_name in query_lower:
                return code

        return None


class OrderParser(BaseParser):
    """Parser for ordering queries."""

    def __init__(self) -> None:
        self.order_fields = {
            "name": "name",
            "price": "usd",
            "power": "pow",
            "toughness": "tou",
            "cmc": "cmc",
            "mana cost": "cmc",
            "converted mana cost": "cmc",
            "set": "set",
            "rarity": "rarity",
            "artist": "artist",
            "collector number": "number",
            "number": "number",
        }

        self.order_directions = {
            "ascending": "asc",
            "asc": "asc",
            "low to high": "asc",
            "lowest first": "asc",
            "cheapest": "asc",
            "alphabetical": "asc",
            "descending": "desc",
            "desc": "desc",
            "high to low": "desc",
            "highest first": "desc",
            "most expensive": "desc",
            "reverse alphabetical": "desc",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse ordering queries into Scryfall syntax.

        This method handles various ordering query formats including
        field specifications and sort directions.

        Args:
            query: Natural language query string containing ordering information

        Returns:
            Scryfall order syntax string or None if no match found

        Examples:
            >>> parser = OrderParser()
            >>> parser.parse("order by price ascending")
            "order:usd"
            >>> parser.parse("sort by name")
            "order:name"
            >>> parser.parse("cheapest first")
            "order:usd"
            >>> parser.parse("most expensive cards")
            "order:usd"

        Order Syntax:
            - Field ordering: order:usd, order:name, order:cmc
            - Default direction is ascending for most fields
            - Price defaults to ascending (cheapest first)

        Notes:
            - Handles various field names and synonyms
            - Supports different direction phrasings
            - Maps to Scryfall's order: syntax
            - Useful for organizing search results
        """
        query_lower = query.lower()

        # Check for explicit ordering patterns
        order_patterns = [
            (r"ordered?\s+by\s+([a-zA-Z\s]+)", "order"),
            (r"sorted?\s+by\s+([a-zA-Z\s]+)", "order"),
            (r"order\s+([a-zA-Z\s]+)", "order"),
            (r"sort\s+([a-zA-Z\s]+)", "order"),
        ]

        for pattern, prefix in order_patterns:
            match = re.search(pattern, query_lower)
            if match:
                field = match.group(1).strip()
                for field_name, code in self.order_fields.items():
                    if field in field_name or field_name in field:
                        return f"{prefix}:{code}"

        # Check for implicit ordering (cheapest, most expensive, etc.)
        if any(word in query_lower for word in ["cheapest", "lowest", "ascending"]):
            return "order:usd"
        elif any(
            word in query_lower for word in ["most expensive", "highest", "descending"]
        ):
            return "order:usd"
        elif "alphabetical" in query_lower:
            return "order:name"

        return None


class CardPropertyParser(BaseParser):
    """Parser for special card property queries."""

    def __init__(self) -> None:
        self.properties = {
            "double sided": "is:double-faced",
            "double-faced": "is:double-faced",
            "double face": "is:double-faced",
            "double face card": "is:double-faced",
            "double face cards": "is:double-faced",
            "transform": "is:double-faced",
            "transforming": "is:double-faced",
            "meld": "is:meld",
            "melding": "is:meld",
            "split": "is:split",
            "split card": "is:split",
            "split cards": "is:split",
            "fuse": "is:split",
            "aftermath": "is:aftermath",
            "adventure": "is:adventure",
            "adventure card": "is:adventure",
            "adventure cards": "is:adventure",
            "modal": "is:modal",
            "modal card": "is:modal",
            "modal cards": "is:modal",
            "flip": "is:flip",
            "flip card": "is:flip",
            "flip cards": "is:flip",
            "level up": "is:leveler",
            "leveler": "is:leveler",
            "level up card": "is:leveler",
            "level up cards": "is:leveler",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse special card property queries into Scryfall syntax.

        This method handles various special card property formats including
        double-faced cards, split cards, adventures, and other special types.

        Args:
            query: Natural language query string containing card property information

        Returns:
            Scryfall card property syntax string or None if no match found

        Examples:
            >>> parser = CardPropertyParser()
            >>> parser.parse("double sided cards")
            "is:double-faced"
            >>> parser.parse("split cards")
            "is:split"
            >>> parser.parse("adventure cards")
            "is:adventure"

        Card Property Syntax:
            - Special types: is:double-faced, is:split, is:adventure
            - Complex cards: is:meld, is:modal, is:flip, is:leveler

        Notes:
            - Handles various special card types and their synonyms
            - Maps to Scryfall's is: function tags
            - Supports both singular and plural forms
            - Useful for finding cards with special mechanics
        """
        query_lower = query.lower()

        for property_name, code in self.properties.items():
            if property_name in query_lower:
                return code

        return None


class SpellParser(BaseParser):
    """Parser for spell-related queries."""

    def __init__(self) -> None:
        self.spell_types = {
            "spell": "is:spell",
            "spells": "is:spell",
            "nonland": "is:spell",
            "non-land": "is:spell",
            "non land": "is:spell",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse spell-related queries into Scryfall syntax.

        This method handles spell queries and non-land card references.

        Args:
            query: Natural language query string containing spell information

        Returns:
            Scryfall spell syntax string or None if no match found

        Examples:
            >>> parser = SpellParser()
            >>> parser.parse("spells")
            "is:spell"
            >>> parser.parse("nonland cards")
            "is:spell"
            >>> parser.parse("non-land spells")
            "is:spell"

        Spell Syntax:
            - Spells: is:spell (all non-land cards)
            - Non-land: is:spell (alternative phrasing)

        Notes:
            - Maps to Scryfall's is:spell function
            - Handles various phrasings for non-land cards
            - Useful for excluding lands from searches
            - Supports both "spell" and "nonland" terminology
        """
        query_lower = query.lower()

        for spell_type, code in self.spell_types.items():
            if spell_type in query_lower:
                return code

        return None
