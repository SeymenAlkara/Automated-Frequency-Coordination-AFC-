import math

from afc_new.link_budget import compute_eirp_dbm, noise_power_dbm, i_threshold_dbm, interference_margin_db
from afc_new.fspl import fspl_db, invert_fspl_distance_m
from afc_new.acir import acir_db, adjacent_channel_interference_dbm
from afc_new.phy import sinr_db
from afc_new.mac import bianchi_fixed_point


def test_eirp_and_noise_and_threshold():
    eirp = compute_eirp_dbm(20.0, 6.0, 1.0)
    assert abs(eirp - 25.0) < 1e-6

    n = noise_power_dbm(20e6, 7.0)
    # Expected around -174 + 10log10(20e6) + 7 = -174 + 73.01 + 7 = -93.99
    assert -95.5 < n < -92.5

    thr = i_threshold_dbm(n, -6.0)
    assert abs(thr - (n - 6.0)) < 1e-9

    im = interference_margin_db(i_dbm=thr - 3.0, i_thresh_dbm=thr)
    assert abs(im - 3.0) < 1e-9


def test_fspl_and_inverse():
    f = 6.0e9
    d = 100.0
    pl = fspl_db(d, f)
    d2 = invert_fspl_distance_m(pl, f)
    assert abs(d - d2) / d < 1e-9


def test_acir():
    acir = acir_db(30.0, 30.0)
    # parallel of two 30 dB attenuations -> ~27 dB
    assert 26.5 < acir < 27.5
    i_adj = adjacent_channel_interference_dbm(-70.0, 30.0, 30.0)
    assert -98.0 < i_adj < -96.0


def test_sinr():
    s = -60.0
    i = -80.0
    n = -94.0
    snr = sinr_db(s, i, n)
    assert snr > 10.0


def test_bianchi_fixed_point():
    tau, p = bianchi_fixed_point(n_stations=10, cwmin=15, m_max_backoff=5)
    assert 0.0 < tau < 1.0
    assert 0.0 <= p < 1.0

