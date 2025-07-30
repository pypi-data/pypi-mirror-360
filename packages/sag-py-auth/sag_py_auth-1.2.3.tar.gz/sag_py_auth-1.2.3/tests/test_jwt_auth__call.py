from typing import Literal, Any

import pytest
from fastapi import HTTPException, Request
from pytest import MonkeyPatch
from starlette.datastructures import Headers

from sag_py_auth.jwt_auth import JwtAuth
from sag_py_auth.models import AuthConfig, Token, TokenRole

from .helpers import get_token_dict

pytest_plugins: tuple[Literal["pytest_asyncio"]] = ("pytest_asyncio",)


def verify_and_decode_token_mock(_: AuthConfig, __: str) -> dict[str, Any]:
    return get_token_dict(None, None)


def _verify_roles_mock(_: JwtAuth, token: Token | None) -> None:
    if token:
        token.token_dict["_verify_roles"] = "True"


def _verify_realm_roles_mock(_: JwtAuth, token: Token | None) -> None:
    if token:
        token.token_dict["_verify_realm_roles"] = "True"


def auth_context_set_token_mock(token: Token) -> None:
    if token:
        token.token_dict["auth_context_set_token"] = "True"


@pytest.mark.asyncio
async def test__call__correctly_processes_request(monkeypatch: MonkeyPatch) -> None:
    # Arrange
    auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
    required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
    required_realm_roles: list[str] = ["realmRoleOne"]

    monkeypatch.setattr("sag_py_auth.jwt_auth.verify_and_decode_token", verify_and_decode_token_mock)
    monkeypatch.setattr("sag_py_auth.jwt_auth.JwtAuth._verify_roles", _verify_roles_mock)
    monkeypatch.setattr("sag_py_auth.jwt_auth.JwtAuth._verify_realm_roles", _verify_realm_roles_mock)
    monkeypatch.setattr("sag_py_auth.jwt_auth.auth_context_set_token", auth_context_set_token_mock)

    jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

    request: Request = Request(scope={"type": "http"})
    request._headers = Headers({"Authorization": "Bearer validToken"})

    # Act
    actual: Token = await jwt(request)

    # Assert - Verify that all steps have been executed
    assert actual.get_field_value("typ") == "Bearer"
    assert actual.get_field_value("azp") == "public-project-swagger"
    assert actual.get_field_value("_verify_roles") == "True"
    assert actual.get_field_value("_verify_realm_roles") == "True"
    assert actual.get_field_value("auth_context_set_token") == "True"


@pytest.mark.asyncio
async def test__call__auth_header_missing() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

        request: Request = Request(scope={"type": "http"})
        request._headers = Headers({})

        # Act
        await jwt(request)

    # Assert
    assert exception.value.status_code == 401
    assert exception.value.detail == "Missing token."


@pytest.mark.asyncio
async def test__call__auth_header_invalid() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

        request: Request = Request(scope={"type": "http"})
        request._headers = Headers({"Authorization": "InvalidValue"})

        # Act
        await jwt(request)

    # Assert
    assert exception.value.status_code == 401
    assert exception.value.detail == "Missing token."


@pytest.mark.asyncio
async def test__call__auth_schema_invalid() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

        request: Request = Request(scope={"type": "http"})
        request._headers = Headers({"Authorization": "invalidSchema tokenString"})

        # Act
        await jwt(request)

    # Assert
    assert exception.value.status_code == 401
    assert exception.value.detail == "Missing token."
