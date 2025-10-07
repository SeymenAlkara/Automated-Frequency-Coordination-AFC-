from afc_new.spec_params import SpecParameters, IncumbentReceiverParams, WiFiRegulatoryLimits, ACIRSpec
from afc_new.allocator import allowed_eirp_dbm_with_spec_multi


def test_allowed_eirp_multi_enforces_minimum():
    params = SpecParameters(
        incumbent=IncumbentReceiverParams(noise_figure_db=4.5, bandwidth_hz=20e6, antenna_gain_dbi=30.0, rx_losses_db=1.0, polarization_mismatch_db=0.0),
        wifi_limits=WiFiRegulatoryLimits(max_eirp_dbm=36.0),
        acir=ACIRSpec(a_tx_db_by_offset_mhz={20: 30.0, 30: 25.0}, a_rx_db_by_offset_mhz={20: 30.0, 30: 25.0}),
    )
    n_dbm = -94.0
    pl = 120.0
    # With 30 MHz ACIR weaker, the multi check should be lower than only 20 MHz.
    e_multi = allowed_eirp_dbm_with_spec_multi(n_dbm, -6.0, pl, params, offsets_mhz=[0, 20, 30])
    e_only20 = allowed_eirp_dbm_with_spec_multi(n_dbm, -6.0, pl, params, offsets_mhz=[0, 20])
    assert e_multi <= e_only20

