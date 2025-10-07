from afc_new.allocator import (
    allowed_eirp_dbm_for_path,
    psd_dbm_per_mhz_from_eirp,
    eirp_total_dbm_from_psd,
    verify_interference_meets_limit,
)


def test_eirp_allocator_cochannel():
    # Example: path loss 120 dB, G_rx 30 dBi FS dish, Rx losses 1 dB.
    n_dbm = -94.0
    inr_limit_db = -6.0
    pl = 120.0
    g_rx = 30.0
    l_rx = 1.0
    l_pol = 0.5
    eirp_allowed = allowed_eirp_dbm_for_path(
        n_dbm=n_dbm,
        inr_limit_db=inr_limit_db,
        path_loss_db=pl,
        g_rx_dbi=g_rx,
        l_rx_losses_db=l_rx,
        l_polarization_db=l_pol,
    )
    # Check that resulting I equals threshold.
    ok = verify_interference_meets_limit(
        eirp_dbm=eirp_allowed,
        path_loss_db=pl,
        g_rx_dbi=g_rx,
        l_rx_losses_db=l_rx,
        l_polarization_db=l_pol,
        n_dbm=n_dbm,
        inr_limit_db=inr_limit_db,
    )
    assert ok


def test_eirp_allocator_adjacent():
    n_dbm = -94.0
    inr_limit_db = -6.0
    pl = 120.0
    g_rx = 30.0
    l_rx = 1.0
    acir = 27.0
    eirp_allowed_adj = allowed_eirp_dbm_for_path(
        n_dbm=n_dbm,
        inr_limit_db=inr_limit_db,
        path_loss_db=pl,
        g_rx_dbi=g_rx,
        l_rx_losses_db=l_rx,
        acir_db_value=acir,
    )
    # Adjacent should allow higher EIRP than co-channel.
    eirp_allowed_co = allowed_eirp_dbm_for_path(
        n_dbm=n_dbm,
        inr_limit_db=inr_limit_db,
        path_loss_db=pl,
        g_rx_dbi=g_rx,
        l_rx_losses_db=l_rx,
    )
    assert eirp_allowed_adj > eirp_allowed_co


def test_psd_eirp_conversions():
    eirp = 36.0
    bw = 20.0
    psd = psd_dbm_per_mhz_from_eirp(eirp, bw)
    eirp2 = eirp_total_dbm_from_psd(psd, bw)
    assert abs(eirp - eirp2) < 1e-9

