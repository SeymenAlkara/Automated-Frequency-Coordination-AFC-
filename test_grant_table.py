from pathlib import Path
import json

import afc_new as afc


def _load_params_and_incumbents():
    root = Path(__file__).resolve().parents[1]
    params = afc.load_params_from_text_file(root / "spec" / "extracted_afc_text.txt")
    incumbents = json.loads((root / "spec" / "example_incumbents.json").read_text(encoding="utf-8"))
    return root, params, incumbents


def test_exact_band_center_forced():
    root, params, incumbents = _load_params_and_incumbents()
    # Force a band equal to 20 MHz and ensure we get exactly one center evaluated
    rows = afc.build_grant_table_with_incumbents(
        spec=params,
        incumbents=incumbents,
        distance_m=None,
        ap_lat=41.015,
        ap_lon=28.979,
        lower_mhz=6025.0 - 10.0,
        upper_mhz=6025.0 + 10.0,
        bandwidths_mhz=(20.0,),
        inr_limit_db=-6.0,
        environment="urban",
        path_model="auto",
    )
    assert len(rows) == 1
    assert abs(rows[0].center_mhz - 6025.0) < 1e-6


def test_tolerant_field_names():
    root, params, incumbents = _load_params_and_incumbents()
    # Rename fields to alternate variants and ensure it still works
    inc_alt = []
    for inc in incumbents:
        inc_alt.append({
            "fs_center_mhz": inc.get("center_mhz"),
            "fs_bandwidth_mhz": inc.get("bandwidth_mhz"),
            "rx_lat": inc.get("lat"),
            "rx_lon": inc.get("lon"),
            "rx_gain_dbi": inc.get("rx_gain_dbi", inc.get("rx_antenna_gain_dbi")),
            "rx_azimuth_deg": inc.get("rx_azimuth_deg", inc.get("rx_antenna_azimuth_deg", 0.0)),
            "polarization": inc.get("polarization", "H"),
        })
    rows = afc.build_grant_table_with_incumbents(
        spec=params,
        incumbents=inc_alt,
        distance_m=3000.0,
        lower_mhz=5925.0,
        upper_mhz=5945.0,
        bandwidths_mhz=(20.0,),
        inr_limit_db=-6.0,
        environment="urban",
        path_model="auto",
    )
    assert len(rows) >= 1

from afc_new.grant_table import enumerate_centers_mhz, channel_number_from_center_mhz, build_grant_table_for_hypothetical_fs
from afc_new.spec_params import SpecParameters, IncumbentReceiverParams, WiFiRegulatoryLimits, ACIRSpec


def test_enumerate_centers_and_channel_numbers():
    centers = enumerate_centers_mhz(5925.0, 6425.0, 20.0)
    assert len(centers) > 0
    # Known first 20 MHz center at/after 5925 should be 5935 or 5955 depending on alignment; ensure grid mapping is integer channel
    ch = channel_number_from_center_mhz(5955.0)
    assert ch == 1


def test_build_grant_table_basic():
    params = SpecParameters(
        incumbent=IncumbentReceiverParams(noise_figure_db=4.5, bandwidth_hz=20e6, antenna_gain_dbi=30.0, rx_losses_db=1.0, polarization_mismatch_db=0.0),
        wifi_limits=WiFiRegulatoryLimits(max_eirp_dbm=36.0),
        acir=ACIRSpec(a_tx_db_by_offset_mhz={20: 30.0, 40: 35.0}, a_rx_db_by_offset_mhz={20: 30.0, 40: 35.0}),
    )
    rows = build_grant_table_for_hypothetical_fs(params, distance_m=1000.0, bandwidths_mhz=(20.0,))
    assert len(rows) > 0
    # Ensure fields are populated
    r0 = rows[0]
    assert isinstance(r0.channel_number, int)
    assert r0.center_mhz > 0
    import math
    assert abs(r0.allowed_psd_dbm_per_mhz - (r0.allowed_eirp_dbm - 10.0 * math.log10(r0.bandwidth_mhz))) < 1e-9

