## Analytical Framework for AFC, PHY, and MAC (U.S. FCC)

Assumptions: U.S. FCC 6 GHz AFC regime. Protection criterion: I/N ≤ −6 dB unless otherwise specified. Propagation: start with FSPL and provide hooks for ITM and WINNER II model selection by distance. Environment/clutter terms are placeholders for now.

### Notation and Constants
- d: distance (m) between interferer (AP site) and incumbent receiver
- f: frequency (Hz)
- c: speed of light ≈ 3.0×10^8 m/s
- P_tx: transmit power at transmitter port (dBm)
- G_tx, G_rx: transmit/receive antenna gains (dBi)
- L_tx_losses, L_rx_losses: Tx/Rx feedline and hardware losses (dB, positive)
- EIRP (dBm) = P_tx (dBm) + G_tx (dBi) − L_tx_losses (dB)
- PL(d): path loss (dB) (FSPL, ITM, WINNER II, ...)
- I(d): interference power at the incumbent receiver terminal (dBm)
- N: noise power over receiver bandwidth (dBm)
- NF: receiver noise figure (dB)
- B_Rx: receiver noise bandwidth (Hz)
- I/N (dB) = I (dBm) − N (dBm)
- I_thresh: maximum allowed interference power at the incumbent receiver (dBm)

Thermal noise PSD at T0 = 290 K: −174 dBm/Hz.

### 1) AFC Layer — Link Budget → Interference → Protection Distance

1.1 Interference at incumbent receiver terminals:
I(d) [dBm] = EIRP − PL(d) + G_rx − L_rx_losses − L_polarization

1.2 Noise power and I/N:
N [dBm] = −174 + 10·log10(B_Rx) + NF
I/N [dB] = I − N
Regulatory condition: I/N ≤ −6 dB ⇒ I ≤ N − 6 dB ⇒ I_thresh = N − 6 dB.

1.3 Interference Margin (IM):
IM [dB] = I_thresh − I
IM > 0: protected; IM = 0: boundary; IM < 0: violation.

1.4 Free‑space protection distance (LoS):
FSPL [dB] = 20·log10(4·π·d·f / c)
Set I(d) = I_thresh and solve for FSPL_required:
FSPL_required = EIRP + G_rx − L_misc − I_thresh
Invert FSPL:
d = (c/(4π f)) · 10^{FSPL_required/20}

1.5 Adjacent‑channel handling (ACIR):
Let A_tx (dB) be Tx out‑of‑channel attenuation and A_rx (dB) be Rx selectivity (ACS). Combine linearly:
ACIR_lin = 1 / (10^{−A_tx/10} + 10^{−A_rx/10})
ACIR [dB] = 10·log10(ACIR_lin)
Adjacent‑channel interference:
I_adj [dBm] = I_cochannel − ACIR [dB]

### 2) PHY Layer — SINR, OFDMA, MIMO

2.1 Single‑stream SINR (narrowband):
S_lin = 10^{S/10}, I_lin = 10^{I_agg/10}, N_lin = 10^{N/10}
SINR_lin = S_lin / (I_lin + N_lin)
SINR [dB] = 10·log10(SINR_lin)

2.2 SU Beamforming (narrowband):
SINR = |h^H v|^2 P_s / ( Σ_j |h^H v_j|^2 P_j + N0·B )

2.3 OFDMA per‑RU capacity:
C_k = Σ_{n∈S_k} Δf_n · log2(1 + SINR_{k,n})

### 3) MAC Layer — Bianchi Saturated DCF

Let τ be transmit probability in a random slot; p collision probability:
p = 1 − (1 − τ)^{N−1}
For CWmin W and m backoff stages:
τ = [ 2 (1 − 2p) ] / [ (1 − 2p) (W + 1) + p W (1 − (2p)^m) ]
Solve fixed point {p, τ} numerically.

### Outputs Needed for AFC Decisions
- I(d) and I_thresh (per channel/BW)
- Interference margin IM and grant decision
- Allowed PSD/EIRP per channel: min(regulatory limit, value meeting I/N criterion)

### Notes
- Use ITM/WINNER II selection by distance; placeholders for clutter/building losses until presets are defined.
- Confirm whether the protection limit is exactly I/N ≤ −6 dB; adjust if different.

