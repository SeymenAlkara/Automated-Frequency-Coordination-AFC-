"""Device constraint helpers.

Apply minimum operational EIRP/PSD constraints to grant decisions so channels
with allowed EIRP below a device’s minimum are marked deny.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceConstraints:
    min_eirp_dbm: float = 0.0
    min_psd_dbm_per_mhz: float = -10.0


def apply_constraints_to_decision(allowed_eirp_dbm: float, psd_dbm_per_mhz: float, cons: DeviceConstraints) -> bool:
    """Return True if both EIRP and PSD meet device minimums."""
    if allowed_eirp_dbm < cons.min_eirp_dbm:
        return False
    if psd_dbm_per_mhz < cons.min_psd_dbm_per_mhz:
        return False
    return True


