# webpage-to-text

**LlamaIndex-powered web content extractor for RAG applications**

Extract clean, structured text from web pages using LlamaIndex's powerful HTML parsing capabilities. Perfect for preparing content for RAG (Retrieval-Augmented Generation) systems, vector databases, and knowledge bases.

## Features

- 🚀 **LlamaIndex Integration**: Leverages LlamaIndex's `SimpleWebPageReader` for high-quality text extraction
- 📄 **Clean Text Output**: Converts HTML to structured, readable text with preserved formatting
- ⚙️ **Configuration-Driven**: Use YAML/JSON files to define extraction jobs
- 🔧 **CLI Interface**: Simple command-line tool for batch processing
- 📊 **Batch Processing**: Extract from multiple URLs with automatic rate limiting
- 🎯 **RAG-Ready**: Output format optimized for vector databases and RAG applications
- 🔄 **Flexible Output**: Support for custom filenames and directory structures

## Installation

### From PyPI (Coming Soon)
```bash
pip install webpage-to-text
```

### From Source
```bash
git clone https://github.com/yourusername/webpage-to-text.git
cd webpage-to-text
pip install -e .
```

## Quick Start

### Command Line Usage

Extract from a single URL:
```bash
webpage-to-text --url https://example.com --output ./texts/
```

Extract from multiple URLs:
```bash
webpage-to-text --url https://example.com --url https://example.com/about --output ./texts/
```

Use a configuration file:
```bash
webpage-to-text --config sites.yaml
```

Create a sample configuration:
```bash
webpage-to-text --create-config sample.yaml
```

### Python API Usage

```python
from webpage_to_text import WebPageExtractor, Config

# Basic usage
extractor = WebPageExtractor(output_dir="./texts")
result = extractor.extract_url("https://example.com")

# Batch processing
urls = ["https://example.com", "https://example.com/about"]
results = extractor.extract_urls(urls)

# Using configuration
config = Config("sites.yaml")
results = extractor.extract_from_config(config.config)
```

## Configuration

### YAML Configuration Example

```yaml
name: "Hotel Chain Extraction"
description: "Extract content from hotel websites"
output_dir: "./hotel_texts"
rate_limit: 1.0

urls:
  - "https://www.hotel.com/"
  - "https://www.hotel.com/rooms"
  - "https://www.hotel.com/amenities"
  - "https://www.hotel.com/contact"

filenames:
  - "001_home.txt"
  - "002_rooms.txt"
  - "003_amenities.txt"
  - "004_contact.txt"
```

### JSON Configuration Example

```json
{
  "name": "E-commerce Site Extraction",
  "description": "Extract product and category pages",
  "output_dir": "./ecommerce_texts",
  "rate_limit": 2.0,
  "urls": [
    "https://shop.example.com/",
    "https://shop.example.com/categories/electronics",
    "https://shop.example.com/categories/clothing"
  ]
}
```

## Use Cases

### RAG Applications
Perfect for creating knowledge bases for chatbots and Q&A systems:
```python
extractor = WebPageExtractor(output_dir="./knowledge_base")
results = extractor.extract_urls([
    "https://company.com/faq",
    "https://company.com/documentation",
    "https://company.com/support"
])
```

### Content Migration
Move content between systems while preserving structure:
```python
# Extract from old site
extractor = WebPageExtractor(output_dir="./migrated_content")
config = Config("old_site_pages.yaml")
results = extractor.extract_from_config(config.config)
```

### Research Data Collection
Collect structured data for analysis:
```python
# Research paper extraction
extractor = WebPageExtractor(output_dir="./research_papers")
urls = ["https://arxiv.org/abs/1234.5678", "https://arxiv.org/abs/8765.4321"]
results = extractor.extract_urls(urls)
```

## Output Format

The extracted text maintains structure while being clean and readable:

```
# Page Title

## Section Header

Content paragraph with proper formatting.

* List item 1
* List item 2

[Link Text](https://example.com)

### Subsection

More content here...
```

## CLI Options

```
webpage-to-text --help

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to configuration file (YAML or JSON)
  --url URL, -u URL     URL to extract (can be used multiple times)
  --create-config CREATE_CONFIG
                        Create a sample configuration file
  --output OUTPUT, -o OUTPUT
                        Output directory for extracted text files
  --rate-limit RATE_LIMIT, -r RATE_LIMIT
                        Rate limit between requests in seconds (default: 1.0)
  --filename FILENAME, -f FILENAME
                        Custom filename for output
  --verbose, -v         Enable verbose output
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/webpage-to-text.git
cd webpage-to-text
pip install -e .[dev]
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [LlamaIndex](https://github.com/run-llama/llama_index) for robust web content extraction
- Inspired by the need for high-quality text extraction for RAG applications
- Thanks to the open-source community for foundational libraries

## Support

- 📖 [Documentation](https://github.com/yourusername/webpage-to-text#readme)
- 🐛 [Bug Reports](https://github.com/yourusername/webpage-to-text/issues)
- 💬 [Discussions](https://github.com/yourusername/webpage-to-text/discussions)

---

Made with ❤️ for the RAG and AI community