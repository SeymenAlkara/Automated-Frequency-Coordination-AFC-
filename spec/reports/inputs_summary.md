## Inputs the simulator can accept

Incumbent (FS) records (ULS-style JSON blocks; see `spec/Example incumbents.txt`)
- Required:
  - `link_id`: string identifier
  - `freq_center_mhz`: FS receiver center frequency (MHz)
  - `bandwidth_mhz`: receiver bandwidth (MHz)
  - `rx_lat`, `rx_lon`: receiver location (deg)
- Optional:
  - `rx_antenna_gain_dbi` (default 30), `rx_antenna_azimuth_deg` (0), `rx_antenna_height_m` (10)
  - `polarization` ("H"/"V"), `rx_rpe_az`, `rx_rpe_el` (Annex‑E tables: [[angle, att], ...])
  - `passive_sites`: list of passive receive points (dicts with `lat`, `lon`, `gain_dbi`, `az_deg`, optional RPE and height)
  - Emission designator (e.g., `40M0F7W`) if available

Spec text (optional)
- `docs/extracted_afc_text.txt`: parsed for NF defaults, bandwidth precedence, and example ACIR masks if present. (WINNF-TS-1014, originally)

Runtime/user inputs
- AP site coordinates: latitude, longitude
- Environment: `urban|suburban|rural|indoor`
- Path model: `auto|fspl|winner|two_slope|itm`
- Protection margin (dB) to tighten I/N (R2‑AIP‑20)
- Indoor/penetration loss: `--indoor` or explicit `penetration_db`
- Device constraints: `min_eirp_dbm`, `min_psd_dbm_per_mhz`

AFC–SPD (TS‑3007) request fields user can supply
- location: `{lat, lon}` (and one of: `ellipse|linearPolygon|radialPolygon` if needed; not multiple simultaneously)
- inquiredChannels: list of `{globalOperatingClass, channelCfi[]}` for channel-based queries (NR‑U supported via Annex A)
- inquiredFrequencyRange: list of `{lowMHz, highMHz}` for frequency-based queries (returns per‑MHz PSD)
- Optional: `environment`, `pathModel`, `protectionMarginDb`
- Optional certification object: `{id, serialNumber}` – used against Certified ID List and Disallowed lists if provided at runtime

Outputs
- Grant CSV or JSON with per‑channel allowed EIRP/PSD and decision; trace fields indicate limiting incumbent and co/adj cause.
- Aggregate INR report for multi‑AP scenarios.


