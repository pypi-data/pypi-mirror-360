import logging
from logging import Logger
from typing import NoReturn, Any

from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from sag_py_auth.auth_context import set_token as auth_context_set_token
from sag_py_auth.models import AuthConfig, Token, TokenRole
from sag_py_auth.token_decoder import verify_and_decode_token
from sag_py_auth.utils import validate_url

logger: Logger = logging.getLogger(__name__)


class JwtAuth(OAuth2AuthorizationCodeBearer):
    def __init__(
        self,
        auth_config: AuthConfig,
        required_roles: list[TokenRole] | None,
        required_realm_roles: list[str] | None,
        scheme_name: str = "auth"
    ) -> None:
        # sourcery skip: raise-specific-error

        if not validate_url(auth_config.issuer) or not auth_config.audience:
            raise Exception("Invalid issuer or audience")

        self.auth_config: AuthConfig = auth_config
        self.required_roles: list[TokenRole] = required_roles or []
        self.required_realm_roles: list[str] = required_realm_roles or []

        super().__init__(
            f"{auth_config.issuer}/protocol/openid-connect/auth",
            f"{auth_config.issuer}/protocol/openid-connect/token",
            scopes={},
            auto_error=False,
            scheme_name=scheme_name,
        )

    async def __call__(self, request: Request) -> Token:  # type: ignore
        token_string: str | None = await super().__call__(request)

        if not token_string:
            logger.warning("Missing auth token")
            self._raise_auth_error(HTTP_401_UNAUTHORIZED, "Missing token.")

        token: Token = self._verify_and_decode_token(token_string)

        self._verify_roles(token)
        self._verify_realm_roles(token)
        auth_context_set_token(token)
        return token

    def _verify_and_decode_token(self, token_string: str) -> Token:
        try:
            token_dict: dict[str, Any] = verify_and_decode_token(self.auth_config, token_string)
            return Token(token_dict)
        except Exception:
            logger.warning("Invalid auth token", exc_info=True)
            self._raise_auth_error(HTTP_401_UNAUTHORIZED, "Invalid token.")

    def _verify_roles(self, token: Token | None) -> None:
        has_all_roles: bool = token is not None and all(
            token.has_role(requiredRole.client, requiredRole.role) for requiredRole in self.required_roles
        )

        if not has_all_roles:
            logger.warning("User requires roles '%s'", self.required_roles)
            self._raise_auth_error(HTTP_403_FORBIDDEN, "Missing role.")

    def _verify_realm_roles(self, token: Token | None) -> None:
        token_realm_roles: list[str] = token.get_realm_roles() if token is not None else []
        has_all_realm_roles: bool = all(realm_role in token_realm_roles for realm_role in self.required_realm_roles)

        if not has_all_realm_roles:
            logger.warning("User requires realm roles '%s'", self.required_realm_roles)
            self._raise_auth_error(HTTP_403_FORBIDDEN, "Missing realm role.")

    def _raise_auth_error(self, status_code: int, detail: str) -> NoReturn:
        raise HTTPException(status_code=status_code, detail=detail, headers={"WWW-Authenticate": "Bearer"})
