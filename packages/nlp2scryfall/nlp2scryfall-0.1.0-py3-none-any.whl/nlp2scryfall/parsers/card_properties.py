"""
Parsers for basic card properties: colors, types, and rarities.
"""

import re
from typing import Optional

from .core import BaseParser


class ColorParser(BaseParser):
    """Parser for color-related queries."""

    def __init__(self) -> None:
        self.colors = {
            "white": "w",
            "blue": "u",
            "black": "b",
            "red": "r",
            "green": "g",
            "colorless": "c",
        }

        self.color_combinations = {
            "azorius": "wu",
            "dimir": "ub",
            "rakdos": "br",
            "gruul": "rg",
            "selesnya": "gw",
            "orzhov": "wb",
            "izzet": "ur",
            "golgari": "bg",
            "boros": "rw",
            "simic": "gu",
            "esper": "wub",
            "grixis": "ubr",
            "jund": "brg",
            "naya": "rwg",
            "bant": "gwu",
            "abzan": "wbg",
            "jeskai": "urw",
            "sultai": "bgu",
            "mardu": "rwb",
            "temur": "gur",
            "five color": "wubrg",
            "five-color": "wubrg",
            "5 color": "wubrg",
            "5-color": "wubrg",
        }

        # Patterns for color queries
        self.patterns = [
            (r"\b(white|blue|black|red|green|colorless)\b", "single_color"),
            (
                r"\b(azorius|dimir|rakdos|gruul|selesnya|orzhov|izzet|golgari|boros|simic)\b",
                "guild",
            ),
            (
                r"\b(esper|grixis|jund|naya|bant|abzan|jeskai|sultai|mardu|temur)\b",
                "shard",
            ),
            (r"\b(five color|five-color|5 color|5-color)\b", "five_color"),
            (
                r"\b(mono|monocolor|mono-color)\s+(white|blue|black|red|green)\b",
                "mono_color",
            ),
            (
                r"\b(white|blue|black|red|green)\s+and\s+(white|blue|black|red|green)\b",
                "two_color",
            ),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse color-related queries into Scryfall syntax.

        This method handles various color query types including single colors,
        color combinations, guilds, shards, mono-color queries, and land queries.
        It automatically determines whether to use card color (c) or color
        identity (id) based on the query context.

        Args:
            query: Natural language query string containing color information

        Returns:
            Scryfall color syntax string or None if no color information found

        Examples:
            >>> parser = ColorParser()
            >>> parser.parse("red cards")
            "c>=r"
            >>> parser.parse("mono blue creatures")
            "c=u"
            >>> parser.parse("green lands")
            "id>=g"
            >>> parser.parse("azorius cards")
            "c>=wu"
            >>> parser.parse("colorless artifacts")
            "c=c"
            >>> parser.parse("white and blue")
            "c>=uw"

        Color Syntax:
            - General colors: c>=r (cards that can be played with red)
            - Mono colors: c=r (cards that are only red)
            - Lands: id>=g (lands with green in color identity)
            - Colorless: c=c (colorless cards)

        Notes:
            - Land queries automatically use color identity (id) instead of card color (c)
            - Colorless queries always use exact match (c=c)
            - Color combinations are sorted in WUBRG order
            - Named combinations (guilds, shards) are recognized
            - "mono", "monocolor", "only" keywords trigger exact color matching
        """
        query_lower = query.lower()

        # Check for named color combinations (guilds, shards, five-color, etc.)
        for name, code in self.color_combinations.items():
            if name in query_lower:
                # Check if this is about lands (use identity instead of card color)
                is_land_query = "land" in query_lower
                if is_land_query:
                    return f"id>={code}"
                else:
                    return f"c>={code}"

        # Find all color mentions in the query
        color_words = re.findall(r"white|blue|black|red|green|colorless", query_lower)
        codes = set()
        for word in color_words:
            if word in self.colors:
                codes.add(self.colors[word])

        # If no colors found, return None
        if not codes:
            return None

        # Check if this is a mono-color query
        is_mono = "mono" in query_lower or "only" in query_lower

        # Check if this is about lands (use identity instead of card color)
        is_land_query = "land" in query_lower

        # Special case: colorless should always be exact match
        if "c" in codes and len(codes) == 1:
            is_mono = True

        # For lands, use identity (id) instead of card color (c)
        if is_land_query:
            if is_mono:
                return f"id={' '.join(codes)}"
            else:
                color_code = "".join(sorted(codes))
                return f"id>={color_code}"

        # For non-lands, use card color (c)
        if is_mono:
            return f"c={' '.join(codes)}"
        else:
            color_code = "".join(sorted(codes))
            return f"c>={color_code}"


class TypeParser(BaseParser):
    """Parser for card type-related queries."""

    def __init__(self) -> None:
        self.types = {
            "creature": "creature",
            "instant": "instant",
            "sorcery": "sorcery",
            "artifact": "artifact",
            "enchantment": "enchantment",
            "land": "land",
            "planeswalker": "planeswalker",
            "tribal": "tribal",
        }

        self.supertypes = {
            "legendary": "legendary",
            "snow": "snow",
            "world": "world",
            "basic": "basic",
        }

        self.subtypes = {
            "dragon": "dragon",
            "goblin": "goblin",
            "elf": "elf",
            "human": "human",
            "zombie": "zombie",
            "angel": "angel",
            "demon": "demon",
            "beast": "beast",
            "bird": "bird",
            "cat": "cat",
            "dog": "dog",
            "fish": "fish",
            "golem": "golem",
            "knight": "knight",
            "merfolk": "merfolk",
            "orc": "orc",
            "soldier": "soldier",
            "spirit": "spirit",
            "vampire": "vampire",
            "wolf": "wolf",
            "wizard": "wizard",
            "aura": "aura",
            "equipment": "equipment",
            "vehicle": "vehicle",
            "forest": "forest",
            "island": "island",
            "mountain": "mountain",
            "plains": "plains",
            "swamp": "swamp",
            "counter": "instant",
        }

    def parse(self, query: str) -> Optional[str]:
        """
        Parse type-related queries into Scryfall syntax.

        This method handles card types, subtypes, and supertypes. It processes
        both explicit type mentions and subtype-to-type mappings. The parser
        is designed to avoid conflicts with other parsers and handles
        irregular plurals and compound terms.

        Args:
            query: Natural language query string containing type information

        Returns:
            Scryfall type syntax string or None if no type information found

        Examples:
            >>> parser = TypeParser()
            >>> parser.parse("creatures")
            "t:creature"
            >>> parser.parse("dragons")
            "t:dragon"
            >>> parser.parse("legendary creatures")
            "t:legendary t:creature"
            >>> parser.parse("dual lands")
            None  # Avoids conflict with land modifiers
            >>> parser.parse("artifact creatures")
            "t:artifact t:creature"

        Type Categories:
            - Main types: creature, instant, sorcery, artifact, enchantment, land, planeswalker, tribal
            - Supertypes: legendary, snow, world, basic
            - Subtypes: dragon, goblin, elf, human, angel, demon, etc.

        Notes:
            - Subtypes are mapped to their main types when appropriate
            - Land modifiers (dual, fetch, shock, etc.) are excluded to avoid conflicts
            - Irregular plurals (elves, wolves, etc.) are handled automatically
            - Multiple types can be combined in a single query
            - The parser runs early in the translation process to avoid conflicts
        """
        query_lower = query.lower()
        components = []

        # Irregular plurals mapping
        irregular_plurals = {
            "sorceries": "sorcery",
            "elves": "elf",
            "wolves": "wolf",
            "golems": "golem",
            "knights": "knight",
            "plains": "plains",  # already plural
        }
        words = query_lower.split()
        word_set = set(words)
        for word in list(word_set):
            if word in irregular_plurals:
                word_set.add(irregular_plurals[word])

        # Subtype to main type mapping
        subtype_main_type = {
            # Creature subtypes
            "dragon": "creature",
            "goblin": "creature",
            "elf": "creature",
            "human": "creature",
            "zombie": "creature",
            "angel": "creature",
            "demon": "creature",
            "beast": "creature",
            "bird": "creature",
            "cat": "creature",
            "dog": "creature",
            "fish": "creature",
            "knight": "creature",
            "merfolk": "creature",
            "orc": "creature",
            "soldier": "creature",
            "spirit": "creature",
            "vampire": "creature",
            "wolf": "creature",
            "wizard": "creature",
            # Artifact subtypes
            "golem": "artifact",
            "equipment": "artifact",
            "vehicle": "artifact",
            # Enchantment subtypes
            "aura": "enchantment",
            # Land subtypes
            "forest": "land",
            "island": "land",
            "mountain": "land",
            "plains": "land",
            "swamp": "land",
        }

        # Track which main types were explicitly found
        explicit_types = set()
        # Check for supertypes first (more specific)
        for supertype, code in self.supertypes.items():
            if supertype in word_set:
                components.append(f"t:{code}")

        # Add explicit types in the order they appear in the query
        for word in words:
            for type_name, code in self.types.items():
                if (
                    word == type_name
                    or word == type_name + "s"
                    or (
                        word in irregular_plurals
                        and irregular_plurals[word] == type_name
                    )
                ):
                    # Special case: don't match "land" if it's part of a compound term like "dual lands"
                    if code == "land":
                        # Check if "land" is preceded by a modifier that makes it a specific land type
                        land_modifiers = [
                            "dual",
                            "fetch",
                            "shock",
                            "check",
                            "fast",
                            "slow",
                            "pain",
                            "filter",
                            "bounce",
                            "manland",
                        ]
                        if any(modifier in query_lower for modifier in land_modifiers):
                            continue
                    if f"t:{code}" not in components:
                        components.append(f"t:{code}")
                        explicit_types.add(code)

        # Check for subtypes last (least specific)
        for word in words:
            for subtype, code in self.subtypes.items():
                if (
                    word == subtype
                    or word == subtype + "s"
                    or (
                        word in irregular_plurals and irregular_plurals[word] == subtype
                    )
                ):
                    if f"t:{code}" not in components:
                        main_type = subtype_main_type.get(code)
                        # Add the subtype first
                        components.append(f"t:{code}")
                        # Only add the main type if "creature" (or other main type) is explicitly mentioned
                        # or if we're in a context where the main type is implied
                        main_type_code = f"t:{main_type}" if main_type else None
                        if (
                            main_type
                            and main_type not in explicit_types
                            and main_type_code not in components
                            and (main_type in word_set or f"{main_type}s" in word_set)
                            and main_type_code is not None
                        ):
                            components.append(main_type_code)

        return " ".join(components) if components else None


class RarityParser(BaseParser):
    """Parser for rarity queries."""

    def __init__(self) -> None:
        self.rarities = {
            "common": "common",
            "uncommon": "uncommon",
            "rare": "rare",
            "mythic": "mythic",
            "mythic rare": "mythic",
            "special": "special",
            "bonus": "bonus",
        }

    def parse(self, query: str) -> Optional[str]:
        """Parse rarity queries."""
        query_lower = query.lower()

        # Check for multi-word rarities first (more specific)
        multi_word_rarities = {k: v for k, v in self.rarities.items() if " " in k}
        for rarity, code in multi_word_rarities.items():
            if re.search(r"\b" + re.escape(rarity) + r"\b", query_lower):
                return f"r:{code}"

        # Then check for single-word rarities
        single_word_rarities = {k: v for k, v in self.rarities.items() if " " not in k}
        for rarity, code in single_word_rarities.items():
            if re.search(r"\b" + re.escape(rarity) + r"\b", query_lower):
                return f"r:{code}"

        return None
