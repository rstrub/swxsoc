# Science Product Table
# Schema:
#   science_product_id: int (primary key)
#   instrument_configuration_id: int (foreign key)
#   mode: str
#   reference_timestamp: datetime

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from swxsoc.db.tracker import get_config

from . import base_table as Base

_cached_class: Any = None
_cached_for_mission: str | None = None


def return_class() -> Any:
    """Return the ScienceProductTable class, creating it if necessary."""
    global _cached_class, _cached_for_mission
    
    config = get_config()
    current_mission = config.mission_name
    
    if _cached_class is None or _cached_for_mission != current_mission:
        # Get the current mission's base
        mission_base = Base.get_or_create_base()
        
        class ScienceProductTable(mission_base):  # type: ignore
            __tablename__ = f"{current_mission}_science_product"

            # ID Of Science Product (Primary Key)
            science_product_id = Column(Integer, primary_key=True, autoincrement=True)

            # ID Of Instrument Configuration (Foreign Key)
            instrument_configuration_id = Column(
                Integer, ForeignKey(f"{current_mission}_instrument_configuration.instrument_configuration_id")
            )

            # Mode Of Science Product
            mode = Column(String)

            # Reference Timestamp Of Science Product
            reference_timestamp = Column(DateTime)

            children = relationship("ScienceFileTable", back_populates="parent", cascade="all, delete")

            def __init__(self, instrument_configuration_id: int, mode: str, reference_timestamp: datetime) -> None:
                """
                Constructor for Science Product Table
                """
                self.instrument_configuration_id = instrument_configuration_id  # type: ignore[assignment]
                self.mode = mode  # type: ignore[assignment]
                self.reference_timestamp = reference_timestamp  # type: ignore[assignment]

            def __repr__(self) -> str:
                return super().__repr__()  # type: ignore[no-any-return]
        
        _cached_class = ScienceProductTable
        _cached_for_mission = current_mission
    
    return _cached_class
