# HTML2RSS AI

AI-powered universal article extractor that automatically detects and extracts article patterns from any website using OpenAI's GPT models.

## Features

- 🤖 **AI-Powered Pattern Detection**: Automatically analyzes webpage structure to find article links
- 💾 **Smart Caching**: Saves patterns for reuse, reducing API calls and improving performance  
- 🐳 **Docker Ready**: Fully containerized with persistent storage
- 📊 **Structured Output**: Exports clean JSON with URLs, titles, and metadata
- ⚡ **Fast & Reliable**: Handles large article listings efficiently
- 🔄 **Force Regeneration**: Option to refresh patterns when websites change

## Quick Start

### 🐳 Docker (Recommended)

1. **Clone and setup**:
```bash
git clone <repository-url>
cd html2rss-ai
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

2. **Extract articles**:
```bash
# Save articles to JSON file
docker compose run --rm html2rss-ai --save "https://example.com/blog"

# Print JSON to stdout (no file saved)
docker compose run --rm html2rss-ai "https://example.com/blog"

# Force pattern regeneration
docker compose run --rm html2rss-ai --save --regenerate "https://example.com/blog"
```

3. **Access results**:
- **Output files**: `./data/output/`
- **Pattern cache**: `./pattern_cache/`

### 📦 Python Package

1. **Install**:
```bash
pip install html2rss-ai
```

2. **Use**:
```bash
export OPENAI_API_KEY="your-api-key"
html2rss-ai --save "https://example.com/blog"
```

## Usage Examples

### Basic Extraction
```bash
# Extract Paul Graham's essays
docker compose run --rm html2rss-ai --save "https://www.paulgraham.com/articles.html"
```

### Batch Processing
```bash
# Multiple sites
for url in "https://blog.example.com" "https://news.example.org"; do
  docker compose run --rm html2rss-ai --save "$url"
done
```

### Custom Directories

**Option 1: CLI Arguments (Recommended)**
```bash
# Docker with custom paths
docker compose run --rm html2rss-ai \
  --output-dir /app/custom/output \
  --pattern-cache-dir /app/custom/cache \
  --save "https://example.com"

# Local Python with custom paths  
html2rss-ai \
  --output-dir ./my-output \
  --pattern-cache-dir ./my-cache \
  --save "https://example.com"
```

**Option 2: Environment Variables**
```bash
# Override default paths via environment
OUTPUT_DIR=/custom/output PATTERN_CACHE_DIR=/custom/cache \
  html2rss-ai --save "https://example.com"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OUTPUT_DIR` | `data/output` | Directory for JSON output files |
| `PATTERN_CACHE_DIR` | `pattern_cache` | Directory for cached patterns |

### CLI Arguments

```bash
# See all available options
docker compose run --rm html2rss-ai --help

# Main arguments:
--output-dir TEXT           Directory to save extracted JSON output files
--pattern-cache-dir TEXT    Directory to store pattern cache files  
--regenerate               Force regeneration of pattern analysis
--save                     Save output to file instead of printing to stdout
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

*Powered by OpenAI GPT and built with ❤️ for the RSS community.*
