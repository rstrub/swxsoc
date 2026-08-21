# File Type Table
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
    """Return FileTypeTable class for the current mission."""
    global _cached_class, _cached_for_mission
    config = get_config()
    current_mission = config.mission_name
    
    if _cached_class is None or _cached_for_mission != current_mission:
        # Get the current mission's base
        mission_base = Base.get_or_create_base()
        
        class FileTypeTable(mission_base):  # type: ignore
            __tablename__ = f"{current_mission}_file_type"
            
            # Short Name Of File Type
            short_name = Column(String, primary_key=True)
            
            # Full Name Of File Type
            full_name = Column(String)
            
            # Description Of File Type
            description = Column(String)
            
            # Extension Of File Type
            extension = Column(String)
            
            def __init__(self, short_name: str, full_name: str, description: str, extension: str) -> None:
                """
                Constructor for File Type Table
                """
                self.short_name = short_name  # type: ignore[assignment]
                self.full_name = full_name  # type: ignore[assignment]
                self.description = description  # type: ignore[assignment]
                self.extension = extension  # type: ignore[assignment]
            
            def __repr__(self) -> str:
                return super().__repr__()  # type: ignore[no-any-return]
        
        _cached_class = FileTypeTable
        _cached_for_mission = current_mission
    
    return _cached_class
