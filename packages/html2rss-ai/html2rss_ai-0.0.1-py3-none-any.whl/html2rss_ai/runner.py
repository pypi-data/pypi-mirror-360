# mypy: ignore-errors
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from html2rss_ai.extractor import UniversalPatternExtractor

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("config/feeds.yml")
OUTPUT_DIR = Path("data/output")
PATTERN_CACHE_DIR = Path("config/pattern_cache")
PATTERN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_config(config_file: Path = CONFIG_PATH) -> list[dict[str, Any]]:
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    with config_file.open("r", encoding="utf-8") as fp:
        cfg = yaml.safe_load(fp) or {}
    return cfg.get("feeds", [])


def _should_regenerate(cache_file: Path, refresh_days: int) -> bool:
    if not cache_file.exists():
        return True
    age = datetime.now(timezone.utc) - datetime.fromtimestamp(
        cache_file.stat().st_mtime,
        tz=timezone.utc,
    )
    return age > timedelta(days=refresh_days)


def _result_to_json(result) -> dict[str, Any]:
    """Convert ExtractedPattern result into JSON-serialisable dict."""
    items = [
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
        "links": items,
    }


async def run_batch(config_file: Path | None = None) -> None:
    """Iterate over all feeds in YAML and write JSON outputs under data/output/."""

    feeds = _load_config(config_file or CONFIG_PATH)
    extractor = UniversalPatternExtractor(cache_dir=str(PATTERN_CACHE_DIR))

    for feed in feeds:
        url: str = feed["url"]
        refresh_days: int = int(feed.get("refresh_days", 7))
        cache_path = Path(extractor._get_cache_file_path(url))  # type: ignore[attr-defined]
        force = _should_regenerate(cache_path, refresh_days)
        logger.info("Processing %s (force_regenerate=%s)", url, force)

        result = await extractor.extract_pattern_links(url, force_regenerate=force)

        # Compose output path: domain_YYYYMMDD.json
        domain = Path(urlparse(url).netloc).as_posix().replace("/", "_")
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        out_file = OUTPUT_DIR / f"{domain}_{date_str}.json"

        json_data = _result_to_json(result)
        json_data["generation_date"] = datetime.now(timezone.utc).isoformat()

        with out_file.open("w", encoding="utf-8") as fp:
            json.dump(json_data, fp, indent=2, ensure_ascii=False)
        logger.info("Written %d items to %s", result.total_found, out_file)
