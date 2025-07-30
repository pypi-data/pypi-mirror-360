# ruff: noqa: RUF001, RUF002, RUF003, PGH003, PTH103, PTH110, PTH118, S324, PLW2901
# mypy: ignore-errors
import asyncio
import hashlib
import json
import logging
import os
import re
from collections import Counter
from typing import Any, cast
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover – openai might be missing in CI
    OpenAI = None  # type: ignore

try:
    # url2md4ai is optional – if unavailable fall back to simple HTTP fetch
    from url2md4ai import Config, ContentExtractor  # type: ignore
except Exception:  # pragma: no cover
    ContentExtractor = None  # type: ignore
    Config = None  # type: ignore

from html2rss_ai.schemas import ExtractedPattern, PatternAnalysis
from html2rss_ai.utils import date_utils as du

logger = logging.getLogger(__name__)


class UniversalPatternExtractor:
    """High-level extractor able to detect repeating content patterns on any web page."""

    def __init__(
        self,
        openai_api_key: str | None = None,
        cache_dir: str = "pattern_cache",
    ) -> None:
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.cache_dir = cache_dir

        # Prepare LLM client (optional)
        if self.openai_api_key and OpenAI is not None:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover
                logging.warning(
                    "Failed to initialise OpenAI client – continuing without LLM: %s",
                    exc,
                )
                self.client = None
        else:
            self.client = None

        # Prepare HTML extractor (optional)
        if ContentExtractor is not None and Config is not None:
            try:
                self._html_extractor = ContentExtractor(Config.from_env())  # type: ignore[arg-type]
            except Exception as exc:  # pragma: no cover
                logging.warning(
                    "Failed to initialise ContentExtractor – falling back to requests: %s",
                    exc,
                )
                self._html_extractor = None
        else:
            self._html_extractor = None

        os.makedirs(self.cache_dir, exist_ok=True)

    # ---------------------------------------------------------------------
    # Cache helpers
    # ---------------------------------------------------------------------
    def _get_domain_hash(self, url: str) -> str:
        """Return an 8-character md5 hash of the domain – used as cache key."""
        domain = urlparse(url).netloc
        return hashlib.md5(domain.encode()).hexdigest()[:8]

    def _get_cache_file_path(self, url: str) -> str:
        domain_hash = self._get_domain_hash(url)
        domain = urlparse(url).netloc
        return os.path.join(self.cache_dir, f"pattern_{domain}_{domain_hash}.json")

    def _load_cached_pattern(self, url: str) -> PatternAnalysis | None:
        cache_file = self._get_cache_file_path(url)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, encoding="utf-8") as fp:
                    return PatternAnalysis(**json.load(fp))
            except Exception as exc:  # pragma: no cover
                logging.warning("Failed to read cache %s – %s", cache_file, exc)
        return None

    def _save_cached_pattern(self, url: str, pattern: PatternAnalysis) -> None:
        cache_file = self._get_cache_file_path(url)
        try:
            with open(cache_file, "w", encoding="utf-8") as fp:
                json.dump(pattern.model_dump(), fp, ensure_ascii=False, indent=2)
            logger.info("💾 Saved new pattern to cache: %s", cache_file)
        except Exception as exc:  # pragma: no cover
            logging.warning("Failed to write cache %s – %s", cache_file, exc)

    # ---------------------------------------------------------------------
    # HTML extraction helpers
    # ---------------------------------------------------------------------
    async def _fetch_html_simple(
        self,
        url: str,
    ) -> str | None:
        """Fetch HTML using *requests* in a thread – fallback when url2md4ai is unavailable."""

        def _get() -> str | None:
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:  # pragma: no cover
                logging.warning("HTTP request failed for %s – %s", url, exc)
                return None

        return await asyncio.to_thread(_get)

    async def _extract_html(self, url: str) -> str | None:
        if self._html_extractor is not None:
            try:
                return await self._html_extractor.extract_html(url)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover
                logging.warning("ContentExtractor failed for %s – %s", url, exc)
        # Fallback to simple HTTP
        return await self._fetch_html_simple(url)

    # ---------------------------------------------------------------------
    # Pattern analysis helpers (structure, LLM)
    # ---------------------------------------------------------------------
    @staticmethod
    def _analyze_html_structure(soup: BeautifulSoup, base_url: str) -> dict[str, Any]:
        all_links = soup.find_all("a", href=True)
        link_contexts: list[dict[str, Any]] = []

        # Analyze parent patterns and CSS classes
        parent_patterns = Counter()
        url_patterns = Counter()
        css_layout_patterns = Counter()

        for link in all_links:
            href = link.get("href")
            text = link.get_text(strip=True)

            if not href or not text or len(text) < 3:
                continue

            # Analyze parent element
            parent = link.parent
            if parent:
                parent_tag = parent.name
                parent_class = " ".join(parent.get("class", []))
                parent_pattern = (
                    f"{parent_tag}.{parent_class}" if parent_class else parent_tag
                )
                parent_patterns[parent_pattern] += 1

                # Look for CSS layout indicators
                for cls in parent.get("class", []):
                    if any(
                        keyword in cls.lower()
                        for keyword in ["grid", "flex", "row", "col", "item", "card"]
                    ):
                        css_layout_patterns[cls] += 1

            # Analyze URL patterns
            parsed_url = urlparse(urljoin(base_url, href))
            path_segments = [seg for seg in parsed_url.path.split("/") if seg]
            if path_segments:
                url_patterns["/".join(path_segments[:2])] += 1

            link_contexts.append(
                {
                    "href": href,
                    "text": text,
                    "parent_tag": parent.name if parent else "unknown",
                    "parent_class": " ".join(parent.get("class", [])) if parent else "",
                },
            )

        return {
            "total_links": len(all_links),
            "parent_patterns": dict(parent_patterns.most_common(10)),
            "url_patterns": dict(url_patterns.most_common(10)),
            "css_layout_patterns": dict(css_layout_patterns.most_common(10)),
            "link_contexts": link_contexts[:20],  # Sample for analysis
        }

    async def _analyze_patterns_with_llm(
        self,
        base_url: str,
        html_content: str,
        structure_analysis: dict[str, Any],
        *,
        force_regenerate: bool = False,
    ) -> PatternAnalysis:
        # Check cache first
        if not force_regenerate:
            cached = self._load_cached_pattern(base_url)
            if cached is not None:
                logger.info("✅ Found and using cached pattern for %s", base_url)
                return cached
            logger.info("🔎 No cached pattern found for %s", base_url)
        else:
            logger.info("🔥 Force-regenerating pattern for %s as requested", base_url)

        if self.client is None:
            raise RuntimeError(
                "LLM client unavailable and fallback is disabled – aborting.",
            )

        system_prompt = (
            "You are an expert at identifying repeating content patterns on web pages. "
            "Find lists of similar content items like blog posts, articles, job listings, products, news items, etc.\n\n"
            "Focus on identifying the PRIMARY pattern that represents the main content list on the page.\n\n"
            "IMPORTANT: Modern websites often use CSS Grid, Flexbox, or other layout techniques instead of semantic HTML tables. "
            "Look for:\n"
            "- Elements with CSS classes containing 'grid', 'flex', 'row', 'col', 'item', 'card'\n"
            "- Repeating <div> or <a> elements with similar class patterns\n"
            "- Container elements with CSS Grid (grid-template-columns, grid-cols-*) or Flexbox properties\n"
            "- Multiple <a> elements with the same parent class structure\n\n"
            "Also identify CSS selectors for publication dates:\n"
            "- <time> elements with datetime attributes\n"
            "- Elements with classes containing 'date', 'time', 'published', 'created'\n"
            "- Date patterns like '2024-01-15', 'Jan 15, 2024', '15 January 2024'\n"
            "- Date information in parent/sibling elements of the main content links"
        )

        context_summary = {
            "url": base_url,
            "total_links": structure_analysis["total_links"],
            "top_parent_patterns": list(structure_analysis["parent_patterns"].keys())[
                :5
            ],
            "top_url_patterns": list(structure_analysis["url_patterns"].keys())[:5],
            "css_layout_patterns": list(
                structure_analysis["css_layout_patterns"].keys(),
            )[:5],
            "sample_links": [
                {
                    "text": ctx["text"][:50],
                    "href": ctx["href"],
                    "parent": (
                        f"{ctx['parent_tag']}.{ctx['parent_class']}"
                        if ctx["parent_class"]
                        else ctx["parent_tag"]
                    ),
                }
                for ctx in structure_analysis["link_contexts"][:10]
            ],
        }

        user_prompt = (
            "Analyze this webpage to identify the main repeating content pattern.\n\n"
            f"URL: {base_url}\n\n"
            "STRUCTURE ANALYSIS:\n"
            f"- Total links: {context_summary['total_links']}\n"
            f"- Most common parent patterns: {context_summary['top_parent_patterns']}\n"
            f"- Most common URL patterns: {context_summary['top_url_patterns']}\n"
            f"- CSS layout patterns found: {context_summary['css_layout_patterns']}\n\n"
            "SAMPLE LINKS:\n"
            f"{json.dumps(context_summary['sample_links'], indent=2)}\n\n"
            "HTML CONTENT (first 12000 chars):\n"
            f"{html_content[:12000]}\n\n"
            "Identify:\n"
            "1. Content pattern type (blog_posts, job_listings, articles, etc.)\n"
            "2. CSS selectors for main content links\n"
            "3. URL regex pattern for content\n"
            "4. Text indicators for content vs navigation\n"
            "5. CSS selectors for publication dates\n"
            "6. Confidence score (0.0-1.0)"
        )

        logger.info("🧠 Generating new pattern with AI...")
        # instructor patches the OpenAI client so .parse is available
        response = self.client.chat.completions.parse(  # type: ignore[attr-defined]
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=PatternAnalysis,
        )
        pattern = cast("PatternAnalysis", response.choices[0].message.parsed)  # type: ignore[attr-defined]
        logger.debug("LLM pattern: %s", pattern.model_dump())
        if pattern is not None:
            self._save_cached_pattern(base_url, pattern)
        return pattern

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _matches_pattern(
        href: str,
        text: str,
        full_url: str,
        pattern: PatternAnalysis,
    ) -> bool:
        # Skip explicit skip patterns
        for skip in pattern.skip_patterns:
            if re.search(skip, href, re.IGNORECASE) or re.search(
                skip,
                text,
                re.IGNORECASE,
            ):
                return False

        # Basic heuristics – skip very short strings / obvious navigation
        if len(text.strip()) < 3:
            return False

        # If model provided a URL regex, enforce it (unless it's the generic '.*')
        if pattern.url_pattern_regex and pattern.url_pattern_regex != ".*":
            try:
                if not re.search(pattern.url_pattern_regex, href) and not re.search(
                    pattern.url_pattern_regex,
                    full_url,
                ):
                    return False
            except re.error:
                # Malformed regex from LLM – ignore the constraint.
                pass

        nav_patterns = [
            r"^(home|about|contact|privacy|terms)$",
            r"^(next|prev|previous|more)$",
            r"^\d+$",
            r"^(←|→|>>|<<)$",
        ]
        return not any(re.search(pat, text, re.IGNORECASE) for pat in nav_patterns)

    def _extract_links_using_pattern(
        self,
        soup: BeautifulSoup,
        base_url: str,
        pattern: PatternAnalysis,
    ) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        selectors_to_try = pattern.primary_selectors + pattern.fallback_selectors

        logger.debug("Trying selectors: %s", selectors_to_try)

        def _sanitize_selector(sel: str) -> str:
            """Convert class names containing dots (e.g. '.my-1.5') into attribute selectors."""
            return re.sub(
                r"\.([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)",
                lambda m: f'[class~="{m.group(1)}"]',
                sel,
            )

        for selector in selectors_to_try:
            raw_selector = selector
            for attempt in range(2):  # at most one sanitised retry
                try:
                    elements = soup.select(selector)
                    logger.debug(
                        "Selector '%s' matched %d elements",
                        selector,
                        len(elements),
                    )
                    break  # success
                except Exception as exc:  # pragma: no cover – invalid selector
                    logger.debug("Selector '%s' raised %s", selector, exc)
                    if attempt == 0:
                        # Try sanitised version once
                        selector = _sanitize_selector(raw_selector)
                        if selector != raw_selector:
                            logger.debug(
                                "Retrying with sanitised selector '%s'",
                                selector,
                            )
                            continue
                    elements = []
                    break

            if not elements:
                continue

            # Iterate found elements
            for element in elements:
                # Accept <a> directly or any element containing one or more <a> tags
                if element.name == "a":
                    links_to_process = [cast("Tag", element)]
                    container = element.parent
                else:
                    links_to_process = element.find_all("a", href=True)
                    if not links_to_process:
                        continue
                    container = element

                # Process all links found within this element
                for link in links_to_process:
                    href_val = link.get("href")  # type: ignore[attr-defined]
                    if not href_val or not isinstance(href_val, str):
                        continue
                    href = href_val
                    text = link.get_text(strip=True)
                    if not href or not text:
                        continue

                    full_url = urljoin(base_url, href)
                    if not self._matches_pattern(href, text, full_url, pattern):
                        continue

                    # Date detection via utils
                    pub_date = (
                        du.extract_publication_date(container, pattern.date_selectors)
                        if container is not None
                        else None
                    )
                    link_data: dict[str, Any] = {
                        "url": full_url,
                        "title": text,
                        "selector_used": selector,
                    }
                    if pub_date:
                        link_data["publication_date"] = pub_date
                    extracted.append(link_data)

            logger.debug(
                "Selector '%s' produced %d valid links so far",
                selector,
                len(extracted),
            )

            # Decide whether to stop iterating after a primary selector.
            if (
                raw_selector in pattern.primary_selectors
                and pattern.estimated_items > 0
            ):
                current_unique = len({item["url"] for item in extracted})
                if current_unique >= pattern.estimated_items:
                    logger.debug(
                        "Primary selector '%s' reached estimated_items=%d; stopping",
                        raw_selector,
                        pattern.estimated_items,
                    )
                    break

        # Deduplicate by URL
        unique_links: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in extracted:
            if item["url"] not in seen:
                seen.add(item["url"])
                unique_links.append(item)

        logger.debug("Total unique links after deduplication: %d", len(unique_links))
        return unique_links

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def extract_pattern_links(
        self,
        url: str,
        *,
        force_regenerate: bool = False,
    ) -> ExtractedPattern:
        logging.info("Extracting patterns from %s", url)
        html = await self._extract_html(url)
        if not html:
            return self._empty_result(url, "HTML extraction failed")

        soup = BeautifulSoup(html, "html.parser")
        structure_analysis = self._analyze_html_structure(soup, url)

        pattern = await self._analyze_patterns_with_llm(
            url,
            html,
            structure_analysis,
            force_regenerate=force_regenerate,
        )

        links = self._extract_links_using_pattern(soup, url, pattern)

        return ExtractedPattern(
            links=links,
            total_found=len(links),
            pattern_used=pattern.pattern_type,
            confidence=pattern.confidence_score,
            base_url=url,
            pattern_analysis=pattern,
        )

    # ------------------------------------------------------------------
    # Helpers / fallbacks
    # ------------------------------------------------------------------
    def _fallback_pattern(self) -> PatternAnalysis:
        """Return a very permissive pattern used when no LLM is available."""
        return PatternAnalysis(
            pattern_type="generic_links",
            primary_selectors=["article a", "li a", "a[href]"],
            fallback_selectors=[".post a", ".entry a"],
            url_pattern_regex=".*",
            content_indicators=[".*"],
            skip_patterns=["about", "contact", "privacy", "login", "signup"],
            confidence_score=0.1,
            pattern_description="Fallback pattern – all links",
            estimated_items=0,
            date_selectors=["time", ".date", ".published", "[datetime]"],
        )

    def _empty_result(self, url: str, reason: str) -> ExtractedPattern:
        logging.warning("Returning empty result for %s – %s", url, reason)
        return ExtractedPattern(
            links=[],
            total_found=0,
            pattern_used="failed",
            confidence=0.0,
            base_url=url,
            pattern_analysis=PatternAnalysis(
                pattern_type="error",
                primary_selectors=[],
                fallback_selectors=[],
                url_pattern_regex="",
                content_indicators=[],
                skip_patterns=[],
                confidence_score=0.0,
                pattern_description=reason,
                estimated_items=0,
                date_selectors=[],
            ),
        )


# ------------------------------------------------------------------
# Convenience wrapper
# ------------------------------------------------------------------
async def extract_pattern_links(
    url: str,
    *,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """Convenience function replicating the snippet API – returns JSON-serialisable result."""
    extractor = UniversalPatternExtractor()
    result = await extractor.extract_pattern_links(
        url,
        force_regenerate=force_regenerate,
    )

    clean_items = [
        {
            "url": item["url"],
            "title": item["title"],
            "publication_date": item.get("publication_date", ""),
        }
        for item in result.links
    ]

    return {
        "extraction_info": {
            "base_url": result.base_url,
            "total_items_found": result.total_found,
            "pattern_type": result.pattern_used,
            "confidence_score": result.confidence,
        },
        "links": clean_items,
    }
