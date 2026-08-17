# see license/LICENSE.rst
import os

try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

from swxsoc.util.config import load_config, print_config
from swxsoc.util.logger import _init_log

# Load user configuration
config = load_config()

log = _init_log(config=config)

_package_directory = os.path.dirname(os.path.abspath(__file__))
_data_directory = os.path.abspath(os.path.join(_package_directory, "data"))


# Function to reconfigure the module for testing
def reconfigure():
    """
    Reconfigure the module by reloading the configuration.

    This function reloads the configuration from the config.yml file
    and updates the global `config` variable. It also reloads dependent
    configurations (e.g., tracker) if their modules have been imported.
    This is useful for testing purposes when changes to the configuration
    file need to be applied without restarting the Python session.

    Example:
        from swxsoc import reconfigure

        # Reconfigure the module to reload the configuration
        reconfigure()
    """
    global config
    config = load_config()
    
    # Reload tracker configuration if it has been imported
    import sys
    if 'swxsoc.db.tracker' in sys.modules:
        try:
            from swxsoc.db import tracker
            #print(f"DEBUG: Reloading tracker config from reconfigure()")
            tracker.set_config()
            #print(f"DEBUG: Tracker config reloaded, mission={tracker.CONFIGURATION.mission_name}")
        except ImportError as e:
            #print(f"DEBUG: Failed to import tracker: {e}")
            pass  # tracker dependencies not available
    else:
        print(f"DEBUG: Tracker not in sys.modules, skipping reload")


# Then you can be explicit to control what ends up in the namespace,
__all__ = ["config", "print_config"]
