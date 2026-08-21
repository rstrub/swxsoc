from typing import Any, Optional

from pathlib import Path

import swxsoc

from swxsoc.db.tracker.config import load_config
from swxsoc.db.tracker.config.config import MetaTrackerConfiguration

log = swxsoc.log


class _ConfigurationProxy:
    """
    Lazy-loading proxy for CONFIGURATION.
    
    Delays loading the configuration until first access, allowing the mission
    to be set before the configuration is actually loaded.
    """
    _instance: Optional[MetaTrackerConfiguration] = None
    
    def _ensure_loaded(self) -> MetaTrackerConfiguration:
        """Load configuration if not already loaded."""
        if self._instance is None:
            self._instance = load_config()
        return self._instance
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying configuration."""
        return getattr(self._ensure_loaded(), name)
    
    def __repr__(self) -> str:
        """Delegate repr to the underlying configuration."""
        return repr(self._ensure_loaded())
    
    def __str__(self) -> str:
        """Delegate str to the underlying configuration."""
        return str(self._ensure_loaded())
    
    def _reload(self, config: Optional[dict[str, Any]] = None) -> None:
        """Force reload of configuration."""
        if config is None:
            self._instance = load_config()
        else:
            self._instance = load_config(config)


CONFIGURATION = _ConfigurationProxy()
_package_directory = Path(__file__).parent
_test_files_directory = _package_directory / "tests" / "test_files"


def get_config() -> MetaTrackerConfiguration:
    """New Mission: Get the current configuration, loading it if necessary."""
    return CONFIGURATION._ensure_loaded()


def set_config(config: Optional[dict[str, Any]] = None) -> None:
    """
    Reload the configuration.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary. If None, reloads from swxsoc config.
    """
    # Clear cached table metadata to prevent mixing missions
    from swxsoc.db.tracker.database.tables import base_table
    from swxsoc.db.tracker.database.tables import (
        file_level_table,
        file_type_table,
        instrument_table,
        instrument_configuration_table,
        science_file_table,
        science_product_table,
        status_table,
    )
    
    # Clear all metadata and mappers
    base_table.clear_metadata()
    
    # Define table modules and their cache attributes to clear
    table_cache_specs = [
        (file_level_table, ['_cached_class', '_cached_for_mission']),
        (file_type_table, ['_cached_class', '_cached_for_mission']),
        (instrument_table, ['_cached_class', '_cached_for_mission']),
        (instrument_configuration_table, ['_cached_table_class', '_cached_for_mission']),
        (science_file_table, ['_cached_class', '_cached_for_mission']),
        (science_product_table, ['_cached_class', '_cached_for_mission']),
        (status_table, ['_cached_class', '_cached_association', '_cached_for_mission']),
    ]
    
    # Clear all cached table classes
    for table_module, cache_attrs in table_cache_specs:
        for attr_name in cache_attrs:
            setattr(table_module, attr_name, None)
    
    # Reload configuration
    CONFIGURATION._reload(config)

# explicit exports
__all__ = [
    "CONFIGURATION",
    "_test_files_directory",
    "get_config",
    "set_config",
    "log",
]
