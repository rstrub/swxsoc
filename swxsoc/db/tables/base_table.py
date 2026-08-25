# SQLAclchemy Base.Base Table
#
# Base is rebuilt (not just mutated) by reconfigure() so that all table
# classes mapped under a previous mission's registry are fully discarded
# rather than left registered alongside the new mission's classes. This
# avoids SQLAlchemy relationship()/string lookups becoming ambiguous when
# switching missions repeatedly within the same process (e.g. in tests).

from typing import Any

from sqlalchemy.orm import declarative_base

Base: Any = declarative_base()


def reconfigure() -> Any:
    """
    Replace the shared declarative base with a fresh one.

    Discards all previously mapped table classes so that mission-dependent
    schemas (table names, foreign keys, and dynamic instrument_N_id columns)
    can be rebuilt from scratch without colliding with stale classes still
    registered under the old base's registry.

    Returns
    -------
    Any
        The newly created declarative base.
    """
    global Base
    Base = declarative_base()
    return Base
