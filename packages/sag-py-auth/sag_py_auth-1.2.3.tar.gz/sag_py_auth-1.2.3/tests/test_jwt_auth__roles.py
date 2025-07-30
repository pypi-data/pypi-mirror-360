import pytest
from fastapi import HTTPException

from sag_py_auth.jwt_auth import JwtAuth
from sag_py_auth.models import AuthConfig, Token, TokenRole

from .helpers import get_token


def test__verify_roles__has_multiple() -> None:
    # Arrange
    jwt_auth = JwtAuth(
        AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"),
        [TokenRole("clientOne", "clientOneRoleOne"), TokenRole("clientTwo", "clientTwoRoleTwo")],
        None,
    )

    resource_access: dict[str, dict[str, list[str]]] = {
        "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
        "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
    }

    token: Token = get_token(None, resource_access)

    # Act
    try:
        jwt_auth._verify_roles(token)
    except Exception:
        pytest.fail("No exception expected if the user has all roles")


def test__verify_roles__requires_none() -> None:
    # Arrange
    jwt_auth = JwtAuth(AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"), None, None)

    resource_access: dict[str, dict[str, list[str]]] = {
        "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
        "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
    }

    token: Token = get_token(None, resource_access)

    # Act
    try:
        jwt_auth._verify_roles(token)
    except Exception:
        pytest.fail("No exception expected if the user requires no roles")


def test__verify_roles__requires_empty() -> None:
    # Arrange
    jwt_auth = JwtAuth(AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"), [], None)

    resource_access: dict[str, dict[str, list[str]]] = {
        "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
        "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
    }

    token: Token = get_token(None, resource_access)

    # Act
    try:
        jwt_auth._verify_roles(token)
    except Exception:
        pytest.fail("No exception expected if the user requires no roles")


def test__verify_roles__missing_role_of_existing_client() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        jwt_auth = JwtAuth(
            AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"),
            [
                TokenRole("clientOne", "clientOneRoleOne"),
                TokenRole("clientTwo", "clientTwoRoleTwo"),
                TokenRole("clientTwo", "missingRole"),
            ],
            None,
        )

        resource_access: dict[str, dict[str, list[str]]] = {
            "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
            "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
        }

        token: Token = get_token(None, resource_access)

        # Act
        jwt_auth._verify_roles(token)

    # Assert
    assert exception.value.status_code == 403
    assert exception.value.detail == "Missing role."


def test__verify_roles__missing_role_of_missing_client() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        jwt_auth = JwtAuth(
            AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"),
            [
                TokenRole("clientOne", "clientOneRoleOne"),
                TokenRole("clientTwo", "clientTwoRoleTwo"),
                TokenRole("missingClient", "missingRole"),
            ],
            None,
        )

        resource_access: dict[str, dict[str, list[str]]] = {
            "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
            "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
        }

        token: Token = get_token(None, resource_access)

        # Act
        jwt_auth._verify_roles(token)

    # Assert
    assert exception.value.status_code == 403
    assert exception.value.detail == "Missing role."


def test__verify_roles__token_with_empty_roles() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        jwt_auth = JwtAuth(
            AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"),
            [
                TokenRole("clientOne", "clientOneRoleOne"),
                TokenRole("clientTwo", "clientTwoRoleTwo"),
                TokenRole("missingClient", "missingRole"),
            ],
            None,
        )

        token: Token = get_token(None, {})

        # Act
        jwt_auth._verify_roles(token)

    # Assert
    assert exception.value.status_code == 403
    assert exception.value.detail == "Missing role."


def test__verify_roles__token_without_roles() -> None:
    with pytest.raises(HTTPException) as exception:
        # Arrange
        jwt_auth = JwtAuth(
            AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne"),
            [
                TokenRole("clientOne", "clientOneRoleOne"),
                TokenRole("clientTwo", "clientTwoRoleTwo"),
                TokenRole("missingClient", "missingRole"),
            ],
            None,
        )

        token: Token = get_token(None, None)

        # Act
        jwt_auth._verify_roles(token)

    # Assert
    assert exception.value.status_code == 403
    assert exception.value.detail == "Missing role."
