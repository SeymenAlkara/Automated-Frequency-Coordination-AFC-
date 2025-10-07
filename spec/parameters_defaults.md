## Parameter defaults (initial)

Incumbent receiver (FS)
- Noise figure (NF): 4.0 dB (≤ 6425 MHz), 4.5 dB (> 6425 MHz) unless specified
- Noise bandwidth (B_Rx): 20 MHz (placeholder)
- Antenna gain (G_rx): 30 dBi (placeholder)
- Rx losses (L_rx): 1 dB (placeholder)
- Polarization mismatch (L_pol): 0 dB (placeholder)

Regulatory limits
- Max EIRP: 36 dBm (configurable per jurisdiction)

Adjacent-channel data (example)
- If ACIR ±20 MHz is 27 dB and detailed ACLR/ACS not given, use A_tx = A_rx = 13.5 dB at 20 MHz.
- Example tables currently seeded in parser: {20: 30 dB, 40: 35 dB} for both ACLR and ACS.

Propagation selector
- WINNER‑II‑like for d < 5 km, ITM‑like for d ≥ 5 km (placeholders).

Wi‑Fi channels considered
- Lower block: 5925–6425 MHz
- Upper block: 6525–6875 MHz
- Bandwidths: 20/40/80/160 MHz

