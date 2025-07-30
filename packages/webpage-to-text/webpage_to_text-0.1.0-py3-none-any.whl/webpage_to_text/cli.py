"""
Command-line interface for webpage-to-text.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .extractor import WebPageExtractor
from .config import Config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract clean text content from web pages using LlamaIndex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from config file
  webpage-to-text --config sites.yaml
  
  # Extract single URL
  webpage-to-text --url https://example.com --output ./texts/
  
  # Extract multiple URLs
  webpage-to-text --url https://example.com --url https://example.com/about
  
  # Create sample config
  webpage-to-text --create-config sample.yaml
        """
    )
    
    # Main operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config", "-c",
        help="Path to configuration file (YAML or JSON)"
    )
    group.add_argument(
        "--url", "-u",
        action="append",
        help="URL to extract (can be used multiple times)"
    )
    group.add_argument(
        "--create-config",
        help="Create a sample configuration file"
    )
    
    # Options
    parser.add_argument(
        "--output", "-o",
        default="./extracted_texts",
        help="Output directory for extracted text files (default: ./extracted_texts)"
    )
    parser.add_argument(
        "--rate-limit", "-r",
        type=float,
        default=1.0,
        help="Rate limit between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--filename", "-f",
        action="append",
        help="Custom filename for output (can be used multiple times, must match URL count)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle create-config
    if args.create_config:
        try:
            Config.create_sample_config(args.create_config)
            print(f"✓ Sample configuration created: {args.create_config}")
            return 0
        except Exception as e:
            print(f"❌ Error creating config: {e}")
            return 1
    
    # Initialize extractor
    extractor = WebPageExtractor(
        html_to_text=True,
        rate_limit=args.rate_limit,
        output_dir=args.output
    )
    
    # Handle config file
    if args.config:
        try:
            config = Config(args.config)
            results = extractor.extract_from_config(config.config)
            
            # Print summary
            success_count = sum(1 for r in results if r["success"])
            total_chars = sum(r["total_chars"] for r in results)
            
            print(f"\n🎉 Extraction complete!")
            print(f"   Processed: {len(results)} URLs")
            print(f"   Successful: {success_count}")
            print(f"   Total characters: {total_chars:,}")
            
            return 0 if success_count == len(results) else 1
            
        except Exception as e:
            print(f"❌ Error processing config: {e}")
            return 1
    
    # Handle direct URLs
    if args.url:
        try:
            # Validate filename count
            if args.filename and len(args.filename) != len(args.url):
                print("❌ Error: Number of filenames must match number of URLs")
                return 1
            
            results = extractor.extract_urls(args.url, args.filename)
            
            # Print summary
            success_count = sum(1 for r in results if r["success"])
            total_chars = sum(r["total_chars"] for r in results)
            
            print(f"\n🎉 Extraction complete!")
            print(f"   Processed: {len(results)} URLs")
            print(f"   Successful: {success_count}")
            print(f"   Total characters: {total_chars:,}")
            
            return 0 if success_count == len(results) else 1
            
        except Exception as e:
            print(f"❌ Error processing URLs: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())