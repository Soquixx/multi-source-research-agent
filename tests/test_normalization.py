import pytest
from app.processing.normalization import normalize_url

@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://Example.com/article",
            "https://example.com/article",
        ),
        (
            "https://example.com/article/",
            "https://example.com/article",
        ),
        (
            "https://example.com/article?utm_source=google",
            "https://example.com/article",
        ),
        (
            "https://example.com/article?utm_source=google&utm_medium=social",
            "https://example.com/article",
        ),
        (
            "https://example.com/article?id=10",
            "https://example.com/article?id=10",
        ),
        (
            "https://example.com/article?id=10&utm_source=x",
            "https://example.com/article?id=10",
        ),
        (
            "https://example.com/article?b=2&a=1",
            "https://example.com/article?a=1&b=2",
        ),
    ],
)
def test_normalize_url(url: str, expected: str):
    assert normalize_url(url) == expected

def test_empty_url():
    assert normalize_url("") == ""

def test_whitespace_url():
    assert normalize_url("   ") == ""