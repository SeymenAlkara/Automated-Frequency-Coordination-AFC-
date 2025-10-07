## GUI (Streamlit) User Guide (short)

Launch:
```bash
python -m pip install streamlit streamlit-folium folium
streamlit run C:\Users\alise\Documents\DOKTORA\AFC_simulation\afc_new\dashboard_app.py
```

Sidebar inputs
- Environment: urban/suburban/rural/indoor
- Path model: auto/fspl/winner/two_slope/itm
- AP coordinates (WGS‑84): latitude/longitude
- Place AP ~0.6 km north of first FS for demo (optional)

Map
- Blue: AP; Red: FS receivers; Gray lines: AP→FS paths.

Results
- UNII‑5 grid shows allowed EIRP per channel with color (green/yellow/red) and value.
- Denied channels count and details table are displayed below; CSV download provided.

TS‑3007 (AFC–SPD) messaging
- Not directly in the UI yet; use the notebook demo cell to build requests and pretty‑print responses.

Notes
- If results disappear on interaction, click Compute grants again (session persistence is on but streamlit reruns on every change).


