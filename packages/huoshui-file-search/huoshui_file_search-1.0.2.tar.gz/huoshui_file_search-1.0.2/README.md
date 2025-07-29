# Huoshui File Search

A Desktop Extension (DXT) that provides fast file search capabilities for macOS using the native `mdfind` command (Spotlight search).

⚠️ **IMPORTANT**: This extension only works on macOS systems. Windows and Linux are not supported.

## Features

- Fast file search using macOS Spotlight index
- Multiple filtering options:
  - Path-based search restrictions
  - Case-sensitive/insensitive search
  - Regular expression matching
  - Sort results by name, size, or date
- Configurable search limits
- Clean JSON-structured responses
- Built with FastMCP framework for optimal performance

## Installation

### Via PyPI (Recommended)

```bash
uvx huoshui-file-search
```

### From Source

```bash
git clone https://github.com/huoshui/huoshui-file-search.git
cd huoshui-file-search
uv sync
```

## Usage

### As a Desktop Extension (DXT)

1. Install the extension via your DXT-compatible application (e.g., Claude Desktop)
2. The extension will be automatically configured and ready to use
3. Use the `search_files` tool with various parameters

### Direct Usage

```python
from server.main import search_files, FileSearchParams

# Basic search
params = FileSearchParams(query="report.pdf")
result = await search_files(None, params)

# Search with filters
params = FileSearchParams(
    query="*.py",
    path="/Users/username/Documents",
    case_sensitive=True,
    sort_by="size",
    limit=50
)
result = await search_files(None, params)
```

## Tool Parameters

- `query` (required): Search query string
- `path` (optional): Directory to limit search scope
- `case_sensitive` (optional): Enable case-sensitive search (default: false)
- `regex` (optional): Regex pattern to filter results by filename
- `sort_by` (optional): Sort results by 'name', 'size', or 'date'
- `limit` (optional): Maximum number of results (default: 100, max: 1000)

## mdfind Query Syntax

The `query` parameter uses macOS Spotlight's mdfind syntax:

- **Simple text search**: `report` - finds files containing "report"
- **File kind**: `kind:pdf`, `kind:image`, `kind:movie`
- **Filename search**: `kMDItemFSName == "*.py"` - finds Python files
- **Combined queries**: `invoice AND kind:pdf` - finds PDF files containing "invoice"
- **Date queries**: `date:today`, `modified:this week`

**Note**: If your query like `'寻找工程车' kind:movie` returns no results, it might mean:
1. No files match both criteria
2. The syntax needs adjustment (try `寻找工程车 AND kind:movie`)
3. Spotlight hasn't indexed the files yet

## Examples

### Basic File Search
```json
{
  "query": "document.pdf"
}
```

### Search in Specific Directory
```json
{
  "query": "*.txt",
  "path": "/Users/username/Documents"
}
```

### Case-Sensitive Search
```json
{
  "query": "README",
  "case_sensitive": true
}
```

### Search with Regex Filter
```json
{
  "query": "kind:text",
  "regex": "log.*2024.*\\.txt$"
}
```

### Sorted and Limited Results
```json
{
  "query": "*.jpg",
  "sort_by": "size",
  "limit": 20
}
```

## Configuration

The extension supports user configuration through the DXT manifest:

- `allowed_directories`: List of directories to limit search scope
- `default_limit`: Default maximum number of search results
- `enable_logging`: Enable debug logging

## Development

### Project Structure
```
huoshui-file-search/
├── manifest.json       # DXT manifest file
├── server/            # MCP server implementation
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
├── pyproject.toml     # Python package configuration
├── requirements.txt   # Python dependencies
├── LICENSE           # MIT License
└── README.md         # This file
```

### Testing Locally

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the server:
   ```bash
   uv run python -m server
   ```

   Or after publishing to PyPI:
   ```bash
   uvx huoshui-file-search
   ```

3. The server will communicate via stdio according to the MCP protocol

### Publishing to PyPI

1. Build the package:
   ```bash
   uv build
   ```

2. Upload to PyPI:
   ```bash
   uv publish
   ```

## System Requirements

- macOS 10.15 or later
- Python 3.10 or later
- uv package manager (install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Spotlight indexing enabled

## Troubleshooting

### "Platform not supported" Error
This extension only works on macOS. Ensure you're running it on a Mac.

### "mdfind command not found" Error
Ensure Spotlight is enabled on your Mac. You can check this in System Preferences > Spotlight.

### No Search Results
- Spotlight may still be indexing new files
- Check if the file path is included in Spotlight's search scope
- Verify the search query syntax

### Search Timeout
Large searches may timeout after 30 seconds. Try:
- Limiting the search path
- Using more specific queries
- Reducing the result limit

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and feature requests, please visit:
https://github.com/huoshui/huoshui-file-search/issues