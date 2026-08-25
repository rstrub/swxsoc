# File Level Table
# Schema:
#   short_name: str (primary key)
#   full_name: str
#   description: str

from typing import Any

from sqlalchemy import Column, String

import swxsoc

from . import base_table as Base

_current_class: Any = None


def _build_class() -> Any:
    class FileLevelTable(Base.Base):  # type: ignore
        # Name Of Table
        __tablename__ = f"{swxsoc.config['mission']['mission_name']}_file_level"

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

    return FileLevelTable


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
