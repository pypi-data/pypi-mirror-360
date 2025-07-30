"""
Tests for webpage_to_text.extractor module.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path

from webpage_to_text.extractor import WebPageExtractor


class TestWebPageExtractor:
    """Test cases for WebPageExtractor class."""
    
    def test_init(self):
        """Test extractor initialization."""
        extractor = WebPageExtractor()
        assert extractor.html_to_text == True
        assert extractor.rate_limit == 1.0
        assert extractor.output_dir == Path("./extracted_texts")
        
    def test_init_with_params(self):
        """Test extractor initialization with parameters."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = WebPageExtractor(
                html_to_text=False,
                rate_limit=2.0,
                output_dir=tmp_dir
            )
            assert extractor.html_to_text == False
            assert extractor.rate_limit == 2.0
            assert extractor.output_dir == Path(tmp_dir)
    
    @patch('webpage_to_text.extractor.SimpleWebPageReader')
    def test_extract_url_success(self, mock_reader_class):
        """Test successful URL extraction."""
        # Mock the reader
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        
        # Mock document
        mock_doc = Mock()
        mock_doc.text = "Sample content"
        mock_reader.load_data.return_value = [mock_doc]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = WebPageExtractor(output_dir=tmp_dir)
            result = extractor.extract_url("https://example.com", "test.txt")
            
            assert result["success"] == True
            assert result["url"] == "https://example.com"
            assert result["total_chars"] == 14
            assert len(result["files"]) == 1
            
            # Check file was created
            file_path = Path(tmp_dir) / "test.txt"
            assert file_path.exists()
            assert file_path.read_text() == "Sample content"
    
    @patch('webpage_to_text.extractor.SimpleWebPageReader')
    def test_extract_url_failure(self, mock_reader_class):
        """Test URL extraction failure."""
        # Mock the reader to raise an exception
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        mock_reader.load_data.side_effect = Exception("Network error")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = WebPageExtractor(output_dir=tmp_dir)
            result = extractor.extract_url("https://example.com", "test.txt")
            
            assert result["success"] == False
            assert result["error"] == "Network error"
            assert len(result["files"]) == 0
    
    @patch('webpage_to_text.extractor.SimpleWebPageReader')
    @patch('time.sleep')
    def test_extract_urls_multiple(self, mock_sleep, mock_reader_class):
        """Test multiple URL extraction."""
        # Mock the reader
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        
        # Mock documents
        mock_doc1 = Mock()
        mock_doc1.text = "Content 1"
        mock_doc2 = Mock()
        mock_doc2.text = "Content 2"
        
        mock_reader.load_data.side_effect = [[mock_doc1], [mock_doc2]]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = WebPageExtractor(output_dir=tmp_dir, rate_limit=0.1)
            
            urls = ["https://example1.com", "https://example2.com"]
            filenames = ["file1.txt", "file2.txt"]
            
            results = extractor.extract_urls(urls, filenames)
            
            assert len(results) == 2
            assert all(r["success"] for r in results)
            assert results[0]["total_chars"] == 9
            assert results[1]["total_chars"] == 9
            
            # Check rate limiting was called
            mock_sleep.assert_called_once_with(0.1)
    
    @patch('webpage_to_text.extractor.SimpleWebPageReader')
    def test_extract_from_config(self, mock_reader_class):
        """Test extraction from configuration."""
        # Mock the reader
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        
        # Mock document
        mock_doc = Mock()
        mock_doc.text = "Config content"
        mock_reader.load_data.return_value = [mock_doc]
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = WebPageExtractor()
            
            config = {
                "urls": ["https://example.com"],
                "filenames": ["config_test.txt"],
                "output_dir": tmp_dir,
                "rate_limit": 0.5
            }
            
            results = extractor.extract_from_config(config)
            
            assert len(results) == 1
            assert results[0]["success"] == True
            assert extractor.output_dir == Path(tmp_dir)
            assert extractor.rate_limit == 0.5