# SQLAlchemy Base Table

from typing import Any, Optional
from sqlalchemy.orm import declarative_base, clear_mappers

_cached_base: Optional[Any] = None
_cached_for_mission: Optional[str] = None

# Fallback global Base for backward compatibility
Base = declarative_base()


def get_or_create_base() -> Any:
    """
    Get or create the declarative base for the current mission.
    
    Creates a new base if the mission has changed, ensuring tables
    from different missions don't mix in the same metadata.
    """
    global _cached_base, _cached_for_mission
    
    from swxsoc.db.tracker import get_config
    config = get_config()
    current_mission = config.mission_name
    
    # Create new base if mission changed or not yet created
    if _cached_base is None or _cached_for_mission != current_mission:
        # Clear all existing mappers to allow remapping
        clear_mappers()
        _cached_base = declarative_base()
        _cached_for_mission = current_mission
        
        # Update the module-level Base for backward compatibility
        global Base
        Base = _cached_base
    
    return _cached_base


def clear_metadata() -> None:
    """
    Clear all table metadata from the base.
    
    This should be called when the mission configuration changes to ensure
    tables from different missions don't mix in the same metadata.
    """
    global _cached_base, _cached_for_mission
    _cached_base = None
    _cached_for_mission = None
    clear_mappers()
