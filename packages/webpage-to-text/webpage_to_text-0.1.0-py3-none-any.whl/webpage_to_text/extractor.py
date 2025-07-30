"""
Core web page content extractor using LlamaIndex SimpleWebPageReader.
"""

import os
import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from llama_index.readers.web import SimpleWebPageReader


class WebPageExtractor:
    """Extract clean text content from web pages using LlamaIndex."""
    
    def __init__(self, 
                 html_to_text: bool = True,
                 rate_limit: float = 1.0,
                 output_dir: Optional[str] = None):
        """
        Initialize the web page extractor.
        
        Args:
            html_to_text: Convert HTML to clean text format
            rate_limit: Delay between requests in seconds
            output_dir: Directory to save extracted text files
        """
        self.html_to_text = html_to_text
        self.rate_limit = rate_limit
        self.output_dir = Path(output_dir) if output_dir else Path("./extracted_texts")
        self.reader = SimpleWebPageReader(html_to_text=self.html_to_text)
        
    def extract_url(self, url: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract content from a single URL.
        
        Args:
            url: URL to extract content from
            filename: Optional custom filename for output
            
        Returns:
            Dictionary with extraction results
        """
        try:
            docs = self.reader.load_data([url])
            
            if not filename:
                # Generate filename from URL
                stem = url.rstrip("/").split("/")[-1] or "home"
                filename = f"{stem}.txt"
            
            results = []
            for i, doc in enumerate(docs):
                if len(docs) > 1:
                    doc_filename = f"{filename.rsplit('.', 1)[0]}-{i+1}.txt"
                else:
                    doc_filename = filename
                    
                filepath = self.output_dir / doc_filename
                
                # Save to file
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(doc.text)
                
                results.append({
                    "url": url,
                    "filepath": str(filepath),
                    "characters": len(doc.text),
                    "success": True
                })
                
            return {
                "url": url,
                "success": True,
                "files": results,
                "total_chars": sum(r["characters"] for r in results)
            }
            
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "files": [],
                "total_chars": 0
            }
    
    def extract_urls(self, urls: List[str], 
                    filenames: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs.
        
        Args:
            urls: List of URLs to extract content from
            filenames: Optional list of custom filenames
            
        Returns:
            List of extraction results
        """
        results = []
        
        for i, url in enumerate(urls):
            filename = filenames[i] if filenames and i < len(filenames) else None
            
            print(f"Processing {i+1}/{len(urls)}: {url}")
            result = self.extract_url(url, filename)
            results.append(result)
            
            if result["success"]:
                for file_info in result["files"]:
                    print(f"✓ Saved {file_info['filepath']} ({file_info['characters']:,} characters)")
            else:
                print(f"⚠️  Error: {result['error']}")
            
            # Rate limiting
            if i < len(urls) - 1:  # Don't sleep after the last URL
                time.sleep(self.rate_limit)
                
        return results
    
    def extract_from_config(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract content based on configuration dictionary.
        
        Args:
            config: Configuration dictionary with URLs and settings
            
        Returns:
            List of extraction results
        """
        urls = config.get("urls", [])
        filenames = config.get("filenames", [])
        
        # Update settings from config
        if "rate_limit" in config:
            self.rate_limit = config["rate_limit"]
        if "output_dir" in config:
            self.output_dir = Path(config["output_dir"])
            
        return self.extract_urls(urls, filenames)