# Instrument Configuration Table
# Schema:
#   instrument_configuration_id: int (primary key)
#   instrument_{i+1}_id: int (foreign key)

from typing import Any, Optional

from sqlalchemy import Column, ForeignKey, Integer

from swxsoc.db.tracker import get_config

from . import base_table as Base

_cached_table_class: Optional[Any] = None
_cached_for_mission: Optional[str] = None


def return_class() -> Any:
    """
    Return the InstrumentConfigurationTable class, creating it if necessary.
    
    The class is cached per mission. If the mission changes, the class is regenerated.
    """
    global _cached_table_class, _cached_for_mission
    
    config = get_config()
    current_mission = config.mission_name
    
    # Regenerate if mission changed or not yet created
    if _cached_table_class is None or _cached_for_mission != current_mission:
        # Get the current mission's base
        mission_base = Base.get_or_create_base()
        
        table_dict = {
            "__tablename__": f"{current_mission}_instrument_configuration",
            "instrument_configuration_id": Column(Integer, primary_key=True),
        }

        for i in range(len(config.instruments)):
            table_dict[f"instrument_{i + 1}_id"] = Column(
                Integer, ForeignKey(f"{current_mission}_instrument.instrument_id")
            )

        _cached_table_class = type("InstrumentConfigurationTable", (mission_base,), table_dict)
        _cached_for_mission = current_mission
    
    return _cached_table_class


# For backward compatibility with direct imports
# This will create the class when first accessed
class InstrumentConfigurationTable:
    """
    Lazy wrapper for the dynamically generated InstrumentConfigurationTable.
    
    Use return_class() to get the actual SQLAlchemy table class.
    """
    @staticmethod
    def return_class() -> Any:
        return return_class()
