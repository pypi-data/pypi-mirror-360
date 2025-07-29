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
