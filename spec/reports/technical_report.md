## AFC Simulation – Technical Summary (1 page)

Scope
- Standard‑Power Wi‑Fi 6E under U.S. FCC/WINNF principles; adaptable to other jurisdictions.
- AFC incumbent protection against Fixed Service (FS) receivers across UNII‑5/7.

Core Protection Logic (WINNF‑TS‑1014 alignment)
- Interference budget: I/N ≤ −6 dB (9.1.1). Thermal noise: N = −174 + 10log10(B_Rx) + NF.
- Co/adjacent channels: co‑channel via link budget; adjacent via ACIR where ACIR⁻¹ = 10^(−ACLR/10)+10^(−ACS/10) (R0‑AIP‑04, R2‑AIP‑03). We interpolate masks and provide defaults when sparse.
- Protection margin: optional extra margin (R2‑AIP‑20) by tightening I/N by protection_margin_db.
- FS parameters (9.1.2): precedence for receiver bandwidth (R2‑AIP‑19) — emission designator > explicit Rx BW > ULS BW > default. FS NF defaults by band; Rx losses and polarization considered.
- Passive sites (R2‑AIP‑31): passive repeaters/billboards modeled as additional FS receivers; strictest limit governs.

Propagation and Geometry (9.1.3)
- Selector: FSPL, simplified WINNER‑like, two‑slope, and ITM scaffolding (Longley–Rice) with typed parameters. Environment clutter and building penetration hooks.
- Geometry: Haversine distance AP→FS; initial bearing for FS antenna discrimination. Off‑axis gain via parabolic model or Annex‑E‑style RPE tables (CSV loaders, interpolation).

Outputs
- Grant tables per band/BW: channel number, center MHz, allowed EIRP/PSD, decision (grant/deny), plus trace (limiting incumbent, co/adj, ACIR). CSV export.
- Aggregate INR: multi‑AP evaluator per channel; worst‑case INR per channel and pass/fail.
- KPIs: grant stats; IPC violation probability from grants or aggregate INR.

APIs, CLI, and UI
- API: `build_available_channels_response(_json)` returns AFC‑style available‑channels JSON (with trace fields).
- CLI: `python -m afc_new.cli --ap-lat --ap-lon --bands {unii5|unii7|both} --env urban --out file.csv` with `--indoor`, `--penetration-db`, `--min-eirp`, `--min-psd`, `--path-model`.
- UI: Streamlit MVP for UNII‑5 grid and map (AP/FS).

TS‑3007 Messaging (AFC–SPD Interface)
- Handler: `protocol.handle_available_spectrum_inquiry(request, spec, incumbents, ...)` (Channel‑Based and Frequency‑Based queries).
- Channel‑Based (NR‑U): supply `inquiredChannels: [{globalOperatingClass, channelCfi[]}]` – Annex A mapping used to find center MHz; response includes `availableChannelInfo` with `channelCfi` and `maxEirp` arrays.
- Frequency‑Based: supply `inquiredFrequencyRange: [{lowMHz, highMHz}]` – response includes `availableFrequencyInfo` with contiguous ranges and `maxPsd` per 1‑MHz bin.
- Response codes per §6.2/6.3: 0 SUCCESS, 101 DEVICE_DISALLOWED, 102 MISSING_PARAM, 103 INVALID_VALUE, 106 UNEXPECTED_PARAM, 301 UNSUPPORTED_BASIS.
- Optional certification enforcement via runtime lists: `certified_ids`, `disallowed_ids`, and `(id, serial)` pairs.

Assumptions and Placeholders
- ITM and RPE are pluggable; current code ships clear hooks and simple placeholders.
- Default ACIR masks are conservative; replace with certified masks when available.
- Device constraints (min EIRP/PSD) optional; fallback decision is EIRP ≥ 0 dBm.

Validation
- Consolidated cell exercises spectrum inquiry near FS (denials), ACIR profile, passive sites, device constraints, and aggregate multi‑AP INR. A copy is saved as `spec/validation_cell.txt`.


