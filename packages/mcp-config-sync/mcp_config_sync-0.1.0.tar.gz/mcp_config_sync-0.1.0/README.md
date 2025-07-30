# MCP Config Sync

[![PyPI version](https://badge.fury.io/py/mcp-config-sync.svg)](https://badge.fury.io/py/mcp-config-sync)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for synchronizing Model Context Protocol (MCP) server configurations across different AI tools and applications.

## Overview

MCP Config Sync helps you maintain consistent MCP server configurations across multiple tools like Claude Desktop, Amazon Q, VS Code extensions, and other MCP-compatible applications. It automatically discovers, combines, and synchronizes your MCP server configurations, ensuring all your tools have access to the same servers.

## Features

- **Automatic Discovery**: Finds MCP configuration files across common locations
- **Smart Merging**: Combines unique MCP servers from multiple configuration files
- **Conflict Resolution**: Handles conflicting configurations intelligently
- **Backup Support**: Creates backups before modifying files (enabled by default)
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Dry Run Mode**: Preview changes before applying them
- **Flexible Configuration**: Support for custom configuration file paths

## Installation

### From PyPI (Recommended)

```bash
pip install mcp-config-sync
```

### From Source

```bash
git clone https://github.com/jon-the-dev/mcp_config_sync.git
cd mcp_config_sync
pip install -e .
```

## Quick Start

### Command Line Usage

After installation, you can use the `mcp-config-sync` command:

```bash
# Sync all registered MCP applications
mcp-config-sync

# List all available MCP applications
mcp-config-sync --list-apps

# Sync specific applications only
mcp-config-sync --apps amazonq cline

# List all discovered MCP servers
mcp-config-sync --list-all

# Remove a specific server from all configurations
mcp-config-sync --remove server-name

# Preview changes without modifying files
mcp-config-sync --dry-run

# Skip creating backup files
mcp-config-sync --no-backup

# Enable verbose logging
mcp-config-sync --verbose
```

### Python API Usage

```python
from mcp_config_sync import MCPServerSync

# Initialize the synchronizer for all apps
syncer = MCPServerSync()

# Or initialize for specific apps
syncer = MCPServerSync(apps=["amazonq", "cline"])

# Or use custom config files
syncer = MCPServerSync(config_files=["/path/to/config1.json", "/path/to/config2.json"])

# Discover existing configuration files
syncer.discover_config_files()

# Combine MCP servers from all files
syncer.combine_mcp_servers()

# Get all servers
servers = syncer.list_all_servers()
print(f"Found {len(servers)} MCP servers")

# Sync configurations across all files
results = syncer.replace_all_configs()
```

### Working with Apps

```python
from mcp_config_sync import get_all_apps, get_app_names, get_app

# Get all available apps
apps = get_all_apps()
print(f"Available apps: {list(apps.keys())}")

# Get app names only
app_names = get_app_names()
print(f"App names: {app_names}")

# Get specific app info
app = get_app("amazonq")
if app:
    print(f"App: {app.display_name}")
    print(f"Config: {app.config_path}")
```

## Supported Applications

MCP Config Sync supports the following MCP-compatible applications:

| App Name | Display Name | Description | Config Path |
|----------|--------------|-------------|-------------|
| `amazonq` | Amazon Q | Amazon Q AI assistant configuration | `~/.aws/amazonq/mcp.json` |
| `cline` | Cline (VS Code) | Cline VS Code extension MCP settings | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` |
| `claude-desktop` | Claude Desktop | Anthropic Claude Desktop application | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### Adding New Applications

To add support for a new MCP application, you can:

1. **Submit a Pull Request**: Add the new app to `mcp_config_sync/apps.py`
2. **Use Custom Config Files**: Use the `--config-files` option for one-off usage

Example PR to add a new app:

```python
# In mcp_config_sync/apps.py
"new-app": MCPApp(
    name="new-app",
    display_name="New MCP App",
    config_path="~/path/to/new-app/config.json",
    description="Description of the new MCP application",
    homepage="https://example.com",
),
```

You can specify custom paths using the `--config-files` option:

```bash
mcp-config-sync --config-files /path/to/config1.json /path/to/config2.json
```

## Configuration File Format

MCP configuration files should contain a `mcpServers` object:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Examples

### Basic Synchronization

```bash
# Sync all registered MCP applications
mcp-config-sync
```

This will:
1. Discover all existing MCP configuration files for registered apps
2. Extract and combine unique MCP servers
3. Create backups of existing files
4. Write the unified configuration to all files

### Sync Specific Applications

```bash
# Sync only Amazon Q and Cline
mcp-config-sync --apps amazonq cline
```

### List Available Applications

```bash
mcp-config-sync --list-apps
```

Output:
```
============================================================
AVAILABLE MCP APPLICATIONS
============================================================

Found 3 registered MCP applications:
----------------------------------------

📱 App: amazonq
   Display Name: Amazon Q
   Description: Amazon Q AI assistant configuration
   Config Path: ~/.aws/amazonq/mcp.json
   Status: ✓ CONFIG EXISTS
   Homepage: https://aws.amazon.com/q/

📱 App: cline
   Display Name: Cline (VS Code)
   Description: Cline VS Code extension MCP settings
   Config Path: ~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   Status: ✓ CONFIG EXISTS
   Homepage: https://github.com/saoudrizwan/claude-dev

📱 App: claude-desktop
   Display Name: Claude Desktop
   Description: Anthropic Claude Desktop application
   Config Path: ~/Library/Application Support/Claude/claude_desktop_config.json
   Status: ✓ CONFIG EXISTS
   Homepage: https://claude.ai/

============================================================
Total: 3 applications (3 with existing configs)
============================================================
```

### List All Servers

```bash
mcp-config-sync --list-all
```

Output:
```
============================================================
ALL MCP SERVERS
============================================================

Found 3 MCP servers:
----------------------------------------

🔧 Server: filesystem
   Command: npx
   Args: -y @modelcontextprotocol/server-filesystem /Users/jon/Documents

🔧 Server: brave-search
   Command: npx
   Args: -y @modelcontextprotocol/server-brave-search
   Environment Variables: BRAVE_API_KEY

🔧 Server: postgres
   Command: npx
   Args: -y @modelcontextprotocol/server-postgres
   Environment Variables: POSTGRES_CONNECTION_STRING
```

### Remove a Server

```bash
# Remove a specific server from all configurations
mcp-config-sync --remove old-server-name
```

### Preview Changes

```bash
# See what would be changed without modifying files
mcp-config-sync --dry-run --verbose
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/jon-the-dev/mcp_config_sync.git
cd mcp_config_sync

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black mcp_config_sync/

# Sort imports
isort mcp_config_sync/

# Type checking
mypy mcp_config_sync/
```

## Publishing to PyPI

### First Time Setup

1. Create accounts on [PyPI](https://pypi.org/account/register/) and [TestPyPI](https://test.pypi.org/account/register/)
2. Install build tools:
   ```bash
   pip install build twine
   ```

### Build and Upload

```bash
# Build the package
python -m build

# Upload to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mcp-config-sync

# Upload to PyPI
python -m twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black . && isort .`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jon** - [jon@zer0day.net](mailto:jon@zer0day.net)

## Changelog

### v0.1.0 (2025-01-07)
- Initial release
- Basic MCP server synchronization functionality
- Command-line interface
- Python API
- Support for common MCP configuration file locations
- Backup and dry-run capabilities