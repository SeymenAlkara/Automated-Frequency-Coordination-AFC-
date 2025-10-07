from afc_new.acir import acir_db_from_spec
from afc_new.spec_params import ACIRSpec


def test_acir_db_from_spec_nearest():
    spec = ACIRSpec(a_tx_db_by_offset_mhz={20: 30.0, 40: 35.0}, a_rx_db_by_offset_mhz={20: 32.0, 40: 36.0})
    # Query at 30 MHz should use nearest keys (20 or 40); both approx yield similar ACIR
    acir_30 = acir_db_from_spec(spec, 30)
    acir_20 = acir_db_from_spec(spec, 20)
    acir_40 = acir_db_from_spec(spec, 40)
    assert min(acir_20, acir_40) - 1.0 < acir_30 < max(acir_20, acir_40) + 1.0

