"""
Module for computing MetaTracker database schema data derived from the
active SWxSOC mission configuration (``swxsoc.config``).
"""

from itertools import combinations
from typing import Any, Dict, List

import swxsoc

__all__ = [
    "compute_instrument_metadata",
    "compute_instrument_configurations",
]


def compute_instrument_metadata() -> List[Dict[str, Any]]:
    """
    Compute instrument metadata for the MetaTracker database from the active
    SWxSOC mission configuration.

    Returns
    -------
    list[dict[str, Any]]
        A list of instrument metadata dictionaries, each containing
        ``instrument_id``, ``description``, ``full_name``, and ``short_name``.
    """
    mission_config = swxsoc.config["mission"]
    inst_names = mission_config["inst_names"]

    return [
        {
            "instrument_id": idx + 1,
            "description": f"{mission_config['inst_fullnames'][idx]} ({mission_config['inst_targetnames'][idx]})",
            "full_name": mission_config["inst_fullnames"][idx],
            "short_name": mission_config["inst_shortnames"][idx],
        }
        for idx in range(len(inst_names))
    ]


def compute_instrument_configurations() -> List[Dict[str, Any]]:
    """
    Compute all possible instrument configurations (combinations of
    instruments) for the MetaTracker database from the active SWxSOC mission
    configuration.

    Returns
    -------
    list[dict[str, Any]]
        A list of instrument configuration dictionaries, each containing an
        ``instrument_configuration_id`` and one ``instrument_{i}_id`` key per
        instrument slot (``None`` if unused in that combination).
    """
    num_instruments = len(swxsoc.config["mission"]["inst_names"])

    instrument_configurations = []
    config_id = 1
    for r in range(1, num_instruments + 1):
        for combo in combinations(range(1, num_instruments + 1), r):
            config: Dict[str, Any] = {"instrument_configuration_id": config_id}
            config.update(
                {
                    f"instrument_{i + 1}_id": combo[i] if i < len(combo) else None
                    for i in range(num_instruments)
                }
            )
            instrument_configurations.append(config)
            config_id += 1

    return instrument_configurations
