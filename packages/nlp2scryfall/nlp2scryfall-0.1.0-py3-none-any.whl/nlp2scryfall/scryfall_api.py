"""
Scryfall API integration for fetching card data, sets, and other information.

This module provides a client for interacting with the Scryfall API, offering
caching, rate limiting, and comprehensive error handling. The ScryfallAPI class supports:

- Set data retrieval with caching
- Card search functionality
- Rate limiting (100ms between requests)
- Comprehensive error handling and fallbacks
- Configurable caching behavior
- Network timeout handling
- JSON parsing error recovery

The API client automatically handles:
- JSON response parsing
- HTTP status code checking
- Request rate limiting
- Cache expiration (1 hour default)
- Network error recovery
- Timeout handling
- Malformed response handling

Example usage:
    api = ScryfallAPI(cache_data=True)
    sets = api.get_sets()
    cards = api.search_cards("c:r t:instant")
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import (
    ConnectionError,
    JSONDecodeError,
    RequestException,
    Timeout,
)

# Configure logging
logger = logging.getLogger(__name__)


class ScryfallAPIError(Exception):
    """Base exception for Scryfall API errors."""

    pass


class ScryfallAPIRequestError(ScryfallAPIError):
    """Exception raised for HTTP request errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class ScryfallAPITimeoutError(ScryfallAPIError):
    """Exception raised for timeout errors."""

    pass


class ScryfallAPIConnectionError(ScryfallAPIError):
    """Exception raised for connection errors."""

    pass


class ScryfallAPIResponseError(ScryfallAPIError):
    """Exception raised for malformed or invalid API responses."""

    pass


class ScryfallAPI:
    """
    Client for interacting with the Scryfall API.
    """

    BASE_URL = "https://api.scryfall.com"
    DEFAULT_TIMEOUT = 30  # 30 seconds timeout
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 1 second between retries

    def __init__(
        self,
        cache_data: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize the Scryfall API client.

        Args:
            cache_data: Whether to cache API responses
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.cache_data = cache_data
        self.timeout = timeout
        self.max_retries = max_retries
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_duration = 3600  # 1 hour cache

        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self) -> None:
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)

        self._last_request_time = time.time()

    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if it exists and is not expired."""
        if not self.cache_data:
            return None

        if key not in self._cache:
            return None

        if time.time() - self._cache_timestamps[key] > self._cache_duration:
            del self._cache[key]
            del self._cache_timestamps[key]
            return None

        return self._cache[key]

    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp."""
        if self.cache_data:
            self._cache[key] = data
            self._cache_timestamps[key] = time.time()

    def _handle_http_error(self, response: requests.Response) -> None:
        """
        Handle HTTP error responses with specific error messages.

        Args:
            response: The HTTP response object

        Raises:
            ScryfallAPIRequestError: With appropriate error message
        """
        status_code = response.status_code

        if status_code == 404:
            raise ScryfallAPIRequestError(
                f"Resource not found: {response.url}",
                status_code=status_code,
                response_text=response.text,
            )
        elif status_code == 429:
            raise ScryfallAPIRequestError(
                "Rate limit exceeded. Please wait before making more requests.",
                status_code=status_code,
                response_text=response.text,
            )
        elif status_code >= 500:
            raise ScryfallAPIRequestError(
                f"Scryfall server error (HTTP {status_code}). Please try again later.",
                status_code=status_code,
                response_text=response.text,
            )
        else:
            raise ScryfallAPIRequestError(
                f"HTTP {status_code} error: {response.text}",
                status_code=status_code,
                response_text=response.text,
            )

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Scryfall API with retry logic and error handling.

        Args:
            endpoint: API endpoint to request
            params: Optional query parameters

        Returns:
            JSON response from the API

        Raises:
            ScryfallAPITimeoutError: If request times out
            ScryfallAPIConnectionError: If connection fails
            ScryfallAPIRequestError: If HTTP error occurs
            ScryfallAPIResponseError: If response is malformed
        """
        self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Making request to {url} (attempt {attempt + 1}/{self.max_retries})"
                )

                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    headers={"User-Agent": "nlp2scryfall/1.0"},
                )

                # Handle HTTP errors
                if response.status_code != 200:
                    self._handle_http_error(response)

                # Parse JSON response
                try:
                    return response.json()
                except JSONDecodeError as e:
                    raise ScryfallAPIResponseError(
                        f"Invalid JSON response from Scryfall API: {e}"
                    ) from e

            except Timeout as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Request to {url} timed out after {self.max_retries} attempts"
                    )
                    raise ScryfallAPITimeoutError(f"Request timed out: {e}") from e
                else:
                    logger.warning(
                        f"Request to {url} timed out, retrying... (attempt {attempt + 1})"
                    )
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

            except ConnectionError as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Connection error for {url} after {self.max_retries} attempts"
                    )
                    raise ScryfallAPIConnectionError(f"Connection failed: {e}") from e
                else:
                    logger.warning(
                        f"Connection error for {url}, retrying... (attempt {attempt + 1})"
                    )
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

            except RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Request error for {url} after {self.max_retries} attempts"
                    )
                    raise ScryfallAPIRequestError(f"Request failed: {e}") from e
                else:
                    logger.warning(
                        f"Request error for {url}, retrying... (attempt {attempt + 1})"
                    )
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        # This should never be reached, but just in case
        raise ScryfallAPIRequestError("Max retries exceeded")

    def get_sets(self) -> List[Dict[str, Any]]:
        """
        Get all Magic: The Gathering sets.

        Returns:
            List of set data dictionaries. Returns empty list if API is unavailable.
        """
        cache_key = "sets"
        cached_data = self._get_cached_data(cache_key)

        if cached_data:
            logger.debug("Returning cached sets data")
            return cached_data

        try:
            logger.info("Fetching sets data from Scryfall API")
            response = self._make_request("sets")

            # Validate response structure
            if not isinstance(response, dict):
                raise ScryfallAPIResponseError(
                    "Invalid response format: expected dictionary"
                )

            sets_data = response.get("data", [])
            if not isinstance(sets_data, list):
                raise ScryfallAPIResponseError(
                    "Invalid response format: 'data' should be a list"
                )

            # Validate each set has required fields
            for set_data in sets_data:
                if not isinstance(set_data, dict):
                    raise ScryfallAPIResponseError(
                        "Invalid set data format: expected dictionary"
                    )
                if "code" not in set_data or "name" not in set_data:
                    raise ScryfallAPIResponseError(
                        "Invalid set data: missing required fields"
                    )

            self._cache_data(cache_key, sets_data)
            logger.info(f"Successfully fetched {len(sets_data)} sets from Scryfall API")
            return sets_data

        except ScryfallAPIError as e:
            logger.error(f"Failed to fetch sets from Scryfall API: {e}")
            # Return empty list as fallback
            return []
        except Exception as e:
            logger.error(f"Unexpected error while fetching sets: {e}")
            return []

    def get_set_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific set by name.

        Args:
            name: Set name to search for

        Returns:
            Set data dictionary or None if not found
        """
        if not name or not name.strip():
            logger.warning("Empty set name provided")
            return None

        try:
            sets = self.get_sets()

            # Try exact match first
            for set_data in sets:
                if set_data.get("name", "").lower() == name.lower():
                    return set_data

            # Try partial match
            for set_data in sets:
                if name.lower() in set_data.get("name", "").lower():
                    return set_data

            logger.debug(f"No set found matching name: {name}")
            return None

        except Exception as e:
            logger.error(f"Error searching for set by name '{name}': {e}")
            return None

    def get_set_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific set by code.

        Args:
            code: Set code to search for

        Returns:
            Set data dictionary or None if not found
        """
        if not code or not code.strip():
            logger.warning("Empty set code provided")
            return None

        try:
            sets = self.get_sets()

            for set_data in sets:
                if set_data.get("code", "").lower() == code.lower():
                    return set_data

            logger.debug(f"No set found matching code: {code}")
            return None

        except Exception as e:
            logger.error(f"Error searching for set by code '{code}': {e}")
            return None

    def get_formats(self) -> List[str]:
        """
        Get all supported formats.

        Returns:
            List of format names
        """
        cache_key = "formats"
        cached_data = self._get_cached_data(cache_key)

        if cached_data:
            return cached_data

        # Standard formats in Magic: The Gathering
        formats = [
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

        self._cache_data(cache_key, formats)
        return formats

    def get_rarities(self) -> List[str]:
        """
        Get all card rarities.

        Returns:
            List of rarity names
        """
        return ["common", "uncommon", "rare", "mythic", "special", "bonus"]

    def get_card_types(self) -> List[str]:
        """
        Get all card types.

        Returns:
            List of card type names
        """
        return [
            "artifact",
            "creature",
            "enchantment",
            "instant",
            "land",
            "planeswalker",
            "sorcery",
            "tribal",
        ]

    def get_supertypes(self) -> List[str]:
        """
        Get all supertypes.

        Returns:
            List of supertype names
        """
        return ["legendary", "snow", "world", "basic"]

    def get_colors(self) -> List[str]:
        """
        Get all colors in Magic: The Gathering.

        Returns:
            List of color names
        """
        return ["white", "blue", "black", "red", "green", "colorless"]

    def get_color_combinations(self) -> Dict[str, str]:
        """
        Get common color combination mappings.

        Returns:
            Dictionary mapping color combination names to Scryfall syntax
        """
        return {
            "azorius": "uw",
            "dimir": "ub",
            "rakdos": "br",
            "gruul": "rg",
            "selesnya": "gw",
            "orzhov": "wb",
            "izzet": "ur",
            "golgari": "bg",
            "boros": "rw",
            "simic": "gu",
            "esper": "uwb",
            "grixis": "ubr",
            "jund": "brg",
            "naya": "rwg",
            "bant": "gwu",
            "abzan": "wbg",
            "jeskai": "urw",
            "sultai": "bgu",
            "mardu": "rwb",
            "temur": "gur",
            "glint": "wubrg",
            "dune": "wubrg",
            "ink": "wubrg",
            "witch": "wubrg",
            "yore": "wubrg",
        }

    def search_cards(self, query: str, page: int = 1) -> Dict[str, Any]:
        """
        Search for cards using Scryfall syntax.

        Args:
            query: Scryfall search query
            page: Page number for pagination

        Returns:
            Search results from Scryfall

        Raises:
            ScryfallAPIError: If search fails
        """
        if not query or not query.strip():
            raise ScryfallAPIRequestError("Empty search query provided")

        if page < 1:
            raise ScryfallAPIRequestError("Page number must be 1 or greater")

        try:
            logger.info(f"Searching cards with query: {query} (page {page})")

            response = self._make_request(
                "cards/search", params={"q": query, "page": page}
            )

            # Validate response structure
            if not isinstance(response, dict):
                raise ScryfallAPIResponseError(
                    "Invalid search response format: expected dictionary"
                )

            # Check for required fields
            if "data" not in response:
                raise ScryfallAPIResponseError(
                    "Invalid search response: missing 'data' field"
                )

            if not isinstance(response["data"], list):
                raise ScryfallAPIResponseError(
                    "Invalid search response: 'data' should be a list"
                )

            logger.info(f"Search returned {len(response['data'])} cards")
            return response

        except ScryfallAPIError:
            # Re-raise Scryfall-specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during card search: {e}")
            raise ScryfallAPIError(f"Card search failed: {e}") from e

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        cache_size = len(self._cache)
        cache_keys = list(self._cache.keys())

        return {
            "enabled": self.cache_data,
            "size": cache_size,
            "keys": cache_keys,
            "duration": self._cache_duration,
        }
