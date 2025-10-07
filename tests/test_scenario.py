from afc_new.spec_params import SpecParameters, IncumbentReceiverParams, WiFiRegulatoryLimits, ACIRSpec
from afc_new.scenario import Scenario, run_scenario, rows_to_table


def test_scenario_basic():
	params = SpecParameters(
		incumbent=IncumbentReceiverParams(noise_figure_db=4.5, bandwidth_hz=20e6, antenna_gain_dbi=30.0, rx_losses_db=1.0, polarization_mismatch_db=0.0),
		wifi_limits=WiFiRegulatoryLimits(max_eirp_dbm=36.0),
		acir=ACIRSpec(a_tx_db_by_offset_mhz={20: 30.0}, a_rx_db_by_offset_mhz={20: 30.0}),
	)
	scn = Scenario(frequency_hz=6.0e9, distances_m=[1000.0], channel_offsets_mhz=[0, 20])
	rows = run_scenario(params, scn)
	assert len(rows) == 2
	# Adjacent should allow more EIRP than co-channel
	co = [r for r in rows if r.channel_offset_mhz == 0][0]
	adj = [r for r in rows if r.channel_offset_mhz == 20][0]
	assert adj.allowed_eirp_dbm > co.allowed_eirp_dbm
	table = rows_to_table(rows)
	assert table[0] == ["distance_m", "offset_mhz", "path_loss_db", "noise_dbm", "allowed_eirp_dbm"]
