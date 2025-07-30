from logging import Filter, LogRecord

from sag_py_auth.auth_context import get_token
from sag_py_auth.models import Token


class UserNameLoggingFilter(Filter):
    """Register this filter to get a field user_name and authorized_party in log entries"""

    def __init__(self, name: str = "") -> None:
        super().__init__(name=name)

    def filter(self, record: LogRecord) -> bool:
        token: Token | None = get_token()
        user_name: str = token.get_field_value("preferred_username") if token else ""
        authorized_party: str = token.get_field_value("azp") if token else ""

        if user_name:
            record.user_name = user_name

        if authorized_party:
            record.authorized_party = authorized_party

        return True
