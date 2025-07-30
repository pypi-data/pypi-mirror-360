from urllib.parse import ParseResult, urlparse


def validate_url(url: str) -> bool:
    result: ParseResult = urlparse(url)
    return all([result.scheme, result.netloc])
