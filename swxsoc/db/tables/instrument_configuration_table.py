# Instrument Configuration Table
# Schema:
#   instrument_configuration_id: int (primary key)
#   instrument_{i+1}_id: int (foreign key)
#
# The number of instrument_{i+1}_id columns depends on the active mission's
# instrument list, which can change at runtime via swxsoc.reconfigure(). The
# ORM class is therefore built lazily (on first use) rather than at module
# import time, and rebuilt via reconfigure() whenever the mission changes,
# mirroring swxsoc.util.config's reconfigure() pattern. Consumers must
# always obtain the class via return_class() rather than importing a
# module-level class.

from typing import Any

from sqlalchemy import Column, ForeignKey, Integer

import swxsoc

from . import base_table as Base

_current_class: Any = None


def _build_class() -> Any:
    mission_name = swxsoc.config["mission"]["mission_name"]
    inst_names = swxsoc.config["mission"]["inst_names"]

    table_dict: dict[str, Any] = {
        "__tablename__": f"{mission_name}_instrument_configuration",
        "instrument_configuration_id": Column(Integer, primary_key=True),
    }

    for i in range(len(inst_names)):
        table_dict[f"instrument_{i + 1}_id"] = Column(
            Integer,
            ForeignKey(f"{mission_name}_instrument.instrument_id"),
        )

    return type("InstrumentConfigurationTable", (Base.Base,), table_dict)


def reconfigure() -> Any:
    """
    Rebuild the ORM class for the currently active mission.
    """
    global _current_class
    _current_class = _build_class()
    return _current_class


def return_class() -> Any:
    """
    Return Class
    """
    if _current_class is None:
        reconfigure()
    return _current_class
