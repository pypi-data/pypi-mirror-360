from unittest.mock import patch, MagicMock

import pytest
from jwt import ExpiredSignatureError, InvalidTokenError
from typing import Any
from sag_py_auth.models import AuthConfig
from sag_py_auth.token_decoder import verify_and_decode_token, get_cached_signing_key, cache


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Fixture to clear the cache before each test."""
    cache.clear()


def test_verify_valid_token() -> None:
    """Test that a valid token is decoded successfully."""
    auth_config = AuthConfig(issuer="https://auth.company.cloud.de/realms/realm", audience="test-audience")
    valid_token = "valid.jwt.token"
    mock_key = MagicMock()

    with patch("sag_py_auth.token_decoder.PyJWKClient") as mock_jwk_client:
        # Mock PyJWKClient behavior
        mock_jwk_client_instance = mock_jwk_client.return_value
        mock_jwk_client_instance.get_signing_key_from_jwt.return_value = mock_key

        # Mock decode function to return a valid payload
        with patch("sag_py_auth.token_decoder.decode", return_value={"sub": "12345", "aud": "test-audience"}):
            result = verify_and_decode_token(auth_config, valid_token)
            assert result["sub"] == "12345"
            assert result["aud"] == "test-audience"


def test_verify_invalid_token() -> None:
    """Test that an invalid token raises a ValueError."""
    auth_config = AuthConfig(issuer="https://auth.company.cloud.de/realms/realm", audience="test-audience")
    invalid_token = "invalid.jwt.token"
    mock_key = MagicMock()

    with patch("sag_py_auth.token_decoder.PyJWKClient") as mock_jwk_client:
        # Mock PyJWKClient behavior
        mock_jwk_client_instance = mock_jwk_client.return_value
        mock_jwk_client_instance.get_signing_key_from_jwt.return_value = mock_key

        # Mock decode function to raise an InvalidTokenError
        with patch("sag_py_auth.token_decoder.decode", side_effect=InvalidTokenError("Invalid signature")):
            try:
                verify_and_decode_token(auth_config, invalid_token)
            except ValueError as e:
                assert "Invalid token signature" in str(e)


def test_verify_expired_token() -> None:
    """Test that an expired token raises a ValueError."""
    auth_config = AuthConfig(issuer="https://auth.company.cloud.de/realms/realm", audience="test-audience")
    expired_token = "expired.jwt.token"
    mock_key = MagicMock()

    with patch("sag_py_auth.token_decoder.PyJWKClient") as mock_jwk_client:
        # Mock PyJWKClient behavior
        mock_jwk_client_instance = mock_jwk_client.return_value
        mock_jwk_client_instance.get_signing_key_from_jwt.return_value = mock_key

        # Mock decode function to raise an ExpiredSignatureError
        with patch("sag_py_auth.token_decoder.decode", side_effect=ExpiredSignatureError("Token has expired")):
            try:
                verify_and_decode_token(auth_config, expired_token)
            except ValueError as e:
                assert "Invalid token signature" in str(e)


def test_caching_behavior() -> None:
    """Test that the signing key is cached and reused."""
    auth_config = AuthConfig(issuer="https://auth.company.cloud.de/realms/realm", audience="test-audience")
    valid_token = "valid.jwt.token"
    mock_key = MagicMock()

    with patch("sag_py_auth.token_decoder.PyJWKClient") as mock_jwk_client:
        # Mock PyJWKClient behavior
        mock_jwk_client_instance = mock_jwk_client.return_value
        mock_jwk_client_instance.get_signing_key_from_jwt.return_value = mock_key

        # Call get_cached_signing_key twice for the same issuer
        key1 = get_cached_signing_key(auth_config.issuer, valid_token)
        key2 = get_cached_signing_key(auth_config.issuer, valid_token)

        # Ensure PyJWKClient was called only once (key was cached)
        assert mock_jwk_client_instance.get_signing_key_from_jwt.call_count == 1
        assert key1 is key2  # Cached key should be reused


def test_thread_safety_of_cache() -> None:
    """Test that the cache is thread-safe."""
    auth_config = AuthConfig(issuer="https://auth.company.cloud.de/realms/realm", audience="test-audience")
    valid_token = "valid.jwt.token"
    mock_key = MagicMock()

    with patch("sag_py_auth.token_decoder.PyJWKClient") as mock_jwk_client:
        # Mock PyJWKClient behavior
        mock_jwk_client_instance = mock_jwk_client.return_value
        mock_jwk_client_instance.get_signing_key_from_jwt.return_value = mock_key

        # Simulate concurrent calls to get_cached_signing_key
        from concurrent.futures import ThreadPoolExecutor

        def call_get_cached_signing_key() -> Any:
            return get_cached_signing_key(auth_config.issuer, valid_token)

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(lambda _: call_get_cached_signing_key(), range(3)))

        # Ensure all threads received the same cached key instance
        for result in results:
            assert result is results[0]
