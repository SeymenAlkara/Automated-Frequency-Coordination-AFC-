from afc_new.acir_masks import interpolate_mask_db, acir_db_from_masks


def test_interpolate_mask_db():
    points = [(0, 0), (20, 30), (40, 40)]
    assert interpolate_mask_db(10, points) == 15
    assert interpolate_mask_db(25, points) == 35
    assert interpolate_mask_db(-5, points) == 0
    assert interpolate_mask_db(100, points) == 40


def test_acir_from_masks_reasonable():
    tx = [(20, 30), (40, 35)]
    rx = [(20, 30), (40, 35)]
    acir20 = acir_db_from_masks(20, tx, rx)
    acir40 = acir_db_from_masks(40, tx, rx)
    assert acir40 > acir20

