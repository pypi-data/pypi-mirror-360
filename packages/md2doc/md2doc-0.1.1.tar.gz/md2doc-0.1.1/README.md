# md2doc - Markdown to DOCX MCP Server

[![PyPI version](https://badge.fury.io/py/md2doc.svg)](https://badge.fury.io/py/md2doc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that converts Markdown text to DOCX format using an external conversion service.

<img src="https://raw.githubusercontent.com/Yorick-Ryu/md2doc-mcp/master/images/md2doc.png" alt="md2doc Demo" width="600" style="max-width: 100%; height: auto;">

## Features

- Convert Markdown text to DOCX format
- Support for custom templates
- Multi-language support (English, Chinese, etc.)
- Automatic file download to user's Downloads directory
- Template listing and management

## Installation

### Prerequisites

1. Install [uv](https://github.com/astral-sh/uv) (recommended):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   ```

   Or install via Homebrew (Only Mac):
   ```bash
   brew install uv
   ```

### Install from PyPI (Recommended)

The easiest way to install and use md2doc:

```bash
uvx md2doc
```

This will automatically install the package and run the MCP server.

### Install from Source

1. Clone this repository
2. Install dependencies using uv (recommended):
   ```bash
   uv pip install -e .
   ```

   Or using traditional pip:
   ```bash
   pip install -e .
   ```

## Environment Variables

### Setting Environment Variables

#### macOS/Linux
```bash
# Temporary (current session only)
export DEEP_SHARE_API_KEY="your-api-key-here"

# Permanent - add to ~/.zshrc or ~/.bashrc
echo 'export DEEP_SHARE_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows (Command Prompt)
```cmd
# Temporary (current session only)
set DEEP_SHARE_API_KEY=your-api-key-here

# Permanent
setx DEEP_SHARE_API_KEY "your-api-key-here"
```

#### Windows (PowerShell)
```powershell
# Temporary (current session only)
$env:DEEP_SHARE_API_KEY="your-api-key-here"

# Permanent
[Environment]::SetEnvironmentVariable("DEEP_SHARE_API_KEY", "your-api-key-here", "User")
```

### API Key

#### Free Trial API Key
Use this key for testing:
```
f4e8fe6f-e39e-486f-b7e7-e037d2ec216f
```

#### Purchase API Key - Super Low Price!

- [Purchase Link](https://www.deepshare.app/purchase-en.html)
- [中国大陆购买](https://www.deepshare.app/purchase.html)

## Usage

### As an MCP Server

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "md2doc": {
      "command": "uv",
      "args": [
        "--directory",
        "/PATH/TO/md2doc-mcp",
        "run",
        "python",
        "-m",
        "md2doc.server"
      ],
      "env": {
        "DEEP_SHARE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Available Tools

- `convert_markdown_to_docx`: Convert markdown text to DOCX
- `list_templates`: Get available templates by language

## Development

### Publishing to PyPI

To publish updates to PyPI:

1. **Set environment variables**:
   ```bash
   export UV_PUBLISH_TOKEN="your-pypi-token-here"
   export UV_PUBLISH_URL="https://upload.pypi.org/legacy/"
   ```

2. **Build and publish**:
   ```bash
   uv build
   uv publish
   ```

3. **Or use the automated script**:
   ```bash
   ./publish.sh
   ```

For detailed publishing instructions, see [PUBLISHING.md](PUBLISHING.md).

## License

MIT 