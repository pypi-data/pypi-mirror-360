"""
Command Line Interface for MCP Config Sync

This module provides the CLI functionality for the MCP Config Sync tool.
"""

import argparse
import logging
import sys
from pathlib import Path


from .apps import get_all_apps, get_app_names, get_existing_apps, validate_app_names
from .sync import MCPServerSync

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: Enable debug level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def print_available_apps() -> None:
    """
    Print a list of all available MCP apps.
    """
    apps = get_all_apps()
    existing_apps = {app.name for app in get_existing_apps()}

    print("\n" + "=" * 60)
    print("AVAILABLE MCP APPLICATIONS")
    print("=" * 60)

    if not apps:
        print("\nNo MCP applications registered.")
        return

    print(f"\nFound {len(apps)} registered MCP applications:")
    print("-" * 40)

    for app in sorted(apps.values(), key=lambda x: x.name):
        status = "✓ CONFIG EXISTS" if app.name in existing_apps else "✗ NO CONFIG"
        print(f"\n📱 App: {app.name}")
        print(f"   Display Name: {app.display_name}")
        print(f"   Description: {app.description}")
        print(f"   Config Path: {app.config_path}")
        print(f"   Status: {status}")
        if app.homepage:
            print(f"   Homepage: {app.homepage}")

    print("\n" + "=" * 60)
    print(
        f"Total: {len(apps)} applications ({len(existing_apps)} with existing configs)"
    )
    print("=" * 60)


def print_server_list(servers: dict) -> None:
    """
    Print a formatted list of MCP servers.

    Args:
        servers: Dictionary of server configurations
    """
    print("\n" + "=" * 60)
    print("ALL MCP SERVERS")
    print("=" * 60)

    if not servers:
        print("\nNo MCP servers found in any configuration files.")
        return

    print(f"\nFound {len(servers)} MCP servers:")
    print("-" * 40)

    for server_name, server_config in sorted(servers.items()):
        print(f"\n🔧 Server: {server_name}")
        if isinstance(server_config, dict):
            # Show key configuration details
            if "command" in server_config:
                print(f"   Command: {server_config['command']}")
            if "args" in server_config and isinstance(server_config["args"], list):
                print(f"   Args: {' '.join(server_config['args'])}")
            if "env" in server_config and isinstance(server_config["env"], dict):
                env_vars = list(server_config["env"].keys())
                print(f"   Environment Variables: {', '.join(env_vars)}")

            # Show all other keys
            other_keys = [
                k for k in server_config.keys() if k not in ["command", "args", "env"]
            ]
            if other_keys:
                for key in other_keys:
                    value = server_config[key]
                    if isinstance(value, (str, int, bool)):
                        print(f"   {key.capitalize()}: {value}")
                    elif isinstance(value, list):
                        print(f"   {key.capitalize()}: [{', '.join(map(str, value))}]")
                    elif isinstance(value, dict):
                        print(f"   {key.capitalize()}: {{{len(value)} items}}")
                    else:
                        print(f"   {key.capitalize()}: {type(value).__name__}")

    print("\n" + "=" * 60)
    print(f"Total: {len(servers)} servers")
    print("=" * 60)


def print_summary(syncer: MCPServerSync) -> None:
    """
    Print a summary of discovered MCP servers and file operations.

    Args:
        syncer: MCPServerSync instance
    """
    print("\n" + "=" * 60)
    print("MCP SERVER SYNCHRONIZATION SUMMARY")
    print("=" * 60)

    # Show selected apps information
    apps_info = syncer.get_selected_apps_info()
    if apps_info["using_custom_files"]:
        print("\nUsing custom configuration files:")
        for file_path in apps_info["config_files"]:
            expanded_path = Path(file_path).expanduser()
            status = "✓ EXISTS" if expanded_path.exists() else "✗ MISSING"
            print(f"  {status} {file_path}")
    else:
        print(f"\nSelected Applications: {len(apps_info['selected_apps'])}")
        for app_info in apps_info["selected_apps"]:
            expanded_path = Path(app_info["config_path"]).expanduser()
            status = "✓ EXISTS" if expanded_path.exists() else "✗ MISSING"
            print(f"  {status} {app_info['display_name']} ({app_info['name']})")
            print(f"      Path: {app_info['config_path']}")

    print(f"\nExisting Files Found: {len(syncer.existing_files)}")
    for config_file in syncer.existing_files:
        print(f"  - {config_file}")

    servers = syncer.list_all_servers()
    print(f"\nCombined MCP Servers: {len(servers)}")
    for server_name, server_config in servers.items():
        print(f"\n  Server: {server_name}")
        if isinstance(server_config, dict):
            for key, value in server_config.items():
                if isinstance(value, (str, int, bool)):
                    print(f"    {key}: {value}")
                elif isinstance(value, list):
                    print(f"    {key}: [{', '.join(map(str, value))}]")
                elif isinstance(value, dict):
                    print(f"    {key}: {{{len(value)} items}}")
                else:
                    print(f"    {key}: {type(value).__name__}")

    print("\n" + "=" * 60)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Synchronize MCP server configurations across tool configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
This script reads from JSON configuration files, combines all unique
MCP servers, and replaces all original files with the unified configuration.

Available applications:
{chr(10).join(f'  {name}: {get_all_apps()[name].display_name}' for name in sorted(get_app_names()))}

Examples:
  mcp-config-sync                           # Sync all registered apps
  mcp-config-sync --apps amazonq cline     # Sync specific apps only
  mcp-config-sync --list-apps              # Show available apps
  mcp-config-sync --list-all               # List all MCP servers
  mcp-config-sync --remove server-name     # Remove a specific server
  mcp-config-sync --no-backup              # Skip creating backups
  mcp-config-sync --verbose --dry-run      # Preview changes
        """,
    )

    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument(
        "--list-apps",
        action="store_true",
        help="List all available MCP applications and their status",
    )

    action_group.add_argument(
        "--list-all",
        action="store_true",
        help="List all MCP servers found in configuration files",
    )

    action_group.add_argument(
        "--remove",
        metavar="SERVER_KEY",
        help="Remove the specified MCP server from all configuration files",
    )

    # Configuration arguments
    config_group = parser.add_mutually_exclusive_group()

    config_group.add_argument(
        "--apps",
        nargs="+",
        metavar="APP_NAME",
        help=f"Sync specific apps only. Available: {', '.join(sorted(get_app_names()))}",
    )

    config_group.add_argument(
        "--config-files",
        nargs="+",
        help="Custom list of configuration file paths (overrides app selection)",
    )

    # Option arguments
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup files before modification",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes (not applicable to --list-* commands)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def main() -> None:
    """Main function to handle command line arguments and execute synchronization."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    setup_logging(args.verbose)

    try:
        # Handle list-apps action first
        if args.list_apps:
            print_available_apps()
            return

        # Validate app names if provided
        if args.apps:
            invalid_apps = validate_app_names(args.apps)
            if invalid_apps:
                logger.error(f"Unknown apps: {', '.join(invalid_apps)}")
                logger.info(f"Available apps: {', '.join(sorted(get_app_names()))}")
                sys.exit(1)

        # Initialize synchronizer
        syncer = MCPServerSync(
            config_files=args.config_files,
            apps=args.apps,
            backup=not args.no_backup,
        )

        # Discover existing configuration files
        existing_files = syncer.discover_config_files()

        if not existing_files:
            logger.warning("No existing configuration files found")
            if not args.list_all:
                logger.info(
                    "Will create new configuration files with any MCP servers found"
                )

        # Combine MCP servers from existing configs
        syncer.combine_mcp_servers()

        # Handle list-all action
        if args.list_all:
            servers = syncer.list_all_servers()
            print_server_list(servers)
            return

        # Handle remove action
        if args.remove:
            servers = syncer.list_all_servers()
            if not servers:
                logger.error("No MCP servers found in any existing configuration files")
                sys.exit(1)

            if args.dry_run:
                if args.remove in servers:
                    print(
                        f"\n[DRY RUN] Would remove server '{args.remove}' from all configuration files"
                    )
                    print(f"Server '{args.remove}' is currently configured with:")
                    server_config = servers[args.remove]
                    for key, value in server_config.items():
                        print(f"  {key}: {value}")
                    print(f"After removal, {len(servers) - 1} servers would remain")
                else:
                    print(
                        f"\n[DRY RUN] Server '{args.remove}' not found in current configuration"
                    )
                return

            # Store count before removal for accurate reporting
            servers_before = syncer.get_server_count()
            success = syncer.remove_mcp_server(args.remove)
            servers_after = syncer.get_server_count()

            if success:
                print(
                    f"\n✅ Successfully removed server '{args.remove}' from all configuration files"
                )
                print(f"   Servers before removal: {servers_before}")
                print(f"   Servers after removal: {servers_after}")
            else:
                print(
                    f"\n❌ Failed to remove server '{args.remove}' - server not found"
                )
                sys.exit(1)
            return

        # Default sync action
        if syncer.get_server_count() == 0:
            logger.error("No MCP servers found in any existing configuration files")
            logger.info("Nothing to synchronize")
            sys.exit(1)

        # Print summary
        print_summary(syncer)

        if args.dry_run:
            print("\n[DRY RUN] No files were modified")
            apps_info = syncer.get_selected_apps_info()
            print(
                f"Would write unified config to {len(apps_info['config_files'])} files"
            )
            return

        # Replace all configurations with unified config
        results = syncer.replace_all_configs()

        # Print results
        failed_writes = [path for path, success in results.items() if not success]
        if failed_writes:
            print(f"\nFailed to write {len(failed_writes)} files:")
            for path in failed_writes:
                print(f"  - {path}")
            sys.exit(1)
        else:
            print(
                f"\n✅ Successfully wrote unified MCP configuration to all {len(results)} files"
            )
            print(f"   Combined {syncer.get_server_count()} unique MCP servers")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
