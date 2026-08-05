from typing import Any, Optional

from pathlib import Path

import swxsoc

from swxsoc.db.tracker.config import load_config
from swxsoc.db.tracker.config.config import MetaTrackerConfiguration

log = swxsoc.log
CONFIGURATION = load_config()
_package_directory = Path(__file__).parent
_test_files_directory = _package_directory / "tests" / "test_files"


def get_config() -> MetaTrackerConfiguration:
    return CONFIGURATION


def set_config(config: Optional[dict[str, Any]] = None) -> None:
    global CONFIGURATION

    if config is None:
        swxsoc.reconfigure()
        CONFIGURATION = load_config()
        return

    CONFIGURATION = load_config(config)


__all__ = [
    "CONFIGURATION",
    "_test_files_directory",
    "get_config",
    "set_config",
    "log",
]
