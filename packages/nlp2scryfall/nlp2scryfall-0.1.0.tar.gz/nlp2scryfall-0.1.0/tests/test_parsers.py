"""
Tests for individual parser classes.
"""

from unittest.mock import Mock

import pytest

from nlp2scryfall.parsers import (
    ArtistParser,
    CollectorNumberParser,
    ColorParser,
    DateParser,
    FormatParser,
    ManaCostParser,
    OrderParser,
    PowerToughnessParser,
    PriceParser,
    RarityParser,
    SetParser,
    TextParser,
    TypeParser,
)


class TestColorParser:
    """Test cases for ColorParser."""

    @pytest.fixture
    def parser(self):
        """Create a ColorParser instance."""
        return ColorParser()

    def test_single_colors(self, parser):
        """Test single color parsing."""
        test_cases = [
            ("red cards", "c>=r"),
            ("blue spells", "c>=u"),
            ("black creatures", "c>=b"),
            ("green lands", "id>=g"),  # Lands use id for color identity
            ("white angels", "c>=w"),
            ("colorless artifacts", "c=c"),  # Colorless is always exact match
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_guild_colors(self, parser):
        """Test guild color combinations."""
        test_cases = [
            ("azorius", "c>=wu"),
            ("dimir", "c>=ub"),
            ("rakdos", "c>=br"),
            ("gruul", "c>=rg"),
            ("selesnya", "c>=gw"),
            ("orzhov", "c>=wb"),
            ("izzet", "c>=ur"),
            ("golgari", "c>=bg"),
            ("boros", "c>=rw"),
            ("simic", "c>=gu"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_shard_colors(self, parser):
        """Test shard color combinations."""
        test_cases = [
            ("esper", "c>=wub"),
            ("grixis", "c>=ubr"),
            ("jund", "c>=brg"),
            ("naya", "c>=rwg"),
            ("bant", "c>=gwu"),
            ("abzan", "c>=wbg"),
            ("jeskai", "c>=urw"),
            ("sultai", "c>=bgu"),
            ("mardu", "c>=rwb"),
            ("temur", "c>=gur"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_five_color(self, parser):
        """Test five-color combinations."""
        test_cases = [
            ("five color", "c>=wubrg"),
            ("five-color", "c>=wubrg"),
            ("5 color", "c>=wubrg"),
            ("5-color", "c>=wubrg"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_two_color_combinations(self, parser):
        """Test two-color combinations with 'and'."""
        test_cases = [
            ("white and blue", "c>=uw"),  # Color order is WUBRG, so uw not wu
            ("red and green", "c>=gr"),  # Order doesn't matter, parser returns gr
            ("black and white", "c>=bw"),  # Order doesn't matter, parser returns bw
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_mono_color(self, parser):
        """Test mono-color queries."""
        test_cases = [
            ("mono red", "c=r"),
            ("monocolor blue", "c=u"),
            ("mono-color black", "c=b"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_no_color_match(self, parser):
        """Test queries with no color match."""
        test_cases = [
            ("creatures", None),
            ("spells", None),
            ("lands", None),
            ("artifacts", None),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestTypeParser:
    """Test cases for TypeParser."""

    @pytest.fixture
    def parser(self):
        """Create a TypeParser instance."""
        return TypeParser()

    def test_card_types(self, parser):
        """Test card type parsing."""
        test_cases = [
            ("creatures", "t:creature"),
            ("instants", "t:instant"),
            ("sorceries", "t:sorcery"),
            ("artifacts", "t:artifact"),
            ("enchantments", "t:enchantment"),
            ("lands", "t:land"),
            ("planeswalkers", "t:planeswalker"),
            ("tribal", "t:tribal"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_supertypes(self, parser):
        """Test supertype parsing."""
        test_cases = [
            ("legendary", "t:legendary"),
            ("snow", "t:snow"),
            ("world", "t:world"),
            ("basic", "t:basic"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_subtypes(self, parser):
        """Test subtype parsing."""
        test_cases = [
            ("dragons", "t:dragon"),
            ("goblins", "t:goblin"),
            ("elves", "t:elf"),
            ("humans", "t:human"),
            ("zombies", "t:zombie"),
            ("angels", "t:angel"),
            ("demons", "t:demon"),
            ("beasts", "t:beast"),
            ("birds", "t:bird"),
            ("cats", "t:cat"),
            ("dogs", "t:dog"),
            ("fish", "t:fish"),
            ("golems", "t:golem"),
            ("knights", "t:knight"),
            ("merfolk", "t:merfolk"),
            ("orcs", "t:orc"),
            ("soldiers", "t:soldier"),
            ("spirits", "t:spirit"),
            ("vampires", "t:vampire"),
            ("wolves", "t:wolf"),
            ("wizards", "t:wizard"),
            ("auras", "t:aura"),
            ("equipment", "t:equipment"),
            ("vehicles", "t:vehicle"),
            ("forests", "t:forest"),
            ("islands", "t:island"),
            ("mountains", "t:mountain"),
            ("plains", "t:plains"),
            ("swamps", "t:swamp"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_multiple_types(self, parser):
        """Test multiple type combinations."""
        test_cases = [
            ("legendary creatures", "t:legendary t:creature"),
            ("artifact creatures", "t:artifact t:creature"),
            ("enchantment auras", "t:enchantment t:aura"),
            ("basic lands", "t:basic t:land"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_no_type_match(self, parser):
        assert parser.parse("this is not a type") is None


class TestSetParser:
    """Test cases for SetParser."""

    @pytest.fixture
    def mock_api(self):
        """Create a mock API."""
        api = Mock()
        api.get_sets.return_value = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
            {"name": "Phyrexia: All Will Be One", "code": "one"},
        ]
        api.get_set_by_name.return_value = {"name": "Dominaria", "code": "dom"}
        return api

    @pytest.fixture
    def parser(self, mock_api):
        """Create a SetParser instance."""
        return SetParser(mock_api)

    def test_special_sets(self, parser):
        """Test special set keywords."""
        test_cases = [
            ("latest set", "s:latest"),
            ("newest cards", "s:latest"),
            ("most recent set", "s:latest"),
            ("oldest cards", "s:oldest"),
            ("first set", "s:oldest"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_from_set_name(self, parser):
        """Test 'from' followed by set name."""
        test_cases = [
            ("from dominaria", "s:dom"),
            ("cards from the brothers war", "s:bro"),  # Mock returns brothers war
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_direct_set_name(self, parser):
        """Test direct set name matching."""
        assert parser.parse("dominaria cards") == "s:dom"

    def test_no_set_match(self, parser):
        assert parser.parse("this is not a set") is None


class TestPowerToughnessParser:
    """Test cases for PowerToughnessParser."""

    @pytest.fixture
    def parser(self):
        """Create a PowerToughnessParser instance."""
        return PowerToughnessParser()

    def test_power_comparisons(self, parser):
        """Test power comparison queries."""
        test_cases = [
            ("power greater than 5", "pow>5"),
            ("power more than 3", "pow>3"),
            ("power over 7", "pow>7"),
            ("power above 4", "pow>4"),
            ("power less than 2", "pow<2"),
            ("power under 6", "pow<6"),
            ("power below 3", "pow<3"),
            ("power equal to 4", "pow=4"),
            ("power exactly 3", "pow=3"),
            ("power 3 or more", "pow>=3"),
            ("power 2 or less", "pow<=2"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_toughness_comparisons(self, parser):
        """Test toughness comparison queries."""
        test_cases = [
            ("toughness greater than 6", "tou>6"),
            ("toughness more than 4", "tou>4"),
            ("toughness over 8", "tou>8"),
            ("toughness above 5", "tou>5"),
            ("toughness less than 3", "tou<3"),
            ("toughness under 7", "tou<7"),
            ("toughness below 4", "tou<4"),
            ("toughness equal to 5", "tou=5"),
            ("toughness exactly 2", "tou=2"),
            ("toughness 4 or more", "tou>=4"),
            ("toughness 3 or less", "tou<=3"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_power_toughness_combinations(self, parser):
        """Test power/toughness combinations."""
        test_cases = [
            ("3/3 creatures", "pow=3 tou=3"),
            ("5/5 dragons", "pow=5 tou=5"),
            ("2/2 goblins", "pow=2 tou=2"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_no_power_toughness_match(self, parser):
        assert parser.parse("this is not a power toughness query") is None


class TestManaCostParser:
    """Test cases for ManaCostParser."""

    @pytest.fixture
    def parser(self):
        """Create a ManaCostParser instance."""
        return ManaCostParser()

    def test_mana_cost_comparisons(self, parser):
        """Test mana cost comparison queries."""
        test_cases = [
            ("mana cost greater than 5", "cmc>5"),
            ("mana cost more than 3", "cmc>3"),
            ("mana cost over 7", "cmc>7"),
            ("mana cost above 4", "cmc>4"),
            ("mana cost less than 2", "cmc<2"),
            ("mana cost under 6", "cmc<6"),
            ("mana cost below 3", "cmc<3"),
            ("mana cost equal to 4", "cmc=4"),
            ("mana cost exactly 3", "cmc=3"),
            ("mana cost 3 or more", "cmc>=3"),
            ("mana cost 2 or less", "cmc<=2"),
            ("costs greater than 5", "cmc>5"),
            ("costs more than 3", "cmc>3"),
            ("costs over 7", "cmc>7"),
            ("costs above 4", "cmc>4"),
            ("costs less than 2", "cmc<2"),
            ("costs under 6", "cmc<6"),
            ("costs below 3", "cmc<3"),
            ("costs equal to 4", "cmc=4"),
            ("costs exactly 3", "cmc=3"),
            ("costs 3 or more", "cmc>=3"),
            ("costs 2 or less", "cmc<=2"),
            ("costing greater than 5", "cmc>5"),
            ("costing more than 3", "cmc>3"),
            ("costing over 7", "cmc>7"),
            ("costing above 4", "cmc>4"),
            ("costing less than 2", "cmc<2"),
            ("costing under 6", "cmc<6"),
            ("costing below 3", "cmc<3"),
            ("costing equal to 4", "cmc=4"),
            ("costing exactly 3", "cmc=3"),
            ("costing 3 or more", "cmc>=3"),
            ("costing 2 or less", "cmc<=2"),
            ("3 mana or less", "cmc<=3"),
            ("5 mana or more", "cmc>=5"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_no_mana_cost_match(self, parser):
        assert parser.parse("this is not a mana cost query") is None


class TestRarityParser:
    """Test cases for RarityParser."""

    @pytest.fixture
    def parser(self):
        """Create a RarityParser instance."""
        return RarityParser()

    def test_rarity_parsing(self, parser):
        """Test rarity parsing."""
        test_cases = [
            ("common cards", "r:common"),
            ("uncommon spells", "r:uncommon"),
            ("rare creatures", "r:rare"),
            ("mythic rares", "r:mythic"),
            ("mythic rare cards", "r:mythic"),
            ("special cards", "r:special"),
            ("bonus cards", "r:bonus"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_no_rarity_match(self, parser):
        assert parser.parse("this is not a rarity") is None


class TestTextParser:
    """Test cases for TextParser."""

    @pytest.fixture
    def parser(self):
        """Create a TextParser instance."""
        return TextParser()

    def test_quoted_text(self, parser):
        """Test quoted text parsing."""
        test_cases = [
            ('"draw a card"', 'o:"draw a card"'),
            ('"destroy target"', 'o:"destroy target"'),
            ('"flying"', 'o:"flying"'),
            ('"counter target spell"', 'o:"counter target spell"'),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected

    def test_with_text(self, parser):
        """Test 'with' followed by text."""
        test_cases = [
            ("with flying", 'o:"flying"'),  # "flying" is a Magic term
            ("with draw a card", None),  # "draw a card" is not a single Magic term
            (
                "with destroy target",
                None,
            ),  # "destroy target" is not a single Magic term
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestFormatParser:
    """Test cases for FormatParser."""

    @pytest.fixture
    def parser(self):
        """Create a FormatParser instance."""
        return FormatParser()

    def test_format_parsing(self, parser):
        """Test format parsing."""
        test_cases = [
            ("standard", "f:standard"),
            ("modern", "f:modern"),
            ("legacy", "f:legacy"),
            ("vintage", "f:vintage"),
            ("commander", "f:commander"),
            ("pauper", "f:pauper"),
            ("pioneer", "f:pioneer"),
            ("historic", "f:historic"),
            ("alchemy", "f:alchemy"),
            ("brawl", "f:brawl"),
            ("oathbreaker", "f:oathbreaker"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestArtistParser:
    """Test cases for ArtistParser."""

    @pytest.fixture
    def parser(self):
        """Create an ArtistParser instance."""
        return ArtistParser()

    def test_artist_parsing(self, parser):
        """Test artist parsing."""
        test_cases = [
            ("by Christopher Rush", "a:Christopher Rush"),
            ("by Rebecca Guay", "a:Rebecca Guay"),
            ("artist Seb McKinnon", "a:Seb McKinnon"),
            ("painted by Noah Bradley", "a:Noah Bradley"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestCollectorNumberParser:
    """Test cases for CollectorNumberParser."""

    @pytest.fixture
    def parser(self):
        """Create a CollectorNumberParser instance."""
        return CollectorNumberParser()

    def test_collector_number_parsing(self, parser):
        """Test collector number parsing."""
        test_cases = [
            ("number 123", "number:123"),
            ("collector number 456", "number:456"),
            ("card number 789", "number:789"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestDateParser:
    """Test cases for DateParser."""

    @pytest.fixture
    def parser(self):
        """Create a DateParser instance."""
        return DateParser()

    def test_date_parsing(self, parser):
        """Test date parsing."""
        test_cases = [
            ("2023", "year:2023"),
            ("released in 2022", "year:2022"),
            ("2021 cards", "year:2021"),
            ("cards from 2020", "year:2020"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestPriceParser:
    """Test cases for PriceParser."""

    @pytest.fixture
    def parser(self):
        """Create a PriceParser instance."""
        return PriceParser()

    def test_price_parsing(self, parser):
        """Test price parsing."""
        test_cases = [
            ("price greater than $10", "usd>10"),
            ("price more than $50", "usd>50"),
            ("price over $25", "usd>25"),
            ("price above $100", "usd>100"),
            ("price less than $5", "usd<5"),
            ("price under $20", "usd<20"),
            ("price below $15", "usd<15"),
            ("price equal to $30", "usd=30"),
            ("price exactly $25", "usd=25"),
            ("$10 or more", "usd>=10"),
            ("$50 or less", "usd<=50"),
            ("under $5.50", "usd<5.50"),
            ("over $25.99", "usd>25.99"),
        ]

        for query, expected in test_cases:
            assert parser.parse(query) == expected


class TestOrderParser:
    """Test cases for OrderParser."""

    @pytest.fixture
    def parser(self):
        """Create an OrderParser instance."""
        return OrderParser()

    def test_no_order_match(self, parser):
        assert parser.parse("this is not an order") is None
