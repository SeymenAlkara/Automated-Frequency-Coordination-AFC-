## CLI User Guide (short)

Run spectrum inquiry and save CSV:
```bash
python -m afc_new.cli --ap-lat 41.0 --ap-lon 29.0 --bands unii5 --env urban --out grants.csv
```

Options
- `--bands {unii5|unii7|both}`: which bands to evaluate.
- `--env {urban|suburban|rural|indoor}`: environment/clutter.
- `--path-model {auto|fspl|winner|two_slope|itm}`: propagation selector.
- `--indoor`: apply default penetration loss (12 dB) unless overridden.
- `--penetration-db N`: explicit building penetration loss.
- `--min-eirp N`, `--min-psd N`: device minimums; channels below these are denied.
- `--spec-text PATH`: path to WINNF text input parsed for defaults.
- `--incs PATH`: path to incumbents text (ULS-style JSON blocks).

TS‑3007 demo (via Python, not CLI yet)
- Use `afc_new.protocol.handle_available_spectrum_inquiry(request, spec, incumbents)` with a dict request. See the notebook demo cell for examples of Channel‑Based (NR‑U) and Frequency‑Based queries.

Outputs
- CSV with: channel, center_mhz, bw_mhz, offset_mhz, path_loss_db, noise_dbm, allowed_eirp_dbm, allowed_psd_dBm_per_MHz, decision.


