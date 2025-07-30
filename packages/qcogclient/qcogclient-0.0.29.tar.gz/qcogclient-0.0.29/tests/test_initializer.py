"""Tests for the Initializer class."""

from unittest.mock import MagicMock, Mock, patch
import pytest

from qcogclient.httpclient import HttpClient
from qcogclient.qcog._initializer import Initializer

from tests._patches import INIT_CLIENT_PATCH, INITIALIZER_STORE_GET_PATCH


def test_initializer_with_http_client() -> None:
    """Test Initializer with direct http_client - highest priority."""
    mock_client = Mock(spec=HttpClient)

    initializer = Initializer(http_client=mock_client)

    assert initializer.client is mock_client


def test_initializer_with_basic_auth() -> None:
    """Test Initializer with basic auth credentials - second priority."""
    mock_client = Mock(spec=HttpClient)

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="admin",
            basic_auth_password="secret",
            base_url="http://test.com",
        )

    assert initializer.client is mock_client
    mock_init.assert_called_once_with(
        basic_auth_username="admin",
        basic_auth_password="secret",
        base_url="http://test.com",
        timeout=3000,
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_with_basic_auth_partial_missing_username(
    mock_get: MagicMock,
) -> None:
    """Test that missing username with password doesn't trigger basic auth."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_password="secret",
        )

    # Should fall back to API key since basic auth is incomplete
    assert initializer.client is mock_client
    mock_init.assert_called_once_with(api_key="stored-api-key", base_url=None)


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_with_basic_auth_partial_missing_password(
    mock_get: MagicMock,
) -> None:
    """Test that missing password with username doesn't trigger basic auth."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="admin",
        )

    # Should fall back to API key since basic auth is incomplete
    assert initializer.client is mock_client
    mock_init.assert_called_once_with(api_key="stored-api-key", base_url=None)


def test_initializer_with_provided_api_key() -> None:
    """Test Initializer with provided API key - third priority."""
    mock_client = Mock(spec=HttpClient)

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            api_key="provided-api-key", base_url="http://test.com"
        )

    assert initializer.client is mock_client
    mock_init.assert_called_once_with(
        api_key="provided-api-key", base_url="http://test.com"
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_with_stored_api_key(mock_get: MagicMock) -> None:
    """Test Initializer with API key from store - fourth priority."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(base_url="http://test.com")

    assert initializer.client is mock_client
    mock_init.assert_called_once_with(
        api_key="stored-api-key", base_url="http://test.com"
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_no_credentials_raises_error(mock_get: MagicMock) -> None:
    """Test Initializer raises ValueError when no credentials are available."""
    mock_get.return_value = {}  # No api_key in store

    with pytest.raises(
        ValueError, match="No API key found. Either provide an API key or login first."
    ):
        Initializer()


def test_initializer_priority_http_client_over_basic_auth() -> None:
    """Test that http_client takes priority over basic auth."""
    mock_http_client = Mock(spec=HttpClient)

    # Even with basic auth provided, http_client should be used
    initializer = Initializer(
        http_client=mock_http_client,
        basic_auth_username="admin",
        basic_auth_password="secret",
    )

    assert initializer.client is mock_http_client


def test_initializer_priority_http_client_over_api_key() -> None:
    """Test that http_client takes priority over API key."""
    mock_http_client = Mock(spec=HttpClient)

    # Even with API key provided, http_client should be used
    initializer = Initializer(http_client=mock_http_client, api_key="test-api-key")

    assert initializer.client is mock_http_client


def test_initializer_priority_basic_auth_over_provided_api_key() -> None:
    """Test that basic auth takes priority over provided API key."""
    mock_client = Mock(spec=HttpClient)

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="admin",
            basic_auth_password="secret",
            api_key="test-api-key",
            base_url="http://test.com",
        )

    assert initializer.client is mock_client
    # Should use basic auth, not API key
    mock_init.assert_called_once_with(
        basic_auth_username="admin",
        basic_auth_password="secret",
        base_url="http://test.com",
        timeout=3000,
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_priority_basic_auth_over_stored_api_key(
    mock_get: MagicMock,
) -> None:
    """Test that basic auth takes priority over stored API key."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="admin",
            basic_auth_password="secret",
            base_url="http://test.com",
        )

    assert initializer.client is mock_client
    # Should use basic auth, not stored API key
    mock_init.assert_called_once_with(
        basic_auth_username="admin",
        basic_auth_password="secret",
        base_url="http://test.com",
        timeout=3000,
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_priority_provided_api_key_over_stored(mock_get: MagicMock) -> None:
    """Test that provided API key takes priority over stored API key."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            api_key="provided-api-key", base_url="http://test.com"
        )

    assert initializer.client is mock_client
    # Should use provided API key, not stored one
    mock_init.assert_called_once_with(
        api_key="provided-api-key", base_url="http://test.com"
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_empty_string_api_key_fallback_to_stored(
    mock_get: MagicMock,
) -> None:
    """Test that empty string API key falls back to stored API key."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            api_key="",  # Empty string should be falsy
            base_url="http://test.com",
        )

    assert initializer.client is mock_client
    # Should use stored API key since empty string is falsy
    mock_init.assert_called_once_with(
        api_key="stored-api-key", base_url="http://test.com"
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_none_api_key_fallback_to_stored(mock_get: MagicMock) -> None:
    """Test that None API key falls back to stored API key."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(api_key=None, base_url="http://test.com")

    assert initializer.client is mock_client
    # Should use stored API key since None is falsy
    mock_init.assert_called_once_with(
        api_key="stored-api-key", base_url="http://test.com"
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_empty_basic_auth_credentials(mock_get: MagicMock) -> None:
    """Test that empty string basic auth credentials don't trigger basic auth."""
    mock_client = Mock(spec=HttpClient)
    mock_get.return_value = {"api_key": "stored-api-key"}

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="", basic_auth_password="", base_url="http://test.com"
        )

    assert initializer.client is mock_client
    # Should fall back to API key since empty strings are falsy
    mock_init.assert_called_once_with(
        api_key="stored-api-key", base_url="http://test.com"
    )


def test_initializer_whitespace_basic_auth_credentials() -> None:
    """Test that whitespace-only basic auth credentials trigger basic auth."""
    mock_client = Mock(spec=HttpClient)

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(
            basic_auth_username="   ",  # Whitespace is truthy
            basic_auth_password="   ",  # Whitespace is truthy
            base_url="http://test.com",
        )

    assert initializer.client is mock_client
    # Should use basic auth since whitespace strings are truthy
    mock_init.assert_called_once_with(
        basic_auth_username="   ",
        basic_auth_password="   ",
        base_url="http://test.com",
        timeout=3000,
    )


@patch(INITIALIZER_STORE_GET_PATCH)
def test_api_key_property_retrieves_from_store(mock_get: MagicMock) -> None:
    mock_get.return_value = {"api_key": "test-api-key-from-store"}

    # 1. Create instance safely with dummy data
    with patch(INIT_CLIENT_PATCH):
        initializer = Initializer(api_key="dummy-to-avoid-store-lookup")

    # 2. Reset mock to isolate the property test
    mock_get.reset_mock()

    # 3. Test the property in isolation
    result = initializer.api_key

    # 4. Verify behavior without affecting real store
    assert result == "test-api-key-from-store"
    mock_get.assert_called_once_with({"api_key": "GET"})


@patch(INITIALIZER_STORE_GET_PATCH)
def test_api_key_property_returns_none_when_not_in_store(mock_get: MagicMock) -> None:
    """Test that api_key property returns None when key not in store."""
    mock_get.return_value = {}  # Empty store

    # Better: Use a real instance but with mocked dependencies
    with patch(INIT_CLIENT_PATCH):
        initializer = Initializer(api_key="dummy-to-avoid-store-lookup")

    # Clear the mock calls from __init__ and test the property
    mock_get.reset_mock()
    result = initializer.api_key

    assert result is None
    mock_get.assert_called_once_with({"api_key": "GET"})


@patch(INITIALIZER_STORE_GET_PATCH)
def test_api_key_property_returns_none_when_key_is_none_in_store(
    mock_get: MagicMock,
) -> None:
    """Test that api_key property returns None when key is None in store."""
    mock_get.return_value = {"api_key": None}

    # Better: Use a real instance but with mocked dependencies
    with patch(INIT_CLIENT_PATCH):
        initializer = Initializer(api_key="dummy-to-avoid-store-lookup")

    # Clear the mock calls from __init__ and test the property
    mock_get.reset_mock()
    result = initializer.api_key

    assert result is None
    mock_get.assert_called_once_with({"api_key": "GET"})


def test_initializer_with_all_parameters() -> None:
    """Test Initializer with all parameters provided to verify behavior."""
    mock_http_client = Mock(spec=HttpClient)

    # When http_client is provided, it should be used regardless of other params
    initializer = Initializer(
        http_client=mock_http_client,
        base_url="http://ignored.com",
        api_key="ignored-api-key",
        basic_auth_username="ignored-username",
        basic_auth_password="ignored-password",
    )

    assert initializer.client is mock_http_client


def test_initializer_base_url_passed_to_init_client() -> None:
    """Test that base_url is correctly passed to init_client."""
    mock_client = Mock(spec=HttpClient)
    custom_base_url = "http://custom.example.com"

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(api_key="test-api-key", base_url=custom_base_url)

    assert initializer.client is mock_client
    mock_init.assert_called_once_with(api_key="test-api-key", base_url=custom_base_url)


def test_initializer_no_base_url_passed_as_none() -> None:
    """Test that when no base_url is provided, None is passed to init_client."""
    mock_client = Mock(spec=HttpClient)

    with patch(INIT_CLIENT_PATCH, return_value=mock_client) as mock_init:
        initializer = Initializer(api_key="test-api-key")

    assert initializer.client is mock_client
    mock_init.assert_called_once_with(api_key="test-api-key", base_url=None)


def test_initializer_error_propagated_from_init_client() -> None:
    """Test that errors from init_client are properly propagated."""
    with patch(INIT_CLIENT_PATCH, side_effect=RuntimeError("Connection failed")):
        with pytest.raises(RuntimeError, match="Connection failed"):
            Initializer(api_key="test-api-key")


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_stored_api_key_is_none_raises_error(mock_get: MagicMock) -> None:
    """Test Initializer raises ValueError when stored API key is None."""
    mock_get.return_value = {"api_key": None}

    with pytest.raises(
        ValueError, match="No API key found. Either provide an API key or login first."
    ):
        Initializer()


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_stored_api_key_is_empty_string_raises_error(
    mock_get: MagicMock,
) -> None:
    """Test Initializer raises ValueError when stored API key is empty string."""
    mock_get.return_value = {"api_key": ""}

    with pytest.raises(
        ValueError, match="No API key found. Either provide an API key or login first."
    ):
        Initializer()


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_provided_empty_string_stored_none_raises_error(
    mock_get: MagicMock,
) -> None:
    """Test Initializer raises ValueError when provided API key is empty and stored is None."""
    mock_get.return_value = {"api_key": None}

    with pytest.raises(
        ValueError, match="No API key found. Either provide an API key or login first."
    ):
        Initializer(api_key="")


@patch(INITIALIZER_STORE_GET_PATCH)
def test_initializer_provided_none_stored_empty_raises_error(
    mock_get: MagicMock,
) -> None:
    """Test Initializer raises ValueError when provided API key is None and stored is empty."""
    mock_get.return_value = {"api_key": ""}

    with pytest.raises(
        ValueError, match="No API key found. Either provide an API key or login first."
    ):
        Initializer(api_key=None)
