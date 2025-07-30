# Batch Processing with JSON Configuration

This document explains how to use the new batch processing feature that allows you to process multiple URLs with different parameters using a JSON configuration file.

## Overview

The batch processing feature extends the existing single-URL processing capability to handle multiple URLs in a loop, each with its own configuration parameters. This is useful for:

- Processing multiple websites with different settings
- Running scheduled extractions for multiple sources
- Bulk processing with different output directories and cache settings

## JSON Configuration Format

Create a JSON file with the following structure:

```json
{
  "urls": [
    {
      "url": "https://example.com/blog",
      "output_dir": "data/output",
      "pattern_cache_dir": "pattern_cache",
      "force_regenerate": false,
      "save_output": true
    },
    {
      "url": "https://another-site.com/articles",
      "output_dir": "data/output/another-site",
      "pattern_cache_dir": "pattern_cache/another-site",
      "force_regenerate": true,
      "save_output": true
    }
  ]
}
```

### Parameters

Each URL configuration supports the following parameters:

- **`url`** (required): The URL to extract articles from
- **`output_dir`** (optional): Directory to save extracted JSON output files (default: "data/output")
- **`pattern_cache_dir`** (optional): Directory to store pattern cache files (default: "pattern_cache")
- **`force_regenerate`** (optional): Force regeneration of pattern analysis (default: false)
- **`save_output`** (optional): Save output to file instead of printing to stdout (default: true for batch processing)

## Usage Options

### 1. Using Docker (Recommended)

Build and run the batch processing container:

```bash
# Build the image
docker-compose build html2rss-ai

# Run with the default configuration
docker-compose run --rm html2rss-ai

# Run with a custom configuration file
docker-compose run --rm html2rss-ai /app/config/my_custom_config.json

# Run with additional options
docker-compose run --rm html2rss-ai /app/config/batch_config.json --continue-on-error --log-level DEBUG
```

### 2. Using the Python Script Directly

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run the batch processor directly
python src/html2rss_ai/batch_processor.py config/batch_config.json

# Run with options
python src/html2rss_ai/batch_processor.py config/batch_config.json --continue-on-error --log-level INFO
```

### 3. Using the Example Script

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run the example script
python examples/run_batch_json.py
```

## Command Line Options

The batch processor supports the following command line options:

- **`config_file`**: Path to the JSON configuration file (required)
- **`--continue-on-error`**: Continue processing even if some URLs fail (optional)
- **`--log-level`**: Set the logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)

## Docker Compose Configuration

The `docker-compose.yml` file includes the `html2rss-ai` service configured for batch processing:

```yaml
html2rss-ai:
  image: html2rss-ai
  container_name: html2rss-ai
  build:
    context: .
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - OUTPUT_DIR=/app/data/output
    - PATTERN_CACHE_DIR=/app/pattern_cache
  volumes:
    - ./data/output:/app/data/output
    - ./pattern_cache:/app/pattern_cache
    - ./config:/app/config:ro
  command: ["/app/config/batch_config.json", "--continue-on-error"]
```

## Output

Each processed URL will generate a JSON file in the specified output directory with the following naming pattern:
```
{domain}_{YYYYMMDD_HHMMSS}.json
```

For example:
- `example_com_20240101_143000.json`
- `news_ycombinator_com_20240101_143015.json`

## Error Handling

- If `--continue-on-error` is specified, the batch processor will continue to the next URL even if one fails
- Without this flag, the processor will stop at the first error
- Failed URLs are logged with error details
- A summary is provided at the end showing successful vs failed processing counts

## Environment Variables

Make sure to set the following environment variables:

- **`OPENAI_API_KEY`**: Your OpenAI API key (required)
- **`OUTPUT_DIR`**: Default output directory (optional, can be overridden per URL)
- **`PATTERN_CACHE_DIR`**: Default pattern cache directory (optional, can be overridden per URL)

## Example Configuration Files

### Basic Configuration
```json
{
  "urls": [
    {
      "url": "https://www.paulgraham.com/articles.html"
    },
    {
      "url": "https://news.ycombinator.com"
    }
  ]
}
```

### Advanced Configuration with Custom Settings
```json
{
  "urls": [
    {
      "url": "https://tech-blog.com/posts",
      "output_dir": "data/output/tech-blog",
      "pattern_cache_dir": "pattern_cache/tech-blog",
      "force_regenerate": false,
      "save_output": true
    },
    {
      "url": "https://news-site.com/articles",
      "output_dir": "data/output/news",
      "pattern_cache_dir": "pattern_cache/news",
      "force_regenerate": true,
      "save_output": true
    }
  ]
}
```

## Tips

1. **Rate Limiting**: The batch processor includes a 1-second delay between requests to be respectful to target websites
2. **Cache Management**: Use different `pattern_cache_dir` values for different sites if they have very different structures
3. **Output Organization**: Use different `output_dir` values to organize extracted data by source
4. **Force Regeneration**: Use `force_regenerate: true` sparingly, as it will re-analyze patterns even if cached versions exist 