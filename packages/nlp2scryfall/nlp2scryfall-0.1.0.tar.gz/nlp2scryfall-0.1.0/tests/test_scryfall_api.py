"""
Tests for the ScryfallAPI class.
"""

import time
from unittest.mock import patch

import pytest
import responses

from nlp2scryfall.scryfall_api import ScryfallAPI


class TestScryfallAPI:
    """Test cases for ScryfallAPI."""

    @pytest.fixture
    def api(self):
        """Create a ScryfallAPI instance."""
        return ScryfallAPI(cache_data=False)

    @pytest.fixture
    def cached_api(self):
        """Create a ScryfallAPI instance with caching enabled."""
        return ScryfallAPI(cache_data=True)

    def test_init(self, api):
        """Test API initialization."""
        assert api.cache_data is False
        assert api._cache == {}
        assert api._cache_timestamps == {}
        assert api._cache_duration == 3600

    def test_init_with_caching(self, cached_api):
        """Test API initialization with caching enabled."""
        assert cached_api.cache_data is True
        assert cached_api._cache == {}
        assert cached_api._cache_timestamps == {}

    def test_rate_limiting(self, api):
        """Test rate limiting functionality."""
        # First call should not wait
        start_time = time.time()
        api._rate_limit()
        first_call_time = time.time() - start_time

        # Second call within 100ms should wait
        start_time = time.time()
        api._rate_limit()
        second_call_time = time.time() - start_time

        # First call should be fast, second call should have waited
        assert first_call_time < 0.05  # Should be very fast
        assert second_call_time >= 0.1  # Should have waited at least 100ms

    @responses.activate
    def test_make_request_success(self, api):
        """Test successful API request."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/test/endpoint",
            status=200,
            json={"data": "test"},
        )

        result = api._make_request("test/endpoint")

        assert result == {"data": "test"}

    @responses.activate
    def test_make_request_failure(self, api):
        """Test failed API request."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/test/endpoint",
            status=404,
            json={"error": "Not found"},
        )

        with pytest.raises(Exception):
            api._make_request("test/endpoint")

    @responses.activate
    def test_get_sets_success(self, cached_api):
        """Test successful sets retrieval."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={
                "data": [
                    {"name": "Dominaria", "code": "dom"},
                    {"name": "The Brothers' War", "code": "bro"},
                ]
            },
        )

        sets = cached_api.get_sets()

        assert len(sets) == 2
        assert sets[0]["name"] == "Dominaria"
        assert sets[0]["code"] == "dom"
        assert sets[1]["name"] == "The Brothers' War"
        assert sets[1]["code"] == "bro"

    @responses.activate
    def test_get_sets_failure(self, cached_api):
        """Test sets retrieval failure."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=500,
            json={"error": "Server error"},
        )

        sets = cached_api.get_sets()

        # Should return empty list on failure
        assert sets == []

    def test_get_sets_caching(self, cached_api):
        """Test sets caching functionality."""
        # Mock the API response
        test_sets = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(
            cached_api, "_make_request", return_value={"data": test_sets}
        ):
            # First call should cache the data
            sets1 = cached_api.get_sets()
            assert sets1 == test_sets

            # Second call should use cached data
            sets2 = cached_api.get_sets()
            assert sets2 == test_sets

            # Cache should contain the data
            assert "sets" in cached_api._cache
            assert cached_api._cache["sets"] == test_sets

    def test_get_set_by_name_exact_match(self, cached_api):
        """Test set retrieval by exact name match."""
        test_sets = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(cached_api, "get_sets", return_value=test_sets):
            set_data = cached_api.get_set_by_name("Dominaria")
            assert set_data["name"] == "Dominaria"
            assert set_data["code"] == "dom"

    def test_get_set_by_name_partial_match(self, cached_api):
        """Test set retrieval by partial name match."""
        test_sets = [
            {"name": "Dominaria United", "code": "dmu"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(cached_api, "get_sets", return_value=test_sets):
            set_data = cached_api.get_set_by_name("Dominaria")
            assert set_data["name"] == "Dominaria United"
            assert set_data["code"] == "dmu"

    def test_get_set_by_name_no_match(self, cached_api):
        """Test set retrieval with no match."""
        test_sets = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(cached_api, "get_sets", return_value=test_sets):
            set_data = cached_api.get_set_by_name("Nonexistent Set")
            assert set_data is None

    def test_get_set_by_code(self, cached_api):
        """Test set retrieval by code."""
        test_sets = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(cached_api, "get_sets", return_value=test_sets):
            set_data = cached_api.get_set_by_code("dom")
            assert set_data["name"] == "Dominaria"
            assert set_data["code"] == "dom"

    def test_get_set_by_code_no_match(self, cached_api):
        """Test set retrieval by code with no match."""
        test_sets = [
            {"name": "Dominaria", "code": "dom"},
            {"name": "The Brothers' War", "code": "bro"},
        ]

        with patch.object(cached_api, "get_sets", return_value=test_sets):
            set_data = cached_api.get_set_by_code("xyz")
            assert set_data is None

    def test_get_formats(self, cached_api):
        """Test formats retrieval."""
        formats = cached_api.get_formats()

        expected_formats = [
            "standard",
            "modern",
            "legacy",
            "vintage",
            "commander",
            "pauper",
            "pioneer",
            "historic",
            "alchemy",
            "brawl",
            "oathbreaker",
            "duel commander",
            "canadian highlander",
            "penny dreadful",
        ]

        assert set(formats) == set(expected_formats)

    def test_get_formats_caching(self, cached_api):
        """Test formats caching."""
        # First call
        formats1 = cached_api.get_formats()

        # Second call should use cache
        formats2 = cached_api.get_formats()

        assert formats1 == formats2
        assert "formats" in cached_api._cache

    def test_get_rarities(self, api):
        """Test rarities retrieval."""
        rarities = api.get_rarities()

        expected_rarities = ["common", "uncommon", "rare", "mythic", "special", "bonus"]
        assert rarities == expected_rarities

    def test_get_card_types(self, api):
        """Test card types retrieval."""
        types = api.get_card_types()

        expected_types = [
            "artifact",
            "creature",
            "enchantment",
            "instant",
            "land",
            "planeswalker",
            "sorcery",
            "tribal",
        ]
        assert types == expected_types

    def test_get_supertypes(self, api):
        """Test supertypes retrieval."""
        supertypes = api.get_supertypes()

        expected_supertypes = ["legendary", "snow", "world", "basic"]
        assert supertypes == expected_supertypes

    def test_get_colors(self, api):
        """Test colors retrieval."""
        colors = api.get_colors()

        expected_colors = ["white", "blue", "black", "red", "green", "colorless"]
        assert colors == expected_colors

    def test_get_color_combinations(self, api):
        """Test color combinations retrieval."""
        combinations = api.get_color_combinations()

        # Test some key combinations
        assert combinations["azorius"] == "uw"
        assert combinations["dimir"] == "ub"
        assert combinations["rakdos"] == "br"
        assert combinations["gruul"] == "rg"
        assert combinations["selesnya"] == "gw"
        assert combinations["esper"] == "uwb"
        assert combinations["grixis"] == "ubr"
        assert combinations["jund"] == "brg"
        assert combinations["naya"] == "rwg"
        assert combinations["bant"] == "gwu"

    @responses.activate
    def test_search_cards_success(self, api):
        """Test successful card search."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            status=200,
            json={
                "data": [{"name": "Lightning Bolt", "type_line": "Instant"}],
                "total_cards": 1,
            },
        )

        result = api.search_cards("c:r t:instant")

        assert result["total_cards"] == 1
        assert result["data"][0]["name"] == "Lightning Bolt"

    @responses.activate
    def test_search_cards_failure(self, api):
        """Test card search failure."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            status=400,
            json={"error": "Bad request"},
        )

        with pytest.raises(Exception):
            api.search_cards("invalid query")

    def test_cache_expiration(self, cached_api):
        """Test cache expiration functionality."""
        # Add some test data to cache
        cached_api._cache["test_key"] = "test_value"
        cached_api._cache_timestamps["test_key"] = time.time() - 7200  # 2 hours ago

        # Data should be expired
        result = cached_api._get_cached_data("test_key")
        assert result is None

        # Cache should be cleaned up
        assert "test_key" not in cached_api._cache
        assert "test_key" not in cached_api._cache_timestamps

    def test_cache_data_method(self, cached_api):
        """Test cache data method."""
        test_data = {"test": "value"}
        cached_api._cache_data("test_key", test_data)

        assert cached_api._cache["test_key"] == test_data
        assert "test_key" in cached_api._cache_timestamps

    def test_cache_data_disabled(self, api):
        """Test cache data method when caching is disabled."""
        test_data = {"test": "value"}
        api._cache_data("test_key", test_data)

        assert "test_key" not in api._cache
        assert "test_key" not in api._cache_timestamps
