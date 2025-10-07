## AFC Project – Module-by-Module Implementation Summary (non-technical)

What each Python file implements and how it maps to the requirements (TS‑1014, TS‑3007). This is a readable index of “what’s where”.

Core protection math and evaluators
- `afc_new/link_budget.py` – Link budget building blocks (EIRP, noise power, I/N, thresholds, interference margin). Used everywhere that computes interference or checks I/N ≤ −6 dB.
- `afc_new/fspl.py` – Free‑space path loss functions (baseline propagation).
- `afc_new/acir.py` – ACIR math (combines Tx ACLR and Rx ACS). Used for adjacent‑channel protection per TS‑1014.
- `afc_new/acir_masks.py` – Interpolates Tx/Rx mask points by offset; computes ACIR at any offset.
- `afc_new/acir_defaults.py` – Conservative default ACIR/ACS masks used when none are provided.
- `afc_new/fs_bandwidth.py` – FS receiver bandwidth precedence (R2‑AIP‑19): emission designator → explicit Rx BW → ULS BW → default.
- `afc_new/propagation.py` – Propagation selector (FSPL, simplified WINNER‑like, two‑slope) plus environment/clutter and building penetration hooks.
- `afc_new/itm.py` – ITM (Longley–Rice) integration point (scaffold). Currently a placeholder with typed parameters; designed to be swapped with a real ITM library later.
- `afc_new/antenna.py` – Simple off‑axis antenna discrimination (parabolic RPE‑like) and azimuth utilities.
- `afc_new/antenna_rpe.py` – Annex‑E‑style RPE interpolation utilities (angle→attenuation curves) for azimuth/elevation.
- `afc_new/geodesy.py` – Geographic math (Haversine distance and initial bearing) for AP→FS geometry and antenna pointing.

Grant tables and spectrum inquiry
- `afc_new/grant_table.py` – The main evaluator producing per‑channel allowed EIRP/PSD and grant/deny. Covers co‑channel and adjacent (ACIR), protection margin (R2‑AIP‑20), passive sites (evaluated as extra receivers; strictest limit applied), device constraints (min EIRP/PSD), indoor/penetration, environment.
- `afc_new/spectrum_inquiry.py` – Single entry point to compute per‑band, per‑BW grant tables for an AP location across all incumbents. Threads protection margin, constraints, env/model flags.
- `afc_new/bands.py` – Helpers to enumerate standard 6 GHz centers per band/BW.
- `afc_new/api.py` – AFC‑style “availableChannels” JSON builder with trace fields (limiting incumbent, co/adj cause, ACIR).
- `afc_new/contours.py` – Generates a PNG “exclusion map” (green=grant, red=deny) around any FS receiver for a chosen channel.

Messaging (TS‑3007 AFC–SPD interface)
- `afc_new/protocol.py` – Minimal handler for AvailableSpectrumInquiry:
  - Validates location, method fields, and parameters; returns responseCode per spec (SUCCESS, MISSING_PARAM, INVALID_VALUE, UNEXPECTED_PARAM, UNSUPPORTED_BASIS, DEVICE_DISALLOWED).
  - Channel‑Based Query: supports NR‑U (3GPP) Annex‑A mapping (globalOperatingClass→BW, CFI→center MHz); returns `availableChannelInfo` with parallel `channelCfi`/`maxEirp` arrays.
  - Frequency‑Based Query: returns merged `availableFrequencyInfo` with `maxPsd` per 1 MHz bins.
  - Optional certification/disallowed list checks via function parameters (simple ID/pair lists).

Aggregates, KPIs, loaders, CLI, and UI
- `afc_new/multi_ap.py` – Aggregate INR evaluator for multiple APs per channel; summary across channels (worst‑case per channel, all‑pass flag).
- `afc_new/kpi.py` – IPC violation probability (from grants or aggregate INR), grant stats.
- `afc_new/loaders.py` – Incumbent record loader (ULS‑style text) and normalization (Annex C mapping, simplified).
- `afc_new/cli.py` – Command‑line utility to run spectrum inquiry across bands and save CSV; supports env, path model, indoor/penetration, device min EIRP/PSD.
- `afc_new/dashboard_app.py` – Streamlit MVP: map (AP/FS), UNII‑5 grant grid, denied‑channels table, CSV download.

What’s configurable at runtime
- AP location (lat/lon), environment (`urban|suburban|rural|indoor`), path model (`auto|fspl|winner|two_slope|itm`), protection margin (dB), indoor/penetration loss (dB), device constraints (min EIRP/PSD), incumbent records (FS positions, gains/azimuths, optional RPE tables and passive sites), ACIR masks (or defaults).

Known placeholders and simplifications (important for audits)
- ITM model: `afc_new/itm.py` is a scaffold. It currently adds a heuristic excess loss. For regulatory audits, integrate a certified Longley–Rice implementation and feed terrain/heights/reliability per TS‑1014.
- RPE patterns: defaults to a simple parabolic envelope unless per‑device Annex‑E RPE tables are supplied. For audits, use manufacturer RPEs (CSV) and include elevation tilt if applicable.
- ACIR masks: `acir_defaults.py` provides conservative placeholders. Replace with masks derived from 47 CFR 15.407(b)(7) / device certification.
- Environment/penetration: fixed offsets (e.g., urban +8 dB, indoor 12 dB). Replace with validated clutter/penetration models.
- Frequency‑based PSD: computed via 1‑MHz “channels” around each MHz bin. This matches the spirit of per‑MHz PSD but is still an approximation; for audits, align binning/merging with the exact response schema and limits.
- Certification lists: handler accepts lists but we don’t persist a database; hook to a real Certified ID / Disallowed list service for production.
- UI: Streamlit is an MVP (persistence and multiple bands pending). This does not affect engine correctness but is not feature‑complete.

Recommended steps to reach audit‑ready status
1) Swap in a certified ITM library and plumb terrain profiles and reliability.
2) Load official RPEs and ACIR masks; remove placeholders.
3) Parameterize environment/penetration with validated models and site data.
4) Persist and maintain Certified/Disallowed device lists.
5) Expand UI to all UNII bands, add tooltips and bottleneck breakdowns, and ensure result persistence on reruns.

Where to start
- For grants: `spectrum_inquiry.py` → `grant_table.py`
- For messaging (TS‑3007): `protocol.py`
- For maps: `contours.py` (static PNG); UI: `dashboard_app.py`
- For aggregates: `multi_ap.py`

