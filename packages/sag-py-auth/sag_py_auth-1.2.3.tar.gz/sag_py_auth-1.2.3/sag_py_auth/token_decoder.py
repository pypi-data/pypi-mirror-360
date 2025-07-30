from cachetools import TTLCache
from threading import Lock
from typing import Any
from jwt import decode, PyJWKClient, PyJWK

from sag_py_auth.models import AuthConfig

# Thread-safe cache with time-to-live
cache: TTLCache[str, PyJWK] = TTLCache(maxsize=10, ttl=600)  # Cache up to 10 keys for 10 minutes
lock = Lock()


def verify_and_decode_token(auth_config: AuthConfig, token_string: str) -> dict[str, Any]:
    """Decode and verify the token

    Returns: The token
    """
    cached_key = get_cached_signing_key(auth_config.issuer, token_string)

    try:
        token: dict[str, Any] = decode(jwt=token_string, key=cached_key, audience=auth_config.audience,
                                       issuer=auth_config.issuer, algorithms=["RS256"])
        return token
    except Exception as e:
        raise ValueError(f"Invalid token signature. Reason: {str(e)}")


def get_cached_signing_key(issuer: str, token_string: str) -> PyJWK:
    """Thread-safe retrieval of signing key."""
    with lock:
        if issuer not in cache:
            jwks_request_headers: dict[str, str] = {"content-type": "application/json"}
            jwks_client = PyJWKClient(f"{issuer}/protocol/openid-connect/certs", headers=jwks_request_headers)
            cache[issuer] = jwks_client.get_signing_key_from_jwt(token_string)
        return cache[issuer]
