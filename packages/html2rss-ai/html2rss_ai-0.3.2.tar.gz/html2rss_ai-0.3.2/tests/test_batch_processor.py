import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from html2rss_ai.batch_processor import (
    load_batch_config,
    process_single_url,
    run_batch_processor,
)
from html2rss_ai.extractor import UniversalPatternExtractor
from html2rss_ai.schemas import ExtractedPattern, PatternAnalysis


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "urls": [
            {
                "url": "https://example.com/blog",
                "output_dir": "data/output/example",
                "pattern_cache_dir": "pattern_cache/example",
                "force_regenerate": False,
                "save_output": True,
            },
            {
                "url": "https://test.com/articles",
                "output_dir": "data/output/test",
                "force_regenerate": True,
                "save_output": True,
            },
        ],
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_config, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    Path(temp_file).unlink()


@pytest.fixture
def mock_extracted_pattern():
    """Mock ExtractedPattern for testing."""
    return ExtractedPattern(
        links=[
            {
                "url": "https://example.com/article1",
                "title": "Test Article 1",
                "selector_used": "h2 > a",
            },
            {
                "url": "https://example.com/article2",
                "title": "Test Article 2",
                "selector_used": "h2 > a",
            },
        ],
        total_found=2,
        pattern_used="articles",
        confidence=0.95,
        base_url="https://example.com/blog",
        pattern_analysis=PatternAnalysis(
            pattern_type="articles",
            primary_selectors=["h2 > a"],
            fallback_selectors=[],
            url_pattern_regex=".*",
            content_indicators=[],
            skip_patterns=[],
            confidence_score=0.95,
            pattern_description="test pattern",
            estimated_items=2,
            date_selectors=[],
        ),
    )


class TestLoadBatchConfig:
    """Test batch configuration loading."""

    def test_load_valid_config(self, temp_config_file, sample_config):
        """Test loading a valid configuration file."""
        result = load_batch_config(temp_config_file)

        assert result == sample_config["urls"]
        assert len(result) == 2
        assert result[0]["url"] == "https://example.com/blog"
        assert result[1]["url"] == "https://test.com/articles"

    def test_load_missing_file(self):
        """Test loading a non-existent configuration file."""
        with pytest.raises(SystemExit):
            load_batch_config("non_existent_file.json")

    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json")
            temp_file = f.name

        try:
            with pytest.raises(SystemExit):
                load_batch_config(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_load_missing_urls_key(self):
        """Test loading a config file without 'urls' key."""
        config = {"feeds": []}  # Wrong key

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_file = f.name

        try:
            with pytest.raises(SystemExit):
                load_batch_config(temp_file)
        finally:
            Path(temp_file).unlink()


class TestProcessSingleUrl:
    """Test single URL processing."""

    @pytest.mark.asyncio
    async def test_process_valid_url(self, mock_extracted_pattern):
        """Test processing a valid URL configuration."""
        url_config = {
            "url": "https://example.com/blog",
            "output_dir": "test_output",
            "pattern_cache_dir": "test_cache",
            "force_regenerate": False,
            "save_output": False,  # Don't save to avoid file I/O in tests
        }

        mock_extractor = MagicMock(spec=UniversalPatternExtractor)
        mock_extractor.extract_pattern_links = AsyncMock(
            return_value=mock_extracted_pattern,
        )
        mock_extractor.cache_dir = "test_cache"

        with patch("html2rss_ai.batch_processor.Path") as mock_path:
            mock_path.return_value.mkdir = MagicMock()

            result = await process_single_url(url_config, mock_extractor)

            assert result is True
            mock_extractor.extract_pattern_links.assert_called_once_with(
                "https://example.com/blog",
                force_regenerate=False,
            )

    @pytest.mark.asyncio
    async def test_process_url_missing_url_key(self):
        """Test processing a configuration without URL."""
        url_config = {
            "output_dir": "test_output",
            "force_regenerate": False,
            "save_output": False,
        }

        mock_extractor = MagicMock(spec=UniversalPatternExtractor)

        result = await process_single_url(url_config, mock_extractor)

        assert result is False

    @pytest.mark.asyncio
    async def test_process_url_with_defaults(self, mock_extracted_pattern):
        """Test processing a URL with default parameters."""
        url_config = {"url": "https://example.com/blog"}

        mock_extractor = MagicMock(spec=UniversalPatternExtractor)
        mock_extractor.extract_pattern_links = AsyncMock(
            return_value=mock_extracted_pattern,
        )
        mock_extractor.cache_dir = "pattern_cache"

        with patch.dict(os.environ, {}, clear=True):
            with patch("html2rss_ai.batch_processor.Path") as mock_path:
                mock_path.return_value.mkdir = MagicMock()

                result = await process_single_url(url_config, mock_extractor)

                assert result is True
                mock_extractor.extract_pattern_links.assert_called_once_with(
                    "https://example.com/blog",
                    force_regenerate=False,
                )

    @pytest.mark.asyncio
    async def test_process_url_with_save_output(self, mock_extracted_pattern):
        """Test processing a URL with file saving."""
        url_config = {
            "url": "https://example.com/blog",
            "output_dir": "test_output",
            "save_output": True,
        }

        mock_extractor = MagicMock(spec=UniversalPatternExtractor)
        mock_extractor.extract_pattern_links = AsyncMock(
            return_value=mock_extracted_pattern,
        )
        mock_extractor.cache_dir = "pattern_cache"

        with patch("html2rss_ai.batch_processor.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.mkdir = MagicMock()
            mock_path_instance.open = MagicMock()

            result = await process_single_url(url_config, mock_extractor)

            assert result is True
            # Verify mkdir was called for output directory
            mock_path_instance.mkdir.assert_called()

    @pytest.mark.asyncio
    async def test_process_url_exception_handling(self):
        """Test handling of exceptions during URL processing."""
        url_config = {"url": "https://example.com/blog", "save_output": False}

        mock_extractor = MagicMock(spec=UniversalPatternExtractor)
        mock_extractor.extract_pattern_links = AsyncMock(
            side_effect=Exception("Test error"),
        )
        mock_extractor.cache_dir = "pattern_cache"

        with patch("html2rss_ai.batch_processor.Path") as mock_path:
            mock_path.return_value.mkdir = MagicMock()

            result = await process_single_url(url_config, mock_extractor)

            assert result is False


class TestRunBatchProcessor:
    """Test the main batch processor function."""

    @pytest.mark.asyncio
    async def test_run_batch_processor_success(
        self,
        temp_config_file,
        mock_extracted_pattern,
    ):
        """Test successful batch processing."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch(
                "html2rss_ai.batch_processor.UniversalPatternExtractor",
            ) as mock_extractor_class:
                mock_extractor = MagicMock()
                mock_extractor.extract_pattern_links = AsyncMock(
                    return_value=mock_extracted_pattern,
                )
                mock_extractor.cache_dir = "pattern_cache"
                mock_extractor_class.return_value = mock_extractor

                with patch("html2rss_ai.batch_processor.Path") as mock_path:
                    mock_path.return_value.mkdir = MagicMock()
                    mock_path.return_value.open = MagicMock()

                    with patch("asyncio.sleep"):  # Skip sleep in tests
                        await run_batch_processor(
                            temp_config_file,
                            continue_on_error=True,
                        )

                # Verify extractor was called for both URLs
                assert mock_extractor.extract_pattern_links.call_count == 2

    @pytest.mark.asyncio
    async def test_run_batch_processor_missing_api_key(self, temp_config_file):
        """Test batch processor with missing OpenAI API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                await run_batch_processor(temp_config_file)

    @pytest.mark.asyncio
    async def test_run_batch_processor_continue_on_error(
        self,
        temp_config_file,
        mock_extracted_pattern,
    ):
        """Test batch processor continuing on errors."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch(
                "html2rss_ai.batch_processor.UniversalPatternExtractor",
            ) as mock_extractor_class:
                mock_extractor = MagicMock()
                # First call succeeds, second fails
                mock_extractor.extract_pattern_links = AsyncMock(
                    side_effect=[mock_extracted_pattern, Exception("Test error")],
                )
                mock_extractor.cache_dir = "pattern_cache"
                mock_extractor_class.return_value = mock_extractor

                with patch("html2rss_ai.batch_processor.Path") as mock_path:
                    mock_path.return_value.mkdir = MagicMock()
                    mock_path.return_value.open = MagicMock()

                    with patch("asyncio.sleep"):  # Skip sleep in tests
                        # Should not raise exception due to continue_on_error=True
                        await run_batch_processor(
                            temp_config_file,
                            continue_on_error=True,
                        )

                # Verify both URLs were attempted
                assert mock_extractor.extract_pattern_links.call_count == 2

    @pytest.mark.asyncio
    async def test_run_batch_processor_stop_on_error(self, temp_config_file):
        """Test batch processor stopping on first error."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch(
                "html2rss_ai.batch_processor.UniversalPatternExtractor",
            ) as mock_extractor_class:
                mock_extractor = MagicMock()
                # First call fails
                mock_extractor.extract_pattern_links = AsyncMock(
                    side_effect=Exception("Test error"),
                )
                mock_extractor.cache_dir = "pattern_cache"
                mock_extractor_class.return_value = mock_extractor

                with patch("html2rss_ai.batch_processor.Path") as mock_path:
                    mock_path.return_value.mkdir = MagicMock()

                    with patch("asyncio.sleep"):  # Skip sleep in tests
                        with pytest.raises(SystemExit):
                            await run_batch_processor(
                                temp_config_file,
                                continue_on_error=False,
                            )

                # Should only attempt first URL
                assert mock_extractor.extract_pattern_links.call_count == 1


class TestBatchProcessorCLI:
    """Test the CLI functionality of the batch processor."""

    def test_main_function_help(self):
        """Test that main function can be imported and has proper argparse structure."""
        from html2rss_ai.batch_processor import main

        # Test that main function exists and is callable
        assert callable(main)

        # We can't easily test argparse without mocking sys.argv,
        # but we can verify the function exists
        assert main.__doc__ == "Main entry point for the batch processor."
