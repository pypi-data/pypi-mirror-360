from sag_py_auth.auth_context import get_token as get_token_from_context
from sag_py_auth.auth_context import set_token as set_token_to_context
from sag_py_auth.models import Token

from .helpers import get_token as get_test_token


# Note: This test is not entirely independent of the other test
# because they run in the same context and therefor share a context.
# That's why the "not_set_token" test has to run before the "with_previously_set_token"
# Furthermore other tests that run the __call__ method of jwt_auth could break that one.
def test__get_token__not_set_token() -> None:
    # Act
    actual: Token | None = get_token_from_context()

    assert actual is None


def test__get_token__with_previously_set_token() -> None:
    # Arrange
    token: Token = get_test_token(None, None)

    # Act
    set_token_to_context(token)
    actual: Token | None = get_token_from_context()

    assert actual == token
