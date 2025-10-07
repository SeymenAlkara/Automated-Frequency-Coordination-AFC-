"""ITM (Longley–Rice) scaffolding.

Provides a typed interface for integrating a proper ITM library later. For now
we expose a placeholder that adds distance/height/climate dependent excess loss
on top of FSPL. This file centralizes ITM parameters so wiring an external
implementation will be straightforward.

WINNF-TS-1014: 9.1.3 Propagation Models — binding location for ITM.
"""

from typing import Optional
import math

from .fspl import fspl_db


def longley_rice_pathloss_db(
    distance_m: float,
    frequency_hz: float,
    tx_height_m: Optional[float] = None,
    rx_height_m: Optional[float] = None,
    climate: Optional[str] = None,
    reliability_pct: float = 50.0,
) -> float:
    """Placeholder for ITM. Returns FSPL plus heuristic excess loss.

    Args:
        distance_m: path distance in meters
        frequency_hz: frequency in Hz
        tx_height_m: Tx antenna height above ground (m)
        rx_height_m: Rx antenna height above ground (m)
        climate: optional climate string ("continental", "maritime", ...)
        reliability_pct: time/rare-event reliability (50/90/99) — informative only here
    """
    base = fspl_db(distance_m, frequency_hz)
    # Heuristic: taller antennas reduce diffraction loss; harsher climate adds loss.
    h_tx = max(1.0, (tx_height_m or 10.0))
    h_rx = max(1.0, (rx_height_m or 10.0))
    height_term = -2.0 * math.log10(h_tx * h_rx)  # small dB reduction for taller sites
    dist_term = 6.0 * math.log10(max(distance_m, 1.0) / 1000.0)  # +dB per km decades
    climate_term = 0.0
    if climate:
        c = climate.lower()
        if "mar" in c:
            climate_term = 2.0
        elif "tropic" in c:
            climate_term = 1.0
        else:
            climate_term = 3.0
    rel_term = 0.0 if reliability_pct <= 50.0 else (reliability_pct - 50.0) * 0.05
    return base + max(0.0, dist_term + climate_term + rel_term + height_term)


