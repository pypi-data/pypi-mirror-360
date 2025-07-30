import json
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


def load_batch_config(config_file: str) -> list[dict[str, Any]]:
    """Load batch configuration from JSON file."""
    try:
        with open(config_file, encoding="utf-8") as f:
            config: dict[str, Any] = json.load(f)

        urls = config.get("urls")
        if not isinstance(urls, list):
            raise TypeError("JSON file must contain 'urls' array")

        return urls
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_file)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in configuration file: %s", e)
        sys.exit(1)
    except (TypeError, ValueError) as e:
        logger.error("Error loading configuration: %s", e)
        sys.exit(1)
