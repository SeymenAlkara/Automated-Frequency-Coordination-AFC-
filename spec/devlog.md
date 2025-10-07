## Development log (high-level)

Milestones
- Initial analytical framework captured in `spec/analytical_framework.md` (I/N, FSPL, ACIR, SINR, Bianchi).
- Core modules scaffolded: link budget, FSPL, ACIR, PHY SINR, MAC Bianchi; unit tests added.
- AFC allocator with co/adjacent handling and ACIR support; spectrum inquiry wrappers.
- Parsing: FS parameters (NF/BW precedence per R2-AIP-19), ACIR/ACLR/ACS regex.
- Propagation: selector (FSPL/WINNER/two_slope) + ITM scaffolding; environment and penetration loss hooks.
- Geometry: Haversine distance, bearing, FS antenna discrimination (parabolic), optional RPE.
- Grant table generators: single FS and multi-incumbent (min across incumbents), CSV export, band/channel helpers.
- KPI: INR violation probability; ACIR profile utility.
- UI: Streamlit MVP (UNII-5 grid, AP/FS map); notes to persist results in session state.
- CLI: run spectrum inquiry across bands and save CSV.
- Aggregate: multi-AP INR evaluator.

Open items (to be refined later)
- Replace ITM placeholder with real Longley–Rice binding.
- RPE from manufacturer/Annex E; elevation tilt and polarization model.
- Aggregate multi-AP scenarios and maps; decision thresholds tied to device capabilities.
- Streamlit polish (tabs per band, tooltips, bottleneck breakdown), result persistence already noted.


