from typing import cast

import pytest
from fastapi.openapi.models import OAuth2 as OAuth2Model

from sag_py_auth.jwt_auth import JwtAuth
from sag_py_auth.models import AuthConfig, TokenRole


def test__jwt_auth__init__with_valid_params__verify_flow() -> None:
    # Arrange
    auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "audienceOne")
    required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
    required_realm_roles: list[str] = ["realmRoleOne"]

    # Act
    jwt = JwtAuth(auth_config, required_roles, required_realm_roles)

    # Assert
    oauth_model: OAuth2Model = cast(OAuth2Model, jwt.model)
    assert jwt.required_roles == required_roles
    assert jwt.required_realm_roles == required_realm_roles
    assert oauth_model.flows.authorizationCode is not None
    assert (
        oauth_model.flows.authorizationCode.authorizationUrl
        == "https://authserver.com/auth/realms/projectName/protocol/openid-connect/auth"
    )
    assert (
        oauth_model.flows.authorizationCode.tokenUrl
        == "https://authserver.com/auth/realms/projectName/protocol/openid-connect/token"
    )


def test__jwt_auth__init__with_invalid_issuer() -> None:
    with pytest.raises(Exception) as exception:
        # Arrange
        auth_config = AuthConfig("malformedUrl", "audienceOne")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        # Act
        JwtAuth(auth_config, required_roles, required_realm_roles)

    # Assert
    assert "Invalid issuer or audience" in str(exception)


def test__jwt_auth__init__with_empty_audience() -> None:
    with pytest.raises(Exception) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", "")
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        # Act
        JwtAuth(auth_config, required_roles, required_realm_roles)

    # Assert
    assert "Invalid issuer or audience" in str(exception)


def test__jwt_auth__init__with_none_audience() -> None:
    with pytest.raises(Exception) as exception:
        # Arrange
        auth_config = AuthConfig("https://authserver.com/auth/realms/projectName", None)  # type: ignore
        required_roles: list[TokenRole] = [TokenRole("clientOne", "clientOneRoleOne")]
        required_realm_roles: list[str] = ["realmRoleOne"]

        # Act
        JwtAuth(auth_config, required_roles, required_realm_roles)

    # Assert
    assert "Invalid issuer or audience" in str(exception)
