from afc_new.phy_mcs import default_mcs_table, pick_mcs_from_snr_db, per_from_snr_db, phy_rate_bps_from_snr_db


def test_pick_mcs_monotonic():
    table = default_mcs_table()
    low = pick_mcs_from_snr_db(5.0, table)
    high = pick_mcs_from_snr_db(30.0, table)
    assert high.mcs_index >= low.mcs_index


def test_per_curve_reasonable():
    table = default_mcs_table()
    m = pick_mcs_from_snr_db(20.0, table)
    per1 = per_from_snr_db(m.snr_db_threshold + 1.0, m)
    per2 = per_from_snr_db(m.snr_db_threshold + 10.0, m)
    assert per2 < per1
    assert 0.0 <= per2 <= 1.0


def test_phy_rate_positive():
    mcs, per, rate = phy_rate_bps_from_snr_db(25.0, bandwidth_hz=20e6, spatial_streams=2)
    assert rate > 0

