"""Aggregate interference utilities (simplified).

Implements helpers to sum multiple AP interference contributions at an FS receiver
and evaluate INR vs the -6 dB criterion (WINNF-TS-1014 9.1.1 aggregate context).
"""

from typing import Iterable, Dict, Any, List
import math

from .spec_params import SpecParameters
from .link_budget import noise_power_dbm
from .propagation import select_pathloss_db
from .geodesy import haversine_distance_m, initial_bearing_deg
from .antenna import AntennaPatternParams, off_axis_azimuth_deg, effective_gain_dbi
from .antenna_rpe import combined_rpe_gain_dbi
from .acir_defaults import ensure_defaults
from .acir_masks import acir_db_from_masks


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


def evaluate_aggregate_inr_for_channel(
    *,
    spec: SpecParameters,
    incumbents: Iterable[Dict[str, Any]],
    aps: Iterable[Dict[str, float]],
    center_mhz: float,
    bandwidth_mhz: float,
    inr_limit_db: float = -6.0,
    environment: str | None = None,
    path_model: str = "auto",
) -> Dict[str, Any]:
    """Evaluate aggregate INR for a channel against all incumbents.

    Args:
        spec: Parsed spec parameters (NF, Rx gain/losses, ACIR tables).
        incumbents: List of FS receiver dicts (lat/lon, gains, center/bw, optional RPE).
        aps: List of AP dicts with keys {lat, lon, eirp_dbm}.
        center_mhz, bandwidth_mhz: Channel center and width.

    Returns a summary dict with worst-case INR across incumbents and details per incumbent.
    """
    a_tx_def, a_rx_def = ensure_defaults(spec.acir.a_tx_db_by_offset_mhz, spec.acir.a_rx_db_by_offset_mhz)
    tx_points = sorted((float(k), float(v)) for k, v in a_tx_def.items())
    rx_points = sorted((float(k), float(v)) for k, v in a_rx_def.items())

    f_hz = center_mhz * 1e6
    ch_lo = center_mhz - bandwidth_mhz / 2.0
    ch_hi = center_mhz + bandwidth_mhz / 2.0

    details: List[Dict[str, Any]] = []
    worst_inr = -1e9
    worst_id = None

    for inc in incumbents:
        # Tolerant field access
        def _v(d: dict, keys: list[str], default=None):
            for k in keys:
                if k in d and d[k] is not None:
                    return d[k]
            return default

        fs_center_mhz = float(_v(inc, ["freq_center_mhz", "center_mhz", "fs_center_mhz"]))
        fs_bw_mhz = float(_v(inc, ["bandwidth_mhz", "fs_bandwidth_mhz", "rx_bw_mhz"], spec.incumbent.bandwidth_hz / 1e6))
        rx_lat = float(_v(inc, ["rx_lat", "lat"], 0.0))
        rx_lon = float(_v(inc, ["rx_lon", "lon"], 0.0))
        fs_rx_gain = float(_v(inc, ["rx_antenna_gain_dbi", "rx_gain_dbi"], spec.incumbent.antenna_gain_dbi))
        rx_az = float(_v(inc, ["rx_antenna_azimuth_deg", "rx_azimuth_deg", "az_deg"], 0.0))
        pol = str(_v(inc, ["polarization"], ""))[:1].upper()
        rpe_az = inc.get("rx_rpe_az")
        rpe_el = inc.get("rx_rpe_el")
        link_id = str(_v(inc, ["link_id", "fs_id", "id"], "unknown"))

        fs_lo = fs_center_mhz - fs_bw_mhz / 2.0
        fs_hi = fs_center_mhz + fs_bw_mhz / 2.0
        overlaps = min(ch_hi, fs_hi) - max(ch_lo, fs_lo)

        # Noise power at FS
        n_dbm = noise_power_dbm(spec.incumbent.bandwidth_hz, spec.incumbent.noise_figure_db)

        # Sum interference from all APs
        i_components: List[float] = []
        for ap in aps:
            ap_lat = float(ap["lat"])  # required
            ap_lon = float(ap["lon"])  # required
            eirp_dbm = float(ap["eirp_dbm"])  # required

            d_m = haversine_distance_m(ap_lat, ap_lon, rx_lat, rx_lon)
            brg = initial_bearing_deg(ap_lat, ap_lon, rx_lat, rx_lon)
            pl_db = select_pathloss_db(distance_m=d_m, frequency_hz=f_hz, environment=environment)

            # Antenna discrimination (azimuth only) at FS side
            delta_az = off_axis_azimuth_deg(rx_az, (brg + 180.0) % 360.0)
            if rpe_az and rpe_el:
                g_eff = combined_rpe_gain_dbi(fs_rx_gain, delta_az, 0.0, rpe_az, rpe_el)
            else:
                g_eff = effective_gain_dbi(AntennaPatternParams(g_max_dbi=fs_rx_gain), delta_az, 0.0)

            i_co_dbm = eirp_dbm - pl_db + g_eff - spec.incumbent.rx_losses_db + spec.incumbent.polarization_mismatch_db

            if overlaps > 0:
                i_components.append(i_co_dbm)
            else:
                offset = abs(center_mhz - fs_center_mhz)
                acir_val = acir_db_from_masks(offset, tx_points, rx_points)
                i_components.append(i_co_dbm - acir_val)

        inr_db = inr_db_from_components(i_components, n_dbm)
        details.append({"incumbent": link_id, "inr_db": inr_db, "num_aps": len(list(aps))})
        if inr_db > worst_inr:
            worst_inr = inr_db
            worst_id = link_id

    meets = worst_inr <= inr_limit_db + 1e-9
    return {
        "center_mhz": center_mhz,
        "bandwidth_mhz": bandwidth_mhz,
        "worst_inr_db": worst_inr,
        "limiting_incumbent": worst_id,
        "meets_inr_limit": meets,
        "details": details,
    }

