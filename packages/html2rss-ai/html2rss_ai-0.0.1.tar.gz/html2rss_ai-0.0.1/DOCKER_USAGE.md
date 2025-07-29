# 🐳 Docker Usage Guide for html2rss-ai

This guide shows how to use **html2rss-ai** with Docker for AI-powered content extraction from websites with modern CSS support.

## 🚀 Quick Start

### Prerequisites

1. **Docker** and **docker-compose** installed
2. **OpenAI API key** for GPT-4 access

### Environment Setup

Create a `.env` file in the project root:

```bash
# Required: OpenAI API key for content extraction
OPENAI_API_KEY=your-openai-api-key-here
```

### Run with Docker Compose

```bash
# Build and run the container
docker-compose up html2rss-ai

# Run in background
docker-compose up -d html2rss-ai
```

This will:
- Extract content from URLs in `config/feeds.yml`
- Save results to `data/output/` directory  
- Cache AI patterns in `pattern_cache/` for faster reuse

## 📁 Directory Structure

```
html2rss-ai/
├── data/output/           # Extracted content (JSON files)
├── pattern_cache/         # AI pattern analysis cache
├── config/feeds.yml       # Website URLs to process
├── docker-compose.yml     # Docker configuration
└── Dockerfile            # Container definition
```

## ⚙️ Configuration

### feeds.yml Configuration

Edit `config/feeds.yml` to specify websites to extract:

```yaml
feeds:
  - url: "https://example-blog.com/posts/"
    refresh_days: 7
  - url: "https://company.com/careers/"
    refresh_days: 1
  - url: "https://news-site.com/articles/"
    refresh_days: 3
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |

## 🛠️ Development Mode

### Interactive Development Container

```bash
# Start development container with shell access
docker-compose up dev
docker-compose exec dev bash

# Inside container:
uv run python examples/extract_ordep_blog.py
uv run examples/batch_extract.py
```

### Development Features

- **Live code mounting**: Changes reflected immediately
- **Full shell access**: Run any commands inside container
- **Debug mode**: Access to all development tools

## 📊 Examples

### Extract Single Website

```bash
# Extract from specific URL
docker-compose exec html2rss-ai python -c "
import asyncio
from html2rss_ai.extractor import UniversalPatternExtractor

async def extract():
    extractor = UniversalPatternExtractor()
    result = await extractor.extract_pattern_links('https://ordep.dev/posts/')
    print(f'Found {result.total_found} articles')

asyncio.run(extract())
"
```

### View Results

```bash
# Check extracted data
cat data/output/ordep.dev_$(date +%Y%m%d).json | jq '.links[] | {title, url}'

# List all extractions
ls -la data/output/
```

### Pattern Cache

```bash
# View cached patterns
ls -la pattern_cache/

# Clear cache to force re-analysis
rm -rf pattern_cache/*
```

## 🔍 Advanced Usage

### Custom Docker Build

```bash
# Build custom image
docker build -t my-html2rss-ai .

# Run with custom image
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data/output:/app/data/output \
  -v $(pwd)/pattern_cache:/app/pattern_cache \
  my-html2rss-ai
```

### Production Deployment

```bash
# Production-ready deployment
docker-compose -f docker-compose.yml up -d html2rss-ai

# Monitor logs
docker-compose logs -f html2rss-ai

# Scale processing (if needed)
docker-compose up --scale html2rss-ai=3
```

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Key Missing**
```bash
# Error: "LLM client unavailable"
# Solution: Set OPENAI_API_KEY in .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

**2. Permission Issues**
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER data/output/
sudo chown -R $USER:$USER pattern_cache/
```

**3. Playwright Issues**
```bash
# Rebuild with fresh browser installation
docker-compose build --no-cache html2rss-ai
```

**4. Memory Issues**
```bash
# Increase Docker memory limit to 4GB+
# Docker Desktop > Settings > Resources > Memory
```

### Debug Mode

```bash
# Run with debug logging
docker-compose exec html2rss-ai env PYTHONPATH=/app/src \
  python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import asyncio
from html2rss_ai.extractor import UniversalPatternExtractor

async def debug():
    extractor = UniversalPatternExtractor()
    result = await extractor.extract_pattern_links('https://example.com', force_regenerate=True)
    print(result.pattern_analysis)

asyncio.run(debug())
"
```

## 📈 Performance Tips

1. **Use caching**: Don't use `force_regenerate=True` unless needed
2. **Batch processing**: Process multiple URLs in single container run
3. **Pattern reuse**: Keep `pattern_cache/` directory between runs
4. **Memory management**: Monitor container memory usage for large sites

## 🔒 Security Notes

- **API Keys**: Never commit `.env` files to version control
- **Network**: Container only needs outbound HTTPS access
- **Volumes**: Mount only necessary directories
- **Updates**: Regularly update base images for security patches

---

## 📚 Next Steps

- Read the main [README.md](README.md) for Python API usage
- Check [examples/](examples/) for more code samples  
- See [CHANGELOG.md](CHANGELOG.md) for latest features
- Visit [PyPI Setup](PYPI_SETUP.md) for publishing information 