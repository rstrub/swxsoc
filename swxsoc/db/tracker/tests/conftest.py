"""
Shared pytest fixtures for all metatracker tests.

These fixtures are automatically available to all test modules in the package.
"""

import pytest


@pytest.fixture(autouse=True, scope="function")
def default_tracker_mission(monkeypatch):
    """
    Force tracker tests to run with the PADRE mission configuration.
    
    With lazy loading, the configuration is only loaded when first accessed,
    so we set the mission and reload the config to ensure it picks up PADRE.
    """
    monkeypatch.setenv("SWXSOC_MISSION", "padre")
    import swxsoc  # type: ignore

    swxsoc.reconfigure()
    
    # Reload tracker configuration with the correct mission
    from swxsoc.db.tracker import set_config
    set_config()
