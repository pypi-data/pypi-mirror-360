import pytest

from sag_py_auth.utils import validate_url


@pytest.mark.parametrize(
    "url",
    [
        "https://google.de",
        "http://google.de",
        "https://google.de/",
        "https://google.de/test/test2",
        "https://localhost",
    ],
)
def test__validate_url__valid_urls(url: str) -> None:
    # Act
    actual: bool = validate_url(url)

    # Assert
    assert actual


@pytest.mark.parametrize("url", ["google.de", "google", "/test/test", "", None])
def test__validate_url__invalid_urls(url: str) -> None:
    # Act
    actual: bool = validate_url(url)

    # Assert
    assert not actual
