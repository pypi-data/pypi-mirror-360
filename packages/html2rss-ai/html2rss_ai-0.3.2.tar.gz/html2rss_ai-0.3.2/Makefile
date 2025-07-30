# HTML2RSS AI - Makefile
# Provides convenient commands for development and usage

.PHONY: help install dev test lint format clean docker-build docker-run batch-build batch-run quality check

# Default target
help: ## Show this help message
	@echo "🤖 HTML2RSS AI - Available Commands"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Setup
install: ## Install dependencies with uv
	@echo "📦 Installing dependencies..."
	uv sync

dev: install ## Install development dependencies
	@echo "🛠️  Installing development dependencies..."
	uv sync --all-extras
	uv run playwright install chromium

# Code Quality
format: ## Format code with black and ruff
	@echo "💄 Formatting code..."
	uv run black src/ tests/ examples/
	uv run ruff check --fix src/ tests/ examples/

lint: ## Run linters
	@echo "🔍 Running linters..."
	uv run ruff check src/ tests/ examples/
	uv run mypy src/ --ignore-missing-imports

test: ## Run tests
	@echo "🧪 Running tests..."
	uv run pytest

check: format lint test ## Run all quality checks
	@echo "✅ All quality checks passed!"

quality: clean-cache format lint test ## Full quality check with cache cleanup
	@echo "✅ Full quality check completed!"

# Environment Setup
check-env: ## Check if required environment variables are set
	@echo "🔍 Checking environment variables..."
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ OPENAI_API_KEY is not set"; \
		echo "Please set your OpenAI API key:"; \
		echo "export OPENAI_API_KEY='your-api-key-here'"; \
		exit 1; \
	else \
		echo "✅ OPENAI_API_KEY is set"; \
	fi

env-example: ## Create example environment file
	@echo "📝 Creating example environment file..."
	@echo "# OpenAI Configuration (Required)" > .env.example
	@echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env.example
	@echo "" >> .env.example
	@echo "# Optional Configuration" >> .env.example
	@echo "OUTPUT_DIR=data/output" >> .env.example
	@echo "PATTERN_CACHE_DIR=pattern_cache" >> .env.example
	@echo "✅ Created .env.example file"

# Single URL Processing
extract: check-env ## Extract articles from a single URL (usage: make extract URL=https://example.com)
	@if [ -z "$(URL)" ]; then \
		echo "❌ Please specify URL. Usage: make extract URL=https://example.com"; \
		exit 1; \
	fi
	@echo "🔍 Extracting articles from $(URL)..."
	uv run html2rss-ai --save "$(URL)"

extract-print: check-env ## Extract and print to stdout (usage: make extract-print URL=https://example.com)
	@if [ -z "$(URL)" ]; then \
		echo "❌ Please specify URL. Usage: make extract-print URL=https://example.com"; \
		exit 1; \
	fi
	@echo "🔍 Extracting articles from $(URL)..."
	uv run html2rss-ai "$(URL)"

extract-force: check-env ## Extract with forced pattern regeneration (usage: make extract-force URL=https://example.com)
	@if [ -z "$(URL)" ]; then \
		echo "❌ Please specify URL. Usage: make extract-force URL=https://example.com"; \
		exit 1; \
	fi
	@echo "🔍 Extracting articles from $(URL) with forced regeneration..."
	uv run html2rss-ai --save --regenerate "$(URL)"

# Batch Processing
batch-config: ## Create example batch configuration file
	@echo "📝 Creating example batch configuration..."
	mkdir -p config
	@echo '{\n  "urls": [\n    {\n      "url": "https://www.paulgraham.com/articles.html",\n      "output_dir": "data/output",\n      "force_regenerate": false\n    },\n    {\n      "url": "https://news.ycombinator.com",\n      "output_dir": "data/output/hn",\n      "force_regenerate": true\n    }\n  ]\n}' > config/batch_config.json
	@echo "✅ Created config/batch_config.json"

batch-run: check-env ## Run batch processing with JSON config (usage: make batch-run CONFIG=config/batch_config.json)
	@CONFIG_FILE="$(or $(CONFIG),config/batch_config.json)"; \
	if [ ! -f "$$CONFIG_FILE" ]; then \
		echo "❌ Configuration file not found: $$CONFIG_FILE"; \
		echo "Run 'make batch-config' to create an example configuration"; \
		exit 1; \
	fi; \
	echo "🔄 Running batch processing with $$CONFIG_FILE..."; \
	python src/html2rss_ai/batch_processor.py "$$CONFIG_FILE" --continue-on-error

batch-example: check-env batch-config ## Create example config and run batch processing
	@echo "🔄 Running batch processing example..."
	python src/html2rss_ai/batch_processor.py config/batch_config.json --continue-on-error

# Docker Commands
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker compose build html2rss-ai

docker-run: ## Run batch processing with Docker (usage: make docker-run CONFIG=config/batch_config.json)
	@CONFIG_FILE="$(or $(CONFIG),config/batch_config.json)"; \
	if [ ! -f "$$CONFIG_FILE" ]; then \
		echo "❌ Configuration file not found: $$CONFIG_FILE"; \
		echo "Run 'make batch-config' to create an example configuration"; \
		exit 1; \
	fi; \
	echo "🐳 Running batch processing with Docker using $$CONFIG_FILE..."; \
	docker compose run --rm html2rss-ai "/app/$$CONFIG_FILE" --continue-on-error

docker-example: docker-build batch-config ## Build image, create config, and run batch processing with Docker
	@echo "🐳 Running batch processing example with Docker..."
	docker compose run --rm html2rss-ai /app/config/batch_config.json --continue-on-error

# Examples
example-paulgraham: ## Extract Paul Graham's essays
	@echo "📝 Extracting Paul Graham's essays..."
	$(MAKE) extract URL=https://www.paulgraham.com/articles.html

example-hn: ## Extract Hacker News articles
	@echo "📰 Extracting Hacker News articles..."
	$(MAKE) extract URL=https://news.ycombinator.com

example-batch: batch-example ## Run batch processing example

# Docker Examples  
docker-example-pg: ## Run Docker with Paul Graham configuration
	@echo "🐳 Running Docker with Paul Graham configuration..."
	$(MAKE) docker-run CONFIG=config/batch_config.json

# Cleanup
clean-cache: ## Clean up cache files
	@echo "🧹 Cleaning cache files..."
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf pattern_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-output: ## Clean up output files
	@echo "🧹 Cleaning output files..."
	rm -rf data/output/*

clean: clean-cache clean-output ## Clean up cache and output files
	@echo "🧹 Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/

clean-docker: ## Clean up Docker images and containers
	@echo "🐳 Cleaning up Docker..."
	docker compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Development
dev-setup: dev env-example ## Setup development environment
	@echo "🛠️  Development environment setup complete!"
	@echo "Don't forget to:"
	@echo "1. Copy .env.example to .env and add your OpenAI API key"
	@echo "2. Run 'make check-env' to verify setup"
	@echo "3. Run 'make example-paulgraham' to test the extraction"

quick-start: install check-env batch-config ## Quick start: install, check env, and create batch config
	@echo "🎉 Quick start completed successfully!"
	@echo "Try running:"
	@echo "- make example-paulgraham (local processing)"
	@echo "- make batch-example (local batch processing)"
	@echo "- make docker-example (Docker batch processing)"
	@echo "- make docker-run CONFIG=config/batch_config.json (Docker with custom config)"

# Information
show-config: ## Show current configuration
	@echo "📋 Current Configuration:"
	@echo "OPENAI_API_KEY: $(if $(OPENAI_API_KEY),✅ Set,❌ Not set)"
	@echo "OUTPUT_DIR: $(or $(OUTPUT_DIR),data/output (default))"
	@echo "PATTERN_CACHE_DIR: $(or $(PATTERN_CACHE_DIR),pattern_cache (default))"
	@echo "PWD: $(PWD)"
	@echo "Batch config exists: $(if $(wildcard config/batch_config.json),✅ Yes,❌ No - run 'make batch-config')"

# Build and Release
build: check ## Build the package
	@echo "📦 Building package..."
	uv build

publish: build ## Publish to PyPI (requires authentication)
	@echo "🚀 Publishing to PyPI..."
	uv publish

bump-version: check ## Bump version and create release (usage: make bump-version VERSION=0.1.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Please specify VERSION. Usage: make bump-version VERSION=0.1.0"; \
		exit 1; \
	fi
	./scripts/release.sh $(VERSION)

release: bump-version publish ## Create a new release and publish to PyPI
	@echo "✅ Release $(VERSION) published successfully!" 