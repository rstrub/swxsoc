# File Level Table
# Schema:
#   short_name: str (primary key)
#   full_name: str
#   description: str

from typing import Any

from sqlalchemy import Column, String

from swxsoc.db.tracker import get_config

from . import base_table as Base


_cached_class: Any = None
_cached_for_mission: str | None = None


def return_class() -> Any:
    """Return FileLevelTable class for the current mission."""
    global _cached_class, _cached_for_mission
    config = get_config()
    current_mission = config.mission_name
    
    if _cached_class is None or _cached_for_mission != current_mission:
        # Get the current mission's base
        mission_base = Base.get_or_create_base()
        
        class FileLevelTable(mission_base):  # type: ignore
            __tablename__ = f"{current_mission}_file_level"
            
            # Short Name Of File Level
            short_name = Column(String, primary_key=True)
            
            # Full Name Of File Level
            full_name = Column(String)
            
            # Description Of File Level
            description = Column(String)
            
            def __init__(self, full_name: str, short_name: str, description: str) -> None:
                """
                Constructor for File Level Table
                """
                self.full_name = full_name  # type: ignore[assignment]
                self.short_name = short_name  # type: ignore[assignment]
                self.description = description  # type: ignore[assignment]
            
            def __repr__(self) -> str:
                return super().__repr__()  # type: ignore[no-any-return]
        
        _cached_class = FileLevelTable
        _cached_for_mission = current_mission
    
    return _cached_class
