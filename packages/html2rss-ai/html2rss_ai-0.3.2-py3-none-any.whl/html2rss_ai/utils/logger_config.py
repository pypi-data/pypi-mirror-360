import logging


def setup_logging(log_level: str = "INFO") -> None:
    """Set up basic logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
