"""
MCP Server Configuration Synchronizer

This module provides the core functionality for synchronizing MCP server
configurations across different tools and applications.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .apps import get_all_apps, get_config_paths_for_apps

logger = logging.getLogger(__name__)


class MCPServerSync:
    """Handles synchronization of MCP server configurations across tools."""

    def __init__(
        self,
        config_files: Optional[List[str]] = None,
        apps: Optional[List[str]] = None,
        backup: bool = True,
    ):
        """
        Initialize the MCP Server Synchronizer.

        Args:
            config_files: List of configuration file paths. Takes precedence over apps.
            apps: List of app names to sync. If None and config_files is None, uses all apps.
            backup: Whether to create backups before modifying files
        """
        self.backup = backup
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        self.existing_files: List[Path] = []

        # Determine which config files to use
        if config_files is not None:
            self.config_files = config_files
            self.selected_apps = []
        elif apps is not None:
            self.config_files = get_config_paths_for_apps(apps)
            self.selected_apps = apps
        else:
            # Default to all registered apps
            all_apps = get_all_apps()
            self.config_files = [app.config_path for app in all_apps.values()]
            self.selected_apps = list(all_apps.keys())

    def discover_config_files(self) -> List[Path]:
        """
        Check which configuration files exist.

        Returns:
            List of Path objects for existing JSON configuration files
        """
        existing_files = []

        for file_path in self.config_files:
            expanded_path = Path(file_path).expanduser()
            if expanded_path.exists() and expanded_path.is_file():
                existing_files.append(expanded_path)
                logger.debug(f"Found existing config: {expanded_path}")
            else:
                logger.debug(f"Config file not found: {expanded_path}")

        self.existing_files = existing_files

        logger.info(
            f"Found {len(existing_files)} existing configuration files out of {len(self.config_files)} total"
        )

        return existing_files

    def parse_config_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a JSON configuration file.

        Args:
            file_path: Path to the JSON configuration file

        Returns:
            Parsed JSON configuration as dictionary
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.debug(f"Successfully parsed: {file_path}")
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {}

    def extract_mcp_servers(
        self, config: Dict[str, Any], source_file: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract MCP server configurations from a parsed config.

        Args:
            config: Parsed configuration dictionary
            source_file: Source file name for logging

        Returns:
            Dictionary of MCP server configurations
        """
        servers = {}

        # Look for mcpServers key specifically
        if "mcpServers" in config and isinstance(config["mcpServers"], dict):
            servers.update(config["mcpServers"])
            logger.debug(f"Found {len(config['mcpServers'])} servers in {source_file}")
        else:
            logger.debug(f"No mcpServers found in {source_file}")

        return servers

    def combine_mcp_servers(self) -> None:
        """
        Combine MCP servers from all existing configuration files.
        """
        all_servers = {}
        server_sources = {}

        for config_file in self.existing_files:
            config = self.parse_config_file(config_file)
            if not config:
                continue

            servers = self.extract_mcp_servers(config, config_file.name)

            for server_name, server_config in servers.items():
                if server_name in all_servers:
                    # Check if configurations are identical
                    if all_servers[server_name] != server_config:
                        logger.warning(
                            f"Conflicting configuration for server '{server_name}' "
                            f"between {server_sources[server_name]} and {config_file.name}"
                        )
                        # Use the more complete configuration (more keys)
                        if len(server_config) > len(all_servers[server_name]):
                            all_servers[server_name] = server_config
                            server_sources[server_name] = config_file.name
                            logger.info(
                                f"Updated '{server_name}' with config from {config_file.name}"
                            )
                    else:
                        logger.debug(
                            f"Duplicate server '{server_name}' found in {config_file.name} (identical config)"
                        )
                else:
                    all_servers[server_name] = server_config
                    server_sources[server_name] = config_file.name

        self.mcp_servers = all_servers
        logger.info(f"Combined {len(self.mcp_servers)} unique MCP servers")

        # Log server summary
        for server_name, source in server_sources.items():
            logger.debug(f"Server '{server_name}' from {source}")

    def generate_unified_config(self) -> Dict[str, Any]:
        """
        Generate a unified configuration with all MCP servers.

        Returns:
            Unified configuration dictionary
        """
        unified_config = {
            "mcpServers": self.mcp_servers,
        }

        return unified_config

    def create_backup(self, file_path: Path) -> Path:
        """
        Create a backup of the configuration file.

        Args:
            file_path: Path to the file to backup

        Returns:
            Path to the backup file
        """
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        logger.debug(f"Created backup: {backup_path}")
        return backup_path

    def write_unified_config(
        self, file_path: Path, unified_config: Dict[str, Any]
    ) -> bool:
        """
        Write the unified configuration to a file.

        Args:
            file_path: Path to write the configuration
            unified_config: Unified configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if file exists and backup is enabled
            if self.backup and file_path.exists():
                self.create_backup(file_path)

            # Write unified configuration
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(unified_config, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully wrote unified config to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error writing unified config to {file_path}: {e}")
            return False

    def replace_all_configs(self) -> Dict[str, bool]:
        """
        Replace all configuration files with the unified configuration.

        Returns:
            Dictionary mapping file paths to write success status
        """
        if not self.mcp_servers:
            logger.error("No MCP servers found to write")
            return {}

        unified_config = self.generate_unified_config()
        results = {}

        # Write to all configured file paths (both existing and new)
        for file_path_str in self.config_files:
            file_path = Path(file_path_str).expanduser()
            success = self.write_unified_config(file_path, unified_config.copy())
            results[str(file_path)] = success

        successful_writes = sum(results.values())
        logger.info(
            f"Successfully wrote unified config to {successful_writes}/{len(results)} files"
        )

        return results

    def remove_mcp_server(self, server_key: str) -> bool:
        """
        Remove an MCP server from all configuration files.

        Args:
            server_key: The server key/name to remove

        Returns:
            True if server was found and removed, False otherwise
        """
        if server_key not in self.mcp_servers:
            logger.warning(f"Server '{server_key}' not found in current configuration")
            return False

        # Remove from combined servers
        del self.mcp_servers[server_key]
        logger.info(f"Removed server '{server_key}' from configuration")

        # Update all config files
        unified_config = self.generate_unified_config()
        results = {}

        for file_path_str in self.config_files:
            file_path = Path(file_path_str).expanduser()
            if file_path.exists():
                success = self.write_unified_config(file_path, unified_config.copy())
                results[str(file_path)] = success

        successful_writes = sum(results.values())
        total_files = len([f for f in results.keys()])
        logger.info(
            f"Successfully updated {successful_writes}/{total_files} files after removal"
        )

        return True

    def list_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all MCP servers found in configuration files.

        Returns:
            Dictionary of server configurations
        """
        return self.mcp_servers.copy()

    def get_server_count(self) -> int:
        """
        Get the number of MCP servers.

        Returns:
            Number of servers
        """
        return len(self.mcp_servers)

    def get_selected_apps_info(self) -> Dict[str, Any]:
        """
        Get information about selected apps.

        Returns:
            Dictionary with app information
        """
        from .apps import get_app

        info = {
            "selected_apps": [],
            "config_files": self.config_files,
            "using_custom_files": len(self.selected_apps) == 0,
        }

        for app_name in self.selected_apps:
            app = get_app(app_name)
            if app:
                info["selected_apps"].append(
                    {
                        "name": app.name,
                        "display_name": app.display_name,
                        "description": app.description,
                        "config_path": app.config_path,
                    }
                )

        return info

    def get_config_files_status(self) -> Dict[str, bool]:
        """
        Get the status of all configured files.

        Returns:
            Dictionary mapping file paths to existence status
        """
        status = {}
        for file_path in self.config_files:
            expanded_path = Path(file_path).expanduser()
            status[file_path] = expanded_path.exists()
        return status
