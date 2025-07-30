"""
Tests for the MCPServerSync class.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch



from mcp_config_sync.sync import MCPServerSync


class TestMCPServerSync:
    """Test cases for MCPServerSync class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        syncer = MCPServerSync()
        assert syncer.backup is True
        assert syncer.mcp_servers == {}
        assert len(syncer.config_files) > 0  # Should have default apps
        assert syncer.existing_files == []
        assert len(syncer.selected_apps) > 0  # Should have selected all apps

    def test_init_custom_files(self):
        """Test initialization with custom config files."""
        custom_files = ["/path/to/config1.json", "/path/to/config2.json"]
        syncer = MCPServerSync(config_files=custom_files, backup=False)
        assert syncer.backup is False
        assert syncer.config_files == custom_files
        assert syncer.selected_apps == []  # No apps when using custom files

    def test_init_custom_apps(self):
        """Test initialization with custom apps."""
        custom_apps = ["amazonq", "cline"]
        syncer = MCPServerSync(apps=custom_apps, backup=False)
        assert syncer.backup is False
        assert syncer.selected_apps == custom_apps
        assert len(syncer.config_files) == 2  # Should have 2 config files

    def test_parse_config_file_valid(self):
        """Test parsing a valid JSON configuration file."""
        syncer = MCPServerSync()

        # Create a temporary config file
        config_data = {
            "mcpServers": {
                "test-server": {"command": "npx", "args": ["-y", "@test/server"]}
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            result = syncer.parse_config_file(temp_path)
            assert result == config_data
        finally:
            temp_path.unlink()

    def test_parse_config_file_invalid_json(self):
        """Test parsing an invalid JSON file."""
        syncer = MCPServerSync()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = Path(f.name)

        try:
            result = syncer.parse_config_file(temp_path)
            assert result == {}
        finally:
            temp_path.unlink()

    def test_extract_mcp_servers(self):
        """Test extracting MCP servers from configuration."""
        syncer = MCPServerSync()

        config = {
            "mcpServers": {
                "server1": {"command": "cmd1"},
                "server2": {"command": "cmd2"},
            },
            "otherData": "ignored",
        }

        servers = syncer.extract_mcp_servers(config, "test.json")
        assert len(servers) == 2
        assert "server1" in servers
        assert "server2" in servers
        assert servers["server1"]["command"] == "cmd1"

    def test_extract_mcp_servers_no_servers(self):
        """Test extracting from config with no MCP servers."""
        syncer = MCPServerSync()

        config = {"otherData": "value"}
        servers = syncer.extract_mcp_servers(config, "test.json")
        assert servers == {}

    def test_generate_unified_config(self):
        """Test generating unified configuration."""
        syncer = MCPServerSync()
        syncer.mcp_servers = {
            "server1": {"command": "cmd1"},
            "server2": {"command": "cmd2"},
        }

        unified = syncer.generate_unified_config()
        assert "mcpServers" in unified
        assert unified["mcpServers"] == syncer.mcp_servers

    def test_get_server_count(self):
        """Test getting server count."""
        syncer = MCPServerSync()
        assert syncer.get_server_count() == 0

        syncer.mcp_servers = {"server1": {}, "server2": {}}
        assert syncer.get_server_count() == 2

    def test_list_all_servers(self):
        """Test listing all servers."""
        syncer = MCPServerSync()
        servers = {"server1": {"command": "cmd1"}}
        syncer.mcp_servers = servers

        result = syncer.list_all_servers()
        assert result == servers
        # Ensure it returns a copy, not the original
        assert result is not syncer.mcp_servers

    @patch("mcp_config_sync.sync.Path")
    def test_get_config_files_status(self, mock_path_class):
        """Test getting configuration files status."""
        syncer = MCPServerSync(config_files=["/test/path1.json", "/test/path2.json"])

        # Mock Path instances
        mock_path1 = MagicMock()
        mock_path2 = MagicMock()
        mock_path1.exists.return_value = True
        mock_path2.exists.return_value = False

        # Mock the Path constructor to return our mock instances
        def path_constructor(path_str):
            if path_str == "/test/path1.json":
                return mock_path1
            elif path_str == "/test/path2.json":
                return mock_path2
            return MagicMock()

        mock_path_class.side_effect = path_constructor
        mock_path1.expanduser.return_value = mock_path1
        mock_path2.expanduser.return_value = mock_path2

        status = syncer.get_config_files_status()
        assert status["/test/path1.json"] is True
        assert status["/test/path2.json"] is False
