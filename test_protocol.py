import json
from pathlib import Path

import afc_new as afc
from afc_new.protocol import handle_available_spectrum_inquiry


def _load_params_and_incumbents():
    root = Path(__file__).resolve().parents[1]
    params = afc.load_params_from_text_file(root / "spec" / "extracted_afc_text.txt")
    incumbents = json.loads((root / "spec" / "example_incumbents.json").read_text(encoding="utf-8"))
    return root, params, incumbents


def test_frequency_based_bins_merge_off():
    root, params, incumbents = _load_params_and_incumbents()
    req = {
        "location": {"lat": 41.015, "lon": 28.979},
        "inquiredFrequencyRange": [{"lowMHz": 5925.0, "highMHz": 5930.0}],
        "environment": "urban",
        "pathModel": "auto",
        "protectionMarginDb": 0.0,
        "mergeBins": False,
    }
    resp = handle_available_spectrum_inquiry(request=req, spec=params, incumbents=incumbents)
    assert resp.get("responseCode") == 0
    afi = resp.get("availableFrequencyInfo", [])
    # Expect 5 bins of 1 MHz
    assert len(afi) == 5


def test_channel_based_with_bandwidth_fallback():
    root, params, incumbents = _load_params_and_incumbents()
    req = {
        "location": {"lat": 41.015, "lon": 28.979},
        "inquiredChannels": [
            {"channelCfi": [636996], "bandwidthMHz": 20},
            {"channelCfi": [636964], "bandwidthMHz": 40},
        ],
        "environment": "urban",
        "pathModel": "auto",
        "protectionMarginDb": 0.0,
    }
    resp = handle_available_spectrum_inquiry(request=req, spec=params, incumbents=incumbents)
    assert resp.get("responseCode") == 0
    aci = resp.get("availableChannelInfo", [])
    assert len(aci) == 2
    # maxEirp should be present (value can be <= 0 depending on geometry)
    for item in aci:
        assert "maxEirp" in item and isinstance(item["maxEirp"], list) and len(item["maxEirp"]) == 1


