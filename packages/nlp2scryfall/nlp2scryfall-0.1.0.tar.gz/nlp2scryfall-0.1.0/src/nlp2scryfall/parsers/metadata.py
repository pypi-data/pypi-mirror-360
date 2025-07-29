"""
Parsers for card metadata: sets, artists, collector numbers, and dates.
"""

import re
from datetime import datetime
from typing import Dict, Optional

from ..scryfall_api import ScryfallAPI
from .core import BaseParser


class SetParser(BaseParser):
    """Parser for set-related queries."""

    def __init__(self, api: Optional[ScryfallAPI] = None) -> None:
        self.api = api or ScryfallAPI()
        self._sets_cache: Optional[Dict[str, str]] = None
        self._sets_cache_time: Optional[datetime] = None

        # Special sets that don't follow normal naming patterns
        self.special_sets = {
            "the list": "plst",
            "list": "plst",
            "secret lair": "sld",
            "commander": "cmd",
            "commander legends": "cml",
            "modern horizons": "mh1",
            "modern horizons 2": "mh2",
            "modern horizons 3": "mh3",
            "time spiral remastered": "tsr",
            "double masters": "2xm",
            "double masters 2022": "2x2",
            "ultimate masters": "uma",
            "masters 25": "a25",
            "iconic masters": "ima",
            "eternal masters": "ema",
            "modern masters": "mma",
            "modern masters 2015": "mm2",
            "modern masters 2017": "mm3",
            "vintage masters": "vma",
        }

    def _get_sets(self) -> Dict[str, str]:
        """
        Get sets from API with caching.

        Returns:
            Dictionary mapping set names to set codes
        """
        # Cache for 1 hour
        if (
            self._sets_cache is None
            or self._sets_cache_time is None
            or (datetime.now() - self._sets_cache_time).seconds > 3600
        ):

            try:
                sets_data = self.api.get_sets()
                cache: Dict[str, str] = {}

                for set_info in sets_data:
                    name = set_info.get("name", "").lower()
                    code = set_info.get("code", "").lower()
                    if name and code:
                        cache[name] = code
                        # Also add without "edition" suffix
                        if name.endswith(" edition"):
                            cache[name[:-8]] = code
                        # Add set code as key too
                        cache[code] = code

                self._sets_cache = cache
                self._sets_cache_time = datetime.now()
            except Exception:
                # Fallback to empty dict if API fails
                self._sets_cache = {}

        return self._sets_cache or {}

    def parse(self, query: str) -> Optional[str]:
        """
        Parse set-related queries into Scryfall syntax.

        This method handles various set query formats including
        set names, abbreviations, and special set references.
        It uses dynamic data from the Scryfall API for accuracy.

        Args:
            query: Natural language query string containing set information

        Returns:
            Scryfall set syntax string or None if no match found

        Examples:
            >>> parser = SetParser()
            >>> parser.parse("cards from dominaria")
            "s:dom"
            >>> parser.parse("theros beyond death")
            "s:thb"
            >>> parser.parse("latest set")
            "s:latest"
            >>> parser.parse("the list cards")
            "s:plst"

        Set Syntax:
            - Set codes: s:dom, s:thb, s:war
            - Special sets: s:plst (The List), s:sld (Secret Lair)
            - Latest: s:latest (most recent set)

        Notes:
            - Uses dynamic data from Scryfall API for set codes
            - Handles various set name formats and abbreviations
            - Special sets have hardcoded mappings for reliability
            - Caches API data for performance
            - Supports "latest" and "most recent" queries
        """
        query_lower = query.lower()

        # Check for special sets first
        for name, code in self.special_sets.items():
            if name in query_lower:
                return f"s:{code}"

        # Check for "latest" or "most recent" queries
        if (
            "latest" in query_lower
            or "most recent" in query_lower
            or "newest" in query_lower
        ):
            # Check if there's a number specified
            num_match = re.search(
                r"(?:the\s+)?(?:most recent|latest)\s+(\d+)", query_lower
            )
            if num_match:
                num_sets = int(num_match.group(1))
                # Get the actual sets data to find the most recent ones
                sets_data = self.api.get_sets() if self.api else []
                if sets_data:
                    # Filter for released sets and sort by release date
                    import datetime

                    today = datetime.date.today()
                    released_sets = []
                    for s in sets_data:
                        released_at = s.get("released_at")
                        if (
                            released_at is not None
                            and s.get("set_type") not in ("promo", "funny")
                            and not s.get("digital", False)
                            and released_at <= today.isoformat()
                        ):
                            released_sets.append(s)
                    # Sort by release date descending (most recent first)
                    released_sets.sort(key=lambda s: s["released_at"], reverse=True)
                    most_recent = released_sets[:num_sets]
                    # Return space-separated set codes
                    set_codes = [f"s:{s['code']}" for s in most_recent]
                    return " ".join(set_codes)
                else:
                    return "s:latest"
            else:
                return "s:latest"

        # Check for "oldest" or "first" queries
        if "oldest" in query_lower or "first" in query_lower:
            return "s:oldest"

        # Get sets from API
        sets = self._get_sets()

        # Check for exact matches (using word boundaries)
        query_words = set(query_lower.split())
        for name, code in sets.items():
            if name in query_words:
                return f"s:{code}"

        # Check for partial matches (words in set names) - more restrictive
        query_words = set(query_lower.split())
        for name, code in sets.items():
            name_words = set(name.split())
            # Only match if there's a significant overlap (not just partial word matches)
            # Require at least 2 words to match for multi-word set names
            if len(name_words) > 1:
                if len(query_words.intersection(name_words)) >= 2:
                    return f"s:{code}"
            else:
                # For single-word set names, require exact word match (not substring)
                if name in query_words:
                    return f"s:{code}"

        return None


class ArtistParser(BaseParser):
    """Parser for artist-related queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"artist\s+([a-zA-Z\s]+)", "artist"),
            (r"by\s+([a-zA-Z\s]+)", "artist"),
            (r"painted\s+by\s+([a-zA-Z\s]+)", "artist"),
            (r"illustrated\s+by\s+([a-zA-Z\s]+)", "artist"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse artist-related queries into Scryfall syntax.

        This method handles various artist query formats including
        explicit artist mentions and different phrasings for attribution.
        It extracts artist names and formats them for Scryfall search.

        Args:
            query: Natural language query string containing artist information

        Returns:
            Scryfall artist syntax string or None if no match found

        Examples:
            >>> parser = ArtistParser()
            >>> parser.parse("artist seb mckinnon")
            "a:seb mckinnon"
            >>> parser.parse("by rebecca guay")
            "a:rebecca guay"
            >>> parser.parse("painted by noah bradley")
            "a:noah bradley"

        Artist Syntax:
            - Artist name: a:seb mckinnon, a:rebecca guay
            - Case-insensitive matching
            - Supports full names and partial matches

        Notes:
            - Extracts artist names from various phrasings
            - Handles "by", "artist", "painted by", "illustrated by"
            - Preserves original case for better matching
            - Supports multi-word artist names
        """
        query_lower = query.lower()

        # Check for artist patterns
        artist_patterns = [
            (r"artist\s+([a-zA-Z\s]+)", "artist"),
            (r"painted\s+by\s+([a-zA-Z\s]+)", "artist"),
            (r"illustrated\s+by\s+([a-zA-Z\s]+)", "artist"),
            # Only match "by" when it's clearly an artist context (not ordering)
            (r"(?<!order\s)(?<!sort\s)by\s+([a-zA-Z\s]+)", "artist"),
        ]

        for pattern, prefix in artist_patterns:
            match = re.search(pattern, query_lower)
            if match:
                artist_name = match.group(1).strip()
                # Find the original case in the query
                original_query = query
                artist_start = original_query.lower().find(artist_name)
                if artist_start != -1:
                    original_artist = original_query[
                        artist_start:artist_start + len(artist_name)
                    ]
                    return f"a:{original_artist}"

        return None


class CollectorNumberParser(BaseParser):
    """Parser for collector number queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"number\s+(\d+)", "number"),
            (r"#(\d+)", "number"),
            (r"collector\s+number\s+(\d+)", "number"),
            (r"card\s+(\d+)", "number"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse collector number queries into Scryfall syntax.

        This method handles various collector number query formats including
        explicit number mentions, hash notation, and different phrasings.

        Args:
            query: Natural language query string containing collector number information

        Returns:
            Scryfall collector number syntax string or None if no match found

        Examples:
            >>> parser = CollectorNumberParser()
            >>> parser.parse("number 123")
            "number:123"
            >>> parser.parse("#456")
            "number:456"
            >>> parser.parse("collector number 789")
            "number:789"

        Collector Number Syntax:
            - Number: number:123, number:456
            - Supports various input formats

        Notes:
            - Handles "number", "#", "collector number", "card" prefixes
            - Extracts numeric values for collector number search
            - Supports both explicit and implicit number references
        """
        query_lower = query.lower()

        # Check for collector number patterns
        number_patterns = [
            (r"number\s+(\d+)", "number"),
            (r"#(\d+)", "number"),
            (r"collector\s+number\s+(\d+)", "number"),
            (r"card\s+(\d+)", "number"),
        ]

        for pattern, prefix in number_patterns:
            match = re.search(pattern, query_lower)
            if match:
                number = match.group(1)
                return f"{prefix}:{number}"

        return None


class DateParser(BaseParser):
    """Parser for date-related queries."""

    def __init__(self) -> None:
        self.patterns = [
            (r"(\d{4})", "year"),
            (r"(\d{1,2})/(\d{1,2})/(\d{4})", "date"),
            (r"(\d{4})-(\d{1,2})-(\d{1,2})", "date"),
        ]

    def parse(self, query: str) -> Optional[str]:
        """
        Parse date-related queries into Scryfall syntax.

        This method handles various date query formats including
        years, full dates, and different date separators.

        Args:
            query: Natural language query string containing date information

        Returns:
            Scryfall date syntax string or None if no match found

        Examples:
            >>> parser = DateParser()
            >>> parser.parse("cards from 2020")
            "year:2020"
            >>> parser.parse("released in 2019")
            "year:2019"
            >>> parser.parse("date 2020-01-15")
            "date:2020-01-15"

        Date Syntax:
            - Year: year:2020, year:2019
            - Full date: date:2020-01-15
            - Supports various date formats

        Notes:
            - Handles year-only and full date queries
            - Supports different date separators (/, -)
            - Extracts years and dates for release date searches
            - Validates date formats for accuracy
        """
        query_lower = query.lower()

        # Check for full date patterns first
        date_patterns = [
            (r"(\d{1,2})/(\d{1,2})/(\d{4})", "date"),
            (r"(\d{4})-(\d{1,2})-(\d{1,2})", "date"),
        ]

        for pattern, prefix in date_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if len(match.groups()) == 3:
                    if pattern == r"(\d{1,2})/(\d{1,2})/(\d{4})":
                        month, day, year = match.groups()
                        return f"{prefix}:{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:
                        year, month, day = match.groups()
                        return f"{prefix}:{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Check for year-only patterns
        year_patterns = [
            (r"(\d{4})", "year"),
        ]

        for pattern, prefix in year_patterns:
            match = re.search(pattern, query_lower)
            if match:
                year = match.group(1)
                # Validate year is reasonable
                if 1993 <= int(year) <= 2030:
                    return f"{prefix}:{year}"

        return None
