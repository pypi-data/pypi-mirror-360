#!/usr/bin/env python3
"""Batch processor that reads URLs and parameters from a JSON file and processes them in a loop."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from html2rss_ai.extractor import UniversalPatternExtractor
from html2rss_ai.utils.config_loader import load_batch_config
from html2rss_ai.utils.logger_config import setup_logging

logger = logging.getLogger(__name__)


async def process_single_url(
    url_config: dict[str, Any],
    extractor: UniversalPatternExtractor,
) -> bool:
    """Process a single URL configuration."""
    try:
        url = url_config.get("url")
        if not url:
            logger.error("URL is required for each configuration")
            return False

        output_dir = url_config.get(
            "output_dir",
            os.getenv("OUTPUT_DIR", "data/output"),
        )
        pattern_cache_dir = url_config.get(
            "pattern_cache_dir",
            os.getenv("PATTERN_CACHE_DIR", "pattern_cache"),
        )
        force_regenerate = url_config.get("force_regenerate", False)
        save_output = url_config.get(
            "save_output",
            True,
        )

        logger.info("Processing URL: %s", url)
        logger.info("  Output dir: %s", output_dir)
        logger.info("  Pattern cache dir: %s", pattern_cache_dir)
        logger.info("  Force regenerate: %s", force_regenerate)
        logger.info("  Save output: %s", save_output)

        # Create directories if they don't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(pattern_cache_dir).mkdir(parents=True, exist_ok=True)

        # Update extractor cache directory if different
        if extractor.cache_dir != pattern_cache_dir:
            extractor.cache_dir = pattern_cache_dir
            Path(extractor.cache_dir).mkdir(parents=True, exist_ok=True)

        # Extract using the same logic as CLI
        result = await extractor.extract_pattern_links(
            url,
            force_regenerate=force_regenerate,
        )

        # Convert to JSON and clean up for final output
        output_data = result.model_dump()
        if "links" in output_data:
            output_data["items"] = [
                {
                    "url": item["url"],
                    "title": item["title"],
                    "publication_date": item.get("publication_date", ""),
                }
                for item in output_data["links"]
            ]
            del output_data["links"]  # Remove original list with selectors

        if save_output:
            # Generate filename based on URL and date
            domain = urlparse(url).netloc.replace(".", "_").replace("/", "_")
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{date_str}.json"
            output_path = Path(output_dir) / filename

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info("✅ Saved %d items to %s", result.total_found, output_path)
        else:
            sys.stdout.write(json.dumps(output_data, indent=2) + "\n")

        return True

    except Exception as e:
        logger.error("Error processing URL %s: %s", url_config.get("url", "unknown"), e)
        return False


async def run_batch_processor(config_file: str, continue_on_error: bool = True) -> None:
    """Run the batch processor with the given configuration file."""

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    url_configs = load_batch_config(config_file)

    extractor = UniversalPatternExtractor(cache_dir="pattern_cache")

    successful = 0
    failed = 0

    for i, url_config in enumerate(url_configs, 1):
        logger.info("Processing %d/%d", i, len(url_configs))

        success = await process_single_url(url_config, extractor)

        if success:
            successful += 1
        else:
            failed += 1
            if not continue_on_error:
                logger.error("Stopping due to error (continue_on_error=False)")
                break

        if i < len(url_configs):
            await asyncio.sleep(1)

    logger.info(
        "Batch processing completed: %d successful, %d failed",
        successful,
        failed,
    )

    if failed > 0 and not continue_on_error:
        sys.exit(1)


def main():
    """Main entry point for the batch processor."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process URLs from JSON configuration",
    )
    parser.add_argument("config_file", help="Path to JSON configuration file")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if some URLs fail",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level",
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    asyncio.run(run_batch_processor(args.config_file, args.continue_on_error))


if __name__ == "__main__":
    main()
