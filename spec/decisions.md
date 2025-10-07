## Project decisions and assumptions (living document)

Scope
- Target: Standard Power Wi‑Fi 6E under U.S. FCC/WINNF; adaptable for Turkey FS case study.
- Protection criterion: I/N ≤ −6 dB at the fixed service receiver input.
- Bands: 5925–6425 MHz and 6525–6875 MHz (gap 6425–6525 not included for SP use).

Propagation
- Default selector: WINNER‑II‑like placeholder for distances < 5 km; ITM‑like placeholder for ≥ 5 km.
- FSPL available for LoS sanity checks; will replace placeholders with proper ITM when ready.

Incumbent (FS) defaults
- Noise figure: 4.0 dB for center ≤ 6425 MHz; 4.5 dB for > 6425 MHz (per ITU‑R F.758 reference in WINNF text) unless explicit NF is provided.
- Noise bandwidth: default 20 MHz unless explicit value is provided or derivable from ULS/metadata.
- Antenna gain: default 30 dBi, Rx losses 1 dB, polarization mismatch 0 dB until real data are available.

Adjacent‑channel handling
- Combine Tx ACLR and Rx ACS via ACIR: ACIR_lin = 1/(10^(−A_tx/10) + 10^(−A_rx/10)).
- If only ACIR is provided in text, split evenly into A_tx/A_rx for computation.
- Nearest‑neighbor lookup across offsets (e.g., 20/40 MHz) when exact entries are missing.

Regulatory power
- Max EIRP cap defaults to 36 dBm (configurable). Allowed EIRP is min(cap, value to satisfy I/N limit).
- PSD↔EIRP relation: EIRP_total_dBm = PSD_dBm/MHz + 10·log10(B_MHz).

Outputs
- Grant table per Wi‑Fi channel (center, bandwidth): allowed EIRP/PSD and grant/deny flag.
- KPI: INR violation probability over scenarios (to be computed after scenario runs).

Turkey FS case study
- Hypothetical FS receiver center at 6175 MHz (mid of 5925–6425) used when exact FS center is unknown.
- We will extend to cover upper block 6525–6875 as needed.

Notes
- This file records decisions so they persist beyond chat context. Update as requirements change.

