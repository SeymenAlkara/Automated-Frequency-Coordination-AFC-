"""Propagation models and selector.

Provides a simple selector between FSPL, a WINNER II-style log-distance placeholder,
and an ITM-like placeholder to be replaced with proper bindings. We also support
simple environment presets that add extra loss.

WINNF-TS-1014 reference:
- 9.1.3 Propagation Models — this file provides the hooks and placeholders.
"""

import math
from typing import Literal, Optional

from .fspl import fspl_db


PathlossModel = Literal["fspl", "winner2", "itm"]
Environment = Literal["urban", "suburban", "rural", "indoor"]


def winner2_pathloss_db(
    distance_m: float,
    frequency_hz: float,
    pathloss_exponent: float = 2.1,
    reference_distance_m: float = 1.0,
    additional_loss_db: float = 0.0,
) -> float:
    """Simplified WINNER II-style log-distance model placeholder.

    PL(d) = PL(d0) + 10 n log10(d/d0) + L_add
    with PL(d0) taken as FSPL at reference distance.
    """
    if distance_m <= 0 or frequency_hz <= 0:
        raise ValueError("distance and frequency must be positive")
    pl_d0 = fspl_db(max(reference_distance_m, 1e-3), frequency_hz)
    return pl_d0 + 10.0 * pathloss_exponent * math.log10(max(distance_m, reference_distance_m) / reference_distance_m) + additional_loss_db


def two_slope_pathloss_db(
    distance_m: float,
    frequency_hz: float,
    breakpoint_m: float = 100.0,
    n1: float = 2.0,
    n2: float = 3.5,
    additional_loss_db: float = 0.0,
) -> float:
    """Simple two-slope model: FSPL at d0, then n1 up to breakpoint, n2 beyond.

    PL(d) = PL(d0) + 10 n1 log10(d/d0) for d <= bp
          = PL(bp) + 10 n2 log10(d/bp) for d > bp
    """
    if distance_m <= 0 or frequency_hz <= 0:
        raise ValueError("distance and frequency must be positive")
    d0 = 1.0
    pl_d0 = fspl_db(d0, frequency_hz)
    if distance_m <= breakpoint_m:
        return pl_d0 + 10.0 * n1 * math.log10(max(distance_m, d0) / d0) + additional_loss_db
    pl_bp = pl_d0 + 10.0 * n1 * math.log10(breakpoint_m / d0)
    return pl_bp + 10.0 * n2 * math.log10(distance_m / breakpoint_m) + additional_loss_db


def itm_pathloss_db(
    distance_m: float,
    frequency_hz: float,
    terrain_profile: Optional[object] = None,
    rx_tx_heights_m: Optional[tuple[float, float]] = None,
    climate: Optional[str] = None,
) -> float:
    """Placeholder for ITM (Longley-Rice) path loss.

    For now, returns FSPL plus a basic excess loss term that grows with log distance.
    Replace with a proper ITM binding later.
    """
    base = fspl_db(distance_m, frequency_hz)
    # placeholder: add 0.1 dB per decade(m) beyond 1 m and +6 dB if non-LoS hint present
    excess = 10.0 * math.log10(max(distance_m, 1.0)) * 0.1
    if terrain_profile is not None:
        excess += 6.0
    return base + excess


def environment_extra_loss_db(env: Environment) -> float:
    """Very simple environment loss presets to nudge realism.

    Values are placeholders; can be replaced by clutter models later.
    """
    return {
        "urban": 8.0,
        "suburban": 4.0,
        "rural": 1.0,
        "indoor": 12.0,
    }[env]


def building_penetration_loss_db(indoor: bool = False, penetration_db: Optional[float] = None) -> float:
    """Simple building penetration loss model.

    If `penetration_db` is provided, use it. Otherwise, if `indoor` is True,
    apply a typical 12 dB indoor loss placeholder; else 0 dB.
    """
    if penetration_db is not None:
        return max(0.0, float(penetration_db))
    return 12.0 if indoor else 0.0


def select_pathloss_db(
    distance_m: float,
    frequency_hz: float,
    selector: PathlossModel | None = None,
    winner_threshold_m: float = 5000.0,
    environment: Environment | None = None,
    indoor: bool = False,
    penetration_db: Optional[float] = None,
) -> float:
    """Select a pathloss model by distance or explicit selector.

    Default: WINNER II-like for d < winner_threshold_m, ITM-like for longer.
    """
    if selector == "fspl":
        pl = fspl_db(distance_m, frequency_hz)
    elif selector == "winner2" or (selector is None and distance_m < winner_threshold_m):
        pl = winner2_pathloss_db(distance_m, frequency_hz)
    elif selector == "itm" or selector is None:
        pl = itm_pathloss_db(distance_m, frequency_hz)
    else:
        raise ValueError("Unknown pathloss selector")

    if environment is not None:
        pl += environment_extra_loss_db(environment)
    # Add optional building penetration loss (e.g., indoor FS or AP)
    pl += building_penetration_loss_db(indoor=indoor, penetration_db=penetration_db)
    return pl

