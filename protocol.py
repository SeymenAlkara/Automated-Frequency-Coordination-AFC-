"""WINNF-TS-3007 AFC–SPD messaging (minimal handler).

Implements a minimal subset aligned with sections 6.2–6.3:
- Validates AvailableSpectrumInquiryRequest-like dicts
- Supports Channel-Based Query for 802.11 (via spectrum_inquiry) and NR-U when
  channel CFIs are provided using Annex A mapping (GOC→BW, CFI→center MHz)
- Returns response codes (SUCCESS, MISSING_PARAM, INVALID_VALUE,
  UNEXPECTED_PARAM, UNSUPPORTED_BASIS) and availabilityExpireTime

This module focuses on correctness and leaves frequency-based queries as
UNSUPPORTED_BASIS unless implemented by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Tuple

from .spec_params import SpecParameters
from .spectrum_inquiry import spectrum_inquiry
from .grant_table import build_grant_table_with_incumbents


# Response codes per TS-3007 §6.2/6.3
RC_SUCCESS = 0
RC_DEVICE_DISALLOWED = 101
RC_MISSING_PARAM = 102
RC_INVALID_VALUE = 103
RC_UNEXPECTED_PARAM = 106
RC_UNSUPPORTED_BASIS = 301


def _expiry_iso8601(seconds: int = 900) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


def _is_number(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def nru_goc_to_bw_mhz(goc: int) -> float | None:
    mapping = {300: 20.0, 301: 40.0, 302: 60.0, 303: 80.0, 304: 100.0}
    return mapping.get(goc)


def nru_cfi_to_center_mhz(cfi: int) -> float:
    # Annex A: Fc (MHz) = 3000 + 15 * (CFI - 600000) / 1000
    return 3000.0 + 15.0 * (float(cfi) - 600000.0) / 1000.0


def handle_available_spectrum_inquiry(
    request: Dict[str, Any],
    spec: SpecParameters,
    incumbents: Iterable[Dict[str, Any]],
    *,
    certified_ids: Iterable[str] | None = None,
    disallowed_ids: Iterable[str] | None = None,
    disallowed_pairs: Iterable[Tuple[str, str]] | None = None,
) -> Dict[str, Any]:
    # Basic validation: location
    missing: List[str] = []
    loc = request.get("location")
    if not isinstance(loc, dict):
        missing.append("location")
    else:
        if not _is_number(loc.get("lat")):
            missing.append("location.lat")
        if not _is_number(loc.get("lon")):
            missing.append("location.lon")
        # §6.2 unexpected if multiple horizontal uncertainty fields present; reject if more than one given
        horiz_fields = [f for f in ("ellipse", "linearPolygon", "radialPolygon") if f in loc]
        if len(horiz_fields) > 1:
            return {"responseCode": RC_UNEXPECTED_PARAM, "supplementalInfo": {"unexpectedParams": horiz_fields}}
    if missing:
        return {
            "responseCode": RC_MISSING_PARAM,
            "supplementalInfo": {"missingParams": missing},
        }
    ap_lat = float(loc["lat"])  # type: ignore[index]
    ap_lon = float(loc["lon"])  # type: ignore[index]

    # §6.2 certification/disallowed lists (optional enforcement)
    cert = request.get("certification", {}) if isinstance(request.get("certification"), dict) else {}
    cert_id = cert.get("id")
    serial = cert.get("serialNumber")
    if certified_ids is not None and cert_id is not None:
        if cert_id not in set(certified_ids):
            return {"responseCode": RC_INVALID_VALUE, "supplementalInfo": {"invalidParams": ["certification.id"]}}
    if disallowed_ids is not None and cert_id is not None:
        if cert_id in set(disallowed_ids):
            return {"responseCode": RC_DEVICE_DISALLOWED}
    if disallowed_pairs is not None and cert_id is not None and serial is not None:
        if (cert_id, str(serial)) in set(disallowed_pairs):
            return {"responseCode": RC_DEVICE_DISALLOWED}

    # Decide which method is requested
    freq_req = request.get("inquiredFrequencyRange")
    chan_req = request.get("inquiredChannels")

    # If both are present -> unexpected per §6.2
    if isinstance(freq_req, list) and isinstance(chan_req, list):
        return {
            "responseCode": RC_UNEXPECTED_PARAM,
            "supplementalInfo": {"unexpectedParams": ["inquiredFrequencyRange", "inquiredChannels"]},
        }

    # Frequency-based query
    if isinstance(freq_req, list):
        # If minDesiredPower is included in a pure frequency-based query: UNEXPECTED_PARAM (per §6.3.3)
        if "minDesiredPower" in request:
            return {"responseCode": RC_UNEXPECTED_PARAM, "supplementalInfo": {"unexpectedParams": ["minDesiredPower"]}}
        # Build 1 MHz bins per range and compute PSD per bin, then merge identical bins
        env = request.get("environment", "urban")
        model = request.get("pathModel", "auto")
        margin = float(request.get("protectionMarginDb", 0.0))
        results = []  # list of AvailableFrequencyInfo {frequencyRange:{low,high}, maxPsd}
        for fr in freq_req:
            try:
                lo = float(fr["lowMHz"])  # type: ignore[index]
                hi = float(fr["highMHz"])  # type: ignore[index]
            except Exception:
                return {"responseCode": RC_INVALID_VALUE, "supplementalInfo": {"invalidParams": ["inquiredFrequencyRange"]}}
            if hi <= lo:
                return {"responseCode": RC_INVALID_VALUE, "supplementalInfo": {"invalidParams": ["inquiredFrequencyRange"]}}
            # 1 MHz bins
            start_mhz = int(lo)
            end_mhz = int(hi)
            bins = []  # (low, high, psd)
            for f in range(start_mhz, end_mhz):
                # evaluate a 1 MHz "channel" [f, f+1]
                rows = build_grant_table_with_incumbents(
                    spec=spec,
                    incumbents=list(incumbents),
                    distance_m=None,
                    ap_lat=ap_lat,
                    ap_lon=ap_lon,
                    lower_mhz=float(f),
                    upper_mhz=float(f + 1),
                    bandwidths_mhz=(1.0,),
                    inr_limit_db=-6.0,
                    environment=env,
                    path_model=model,
                    protection_margin_db=margin,
                )
                if not rows:
                    continue
                # Use PSD field from evaluator; for 1 MHz, EIRP == PSD numerically, but PSD is explicit
                psd = rows[0].allowed_psd_dbm_per_mhz
                bins.append((float(f), float(f + 1), float(psd)))
            # Merge adjacent bins with same PSD (within tol)
            tol = 1e-6
            merged: List[Tuple[float, float, float]] = []
            for b in bins:
                if not merged:
                    merged.append(list(b))  # type: ignore[list-item]
                else:
                    last = merged[-1]
                    if abs(last[2] - b[2]) < tol and abs(last[1] - b[0]) < 1e-9:
                        merged[-1] = (last[0], b[1], last[2])
                    else:
                        merged.append(b)
            for lo_b, hi_b, psd in merged:
                results.append({
                    "frequencyRange": {"lowMHz": lo_b, "highMHz": hi_b},
                    "maxPsd": psd,
                })
        return {"responseCode": RC_SUCCESS, "availabilityExpireTime": _expiry_iso8601(), "availableFrequencyInfo": results}

    # Channel-based query
    if not isinstance(chan_req, list) or not chan_req:
        return {"responseCode": RC_MISSING_PARAM, "supplementalInfo": {"missingParams": ["inquiredChannels"]}}

    # Each entry should have a globalOperatingClass; channelCfi optional
    centers: List[Tuple[float, float]] = []  # (center_mhz, bw_mhz)
    invalid: List[str] = []
    for item in chan_req:
        if not isinstance(item, dict):
            invalid.append("inquiredChannels[]")
            continue
        goc = item.get("globalOperatingClass")
        if not isinstance(goc, int):
            invalid.append("globalOperatingClass")
            continue
        cfis = item.get("channelCfi")
        if cfis is None:
            # No CFIs provided: we require explicit CFIs for NR-U in this minimal handler
            return {"responseCode": RC_UNSUPPORTED_BASIS}
        if not isinstance(cfis, list) or not all(isinstance(c, int) for c in cfis):
            invalid.append("channelCfi")
            continue
        bw = nru_goc_to_bw_mhz(goc)
        if bw is None:
            invalid.append("globalOperatingClass")
            continue
        for cfi in cfis:
            centers.append((nru_cfi_to_center_mhz(cfi), bw))

    if invalid:
        return {"responseCode": RC_INVALID_VALUE, "supplementalInfo": {"invalidParams": list(set(invalid))}}

    # Evaluate via spectrum inquiry across tiny per-channel bands
    band_ranges = [(fc - bw / 2.0, fc + bw / 2.0) for fc, bw in centers]
    rows = spectrum_inquiry(
        spec=spec,
        incumbents=list(incumbents),
        ap_lat=ap_lat,
        ap_lon=ap_lon,
        band_ranges_mhz=band_ranges,
        bandwidths_mhz=tuple(sorted({bw for _, bw in centers})),
        inr_limit_db=-6.0,
        environment=request.get("environment", "urban"),
        path_model=request.get("pathModel", "auto"),
        protection_margin_db=float(request.get("protectionMarginDb", 0.0)),
    )

    # Build AvailableChannelInfo with parallel arrays channelCfi/maxEirp as per §6.3.4
    # We preserve the order of CFIs provided per GOC item.
    # Map (center_mhz, bw) -> EIRP
    key_to_eirp = {(r.center_mhz, r.bandwidth_mhz): r.allowed_eirp_dbm for r in rows}

    available = []
    for item in chan_req:
        goc = item["globalOperatingClass"]
        cfis = item.get("channelCfi", [])
        bw = nru_goc_to_bw_mhz(goc)
        max_eirp_list: List[float] = []
        for cfi in cfis:
            fc = nru_cfi_to_center_mhz(cfi)
            eirp = key_to_eirp.get((fc, bw), 0.0)
            max_eirp_list.append(eirp)
        available.append({
            "globalOperatingClass": goc,
            "channelCfi": cfis,
            "maxEirp": max_eirp_list,
        })

    return {"responseCode": RC_SUCCESS, "availabilityExpireTime": _expiry_iso8601(), "availableChannelInfo": available}


