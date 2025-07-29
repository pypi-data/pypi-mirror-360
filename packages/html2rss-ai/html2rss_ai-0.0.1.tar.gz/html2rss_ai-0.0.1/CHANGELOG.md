# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-27

### Added
- 🚀 **Complete package restructure**: Transformed from `url2md4ai` to `html2rss-ai`
- 🧠 **LLM-powered article extraction**: Uses OpenAI GPT models for intelligent website analysis
- 📡 **RSS & Atom feed generation**: Creates standard-compliant feeds from extracted articles
- 🎯 **Smart content detection**: Automatically identifies article links and extracts metadata
- 💾 **Intelligent caching**: Saves extraction rules for faster subsequent runs
- 🎭 **Playwright support**: Optional dynamic content handling for JavaScript-heavy sites
- ⚡ **CLI interface**: Command-line tool for easy feed generation
- 📚 **Python library**: Comprehensive API for programmatic use
- 🏗️ **SOLID architecture**: Clean separation of concerns with modular design

### Core Components
- `SmartArticleExtractor`: Main extraction class with LLM analysis
- `Article`, `ExtractionRules`, `SiteStructureAnalysis`: Pydantic data models
- RSS 2.0 and Atom 1.0 generators with proper XML formatting
- CLI with configurable options and environment variable support
- Comprehensive error handling and logging

### Features
- Automatic website structure analysis using GPT models
- CSS selector generation for precise content extraction
- Date, author, excerpt, and tag extraction
- Configurable feed metadata and formatting
- Fallback extraction strategies for robust operation
- Support for both static and dynamic content

### Dependencies
- `requests`: HTTP client for web scraping
- `beautifulsoup4`: HTML parsing and manipulation
- `openai`: OpenAI API client for LLM analysis
- `pydantic`: Data validation and serialization
- `click`: Command-line interface framework
- `lxml`: XML processing for feed generation
- `playwright` (optional): Dynamic content rendering

### Breaking Changes
- 🔥 **Complete API change**: All previous `url2md4ai` functionality removed
- 🔄 **New package name**: `html2rss-ai` instead of `url2md4ai`
- 📦 **New module structure**: Organized into `core`, `generators`, and `utils`
- 🎯 **Different purpose**: RSS/Atom generation instead of markdown conversion

### Migration Guide
This is a complete rewrite. Previous users of `url2md4ai` will need to:
1. Uninstall the old package: `pip uninstall url2md4ai`
2. Install the new package: `pip install html2rss-ai`
3. Update imports and code to use the new API
4. Set up OpenAI API key for LLM functionality

### Documentation
- 📖 Comprehensive README with examples and API reference
- 🛠️ Example usage script demonstrating all features
- 🧪 Basic test suite covering core functionality
- 📝 Type hints throughout for better development experience

---

## Previous Versions

All previous versions were part of the `url2md4ai` package and are not compatible with this release.
This represents a complete architectural shift towards intelligent RSS feed generation. 