from pathlib import Path

from afc_new.heatmaps import APSiteClient, generate_ap_heatmaps


def test_heatmaps_wrapper_args(tmp_path: Path):
    out_dir = tmp_path
    aps = [
        APSiteClient(lat=41.015, lon=28.979, eirp_dbm=30.0),
        APSiteClient(lat=41.020, lon=28.990, eirp_dbm=27.0),
    ]
    res = generate_ap_heatmaps(
        aps=aps,
        grid_center=(41.017, 28.985),
        grid_size_m=200.0,
        resolution_m=50.0,
        center_mhz=6055.0,
        bandwidth_mhz=20.0,
        environment='urban',
        path_model='auto',
        out_dir=out_dir
    )
    # We expect result keys per AP
    assert isinstance(res, dict) and len(res) == 2


