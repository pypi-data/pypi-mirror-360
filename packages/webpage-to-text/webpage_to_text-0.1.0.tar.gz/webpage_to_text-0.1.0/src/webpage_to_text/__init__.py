"""
webpage-to-text: LlamaIndex-powered web content extractor for RAG applications.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .extractor import WebPageExtractor
from .config import Config

__all__ = ["WebPageExtractor", "Config"]