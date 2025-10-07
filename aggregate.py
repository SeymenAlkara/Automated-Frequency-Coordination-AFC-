"""Aggregate interference utilities (simplified).

Implements helpers to sum multiple AP interference contributions at an FS receiver
and evaluate INR vs the -6 dB criterion (WINNF-TS-1014 9.1.1 aggregate context).
"""

from typing import Iterable
import math


def lin_from_dbm(dbm: float) -> float:
    return 10.0 ** (dbm / 10.0)


def dbm_from_lin(mw: float) -> float:
    if mw <= 0:
        return -math.inf
    return 10.0 * math.log10(mw)


def aggregate_interference_dbm(components_dbm: Iterable[float]) -> float:
    """Sum multiple interference powers (dBm) in linear domain and return dBm."""
    total_mw = 0.0
    for x in components_dbm:
        total_mw += lin_from_dbm(x)
    return dbm_from_lin(total_mw)


def inr_db_from_components(i_components_dbm: Iterable[float], noise_dbm: float) -> float:
    """INR (dB) from a list of interference components and noise power."""
    i_agg_dbm = aggregate_interference_dbm(i_components_dbm)
    return i_agg_dbm - noise_dbm


def meets_inr_limit(i_components_dbm: Iterable[float], noise_dbm: float, inr_limit_db: float = -6.0) -> bool:
    """Return True if INR ≤ limit for the aggregate interference."""
    return inr_db_from_components(i_components_dbm, noise_dbm) <= inr_limit_db + 1e-9


