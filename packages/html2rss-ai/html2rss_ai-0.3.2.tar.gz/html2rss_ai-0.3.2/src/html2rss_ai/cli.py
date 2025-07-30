import asyncio
import json
import logging
import os
from pathlib import Path

import typer

from html2rss_ai.extractor import UniversalPatternExtractor

app = typer.Typer()


@app.command()
def extract(
    url: str = typer.Argument(..., help="The URL to extract articles from."),
    output_dir: str = typer.Option(
        os.getenv("OUTPUT_DIR", "data/output"),
        help="Directory to save extracted JSON output files.",
    ),
    pattern_cache_dir: str = typer.Option(
        os.getenv("PATTERN_CACHE_DIR", "pattern_cache"),
        help="Directory to store pattern cache files.",
    ),
    force_regenerate: bool = typer.Option(
        False,
        "--regenerate",
        help="Force regeneration of pattern analysis.",
    ),
    save_output: bool = typer.Option(
        False,
        "--save",
        help="Save output to file instead of printing to stdout.",
    ),
):
    """
    Extracts articles from a given URL and outputs them as JSON.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not os.getenv("OPENAI_API_KEY"):
        typer.echo("Error: OPENAI_API_KEY environment variable not set.", err=True)
        raise typer.Exit(code=1)

    # Create directories if they don't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(pattern_cache_dir).mkdir(parents=True, exist_ok=True)

    extractor = UniversalPatternExtractor(cache_dir=pattern_cache_dir)
    result = asyncio.run(
        extractor.extract_pattern_links(url, force_regenerate=force_regenerate),
    )

    # Convert to JSON
    output_data = result.model_dump()

    if save_output:
        # Generate filename based on URL and date
        from datetime import datetime, timezone
        from urllib.parse import urlparse

        domain = urlparse(url).netloc.replace(".", "_").replace("/", "_")
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"{domain}_{date_str}.json"
        output_path = Path(output_dir) / filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        typer.echo(f"✅ Saved {result.total_found} items to {output_path}")
    else:
        typer.echo(json.dumps(output_data, indent=2))


if __name__ == "__main__":
    app()
