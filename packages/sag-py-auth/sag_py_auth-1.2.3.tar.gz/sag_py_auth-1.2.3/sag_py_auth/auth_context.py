from contextvars import ContextVar

from sag_py_auth.models import Token

token: ContextVar[Token | None] = ContextVar("token", default=None)


def get_token() -> Token | None:
    """Gets the context local token. See library contextvars for details.

    Returns: The token
    """
    return token.get(None)


def set_token(token_to_set: Token) -> None:
    """Sets the context local token. See library contextvars for details."""
    token.set(token_to_set)
