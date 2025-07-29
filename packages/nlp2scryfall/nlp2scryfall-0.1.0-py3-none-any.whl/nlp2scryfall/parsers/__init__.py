"""
Parser package for nlp2scryfall.

This package contains specialized parser classes organized by functionality:
- core: Base parser and core functionality
- card_properties: Color, type, rarity, and basic card properties
- numerical: Power/toughness, mana cost, price, and numerical comparisons
- metadata: Set, artist, collector number, date, and metadata queries
- text: Text-based searches and content queries
- special: Format, function, order, and special property queries
"""

from .card_properties import ColorParser, RarityParser, TypeParser
from .core import BaseParser
from .metadata import ArtistParser, CollectorNumberParser, DateParser, SetParser
from .numerical import ManaCostParser, PowerToughnessParser, PriceParser
from .special import (
    CardPropertyParser,
    FormatParser,
    FunctionParser,
    OrderParser,
    SpellParser,
)
from .text import TextParser

__all__ = [
    "BaseParser",
    "ColorParser",
    "TypeParser",
    "RarityParser",
    "PowerToughnessParser",
    "ManaCostParser",
    "PriceParser",
    "SetParser",
    "ArtistParser",
    "CollectorNumberParser",
    "DateParser",
    "TextParser",
    "FormatParser",
    "FunctionParser",
    "OrderParser",
    "CardPropertyParser",
    "SpellParser",
]
