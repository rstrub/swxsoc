"""
Module to handle database operations
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from swxsoc.db._optional import HAS_SQLALCHEMY, require_tracker_dependencies

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session, sessionmaker

__all__ = [
    "HAS_SQLALCHEMY",
    "check_connection",
    "create_engine",
    "create_session",
    "reconfigure",
]


# Function to check if you can connect to the database with SQLAlchemy
def check_connection(engine: Engine) -> bool:
    """
    Check Connection

    :param engine: SQLAlchemy Engine
    :type engine: Engine
    :return: Connection Status
    :rtype: bool
    """

    require_tracker_dependencies()
    with engine.connect():
        return True


def create_engine(db_host: str) -> Engine:
    """
    Create Engine

    :param db_host: Database Host
    :type db_host: str
    :return: SQLAlchemy Engine
    :rtype: Engine
    """

    require_tracker_dependencies()
    from sqlalchemy import create_engine as sqlalchemy_create_engine

    engine = sqlalchemy_create_engine(db_host)
    return engine


# Function to create a database session
def create_session(engine: Engine) -> sessionmaker[Session]:
    """
    Create Session

    :param engine: SQLAlchemy Engine
    :type engine: Engine
    :return: SQLAlchemy Session
    :rtype: sessionmaker[Session]
    """

    require_tracker_dependencies()
    from sqlalchemy.orm import sessionmaker

    session = sessionmaker(bind=engine)
    return session


def reconfigure() -> None:
    """
    Rebuild all ORM table classes to match the currently active mission.

    Thin wrapper around ``swxsoc.db.tables.reconfigure()``. Must be called
    any time ``swxsoc.reconfigure()`` changes the active mission, so that
    mission-dependent table schemas -- table names, foreign key targets, and
    the dynamic ``instrument_N_id`` columns -- are rebuilt to match instead
    of retaining stale classes from the previous mission.

    The import is deferred to avoid a circular import, since
    ``swxsoc.db.tables`` imports from ``swxsoc.db`` at module load time.
    """
    require_tracker_dependencies()
    from swxsoc.db.tables import reconfigure as _reconfigure_tables

    _reconfigure_tables()
