#!/usr/bin/env python3
"""
Example: Extract articles from ordep.dev blog using html2rss-ai

This example demonstrates how to use the UniversalPatternExtractor to extract
blog posts from https://ordep.dev/posts/ and display them in a formatted way.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from html2rss_ai.extractor import (
    UniversalPatternExtractor,
    extract_pattern_links as extract_links_json,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def extract_ordep_blog():
    """Extract articles from ordep.dev blog."""
    
    # Initialize the extractor
    extractor = UniversalPatternExtractor()
    
    # URL of the blog
    blog_url = "https://blog.pragmaticengineer.com/"
    
    print(f"🔍 Extracting articles from: {blog_url}")
    print("=" * 60)
    
    try:
        # Extract the articles
        result = await extractor.extract_pattern_links(blog_url)
        
        # Display extraction info
        print(f"📊 Extraction Results:")
        print(f"   Pattern Type: {result.pattern_analysis.pattern_type}")
        print(f"   Confidence Score: {result.confidence:.2f}")
        print(f"   Total Items Found: {result.total_found}")
        print()
        
        # Display articles
        if result.links:
            print("📝 Articles Found:")
            print("-" * 60)
            
            for i, item in enumerate(result.links, 1):
                print(f"{i:2d}. {item['title']}")
                print(f"    URL: {item['url']}")
                if item.get('publication_date'):
                    print(f"    Date: {item['publication_date']}")
                print()
        else:
            print("❌ No articles found!")
            
        # Save to JSON file
        output_file = Path("ordep_blog_articles.json")
        json_result = await extract_links_json(blog_url)
        
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
        
        # Display sample JSON structure
        print("\n📋 Sample JSON structure:")
        print(json.dumps(json_result, indent=2, ensure_ascii=False)[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error extracting articles: {e}")
        logging.error(f"Extraction failed: {e}", exc_info=True)

def display_usage_info():
    """Display usage information."""
    print("🚀 html2rss-ai Example: Extract from ordep.dev blog")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("• How to use UniversalPatternExtractor")
    print("• Extracting blog articles from a webpage")
    print("• Handling the extracted data")
    print("• Saving results to JSON")
    print()
    print("Requirements:")
    print("• OPENAI_API_KEY environment variable set")
    print("• Internet connection to access ordep.dev")
    print("• Required packages: html2rss-ai, openai, beautifulsoup4")
    print()

if __name__ == "__main__":
    display_usage_info()
    
    # Check if OpenAI API key is available
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("   Please set your OpenAI API key to use this example.")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # Run the extraction
    asyncio.run(extract_ordep_blog()) 