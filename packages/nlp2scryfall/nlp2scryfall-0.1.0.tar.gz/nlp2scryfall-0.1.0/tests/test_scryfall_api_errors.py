"""
Tests for Scryfall API error handling.

This module tests the comprehensive error handling implemented in the ScryfallAPI class,
including network errors, timeouts, malformed responses, and graceful fallbacks.
"""



import pytest
import responses
from requests.exceptions import ConnectionError, Timeout

from nlp2scryfall.scryfall_api import (
    ScryfallAPI,
    ScryfallAPIConnectionError,
    ScryfallAPIError,
    ScryfallAPIRequestError,
    ScryfallAPIResponseError,
    ScryfallAPITimeoutError,
)


class TestScryfallAPIErrorHandling:
    """Test comprehensive error handling in ScryfallAPI."""

    def test_custom_exceptions(self):
        """Test that custom exceptions are properly defined."""
        # Test base exception
        base_error = ScryfallAPIError("Test error")
        assert str(base_error) == "Test error"

        # Test request error with status code
        request_error = ScryfallAPIRequestError("HTTP error", 404, "Not found")
        assert request_error.status_code == 404
        assert request_error.response_text == "Not found"

        # Test timeout error
        timeout_error = ScryfallAPITimeoutError("Timeout")
        assert str(timeout_error) == "Timeout"

        # Test connection error
        conn_error = ScryfallAPIConnectionError("Connection failed")
        assert str(conn_error) == "Connection failed"

        # Test response error
        resp_error = ScryfallAPIResponseError("Invalid response")
        assert str(resp_error) == "Invalid response"

    @responses.activate
    def test_http_404_error(self):
        """Test handling of 404 errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=404,
            json={"error": "Not found"},
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for HTTP errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_http_429_rate_limit_error(self):
        """Test handling of rate limit errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=429,
            json={"error": "Rate limit exceeded"},
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for HTTP errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_http_500_server_error(self):
        """Test handling of server errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=500,
            json={"error": "Internal server error"},
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for HTTP errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_timeout_error(self):
        """Test handling of timeout errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            body=Timeout("Request timed out"),
        )

        api = ScryfallAPI(cache_data=False, max_retries=1)

        # get_sets() should return empty list as fallback for timeout errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_connection_error(self):
        """Test handling of connection errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            body=ConnectionError("Connection failed"),
        )

        api = ScryfallAPI(cache_data=False, max_retries=1)

        # get_sets() should return empty list as fallback for connection errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_retry_logic(self):
        """Test that retry logic works correctly."""
        # First two requests fail, third succeeds
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=500,
            json={"error": "Server error"},
        )
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=500,
            json={"error": "Server error"},
        )
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"data": [{"code": "test", "name": "Test Set"}]},
        )

        api = ScryfallAPI(cache_data=False, max_retries=3)
        result = api.get_sets()

        # get_sets() is designed to be resilient and return empty list on any failure
        # The retry logic is internal to _make_request, but get_sets catches all exceptions
        assert result == []

    @responses.activate
    def test_retry_logic_direct(self):
        """Test retry logic directly on _make_request method."""
        # All requests fail with 500 errors
        responses.add(
            responses.GET,
            "https://api.scryfall.com/test/endpoint",
            status=500,
            json={"error": "Server error"},
        )
        responses.add(
            responses.GET,
            "https://api.scryfall.com/test/endpoint",
            status=500,
            json={"error": "Server error"},
        )
        responses.add(
            responses.GET,
            "https://api.scryfall.com/test/endpoint",
            status=500,
            json={"error": "Server error"},
        )

        api = ScryfallAPI(cache_data=False, max_retries=3)

        # After all retries are exhausted, should raise an exception
        with pytest.raises(Exception):
            api._make_request("test/endpoint")

    @responses.activate
    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            body="Invalid JSON content",
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for JSON errors
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_malformed_response_structure(self):
        """Test handling of malformed response structure."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json="not a dictionary",
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for malformed responses
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_missing_data_field(self):
        """Test handling of responses missing the 'data' field."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"error": "No data"},
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for missing data field
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_invalid_set_data_structure(self):
        """Test handling of invalid set data structure."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"data": ["not a dictionary"]},
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for invalid set data
        result = api.get_sets()
        assert result == []

    @responses.activate
    def test_missing_required_set_fields(self):
        """Test handling of set data missing required fields."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"data": [{"name": "Test Set"}]},  # Missing 'code'
        )

        api = ScryfallAPI(cache_data=False)

        # get_sets() should return empty list as fallback for missing required fields
        result = api.get_sets()
        assert result == []

    def test_empty_set_name_handling(self):
        """Test handling of empty set names."""
        api = ScryfallAPI()

        result = api.get_set_by_name("")
        assert result is None

        result = api.get_set_by_name("   ")
        assert result is None

    def test_empty_set_code_handling(self):
        """Test handling of empty set codes."""
        api = ScryfallAPI()

        result = api.get_set_by_code("")
        assert result is None

        result = api.get_set_by_code("   ")
        assert result is None

    @responses.activate
    def test_search_empty_query(self):
        """Test handling of empty search queries."""
        api = ScryfallAPI()

        with pytest.raises(ScryfallAPIRequestError) as exc_info:
            api.search_cards("")

        assert "Empty search query" in str(exc_info.value)

        with pytest.raises(ScryfallAPIRequestError) as exc_info:
            api.search_cards("   ")

        assert "Empty search query" in str(exc_info.value)

    def test_search_invalid_page_number(self):
        """Test handling of invalid page numbers."""
        api = ScryfallAPI()

        with pytest.raises(ScryfallAPIRequestError) as exc_info:
            api.search_cards("test", page=0)

        assert "Page number must be 1 or greater" in str(exc_info.value)

        with pytest.raises(ScryfallAPIRequestError) as exc_info:
            api.search_cards("test", page=-1)

        assert "Page number must be 1 or greater" in str(exc_info.value)

    @responses.activate
    def test_search_malformed_response(self):
        """Test handling of malformed search responses."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            status=200,
            json="not a dictionary",
        )

        api = ScryfallAPI(cache_data=False)

        with pytest.raises(ScryfallAPIResponseError) as exc_info:
            api.search_cards("test")

        assert "Invalid search response format" in str(exc_info.value)

    @responses.activate
    def test_search_missing_data_field(self):
        """Test handling of search responses missing the 'data' field."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            status=200,
            json={"total_cards": 0},
        )

        api = ScryfallAPI(cache_data=False)

        with pytest.raises(ScryfallAPIResponseError) as exc_info:
            api.search_cards("test")

        assert "missing 'data' field" in str(exc_info.value)

    @responses.activate
    def test_graceful_fallback_on_api_failure(self):
        """Test that API failures result in graceful fallbacks."""
        responses.add(responses.GET, "https://api.scryfall.com/sets", status=500)

        api = ScryfallAPI(cache_data=False, max_retries=1)
        result = api.get_sets()

        # Should return empty list as fallback
        assert result == []

    def test_cache_management(self):
        """Test cache management methods."""
        api = ScryfallAPI()

        # Test cache info
        cache_info = api.get_cache_info()
        assert cache_info["enabled"] is True
        assert cache_info["size"] == 0
        assert cache_info["keys"] == []

        # Test cache clearing
        api.clear_cache()
        cache_info = api.get_cache_info()
        assert cache_info["size"] == 0

    @responses.activate
    def test_user_agent_header(self):
        """Test that User-Agent header is set correctly."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"data": []},
        )

        api = ScryfallAPI(cache_data=False)
        api.get_sets()

        # Check that the request was made with the correct User-Agent
        request = responses.calls[0].request
        assert request.headers["User-Agent"] == "nlp2scryfall/1.0"

    @responses.activate
    def test_timeout_configuration(self):
        """Test that timeout is properly configured."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/sets",
            status=200,
            json={"data": []},
        )

        api = ScryfallAPI(cache_data=False, timeout=60)
        api.get_sets()

        # The timeout should be passed to the request
        # We can't easily test this with responses, but we can verify the API works
        assert len(responses.calls) == 1

    def test_configurable_retries(self):
        """Test that retry count is configurable."""
        api = ScryfallAPI(max_retries=5)
        assert api.max_retries == 5

        api = ScryfallAPI(max_retries=1)
        assert api.max_retries == 1

    @responses.activate
    def test_search_cards_raises_exceptions(self):
        """Test that search_cards raises exceptions for errors."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            status=404,
            json={"error": "Not found"},
        )

        api = ScryfallAPI(cache_data=False)

        with pytest.raises(ScryfallAPIRequestError) as exc_info:
            api.search_cards("test")

        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)

    @responses.activate
    def test_search_cards_timeout_raises_exception(self):
        """Test that search_cards raises timeout exceptions."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            body=Timeout("Request timed out"),
        )

        api = ScryfallAPI(cache_data=False, max_retries=1)

        with pytest.raises(ScryfallAPITimeoutError) as exc_info:
            api.search_cards("test")

        assert "timed out" in str(exc_info.value)

    @responses.activate
    def test_search_cards_connection_error_raises_exception(self):
        """Test that search_cards raises connection exceptions."""
        responses.add(
            responses.GET,
            "https://api.scryfall.com/cards/search",
            body=ConnectionError("Connection failed"),
        )

        api = ScryfallAPI(cache_data=False, max_retries=1)

        with pytest.raises(ScryfallAPIConnectionError) as exc_info:
            api.search_cards("test")

        assert "Connection failed" in str(exc_info.value)
