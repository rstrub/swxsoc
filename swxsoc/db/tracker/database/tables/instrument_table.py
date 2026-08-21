# Instrument Table
# Schema:
#   instrument_id: int (primary key)
#   instrument_configuration_id: int (foreign key)
#   mode: str
#   reference_timestamp: datetime

from typing import Any

from sqlalchemy import Column, Integer, String

from swxsoc.db.tracker import get_config

from . import base_table as Base


_cached_class: Any = None
_cached_for_mission: str | None = None


def return_class() -> Any:
    """Return InstrumentTable class for the current mission."""
    global _cached_class, _cached_for_mission
    config = get_config()
    current_mission = config.mission_name
    
    if _cached_class is None or _cached_for_mission != current_mission:
        # Get the current mission's base
        mission_base = Base.get_or_create_base()
        
        class InstrumentTable(mission_base):  # type: ignore
            __tablename__ = f"{current_mission}_instrument"
            
            # ID Of Instrument (Primary Key)
            instrument_id = Column(Integer, primary_key=True)
            
            # Full Name Of Instrument
            full_name = Column(String)
            
            # Short Name Of Instrument
            short_name = Column(String)
            
            # Description Of Instrument
            description = Column(String)
            
            def __init__(self, instrument_id: int, full_name: str, short_name: str, description: str) -> None:
                """
                Constructor for Instrument Table
                """
                self.instrument_id = instrument_id  # type: ignore[assignment]
                self.full_name = full_name  # type: ignore[assignment]
                self.short_name = short_name  # type: ignore[assignment]
                self.description = description  # type: ignore[assignment]
            
            def __repr__(self) -> str:
                return super().__repr__()  # type: ignore[no-any-return]
        
        _cached_class = InstrumentTable
        _cached_for_mission = current_mission
    
    return _cached_class
