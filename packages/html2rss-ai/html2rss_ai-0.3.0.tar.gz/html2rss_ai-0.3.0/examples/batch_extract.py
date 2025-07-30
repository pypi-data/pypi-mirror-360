#!/usr/bin/env python3
"""Run batch feed extraction based on config/feeds.yml."""

import asyncio
import logging

from html2rss_ai.runner import run_batch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    asyncio.run(run_batch()) 