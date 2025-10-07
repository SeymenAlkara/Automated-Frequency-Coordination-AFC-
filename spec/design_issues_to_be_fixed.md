## Design issues to revisit

1) Streamlit result persistence/flicker
- Symptom: grant grid appears briefly, then disappears on rerun.
- Root cause: Streamlit reruns the script on every widget interaction; results were only rendered inside the button branch.
- Mitigation: cache rows in `st.session_state` and render outside the button branch; consider `st.cache_data` for heavy calls.

2) Map/UI polish
- Add tabs per band (UNII‑5/6/7/8), scroll/zoom controls, hover tooltips, bottleneck incumbent details.
- Proper icons and legend for grant/deny colors.

3) ITM integration
- Replace placeholder model with a real Longley–Rice binding; support terrain profiles and reliability parameters.

4) Antenna RPE
- Replace simplified RPE with manufacturer/Annex E tables; support elevation tilt and polarization discrimination.

5) Decision threshold & device constraints
- Expose min operational EIRP/PSD in UI; deny if allowed EIRP below device minimum.

6) Aggregate interference
- Add scenario management for multiple APs and spatial layouts; visualize INR heatmaps.


