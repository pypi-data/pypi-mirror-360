#!/usr/bin/env python3
"""
Basic usage examples for webpage-to-text.
"""

from webpage_to_text import WebPageExtractor, Config


def example_single_url():
    """Extract content from a single URL."""
    print("=== Single URL Example ===")
    
    extractor = WebPageExtractor(output_dir="./example_outputs")
    result = extractor.extract_url("https://example.com", "example_site.txt")
    
    if result["success"]:
        print(f"✓ Successfully extracted {result['total_chars']:,} characters")
        for file_info in result["files"]:
            print(f"  Saved to: {file_info['filepath']}")
    else:
        print(f"✗ Error: {result['error']}")


def example_multiple_urls():
    """Extract content from multiple URLs."""
    print("\n=== Multiple URLs Example ===")
    
    urls = [
        "https://httpbin.org/",
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    
    filenames = [
        "httpbin_home.txt",
        "httpbin_html.txt", 
        "httpbin_json.txt"
    ]
    
    extractor = WebPageExtractor(
        output_dir="./example_outputs",
        rate_limit=0.5  # Faster for testing
    )
    
    results = extractor.extract_urls(urls, filenames)
    
    success_count = sum(1 for r in results if r["success"])
    total_chars = sum(r["total_chars"] for r in results)
    
    print(f"✓ Processed {len(results)} URLs")
    print(f"✓ Successful: {success_count}")
    print(f"✓ Total characters: {total_chars:,}")


def example_config_file():
    """Extract content using a configuration file."""
    print("\n=== Configuration File Example ===")
    
    # Create a sample config
    config_data = {
        "name": "Sample Extraction",
        "description": "Extract content from sample sites",
        "output_dir": "./example_outputs",
        "rate_limit": 1.0,
        "urls": [
            "https://httpbin.org/",
            "https://httpbin.org/html"
        ],
        "filenames": [
            "config_httpbin_home.txt",
            "config_httpbin_html.txt"
        ]
    }
    
    extractor = WebPageExtractor()
    results = extractor.extract_from_config(config_data)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"✓ Config-based extraction completed: {success_count}/{len(results)} successful")


def example_yaml_config():
    """Extract content using a YAML configuration file."""
    print("\n=== YAML Configuration Example ===")
    
    try:
        config = Config("../configs/eau_palm_beach.yaml")
        extractor = WebPageExtractor()
        
        # Just extract the first 2 URLs for demo
        limited_config = config.config.copy()
        limited_config["urls"] = limited_config["urls"][:2]
        limited_config["filenames"] = limited_config["filenames"][:2]
        limited_config["output_dir"] = "./example_outputs"
        
        results = extractor.extract_from_config(limited_config)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"✓ YAML config extraction: {success_count}/{len(results)} successful")
        
    except Exception as e:
        print(f"✗ Error with YAML config: {e}")


if __name__ == "__main__":
    # Run all examples
    example_single_url()
    example_multiple_urls()
    example_config_file()
    example_yaml_config()
    
    print("\n🎉 All examples completed! Check the './example_outputs' directory for results.")