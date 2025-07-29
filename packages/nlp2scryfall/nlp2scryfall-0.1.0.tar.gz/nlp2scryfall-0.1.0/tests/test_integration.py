"""
Integration tests with real-world natural language queries.
"""

import re

import pytest

from nlp2scryfall import Translator


class TestIntegration:
    """Integration tests with real-world queries."""

    @pytest.fixture
    def translator(self):
        """Create a translator instance for testing."""
        return Translator(cache_data=False)

    def assert_components_present(
        self, result: str, expected_components: list, query: str
    ):
        """Assert that all expected components are present in the result, allowing any order for color codes."""

        def normalize_color_clause(clause):
            # Match c:wu, c>=wu, id:rg, id>=rg, etc.
            m = re.match(r"(c|id)(:?|>=|=)([wubrgc]+)", clause)
            if m:
                prefix, op, colors = m.groups()
                return (prefix, op, "".join(sorted(colors)))
            return None

        def normalize_artist_clause(clause):
            # Match a:Artist Name and normalize to lowercase
            m = re.match(r"a:(.+)", clause)
            if m:
                return m.group(1).lower()
            return None

        def clause_in_result(expected_clause, result):
            # Handle exact artist name matches first (case-sensitive)
            if expected_clause.startswith("a:"):
                return expected_clause in result

            # Handle color clauses (order-agnostic)
            norm_expected = normalize_color_clause(expected_clause)
            if norm_expected:
                # Look for any matching color clause in result
                for part in result.split():
                    norm_part = normalize_color_clause(part)
                    if (
                        norm_part
                        and norm_part[0] == norm_expected[0]
                        and norm_part[1] == norm_expected[1]
                        and set(norm_part[2]) == set(norm_expected[2])
                    ):
                        return True
                return False

            # Handle artist clauses (case-insensitive) - for backward compatibility
            norm_expected_artist = normalize_artist_clause(expected_clause)
            if norm_expected_artist:
                for part in result.split():
                    norm_part_artist = normalize_artist_clause(part)
                    if norm_part_artist and norm_part_artist == norm_expected_artist:
                        return True
                return False

            # Handle mono-color variations (c:r vs c=r)
            if expected_clause.startswith("c:") and len(expected_clause) == 3:
                color = expected_clause[2]
                for part in result.split():
                    if part in [f"c:{color}", f"c={color}"]:
                        return True
                return False

            # Default string matching
            return expected_clause in result

        for component in expected_components:
            assert clause_in_result(
                component, result
            ), f"Expected component '{component}' not found in result '{result}' for query '{query}'"

    def test_basic_color_queries(self, translator):
        """Test basic color queries from real-world usage.
        For now we will use c for any queries that talk about color, unless it's a land then use id.
        """
        test_cases = [
            ("find all cards that can be played with red", ["c>=r"]),
            ("find all cards that can be played with only red", ["c=r"]),
            ("show me blue creatures", ["c>=u", "t:creature"]),
            ("mono blue creatures", ["c=u", "t:creature"]),
            ("black spells", ["c>=b", "is:spell"]),
            ("mono black spells", ["c=b", "is:spell"]),
            # can't use c>= or c= card color for lands because most lands have no printed color, need to use ID
            ("green lands", ["t:land", "id>=g"]),
            ("mono green lands", ["t:land", "id=g"]),
            ("white angels", ["t:angel", "c>=w"]),
            ("mono white angels", ["t:angel", "c=w"]),
            ("colorless artifacts", ["t:artifact", "c=c"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_guild_queries(self, translator):
        """Test guild (two-color) queries."""
        test_cases = [
            ("azorius cards", ["c>=wu"]),
            ("dimir cards", ["c>=ub"]),
            ("rakdos cards", ["c>=br"]),
            ("gruul cards", ["c>=rg"]),
            ("selesnya cards", ["c>=gw"]),
            ("orzhov cards", ["c>=wb"]),
            ("izzet cards", ["c>=ur"]),
            ("golgari cards", ["c>=bg"]),
            ("boros cards", ["c>=rw"]),
            ("simic cards", ["c>=gu"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_shard_queries(self, translator):
        """Test shard (three-color) queries."""
        test_cases = [
            ("bant cards", ["c>=gwu"]),
            ("esper cards", ["c>=wub"]),
            ("grixis cards", ["c>=ubr"]),
            ("jund cards", ["c>=brg"]),
            ("naya cards", ["c>=rgw"]),
            ("abzan cards", ["c>=wbg"]),
            ("jeskai cards", ["c>=urw"]),
            ("sultai cards", ["c>=bgu"]),
            ("mardu cards", ["c>=rwb"]),
            ("temur cards", ["c>=gur"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_creature_queries(self, translator):
        """Test creature-specific queries."""
        test_cases = [
            ("dragon creatures", ["t:dragon", "t:creature"]),
            ("goblin creatures", ["t:goblin", "t:creature"]),
            ("elf creatures", ["t:elf", "t:creature"]),
            ("human soldiers", ["t:human", "t:soldier"]),
            ("zombie creatures", ["t:zombie", "t:creature"]),
            ("angel creatures", ["t:angel", "t:creature"]),
            ("demon creatures", ["t:demon", "t:creature"]),
            ("beast creatures", ["t:beast", "t:creature"]),
            ("bird creatures", ["t:bird", "t:creature"]),
            ("cat creatures", ["t:cat", "t:creature"]),
            ("dog creatures", ["t:dog", "t:creature"]),
            ("fish creatures", ["t:fish", "t:creature"]),
            ("knight creatures", ["t:knight", "t:creature"]),
            ("merfolk creatures", ["t:merfolk", "t:creature"]),
            ("orc creatures", ["t:orc", "t:creature"]),
            ("spirit creatures", ["t:spirit", "t:creature"]),
            ("vampire creatures", ["t:vampire", "t:creature"]),
            ("wolf creatures", ["t:wolf", "t:creature"]),
            ("wizard creatures", ["t:wizard", "t:creature"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_type_queries(self, translator):
        """Test type-specific queries."""
        test_cases = [
            ("dragon", ["t:dragon"]),
            ("goblin", ["t:goblin"]),
            ("elf", ["t:elf"]),
            ("human", ["t:human"]),
            ("zombie", ["t:zombie"]),
            ("angel", ["t:angel"]),
            ("demon", ["t:demon"]),
            ("beast", ["t:beast"]),
            ("bird", ["t:bird"]),
            ("cat", ["t:cat"]),
            ("dog", ["t:dog"]),
            ("fish", ["t:fish"]),
            ("knight", ["t:knight"]),
            ("merfolk", ["t:merfolk"]),
            ("orc", ["t:orc"]),
            ("spirit", ["t:spirit"]),
            ("vampire", ["t:vampire"]),
            ("wolf", ["t:wolf"]),
            ("wizard", ["t:wizard"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_spell_queries(self, translator):
        """Test spell-type queries."""
        test_cases = [
            ("instant spells", ["t:instant"]),
            ("instant", ["t:instant"]),
            ("sorcery spells", ["t:sorcery"]),
            ("sorceries", ["t:sorcery"]),
            ("spells", ["is:spell"]),
            # Use Scryfall's community tags to grab every counterspell (hard or soft).
            # Tagger tags label cards by mechanical role; function:counterspell pulls them all.
            ("counter spells", ["function:counterspell", "is:spell"]),
            ("counterspells", ["function:counterspell", "is:spell"]),
            ("removal spells", ["function:removal", "is:spell"]),
            ("removal", ["function:removal"]),
            ("burn spells", ["function:burn", "is:spell"]),
            ("burn", ["function:burn"]),
            ("draw spells", ["function:draw", "is:spell"]),
            ("draw", ["function:draw"]),
            ("lifegain spells", ["function:lifegain", "is:spell"]),
            ("lifegain", ["function:lifegain"]),
            ("mana rocks", ["function:mana_rock"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            if expected_components:
                self.assert_components_present(result, expected_components, query)
            else:
                assert (
                    result == ""
                ), f"Expected empty result for query '{query}', got '{result}'"

    def test_land_queries(self, translator):
        """Test land queries."""
        test_cases = [
            ("basic lands", ["t:basic", "t:land"]),
            ("forest lands", ["t:forest", "t:land"]),
            ("island lands", ["t:island", "t:land"]),
            ("mountain lands", ["t:mountain", "t:land"]),
            ("plains lands", ["t:plains", "t:land"]),
            ("swamp lands", ["t:swamp", "t:land"]),
            ("dual lands", ["function:dual-land"]),
            ("fetch lands", ["function:fetchland"]),
            ("shock lands", ["function:shockland"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            if expected_components:
                self.assert_components_present(result, expected_components, query)
            else:
                assert (
                    result == ""
                ), f"Expected empty result for query '{query}', got '{result}'"

    def test_power_toughness_queries(self, translator):
        """Test power/toughness queries."""
        test_cases = [
            ("creatures with power greater than 5", ["t:creature", "pow>5"]),
            ("power 3 or more", ["pow>=3"]),
            ("power less than 2", ["pow<2"]),
            ("power equal to 4", ["pow=4"]),
            ("toughness greater than 6", ["tou>6"]),
            ("toughness 2 or less", ["tou<=2"]),
            ("toughness exactly 3", ["tou=3"]),
            ("3/3 creatures", ["t:creature", "pow=3", "tou=3"]),
            ("5/5 dragons", ["t:dragon", "pow=5", "tou=5"]),
            ("power over 7", ["pow>7"]),
            ("power above 4", ["pow>4"]),
            ("power under 3", ["pow<3"]),
            ("power below 6", ["pow<6"]),
            ("toughness over 8", ["tou>8"]),
            ("toughness above 5", ["tou>5"]),
            ("toughness under 4", ["tou<4"]),
            ("toughness below 7", ["tou<7"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_mana_cost_queries(self, translator):
        """Test mana cost queries."""
        test_cases = [
            ("cards that cost 3 or less", ["cmc<=3"]),
            ("mana cost greater than 5", ["cmc>5"]),
            ("costs 2 or more", ["cmc>=2"]),
            ("mana cost equal to 4", ["cmc=4"]),
            ("costs less than 3", ["cmc<3"]),
            ("costs more than 6", ["cmc>6"]),
            ("costs exactly 1", ["cmc=1"]),
            ("3 mana or less", ["cmc<=3"]),
            ("5 mana or more", ["cmc>=5"]),
            ("costing over 4", ["cmc>4"]),
            ("costing under 2", ["cmc<2"]),
            ("costing above 7", ["cmc>7"]),
            ("costing below 3", ["cmc<3"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_rarity_queries(self, translator):
        """Test rarity queries."""
        test_cases = [
            ("common cards", ["r:common"]),
            ("uncommon spells", ["r:uncommon", "is:spell"]),
            ("rare creatures", ["r:rare", "t:creature"]),
            ("mythic rares", ["r:mythic"]),
            ("mythic rare cards", ["r:mythic"]),
            ("special cards", ["r:special"]),
            ("bonus cards", ["r:bonus"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_format_queries(self, translator):
        """Test format queries."""
        test_cases = [
            ("standard legal cards", ["f:standard"]),
            ("modern format", ["f:modern"]),
            ("legacy legal", ["f:legacy"]),
            ("vintage format", ["f:vintage"]),
            ("commander legal", ["f:commander"]),
            ("pauper format", ["f:pauper"]),
            ("pioneer legal", ["f:pioneer"]),
            ("historic format", ["f:historic"]),
            ("alchemy legal", ["f:alchemy"]),
            ("brawl format", ["f:brawl"]),
            ("oathbreaker legal", ["f:oathbreaker"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_text_queries(self, translator):
        """Test text-based queries."""
        test_cases = [
            ('cards with "draw a card"', ['o:"draw a card"']),
            ('with "destroy target"', ['o:"destroy target"']),
            ('"flying" creatures', ['o:"flying"', "t:creature"]),
            ('cards containing "counter"', ['o:"counter"']),
            ('with "deals damage"', ['o:"deals damage"']),
            ('"enters the battlefield"', ['o:"enters the battlefield"']),
            ('"when this creature dies"', ['o:"when this creature dies"']),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_artist_queries(self, translator):
        """Test artist queries."""
        test_cases = [
            ("cards by Christopher Rush", ["a:Christopher Rush"]),
            ("art by Rebecca Guay", ["a:Rebecca Guay"]),
            ("artist Seb McKinnon", ["a:Seb McKinnon"]),
            ("painted by Noah Bradley", ["a:Noah Bradley"]),
            ("by Raymond Swanland", ["a:Raymond Swanland"]),
            ("artist Terese Nielsen", ["a:Terese Nielsen"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_collector_number_queries(self, translator):
        """Test collector number queries."""
        test_cases = [
            ("card number 123", ["number:123"]),
            ("collector number 456", ["number:456"]),
            ("number 789", ["number:789"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_date_queries(self, translator):
        """Test date queries."""
        test_cases = [
            ("cards from 2023", ["year:2023"]),
            ("released in 2022", ["year:2022"]),
            ("2021 cards", ["year:2021"]),
            ("cards from 2020", ["year:2020"]),
            ("2019 set", ["year:2019"]),
            ("cards from 2018", ["year:2018"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_price_queries(self, translator):
        """Test price queries."""
        test_cases = [
            ("cards under $10", ["usd<10"]),
            ("price over $50", ["usd>50"]),
            ("$20 or less", ["usd<=20"]),
            ("$100 or more", ["usd>=100"]),
            ("price exactly $5", ["usd=5"]),
            ("under $5.50", ["usd<5.50"]),
            ("over $25.99", ["usd>25.99"]),
            ("cheap cards under $1", ["usd<1"]),
            ("expensive cards over $100", ["usd>100"]),
            ("ordered by price", ["order:usd"]),
            ("order by mana cost", ["order:cmc"]),
            ("sort by power", ["order:pow"]),
            ("sorted by name", ["order:name"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_complex_combined_queries(self, translator):
        """Test complex queries with multiple components."""
        test_cases = [
            (
                "red dragon creatures with power greater than 5",
                ["c>=r", "t:dragon", "t:creature", "pow>5"],
            ),
            (
                "blue and white legendary creatures",
                ["c>=wu", "t:legendary", "t:creature"],
            ),
            ("green creatures that cost 3 or less", ["c>=g", "t:creature", "cmc<=3"]),
            ("mythic rare planeswalkers", ["r:mythic", "t:planeswalker"]),
            ("common instant spells under $1", ["r:common", "t:instant", "usd<1"]),
            (
                "legendary creatures with power 4/4",
                ["t:legendary", "t:creature", "pow=4", "tou=4"],
            ),
            (
                "black zombie creatures with toughness greater than 3",
                ["c>=b", "t:zombie", "t:creature", "tou>3"],
            ),
            ("white and blue cards from 2023", ["c>=wu", "year:2023"]),
            (
                "red goblin creatures costing 2 or less",
                ["c>=r", "t:goblin", "t:creature", "cmc<=2"],
            ),
            (
                "artifact creatures with power 5/5",
                ["t:artifact", "t:creature", "pow=5", "tou=5"],
            ),
            ("legendary angels with flying", ["t:legendary", "t:angel", 'o:"flying"']),
            (
                "red burn spells under $5",
                ["c>=r", "function:burn", "is:spell", "usd<5"],
            ),
            ("green ramp spells costing 3 or more", ["c>=g", "cmc>=3"]),
            ("blue control spells with counter", ["c>=u", 'o:"counter"']),
            ("black removal spells", ["c>=b"]),
            ("white lifegain cards", ["c>=w"]),
            ("colorless artifacts under $10", ["c=c", "t:artifact", "usd<10"]),
            ("mythic rare dragons over $50", ["r:mythic", "t:dragon", "usd>50"]),
            ("common lands from 2022", ["r:common", "t:land", "year:2022"]),
            (
                "uncommon creatures with power 3/3",
                ["r:uncommon", "t:creature", "pow=3", "tou=3"],
            ),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_real_world_deck_queries(self, translator):
        """Test real-world deck building queries."""
        test_cases = [
            ("red aggro creatures", ["c>=r", "t:creature"]),
            ("blue control spells", ["c>=u"]),
            ("green ramp creatures", ["c>=g", "t:creature"]),
            ("white weenie creatures", ["c>=w", "t:creature"]),
            ("black removal spells", ["c>=b"]),
            ("burn spells", ["function:burn", "is:spell"]),
            ("counterspells", ["function:counterspell", "is:spell"]),
            ("ramp spells", ["function:ramp", "is:spell"]),
            ("removal spells", ["function:removal", "is:spell"]),
            ("card draw spells", ["function:draw", "is:spell"]),
            ("mana rocks", ["function:mana_rock"]),
            ("mana dorks", ["function:mana_dork"]),
            ("finishers", []),
            ("sideboard cards", []),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            if expected_components:
                self.assert_components_present(result, expected_components, query)
            else:
                assert (
                    result == ""
                ), f"Expected empty result for query '{query}', got '{result}'"

    def test_commander_queries(self, translator):
        """Test commander-specific queries."""
        test_cases = [
            ("commander legal cards", ["f:commander"]),
            (
                "legendary creatures for commander",
                ["t:legendary", "t:creature", "f:commander"],
            ),
            ("commander staples", ["f:commander"]),
            ("commander removal", ["f:commander"]),
            ("commander ramp", ["f:commander"]),
            ("commander card draw", ["f:commander"]),
            ("commander lands", ["t:land", "f:commander"]),
            ("commander artifacts", ["t:artifact", "f:commander"]),
            ("commander enchantments", ["t:enchantment", "f:commander"]),
            ("commander instants", ["t:instant", "f:commander"]),
            ("commander sorceries", ["t:sorcery", "f:commander"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_modern_queries(self, translator):
        """Test modern format queries."""
        test_cases = [
            ("modern legal cards", ["f:modern"]),
            ("modern creatures", ["t:creature", "f:modern"]),
            ("modern spells", ["f:modern"]),
            ("modern lands", ["t:land", "f:modern"]),
            ("modern artifacts", ["t:artifact", "f:modern"]),
            ("modern enchantments", ["t:enchantment", "f:modern"]),
            ("modern instants", ["t:instant", "f:modern"]),
            ("modern sorceries", ["t:sorcery", "f:modern"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_standard_queries(self, translator):
        """Test standard format queries."""
        test_cases = [
            ("standard legal cards", ["f:standard"]),
            ("standard creatures", ["t:creature", "f:standard"]),
            ("standard spells", ["f:standard"]),
            ("standard lands", ["t:land", "f:standard"]),
            ("standard artifacts", ["t:artifact", "f:standard"]),
            ("standard enchantments", ["t:enchantment", "f:standard"]),
            ("standard instants", ["t:instant", "f:standard"]),
            ("standard sorceries", ["t:sorcery", "f:standard"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_edge_cases(self, translator):
        """Test edge cases and unusual queries."""
        test_cases = [
            ("", []),
            ("   ", []),
            ("random text", []),
            ("cards that don't exist", []),
            ("very specific obscure query", []),
            ("cards with very long descriptions", []),
            ("multiple colors and types and costs", []),
            ("complex nested queries", []),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            if expected_components:
                self.assert_components_present(result, expected_components, query)
            else:
                assert (
                    result == ""
                ), f"Expected empty result for query '{query}', got '{result}'"

    def test_empty_query(self, translator):
        """Test handling of empty queries."""
        assert translator.translate("") == ""
        assert translator.translate("   ") == ""
        assert translator.translate(None) == ""

    def test_simple_color_queries(self, translator):
        """Test simple color queries."""
        test_cases = [
            ("find all red cards", ["c>=r"]),
            ("show me blue cards", ["c>=u"]),
            ("black cards", ["c>=b"]),
            ("green creatures", ["c>=g", "t:creature"]),
            ("white and blue cards", ["c>=wu"]),
            ("colorless artifacts", ["c=c", "t:artifact"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_supertype_queries(self, translator):
        """Test supertype queries."""
        test_cases = [
            ("legendary creatures", ["t:legendary", "t:creature"]),
            ("snow lands", ["t:snow", "t:land"]),
            ("basic lands", ["t:basic", "t:land"]),
            ("legendary planeswalkers", ["t:legendary", "t:planeswalker"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_filler_word_removal(self, translator):
        """Test that filler words are properly removed."""
        test_cases = [
            ("please find all red cards", ["c>=r"]),
            ("can you show me blue creatures", ["c>=u", "t:creature"]),
            ("i want black dragons", ["c>=b", "t:dragon"]),
            ("i need green spells", ["c>=g"]),
            ("i would like white angels", ["c>=w", "t:angel"]),
            ("i am looking for red goblins", ["c>=r", "t:goblin"]),
            ("i am searching for blue counterspells", ["c>=u"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_case_insensitivity(self, translator):
        """Test that queries are case insensitive."""
        test_cases = [
            ("RED CARDS", ["c>=r"]),
            ("Blue Creatures", ["c>=u", "t:creature"]),
            ("Black Dragons", ["c>=b", "t:dragon"]),
            ("Green Spells", ["c>=g"]),
            ("White Angels", ["c>=w", "t:angel"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_whitespace_normalization(self, translator):
        """Test that whitespace is properly normalized."""
        test_cases = [
            ("red   cards", ["c>=r"]),
            ("blue\tcreatures", ["c>=u", "t:creature"]),
            ("black\ndragons", ["c>=b", "t:dragon"]),
            ("  green spells  ", ["c>=g"]),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_real_world_queries(self, translator):
        """Test real-world queries."""
        test_cases = [
            ("double sided The List cards", ["s:plst", "is:double-faced"]),
            # Mock the dynamic test with static data
            (
                "the most recent 5 sets ordered by price asc",
                ["s:tfin", "s:afin", "s:tfic", "s:fic", "s:fca", "order:usd"],
            ),
        ]

        for query, expected_components in test_cases:
            result = translator.translate(query)
            self.assert_components_present(result, expected_components, query)

    def test_supported_features(self, translator):
        """Test that supported features are correctly listed."""
        features = translator.get_supported_features()
        expected_features = [
            "color",
            "type",
            "set",
            "power_toughness",
            "mana_cost",
            "rarity",
            "text",
            "format",
            "artist",
            "collector_number",
            "date",
            "price",
            "spell",
            "function",
            "order",
            "card_property",
        ]

        assert set(features) == set(expected_features)
