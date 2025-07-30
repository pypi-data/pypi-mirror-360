#!/usr/bin/env python3
"""Example script showing how to run batch processing with JSON configuration."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import the batch processor
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from html2rss_ai.batch_processor import run_batch_processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main():
    """Run batch processing with the example configuration."""
    # Path to the configuration file
    config_file = Path(__file__).parent.parent / "config" / "batch_config.json"

    if not config_file.exists():
        logging.error("Configuration file not found: %s", config_file)
        logging.error("Please create a batch_config.json file in the config directory.")
        sys.exit(1)

    # Check for required environment variable
    if not os.getenv("OPENAI_API_KEY"):
        logging.error("Error: OPENAI_API_KEY environment variable not set.")
        logging.error(
            "Please set your OpenAI API key before running the batch processor.",
        )
        sys.exit(1)

    logging.info("Starting batch processing with configuration: %s", config_file)
    logging.info("Press Ctrl+C to stop the processing...")

    try:
        await run_batch_processor(str(config_file), continue_on_error=True)
        logging.info("Batch processing completed successfully!")
    except KeyboardInterrupt:
        logging.info("\nBatch processing interrupted by user.")
    except Exception:
        logging.exception("Error during batch processing")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
