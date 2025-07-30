from sag_py_auth.models import Token

from .helpers import get_token


def test__token__get_field_value__with_existing_key() -> None:
    # Arrange
    token: Token = get_token(None, None)

    # Act
    actual: str = token.get_field_value("azp")

    # Assert
    assert actual == "public-project-swagger"


def test__token__get_field_value__with_missing_key() -> None:
    # Arrange
    token: Token = get_token(None, None)

    # Act
    actual: str = token.get_field_value("missingKey")

    # Assert
    assert not actual


def test__token__roles() -> None:
    # Arrange
    resource_access: dict[str, dict[str, list[str]]] = {
        "clientOne": {"roles": ["clientOneRoleOne", "clientOneRoleTwo"]},
        "clientTwo": {"roles": ["clientTwoRoleOne", "clientTwoRoleTwo"]},
    }

    token: Token = get_token(None, resource_access)

    # Act
    actual_client_one: list[str] = token.get_roles("clientOne")
    actual_missing_client: list[str] = token.get_roles("missingClient")

    actual_has_one: bool = token.has_role("clientOne", "clientOneRoleOne")
    actual_has_missing_role: bool = token.has_role("clientOne", "missingRole")
    actual_has_missing_client: bool = token.has_role("missingClient", "missingRole")

    # Assert
    assert actual_client_one == ["clientOneRoleOne", "clientOneRoleTwo"]
    assert not actual_missing_client
    assert actual_has_one
    assert not actual_has_missing_role
    assert not actual_has_missing_client


def test__token__realm_roles() -> None:
    # Arrange
    realm_access: dict[str, list[str]] = {"roles": ["realmRoleOne", "realmRoleTwo"]}

    token: Token = get_token(realm_access, None)

    # Act
    actual_realm_roles: list[str] = token.get_realm_roles()

    actual_has_one: bool = token.has_realm_role("realmRoleOne")
    actual_has_missing: bool = token.has_realm_role("missingRole")

    # Assert
    assert actual_realm_roles == ["realmRoleOne", "realmRoleTwo"]
    assert actual_has_one
    assert not actual_has_missing
