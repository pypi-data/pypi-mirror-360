from logging import LogRecord
from typing import cast

from sag_py_auth.auth_context import set_token as set_token_to_context
from sag_py_auth.models import Token, UserInfoLogRecord
from sag_py_auth.user_name_logging_filter import UserNameLoggingFilter

from .helpers import get_token


def test__get_field_value__with_valid_data() -> None:
    # Arrange
    logging_filter = UserNameLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    token: Token = get_token(None, None)
    set_token_to_context(token)

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert cast(UserInfoLogRecord, log_entry).user_name == "preferredUsernameValue"
    assert cast(UserInfoLogRecord, log_entry).authorized_party == "public-project-swagger"


def test__get_field_value__with_missing_data() -> None:
    # Arrange
    logging_filter = UserNameLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    token: Token = get_token(None, None)
    token.token_dict["preferred_username"] = None
    token.token_dict["azp"] = None
    set_token_to_context(token)

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert not hasattr(log_entry, "user_name")
    assert not hasattr(log_entry, "authorized_party")
