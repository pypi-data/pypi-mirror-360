# PyPI Release Setup Guide (English)

This guide explains how to configure **Trusted Publishing** and publish the `html2rss-ai` package to both Test PyPI and the official PyPI index.

---
## 🎯 Overview

**html2rss-ai** converts any website into structured data using AI-powered extraction with modern CSS support. Features include CSS Grid/Flexbox recognition, Tailwind CSS compatibility, and automatic CSS selector sanitization. Releases are automated via GitHub Actions using PyPI's **Trusted Publishing** for maximum security (no API tokens needed).

---
## 📋 Prerequisites

1. A **GitHub repository** where you have admin rights.
2. Accounts on both **PyPI** (`pypi.org`) and **Test PyPI** (`test.pypi.org`).
3. Local tools installed: `uv`, `git`, and the project's dev dependencies (`make dev`).

---
## 🔧 One-time Setup

### 1. Add `html2rss-ai` as a *Pending Publisher* on PyPI

Repeat the steps below **twice**—once on Test PyPI and once on Production PyPI.

1. Log in to the desired index.
2. Navigate to **Account settings → Publishing**.
3. Click **Add a new pending publisher** and fill in:
   * **PyPI project name:** `html2rss-ai`
   * **Owner:** `mazzasaverio`  *(or your PyPI username)*
   * **Repository name:** `html2rss-ai`
   * **Workflow filename:** `release.yml`
   * **Environment name:** `testpypi` *or* `pypi`

### 2. Create matching *Environments* in GitHub

In the GitHub repo:

1. **Settings → Environments → New environment**
2. Name it exactly `testpypi` (repeat for `pypi`).
3. For production (`pypi`) set protection rules such as *required reviewers* and *branch restrictions*.

---
## 🚀 Release Workflow

### Automatic (recommended)

```bash
# Bump version & trigger CI
make bump-version VERSION=0.2.0
```

The script will:
1. Ensure you're on `master/main` and the working tree is clean.
2. Run tests & linters.
3. Update `src/html2rss_ai/__init__.py` and `CHANGELOG.md`.
4. Commit, tag (`v0.2.0`), and push.
5. CI builds & publishes first to Test PyPI; once that succeeds, to PyPI.

### Manual (fallback)

```bash
make check-release          # final quality gate
vim src/html2rss_ai/__init__.py  # update __version__
vim CHANGELOG.md                # add release notes

git commit -am "🔖 Bump to 0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin master --tags     # triggers CI
```

---
## 🧪 Testing the build

Install from Test PyPI in a clean virtualenv:

```bash
python -m venv /tmp/rss-test
source /tmp/rss-test/bin/activate
pip install -i https://test.pypi.org/simple/ html2rss-ai==0.2.0

html2rss-ai --help           # or use extractor via Python
```

---
## 📊 Monitoring

* **GitHub Actions:** <https://github.com/mazzasaverio/html2rss-ai/actions>
* **PyPI:** <https://pypi.org/project/html2rss-ai/>
* **GitHub Releases:** <https://github.com/mazzasaverio/html2rss-ai/releases>

---
## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| *"Package already exists"* | Increment the version and push again. |
| *"Trusted publisher not found"* | Check that the pending publisher entry matches repo, workflow & environment names. |
| CI fails on *tests/linters* | Re-run `make quality` locally and fix issues. |
| Docker build fails | `docker build -t html2rss-ai .` locally to debug. |

---
## 🗂️ Project layout recap

```
html2rss-ai/
├── src/html2rss_ai/
│   ├── __init__.py       # version
│   ├── extractor.py      # UniversalPatternExtractor
│   └── utils/
├── tests/
├── examples/
└── pyproject.toml
```

---
## 📦 Dependencies

*Core:* `beautifulsoup4`, `openai`, `instructor`, `pydantic`, `requests`  
*Modern CSS:* Advanced CSS Grid/Flexbox recognition, Tailwind CSS support  
*AI:* GPT-4 integration with enhanced prompts for modern layouts  
*Optional:* `playwright` (for JavaScript-heavy sites)  
*Dev:* `pytest`, `ruff`, `black`, `mypy`, `pytest-asyncio`

---
All set—happy publishing!  🎉 