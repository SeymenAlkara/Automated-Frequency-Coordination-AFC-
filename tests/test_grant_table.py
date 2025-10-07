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
    assert r0.channel_number >= 1
    assert r0.center_mhz > 0
    assert r0.allowed_psd_dbm_per_mhz == r0.allowed_eirp_dbm - 10.0

