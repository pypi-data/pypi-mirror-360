from typing import Any

import pytest
from fastapi import HTTPException
from pytest import MonkeyPatch

from sag_py_auth.jwt_auth import JwtAuth
from sag_py_auth.models import AuthConfig, Token, TokenRole

from .helpers import get_token_dict


def verify_and_decode_token_mock(auth_config: AuthConfig, token_string: str) -> dict[str, Any]:
    if token_string == "validToken":
        return get_token_dict(None, None)
    else:
        raise Exception(f"Invalid payload string: {token_string}")


def test__verify_and_decode_token__with_valid_token(monkeypatch: MonkeyPatch) -> None:
    # Arrange
    auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
    required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
    required_realm_roles: list[str] = ["realmRoleOne"]

    monkeypatch.setattr("sag_py_auth.jwt_auth.verify_and_decode_token", verify_and_decode_token_mock)

    jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

    # Act
    actual: Token = jwt._verify_and_decode_token("validToken")

    # Assert
    assert actual.get_field_value("typ") == "Bearer"
    assert actual.get_field_value("azp") == "public-project-swagger"


def test__verify_and_decode_token__with_invalid_token(monkeypatch: MonkeyPatch) -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        monkeypatch.setattr("sag_py_auth.jwt_auth.verify_and_decode_token", verify_and_decode_token_mock)

        jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

        # Act
        jwt._verify_and_decode_token("invalidToken")

    # Assert
    assert exception.value.status_code == 401
    assert exception.value.detail == "Invalid token."
