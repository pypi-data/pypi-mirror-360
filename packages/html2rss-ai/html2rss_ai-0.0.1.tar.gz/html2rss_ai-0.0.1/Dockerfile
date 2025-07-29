# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Install system dependencies including Playwright requirements
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code first (needed for editable install)
COPY . .

# Install dependencies and the package
RUN uv sync --frozen

# Install Playwright and browsers (optional, for JavaScript sites)
RUN uv run playwright install chromium --with-deps || echo "Playwright installation failed, continuing without JS support"

# Create output and cache directories
RUN mkdir -p output pattern_cache

# Set environment variables for html2rss-ai
ENV PYTHONPATH=/app/src
ENV OPENAI_API_KEY=""

# Default command - run batch extraction example
ENTRYPOINT ["uv", "run", "python", "examples/batch_extract.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "from html2rss_ai import __version__; print(__version__)" || exit 1

# Labels for better container management  
LABEL name="html2rss-ai"
LABEL version="2.0.0"
LABEL description="🚀 AI-powered web scraping with modern CSS support. Extract content using GPT-4, handles CSS Grid/Flexbox layouts automatically."
LABEL maintainer="Saverio Mazza <saverio3107@gmail.com>" 