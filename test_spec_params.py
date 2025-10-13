from pathlib import Path

import afc_new as afc
from afc_new.spec_params import parse_spec_text_to_params


def test_parse_defaults_when_missing():
    txt = """
    This is a small extract without explicit NF/BW. ACIR ±20 MHz: 28 dB
    """
    params = parse_spec_text_to_params(txt)
    assert params.incumbent.noise_figure_db > 0
    assert params.incumbent.bandwidth_hz > 0
    # ACIR split between Tx/Rx
    assert 20 in params.acir.a_tx_db_by_offset_mhz
    assert 20 in params.acir.a_rx_db_by_offset_mhz

from afc_new.spec_params import parse_spec_text_to_params


def test_parse_spec_text_simple():
    text = """
    Noise Figure: 7 dB
    Receiver bandwidth: 40 MHz
    Incumbent antenna gain: 32 dBi
    Rx losses: 1.5 dB
    Polarization mismatch: 0.5 dB
    Max EIRP: 33 dBm
    ACIR ±20 MHz: 27 dB
    ACLR at 40 MHz: 35 dB
    ACS at 40 MHz: 37 dB
    """
    params = parse_spec_text_to_params(text)
    assert params.incumbent.noise_figure_db == 7.0
    assert abs(params.incumbent.bandwidth_hz - 40e6) < 1
    assert params.incumbent.antenna_gain_dbi == 32.0
    assert params.incumbent.rx_losses_db == 1.5
    assert params.incumbent.polarization_mismatch_db == 0.5
    assert params.wifi_limits.max_eirp_dbm == 33.0
    # ACIR only provided at 20 MHz -> split between ACLR/ACS
    assert params.acir.a_tx_db_by_offset_mhz[20] == 13.5
    assert params.acir.a_rx_db_by_offset_mhz[20] == 13.5
    assert params.acir.a_tx_db_by_offset_mhz[40] == 35.0
    assert params.acir.a_rx_db_by_offset_mhz[40] == 37.0


def test_nf_default_by_center_frequency():
    text_low = "Fc, FS-Rx: 6.3 GHz\n(omitting NF explicit)"
    params_low = parse_spec_text_to_params(text_low)
    assert params_low.incumbent.noise_figure_db == 4.0

    text_high = "Center frequency: 6.6 GHz\nReceiver bandwidth: 20 MHz"
    params_high = parse_spec_text_to_params(text_high)
    assert params_high.incumbent.noise_figure_db == 4.5

