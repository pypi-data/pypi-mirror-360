"""
Tests for the apps module.
"""

import pytest

from mcp_config_sync.apps import (
    MCP_APPS,
    get_all_apps,
    get_app,
    get_app_names,
    get_config_paths_for_apps,
    validate_app_names,
)


class TestApps:
    """Test cases for apps module functions."""

    def test_get_app_existing(self):
        """Test getting an existing app."""
        app = get_app("amazonq")
        assert app is not None
        assert app.name == "amazonq"
        assert app.display_name == "Amazon Q"
        assert "amazonq" in app.config_path

    def test_get_app_nonexistent(self):
        """Test getting a non-existent app."""
        app = get_app("nonexistent")
        assert app is None

    def test_get_app_case_insensitive(self):
        """Test that app lookup is case insensitive."""
        app1 = get_app("amazonq")
        app2 = get_app("AMAZONQ")
        app3 = get_app("AmazonQ")
        assert app1 == app2 == app3

    def test_get_all_apps(self):
        """Test getting all apps."""
        apps = get_all_apps()
        assert isinstance(apps, dict)
        assert len(apps) >= 3  # At least amazonq, cline, claude-desktop
        assert "amazonq" in apps
        assert "cline" in apps
        assert "claude-desktop" in apps

    def test_get_app_names(self):
        """Test getting app names."""
        names = get_app_names()
        assert isinstance(names, list)
        assert len(names) >= 3
        assert "amazonq" in names
        assert "cline" in names
        assert "claude-desktop" in names

    def test_get_config_paths_for_apps(self):
        """Test getting config paths for specific apps."""
        paths = get_config_paths_for_apps(["amazonq", "cline"])
        assert len(paths) == 2
        assert any("amazonq" in path for path in paths)
        assert any("cline" in path for path in paths)

    def test_get_config_paths_for_invalid_app(self):
        """Test getting config paths with invalid app name."""
        with pytest.raises(ValueError, match="Unknown app: invalid"):
            get_config_paths_for_apps(["amazonq", "invalid"])

    def test_validate_app_names_valid(self):
        """Test validating valid app names."""
        invalid = validate_app_names(["amazonq", "cline"])
        assert invalid == []

    def test_validate_app_names_invalid(self):
        """Test validating invalid app names."""
        invalid = validate_app_names(["amazonq", "invalid1", "invalid2"])
        assert len(invalid) == 2
        assert "invalid1" in invalid
        assert "invalid2" in invalid

    def test_validate_app_names_mixed(self):
        """Test validating mixed valid/invalid app names."""
        invalid = validate_app_names(["amazonq", "invalid", "cline"])
        assert len(invalid) == 1
        assert "invalid" in invalid

    def test_mcp_apps_structure(self):
        """Test that MCP_APPS has the expected structure."""
        assert isinstance(MCP_APPS, dict)

        for app_name, app in MCP_APPS.items():
            assert isinstance(app_name, str)
            assert app.name == app_name
            assert isinstance(app.display_name, str)
            assert isinstance(app.config_path, str)
            assert isinstance(app.description, str)
            # homepage is optional
            if app.homepage is not None:
                assert isinstance(app.homepage, str)
