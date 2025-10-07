"""Simple antenna pattern helpers (placeholders for RPE models).

Goal: provide beginner-friendly utilities to estimate how antenna gain drops
when looking away from the main beam (boresight). Real FS antenna patterns are
given by Radiation Pattern Envelopes (RPE). Here, we implement a gentle, easy
to understand model you can later replace by a true RPE table.

Model used (per plane):
- Off-axis attenuation A(Δ) [dB] = min( 12 * (Δ / HPBW)^2, SLL )
  where Δ is the off-axis angle in degrees, HPBW is the half-power beamwidth
  (3 dB beamwidth), and SLL is a sidelobe level floor (e.g., 20 dB).
- Gain at off-axis angle: G(Δ) = G_max - A(Δ)

For 2D (azimuth + elevation) we sum the attenuations in the two planes and
cap at a backlobe floor.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AntennaPatternParams:
    """Defines a very simple pattern by beamwidths and limits.

    g_max_dbi: main beam (boresight) gain in dBi
    hpbw_az_deg: 3 dB beamwidth in azimuth (degrees)
    hpbw_el_deg: 3 dB beamwidth in elevation (degrees)
    sidelobe_floor_db: max attenuation (dB) per plane before sidelobes (default 20 dB)
    backlobe_floor_dbi: minimum gain anywhere (e.g., -10 dBi)
    """

    g_max_dbi: float = 30.0
    hpbw_az_deg: float = 3.0
    hpbw_el_deg: float = 3.0
    sidelobe_floor_db: float = 20.0
    backlobe_floor_dbi: float = -10.0


def off_axis_azimuth_deg(antenna_azimuth_deg: float, bearing_to_target_deg: float) -> float:
    """Absolute azimuth off-axis angle between antenna boresight and target bearing."""
    d = abs(((bearing_to_target_deg - antenna_azimuth_deg + 180.0) % 360.0) - 180.0)
    return d


def _attenuation_parabolic(delta_deg: float, hpbw_deg: float, sidelobe_floor_db: float) -> float:
    if hpbw_deg <= 0:
        return sidelobe_floor_db
    att = 12.0 * (delta_deg / hpbw_deg) ** 2
    return min(att, sidelobe_floor_db)


def effective_gain_dbi(
    pattern: AntennaPatternParams,
    azimuth_offaxis_deg: float,
    elevation_offaxis_deg: float,
) -> float:
    """Compute effective gain at given off-axis angles.

    Args:
        pattern: antenna pattern parameters
        azimuth_offaxis_deg: |Δ_az| from boresight (degrees)
        elevation_offaxis_deg: |Δ_el| from boresight (degrees)

    Returns:
        gain in dBi (capped by backlobe floor)
    """
    a_az = _attenuation_parabolic(abs(azimuth_offaxis_deg), pattern.hpbw_az_deg, pattern.sidelobe_floor_db)
    a_el = _attenuation_parabolic(abs(elevation_offaxis_deg), pattern.hpbw_el_deg, pattern.sidelobe_floor_db)
    g = pattern.g_max_dbi - (a_az + a_el)
    return max(g, pattern.backlobe_floor_dbi)

