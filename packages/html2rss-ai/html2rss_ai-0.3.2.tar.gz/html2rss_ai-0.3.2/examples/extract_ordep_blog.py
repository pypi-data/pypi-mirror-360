#!/usr/bin/env python3
"""
Example: Extract articles from ordep.dev blog using html2rss-ai

This example demonstrates how to use the UniversalPatternExtractor to extract
blog posts from https://ordep.dev/posts/ and display them in a formatted way.
"""

import asyncio
import json
import logging
from pathlib import Path

from html2rss_ai.extractor import (
    UniversalPatternExtractor,
)
from html2rss_ai.extractor import (
    extract_pattern_links as extract_links_json,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def extract_ordep_blog():
    """Extract articles from ordep.dev blog."""

    # Initialize the extractor
    extractor = UniversalPatternExtractor()

    # URL of the blog
    blog_url = "https://blog.pragmaticengineer.com/"

    logging.info("🔍 Extracting articles from: %s", blog_url)
    logging.info("=" * 60)

    try:
        # Extract the articles
        result = await extractor.extract_pattern_links(blog_url)

        # Display extraction info
        logging.info("📊 Extraction Results:")
        logging.info("   Pattern Type: %s", result.pattern_analysis.pattern_type)
        logging.info("   Confidence Score: %.2f", result.confidence)
        logging.info("   Total Items Found: %d", result.total_found)
        logging.info("")

        # Display articles
        if result.links:
            logging.info("📝 Articles Found:")
            logging.info("-" * 60)

            for i, item in enumerate(result.links, 1):
                logging.info("%2d. %s", i, item["title"])
                logging.info("    URL: %s", item["url"])
                if item.get("publication_date"):
                    logging.info("    Date: %s", item["publication_date"])
                logging.info("")
        else:
            logging.warning("❌ No articles found!")

        # Save to JSON file
        output_file = Path("ordep_blog_articles.json")
        json_result = await extract_links_json(blog_url)

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)

        logging.info("💾 Results saved to: %s", output_file)

        # Display sample JSON structure
        logging.info("\n📋 Sample JSON structure:")
        logging.info(
            "%s...",
            json.dumps(json_result, indent=2, ensure_ascii=False)[:500],
        )

    except Exception:
        logging.exception("❌ Error extracting articles")


def display_usage_info():
    """Display usage information."""
    logging.info("🚀 html2rss-ai Example: Extract from ordep.dev blog")
    logging.info("=" * 60)
    logging.info("")
    logging.info("This example demonstrates:")
    logging.info("• How to use UniversalPatternExtractor")
    logging.info("• Extracting blog articles from a webpage")
    logging.info("• Handling the extracted data")
    logging.info("• Saving results to JSON")
    logging.info("")
    logging.info("Requirements:")
    logging.info("• OPENAI_API_KEY environment variable set")
    logging.info("• Internet connection to access ordep.dev")
    logging.info("• Required packages: html2rss-ai, openai, beautifulsoup4")
    logging.info("")


if __name__ == "__main__":
    display_usage_info()

    # Check if OpenAI API key is available
    import os

    if not os.getenv("OPENAI_API_KEY"):
        logging.warning("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        logging.warning("   Please set your OpenAI API key to use this example.")
        logging.warning("   Example: export OPENAI_API_KEY='your-api-key-here'")
        logging.warning("")

    # Run the extraction
    asyncio.run(extract_ordep_blog())
