"""
Module to handle database operations
"""

from pathlib import Path

from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from swxsoc.db.config import load_config

_package_directory = Path(__file__).parent
_test_files_directory = _package_directory / "tests" / "test_files"

CONFIGURATION = load_config()


def reconfigure():
    """
    Reconfigure the module by reloading the configuration.

    This function reloads the configuration from the config.yml file
    and updates the global `CONFIGURATION` variable. It also reloads dependent
    configurations (e.g., tracker) if their modules have been imported.
    This is useful for testing purposes when changes to the configuration
    file need to be applied without restarting the Python session.

    Example:
        from swxsoc.db import reconfigure

        # Reconfigure the module to reload the configuration
        reconfigure()
    """
    global CONFIGURATION
    CONFIGURATION = load_config()


# Function to check if you can connect to the database with SQLAlchemy
def check_connection(engine: Engine) -> bool:
    """
    Check Connection

    :param engine: SQLAlchemy Engine
    :type engine: Engine
    :return: Connection Status
    :rtype: bool
    """

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

    session = sessionmaker(bind=engine)
    return session
