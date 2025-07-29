"""
Parsers for text-based searches and content queries.
"""

import re
from typing import Optional

from .core import BaseParser


class TextParser(BaseParser):
    """Parser for text-based queries."""

    def __init__(self) -> None:
        # Common Magic: The Gathering terms that should be treated as text
        self.magic_terms = {
            "draw",
            "discard",
            "exile",
            "graveyard",
            "hand",
            "library",
            "battlefield",
            "stack",
            "mana",
            "life",
            "damage",
            "healing",
            "counter",
            "destroy",
            "sacrifice",
            "tap",
            "untap",
            "flying",
            "first strike",
            "double strike",
            "vigilance",
            "haste",
            "hexproof",
            "indestructible",
            "lifelink",
            "menace",
            "reach",
            "trample",
            "deathtouch",
            "defender",
            "flash",
            "protection",
            "shroud",
            "banding",
            "bushido",
            "cascade",
            "convoke",
            "dash",
            "delve",
            "devotion",
            "dredge",
            "echo",
            "entwine",
            "evoke",
            "exalted",
            "extort",
            "fabricate",
            "fading",
            "fear",
            "flanking",
            "flashback",
            "forecast",
            "fortify",
            "frenzy",
            "fuse",
            "graft",
            "grandeur",
            "gravestorm",
            "haste",
            "haunt",
            "hideaway",
            "horsemanship",
            "imprint",
            "indestructible",
            "infect",
            "intimidate",
            "kicker",
            "landfall",
            "level up",
            "living weapon",
            "madness",
            "miracle",
            "modular",
            "morph",
            "multikicker",
            "ninjutsu",
            "offering",
            "outlast",
            "overload",
            "persist",
            "phasing",
            "poisonous",
            "proliferate",
            "protection",
            "provoke",
            "prowl",
            "radiance",
            "raid",
            "rally",
            "rampage",
            "reach",
            "rebound",
            "recover",
            "reinforce",
            "replicate",
            "retrace",
            "ripple",
            "scavenge",
            "scry",
            "shadow",
            "shroud",
            "soulbond",
            "soulshift",
            "splice",
            "split second",
            "storm",
            "sunburst",
            "suspend",
            "sweep",
            "threshold",
            "totem armor",
            "transfigure",
            "transmute",
            "tribute",
            "typecycling",
            "undaunted",
            "undying",
            "unearth",
            "unleash",
            "vanishing",
            "vigilance",
            "wither",
            "wizardcycling",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse text-based queries into Scryfall syntax.

        This method handles various text query formats including
        card names, oracle text content, and flavor text. It's designed
        to be more restrictive to avoid overmatching other query types.

        Args:
            query: Natural language query string containing text information

        Returns:
            Scryfall text syntax string or None if no match found

        Examples:
            >>> parser = TextParser()
            >>> parser.parse("cards that say draw")
            "o:draw"
            >>> parser.parse("text contains flying")
            "o:flying"
            >>> parser.parse("name lightning bolt")
            "name:lightning bolt"
            >>> parser.parse("flavor text about dragons")
            "ft:dragons"

        Text Syntax:
            - Oracle text: o:draw, o:flying
            - Card name: name:lightning bolt
            - Flavor text: ft:dragons
            - Full text: text:lightning

        Notes:
            - More restrictive to avoid conflicts with other parsers
            - Handles Magic: The Gathering specific terminology
            - Supports various text search contexts
            - Avoids overmatching common words
            - Prioritizes specific text contexts over general terms
        """
        query_lower = query.lower()

        # Check for specific text contexts first
        if "name" in query_lower or "called" in query_lower:
            # Extract potential card name
            name_match = re.search(r"(?:name|called)\s+([a-zA-Z\s]+)", query_lower)
            if name_match:
                name = name_match.group(1).strip()
                return f"name:{name}"

        if "flavor" in query_lower or "flavour" in query_lower:
            # Extract flavor text content
            flavor_match = re.search(
                r"(?:flavor|flavour)\s+(?:text\s+)?(?:about\s+)?([a-zA-Z\s]+)",
                query_lower,
            )
            if flavor_match:
                text = flavor_match.group(1).strip()
                return f"ft:{text}"

        if "oracle" in query_lower or "rules" in query_lower:
            # Extract oracle text content
            oracle_match = re.search(
                r"(?:oracle|rules)\s+(?:text\s+)?(?:contains\s+)?([a-zA-Z\s]+)",
                query_lower,
            )
            if oracle_match:
                text = oracle_match.group(1).strip()
                return f"o:{text}"

        # Check for quoted text
        quoted_match = re.search(r'"([^"]+)"', query_lower)
        if quoted_match:
            text = quoted_match.group(1)
            return f'o:"{text}"'

        # Check for "with" patterns (more restrictive)
        with_match = re.search(r"with\s+([a-zA-Z\s]+)", query_lower)
        if with_match:
            text = with_match.group(1).strip()
            # Only match if it's a Magic-specific term or a quoted phrase
            if text in self.magic_terms or '"' in query_lower:
                return f'o:"{text}"'

        # Check for general text patterns
        text_patterns = [
            (r"(?:text|says?|contains?)\s+([a-zA-Z\s]+)", "o"),
            (r"([a-zA-Z\s]+)\s+(?:text|says?|contains?)", "o"),
        ]

        for pattern, prefix in text_patterns:
            match = re.search(pattern, query_lower)
            if match:
                text = match.group(1).strip()
                # Check if it's a Magic-specific term
                if text in self.magic_terms:
                    return f"{prefix}:{text}"
                # Check if it's a multi-word phrase (more likely to be intentional)
                if " " in text:
                    return f"{prefix}:{text}"

        # Check for standalone Magic terms (more restrictive)
        words = query_lower.split()
        for word in words:
            if word in self.magic_terms and len(word) > 3:  # Avoid short words
                # Only match if it's clearly a text search
                if any(
                    phrase in query_lower
                    for phrase in ["text", "says", "contains", "ability"]
                ):
                    return f"o:{word}"

        return None
