# HTML2RSS AI

AI-powered universal article extractor that automatically detects and extracts article patterns from any website using OpenAI's GPT models.

## Features

- 🤖 **AI-Powered Pattern Detection**: Automatically analyzes webpage structure to find article links
- 💾 **Smart Caching**: Saves patterns for reuse, reducing API calls and improving performance  
- 🐳 **Docker Ready**: Fully containerized with persistent storage
- 📊 **Structured Output**: Exports clean JSON with URLs, titles, and metadata
- ⚡ **Fast & Reliable**: Handles large article listings efficiently
- 🔄 **Force Regeneration**: Option to refresh patterns when websites change
- 📋 **Batch Processing**: Process multiple URLs with JSON configuration files

## Quick Start

### 🐳 Docker (Recommended)

1. **Clone and setup**:
```bash
git clone <repository-url>
cd html2rss-ai
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

2. **Create batch configuration**:
```bash
# Create config/batch_config.json with your URLs
{
  "urls": [
    {
      "url": "https://example.com/blog",
      "output_dir": "data/output/example",
      "force_regenerate": false
    }
  ]
}
```

3. **Run batch processing**:
```bash
# Process all URLs in batch_config.json
docker compose run --rm html2rss-ai

# Use custom configuration file
docker compose run --rm html2rss-ai /app/config/my_config.json
```

4. **Access results**:
- **Output files**: `./data/output/`
- **Pattern cache**: `./pattern_cache/`

### 📦 Python Package

1. **Install**:
```bash
pip install html2rss-ai
```

2. **Create a JSON configuration file** (`config.json`):
```json
{
  "urls": [
    {
      "url": "https://example.com/blog",
      "output_dir": "output",
      "force_regenerate": false
    }
  ]
}
```

3. **Run batch processing**:
```bash
export OPENAI_API_KEY="your-api-key"
python -m html2rss_ai.batch_processor config.json
```

## Usage Examples

### Basic Batch Processing
```bash
# Create configuration with Paul Graham's essays
echo '{
  "urls": [
    {
      "url": "https://www.paulgraham.com/articles.html",
      "output_dir": "data/output/paulgraham",
      "force_regenerate": false
    }
  ]
}' > config/paulgraham.json

# Process with Docker
docker compose run --rm html2rss-ai /app/config/paulgraham.json
```

### Batch Processing with JSON Configuration

**Option 1: JSON-based Batch Processing (Recommended for multiple URLs)**

1. **Create a configuration file** (`config/batch_config.json`):
```json
{
  "urls": [
    {
      "url": "https://www.paulgraham.com/articles.html",
      "output_dir": "data/output",
      "force_regenerate": false
    },
    {
      "url": "https://news.ycombinator.com",
      "output_dir": "data/output/hn",
      "force_regenerate": true
    }
  ]
}
```

2. **Run batch processing**:
```bash
# Build and run the batch processor
docker compose build html2rss-ai
docker compose run --rm html2rss-ai

# With custom configuration
docker compose run --rm html2rss-ai /app/config/my_config.json

# With error handling options
docker compose run --rm html2rss-ai /app/config/batch_config.json --continue-on-error
```

📖 **[Complete Batch Processing Guide](docs/BATCH_PROCESSING.md)** - Detailed documentation with all configuration options.

### Custom Configuration

All settings are configured through the JSON configuration file:

```json
{
  "urls": [
    {
      "url": "https://example.com/blog",
      "output_dir": "data/output/custom",
      "pattern_cache_dir": "pattern_cache/custom", 
      "force_regenerate": false,
      "save_output": true
    }
  ]
}
```

## Configuration

### Batch Processing Configuration

For processing multiple URLs, create a JSON configuration file:

```json
{
  "urls": [
    {
      "url": "https://example.com/blog",
      "output_dir": "data/output/example", 
      "pattern_cache_dir": "pattern_cache/example",
      "force_regenerate": false,
      "save_output": true
    }
  ]
}
```

See [docs/BATCH_PROCESSING.md](docs/BATCH_PROCESSING.md) for complete configuration options.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OUTPUT_DIR` | `data/output` | Directory for JSON output files |
| `PATTERN_CACHE_DIR` | `pattern_cache` | Directory for cached patterns |

### Batch Processor Arguments

```bash
# See all available options
docker compose run --rm html2rss-ai --help

# Main arguments:
config_file                Path to JSON configuration file (required)
--continue-on-error        Continue processing even if some URLs fail  
--log-level LEVEL          Set logging level (DEBUG, INFO, WARNING, ERROR)
```

### Docker Environment

The Docker setup uses:
- **Host directories**: `./data/output/` and `./pattern_cache/`
- **Container paths**: `/app/data/output/` and `/app/pattern_cache/`
- **User mapping**: Runs as UID/GID 1000 to avoid permission issues

## Output Format

```json
{
  "links": [
    {
      "url": "https://example.com/article-1",
      "title": "Article Title",
      "selector_used": "h2 > a"
    }
  ],
  "total_found": 42,
  "pattern_used": "articles",
  "confidence": 0.95,
  "base_url": "https://example.com/blog",
  "pattern_analysis": {
    "pattern_type": "articles",
    "primary_selectors": ["h2 > a"],
    "confidence_score": 0.95
  }
}
```

## Development

### Build Docker Image
```bash
# Build with Docker Compose (creates html2rss-ai:latest)
docker compose build

# Or build directly with custom tag
docker build -t html2rss-ai:v1.0 .
```

### Install for Development
```bash
pip install -e ".[playwright]"
playwright install chromium
```

### Run Tests
```bash
pytest tests/
```

## Requirements

- **OpenAI API Key**: GPT-3.5/4 access for pattern analysis
- **Docker** (recommended) or **Python 3.8+**
- **Internet connection**: For webpage scraping and API calls

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- 🐛 **Issues**: Report bugs via GitHub Issues
- 💡 **Features**: Suggest improvements via GitHub Discussions
- 📧 **Contact**: [Your contact info]

---

