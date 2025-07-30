from typing import Any

from pydantic import BaseModel


class PatternAnalysis(BaseModel):
    pattern_type: str
    primary_selectors: list[str]
    fallback_selectors: list[str]
    url_pattern_regex: str
    content_indicators: list[str]
    skip_patterns: list[str]
    confidence_score: float
    pattern_description: str
    estimated_items: int
    date_selectors: list[str]


class ExtractedPattern(BaseModel):
    links: list[dict[str, Any]]
    total_found: int
    pattern_used: str
    confidence: float
    base_url: str
    pattern_analysis: PatternAnalysis
