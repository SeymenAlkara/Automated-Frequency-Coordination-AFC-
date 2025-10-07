from afc_new.propagation import select_pathloss_db, winner2_pathloss_db, itm_pathloss_db
from afc_new.kpi import inr_violation_probability


def test_propagation_selector_threshold():
    f = 6.0e9
    pl_short = select_pathloss_db(100.0, f)  # winner by default
    pl_long = select_pathloss_db(10000.0, f)  # itm by default
    assert pl_long > pl_short


def test_winner_itm_api_exist():
    f = 6.0e9
    assert winner2_pathloss_db(10.0, f) > 0
    assert itm_pathloss_db(10.0, f) > 0


def test_inr_violation_probability():
    vals = [-10.0, -7.0, -6.0, -5.0, -3.0]
    p = inr_violation_probability(vals, limit_db=-6.0)
    # Violations are those > -6: (-5, -3) => 2/5 = 0.4
    assert abs(p - 0.4) < 1e-9

