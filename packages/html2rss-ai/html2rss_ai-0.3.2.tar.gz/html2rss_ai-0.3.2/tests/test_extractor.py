from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from html2rss_ai.extractor import UniversalPatternExtractor
from html2rss_ai.schemas import PatternAnalysis

HTML_SAMPLE = """
<!doctype html>
<html>
  <body>
    <ul>
      <li class="my-1.5 text-md"><a href="/post1">Post 1</a></li>
      <li class="my-1.5 text-md"><a href="/post2">Post 2</a></li>
    </ul>
  </body>
</html>
"""


def _make_pattern() -> PatternAnalysis:
    """Return a PatternAnalysis that uses a selector with a dotted class."""
    return PatternAnalysis(
        pattern_type="test",
        primary_selectors=["li.my-1.5.text-md > a"],
        fallback_selectors=[],
        url_pattern_regex=".*",
        content_indicators=[],
        skip_patterns=[],
        confidence_score=1.0,
        pattern_description="test pattern",
        estimated_items=2,
        date_selectors=[],
    )


def test_dotted_class_selector_extracts_links():
    """Extractor should handle selectors that include dotted Tailwind classes."""
    soup = BeautifulSoup(HTML_SAMPLE, "html.parser")
    extractor = UniversalPatternExtractor()
    pattern = _make_pattern()

    links = extractor._extract_links_using_pattern(  # pylint: disable=protected-access
        soup,
        "https://example.com",
        pattern,
    )

    assert len(links) == 2, "Expected two links to be extracted"
    urls = {link["url"] for link in links}
    assert urls == {
        "https://example.com/post1",
        "https://example.com/post2",
    }


def test_extractor_initialization():
    """Test that extractor can be initialized with various parameters."""
    # Test with default parameters
    extractor1 = UniversalPatternExtractor()
    assert extractor1.cache_dir == "pattern_cache"

    # Test with custom cache directory
    extractor2 = UniversalPatternExtractor(cache_dir="custom_cache")
    assert extractor2.cache_dir == "custom_cache"

    # Test with API key
    extractor3 = UniversalPatternExtractor(openai_api_key="test-key")
    assert extractor3.openai_api_key == "test-key"


def test_get_domain_hash():
    """Test domain hash generation."""
    extractor = UniversalPatternExtractor()

    # Test consistent hashing
    hash1 = extractor._get_domain_hash("https://example.com/page")
    hash2 = extractor._get_domain_hash("https://example.com/other")
    assert hash1 == hash2  # Same domain should give same hash
    assert len(hash1) == 8  # Should be 8 characters long

    # Different domains should give different hashes
    hash3 = extractor._get_domain_hash("https://other.com/page")
    assert hash1 != hash3


def test_cache_file_path_generation():
    """Test cache file path generation."""
    extractor = UniversalPatternExtractor(cache_dir="test_cache")

    path = extractor._get_cache_file_path("https://example.com/page")

    assert "test_cache" in path
    assert "example.com" in path
    assert path.endswith(".json")


def test_pattern_analysis_structure():
    """Test that PatternAnalysis has the expected structure."""
    pattern = _make_pattern()

    # Verify required fields exist
    assert hasattr(pattern, "pattern_type")
    assert hasattr(pattern, "primary_selectors")
    assert hasattr(pattern, "confidence_score")
    assert hasattr(pattern, "pattern_description")

    # Verify types
    assert isinstance(pattern.primary_selectors, list)
    assert isinstance(pattern.confidence_score, int | float)
    assert isinstance(pattern.pattern_description, str)


@pytest.mark.asyncio
async def test_extract_html_fallback():
    """Test HTML extraction fallback when url2md4ai is not available."""
    extractor = UniversalPatternExtractor()

    # Mock the _html_extractor to be None (simulating unavailable url2md4ai)
    extractor._html_extractor = None

    with patch("html2rss_ai.extractor.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await extractor._extract_html("https://example.com")

        assert result == "<html><body>Test</body></html>"
        mock_get.assert_called_once()


def test_matches_pattern():
    """Test pattern matching logic."""
    pattern = _make_pattern()

    # Test matching URL
    assert UniversalPatternExtractor._matches_pattern(
        href="/test-post",
        text="Test Post",
        full_url="https://example.com/test-post",
        pattern=pattern,
    )

    # Test with empty text (should not match)
    assert not UniversalPatternExtractor._matches_pattern(
        href="/test-post",
        text="",
        full_url="https://example.com/test-post",
        pattern=pattern,
    )
