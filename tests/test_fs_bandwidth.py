from afc_new.fs_bandwidth import parse_emission_designator_bw_hz, determine_fs_noise_bw_hz
from afc_new.spec_params import SpecParameters, IncumbentReceiverParams, WiFiRegulatoryLimits, ACIRSpec


def test_parse_emission_designator():
    assert abs(parse_emission_designator_bw_hz('25M0F7W') - 25e6) < 1
    assert abs(parse_emission_designator_bw_hz('200K0F3E') - 200e3) < 1
    assert abs(parse_emission_designator_bw_hz('5M50D7W') - 5.5e6) < 1
    assert parse_emission_designator_bw_hz('XYZ') is None


def test_determine_fs_noise_bw():
    params = SpecParameters(
        incumbent=IncumbentReceiverParams(noise_figure_db=4.5, bandwidth_hz=20e6, antenna_gain_dbi=30.0, rx_losses_db=1.0, polarization_mismatch_db=0.0),
        wifi_limits=WiFiRegulatoryLimits(max_eirp_dbm=36.0),
        acir=ACIRSpec(a_tx_db_by_offset_mhz={20: 30.0}, a_rx_db_by_offset_mhz={20: 30.0}),
    )
    # Precedence: emission designator beats explicit
    bw = determine_fs_noise_bw_hz(spec=params, emission_designator='40M0F7W', explicit_rx_bw_hz=10e6)
    assert abs(bw - 40e6) < 1
    # Then explicit beats default
    bw = determine_fs_noise_bw_hz(spec=params, emission_designator=None, explicit_rx_bw_hz=15e6)
    assert abs(bw - 15e6) < 1
    # Then default
    bw = determine_fs_noise_bw_hz(spec=params)
    assert abs(bw - 20e6) < 1

