"""Helpers for optional database dependencies."""

from importlib.util import find_spec

HAS_SQLALCHEMY = find_spec("sqlalchemy") is not None
HAS_TENACITY = find_spec("tenacity") is not None


def require_tracker_dependencies(*, tenacity: bool = False) -> None:
    """Require dependencies used by tracker-backed database functionality.

    Parameters
    ----------
    tenacity : bool, optional
        Also require tenacity, which is needed by ``MetaTracker`` but not by
        the SQLAlchemy table helpers.

    Raises
    ------
    ImportError
        If a required optional dependency is unavailable.
    """
    missing = []
    if not HAS_SQLALCHEMY:
        missing.append("SQLAlchemy")
    if tenacity and not HAS_TENACITY:
        missing.append("tenacity")

    if missing:
        dependencies = " and ".join(missing)
        raise ImportError(
            f"{dependencies} is required for database tracker operations. "
            "Install it with: pip install swxsoc[tracker]"
        )
