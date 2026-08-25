"""
Tests for the idempotent upsert behaviour of ``create_tables`` and the
individual ``populate_*`` / ``sync_instrument_configuration_schema`` helpers.

All tests use in-memory SQLite — no external database is required.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.engine import Engine

import swxsoc
from swxsoc.db import create_engine, create_session
from swxsoc.db.config import (
    compute_instrument_configurations,
    compute_instrument_metadata,
)
from swxsoc.db.tables import (
    create_tables,
    file_level_table,
    file_type_table,
    get_columns,
    instrument_configuration_table,
    instrument_table,
    populate_file_level_table,
    populate_file_type_table,
    populate_instrument_configuration_table,
    populate_instrument_table,
    science_product_table,
    sync_instrument_configuration_schema,
)
from swxsoc.db.tests import _optional_dependencies  # noqa: F401

MISSION_NAME = swxsoc.config["mission"]["mission_name"]


def _setup_db() -> Engine:
    """Return a fresh in-memory engine with all tables created and populated."""
    engine = create_engine("sqlite://")
    create_tables(engine)
    return engine


def test_create_tables_idempotent() -> None:
    """Calling ``create_tables`` multiple times must not raise and must leave
    row counts unchanged."""
    engine = _setup_db()
    session = create_session(engine)
    FileLevelTable = file_level_table.return_class()
    FileTypeTable = file_type_table.return_class()
    InstrumentTable = instrument_table.return_class()
    InstrumentConfigurationTable = instrument_configuration_table.return_class()

    def _count(table_cls: Any) -> int:
        with session.begin() as s:
            return s.query(table_cls).count()  # type: ignore[no-any-return]

    counts_first = {
        "file_level": _count(FileLevelTable),
        "file_type": _count(FileTypeTable),
        "instrument": _count(InstrumentTable),
        "instrument_config": _count(InstrumentConfigurationTable),
    }

    # Second and third calls — must be no-ops
    create_tables(engine)
    create_tables(engine)

    counts_after = {
        "file_level": _count(FileLevelTable),
        "file_type": _count(FileTypeTable),
        "instrument": _count(InstrumentTable),
        "instrument_config": _count(InstrumentConfigurationTable),
    }

    assert counts_first == counts_after


def test_upsert_inserts_new_file_level() -> None:
    """A new file level added to the config list is inserted on the next call."""
    engine = _setup_db()
    session = create_session(engine)
    FileLevelTable = file_level_table.return_class()

    new_level = {
        "short_name": "l5",
        "full_name": "Level 5",
        "description": "Level 5 File",
    }
    extended_levels = swxsoc.config["mission"]["data_levels"] + [new_level]

    populate_file_level_table(session, extended_levels, FileLevelTable)

    with session.begin() as s:
        row = s.query(FileLevelTable).filter_by(short_name="l5").first()
        assert row is not None
        assert row.full_name == "Level 5"
        assert row.description == "Level 5 File"


def test_upsert_updates_existing_file_level() -> None:
    """Changed metadata on an existing file level is updated in place."""
    engine = _setup_db()
    session = create_session(engine)
    FileLevelTable = file_level_table.return_class()

    # Mutate the first level's description
    mutated_levels = [dict(fl) for fl in swxsoc.config["mission"]["data_levels"]]
    mutated_levels[0]["description"] = "UPDATED DESCRIPTION"

    populate_file_level_table(session, mutated_levels, FileLevelTable)

    with session.begin() as s:
        row = (
            s.query(FileLevelTable)
            .filter_by(short_name=mutated_levels[0]["short_name"])
            .first()
        )
        assert row is not None
        assert row.description == "UPDATED DESCRIPTION"


def test_upsert_inserts_new_file_type() -> None:
    """A new file type is inserted."""
    engine = _setup_db()
    session = create_session(engine)
    FileTypeTable = file_type_table.return_class()

    new_type = {
        "short_name": "hdf5",
        "full_name": "Hierarchical Data Format",
        "description": "HDF5 File",
        "extension": ".h5",
    }
    extended_types = swxsoc.config["file_types"] + [new_type]

    populate_file_type_table(session, extended_types, FileTypeTable)

    with session.begin() as s:
        row = s.query(FileTypeTable).filter_by(short_name="hdf5").first()
        assert row is not None
        assert row.extension == ".h5"


def test_upsert_updates_existing_file_type() -> None:
    """Changed metadata on an existing file type is updated."""
    engine = _setup_db()
    session = create_session(engine)
    FileTypeTable = file_type_table.return_class()

    mutated_types = [dict(ft) for ft in swxsoc.config["file_types"]]
    mutated_types[0]["description"] = "UPDATED FILE TYPE DESC"

    populate_file_type_table(session, mutated_types, FileTypeTable)

    with session.begin() as s:
        row = (
            s.query(FileTypeTable)
            .filter_by(short_name=mutated_types[0]["short_name"])
            .first()
        )
        assert row is not None
        assert row.description == "UPDATED FILE TYPE DESC"


def test_upsert_inserts_new_instrument() -> None:
    """A new instrument is inserted when its id is not yet in the table."""
    engine = _setup_db()
    session = create_session(engine)
    InstrumentTable = instrument_table.return_class()

    max_id = max(inst["instrument_id"] for inst in compute_instrument_metadata())
    new_instrument = {
        "instrument_id": max_id + 1,
        "short_name": "newi",
        "full_name": "New Instrument",
        "description": "A brand-new instrument",
    }
    extended = compute_instrument_metadata() + [new_instrument]

    populate_instrument_table(session, extended, InstrumentTable)

    with session.begin() as s:
        row = s.query(InstrumentTable).filter_by(instrument_id=max_id + 1).first()
        assert row is not None
        assert row.short_name == "newi"


def test_upsert_updates_existing_instrument() -> None:
    """Changed metadata on an existing instrument is updated."""
    engine = _setup_db()
    session = create_session(engine)
    InstrumentTable = instrument_table.return_class()

    mutated = [dict(inst) for inst in compute_instrument_metadata()]
    mutated[0]["description"] = "UPDATED INSTRUMENT DESC"

    populate_instrument_table(session, mutated, InstrumentTable)

    with session.begin() as s:
        row = (
            s.query(InstrumentTable)
            .filter_by(instrument_id=mutated[0]["instrument_id"])
            .first()
        )
        assert row is not None
        assert row.description == "UPDATED INSTRUMENT DESC"


def test_upsert_inserts_new_instrument_configuration() -> None:
    """A new instrument configuration row is inserted."""
    engine = _setup_db()
    session = create_session(engine)
    InstrumentConfigurationTable = instrument_configuration_table.return_class()

    max_id = max(
        ic["instrument_configuration_id"] for ic in compute_instrument_configurations()
    )
    # Build a new config row using the same number of instrument_N_id keys
    new_config = {"instrument_configuration_id": max_id + 1}
    for i in range(len(swxsoc.config["mission"]["inst_names"])):
        new_config[f"instrument_{i + 1}_id"] = None
    # Point the first instrument slot to instrument 1
    new_config["instrument_1_id"] = 1

    extended = compute_instrument_configurations() + [new_config]

    populate_instrument_configuration_table(
        session, extended, InstrumentConfigurationTable
    )

    with session.begin() as s:
        row = (
            s.query(InstrumentConfigurationTable)
            .filter_by(instrument_configuration_id=max_id + 1)
            .first()
        )
        assert row is not None
        assert row.instrument_1_id == 1


def test_upsert_updates_existing_instrument_configuration() -> None:
    """Changed instrument_N_id on an existing configuration is updated."""
    engine = _setup_db()
    session = create_session(engine)
    InstrumentConfigurationTable = instrument_configuration_table.return_class()

    mutated = [dict(ic) for ic in compute_instrument_configurations()]
    # Pick a config that has instrument_1_id set and clear it
    target = mutated[0]
    original_val = target.get("instrument_1_id")
    target["instrument_1_id"] = None

    populate_instrument_configuration_table(
        session, mutated, InstrumentConfigurationTable
    )

    with session.begin() as s:
        row = (
            s.query(InstrumentConfigurationTable)
            .filter_by(
                instrument_configuration_id=target["instrument_configuration_id"]
            )
            .first()
        )
        assert row is not None
        assert row.instrument_1_id is None

    # Restore and re-upsert to prove update works both ways
    target["instrument_1_id"] = original_val
    populate_instrument_configuration_table(
        session, mutated, InstrumentConfigurationTable
    )

    with session.begin() as s:
        row = (
            s.query(InstrumentConfigurationTable)
            .filter_by(
                instrument_configuration_id=target["instrument_configuration_id"]
            )
            .first()
        )
        assert row is not None
        assert row.instrument_1_id == original_val


def test_sync_schema_noop_when_up_to_date() -> None:
    """No error and no changes when schema already matches ORM."""
    engine = _setup_db()
    InstrumentConfigurationTable = instrument_configuration_table.return_class()
    # Calling sync again is a no-op
    sync_instrument_configuration_schema(engine)

    ic_table_name = InstrumentConfigurationTable.__table__.name  # type: ignore[attr-defined]
    db_cols = {col["name"] for col in get_columns(engine, ic_table_name)}
    orm_cols = {col.name for col in InstrumentConfigurationTable.__table__.columns}  # type: ignore[attr-defined]
    assert orm_cols == db_cols


def test_existing_fk_references_survive_upsert() -> None:
    """Adding new rows via upsert must not disturb existing FK references."""
    engine = _setup_db()
    session = create_session(engine)
    ScienceProductTable = science_product_table.return_class()

    # Insert a ScienceProduct referencing an existing instrument configuration
    first_config_id = compute_instrument_configurations()[0][
        "instrument_configuration_id"
    ]
    with session.begin() as s:
        product = ScienceProductTable(
            instrument_configuration_id=first_config_id,
            mode="test_mode",
            reference_timestamp=datetime.now(timezone.utc),
        )
        s.add(product)
        s.flush()
        product_id = product.science_product_id

    # Now upsert again (simulating a config update)
    create_tables(engine)

    # The product must still exist and its FK must still be valid
    with session.begin() as s:
        product = (
            s.query(ScienceProductTable)
            .filter_by(science_product_id=product_id)
            .first()
        )  # type: ignore[assignment]
        assert product is not None
        assert product.instrument_configuration_id == first_config_id


def test_sync_schema_rejects_invalid_column_name(monkeypatch: Any) -> None:
    """sync_instrument_configuration_schema raises ValueError when a missing
    column does not match the ``instrument_N_id`` naming pattern."""
    import swxsoc.db.tables as tables_pkg

    engine = _setup_db()

    # Build a fake ORM class whose __table__.columns includes an invalid name
    real_table = instrument_configuration_table.return_class().__table__  # type: ignore[attr-defined]
    bad_col = SimpleNamespace(name="not_a_valid_column")
    fake_table = SimpleNamespace(
        name=real_table.name,
        columns=list(real_table.columns) + [bad_col],
    )
    fake_class = SimpleNamespace(__table__=fake_table)

    monkeypatch.setattr(
        tables_pkg.InstrumentConfigurationTable,
        "return_class",
        lambda: fake_class,
    )

    with pytest.raises(ValueError, match="does not match the expected"):
        sync_instrument_configuration_schema(engine)


def test_upsert_preserves_orphaned_rows() -> None:
    """Rows in lookup tables that are no longer in config survive the upsert."""
    engine = _setup_db()
    session = create_session(engine)
    FileLevelTable = file_level_table.return_class()

    # Verify the first file level exists
    first_level = swxsoc.config["mission"]["data_levels"][0]["short_name"]
    with session.begin() as s:
        assert (
            s.query(FileLevelTable).filter_by(short_name=first_level).first()
            is not None
        )

    # Upsert with a subset that excludes the first level
    subset_levels = swxsoc.config["mission"]["data_levels"][1:]
    populate_file_level_table(session, subset_levels, FileLevelTable)

    # The excluded level must still be in the DB (orphan preserved)
    with session.begin() as s:
        assert (
            s.query(FileLevelTable).filter_by(short_name=first_level).first()
            is not None
        )
