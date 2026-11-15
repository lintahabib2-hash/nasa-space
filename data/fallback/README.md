# Fallback: cited static chart (not ingested data)

Owner: Member 4 (Environment & Radiation).

`eda-rr1-co2-iss.svg` is the documented fallback the plan asks for. If the NASA EDA export cannot be
retrieved, show this image instead of an ingested series. It is visibly labelled **"Static reference image:
not ingested data"** and carries the EDA citation, so it is never mistaken for live or ingested data.
In the app, setting `is_fallback_not_ingested: true` on the environment series makes the card show the same label.

Rebuild it (no network or extra packages needed):

    python backend/scripts/make_fallback_chart.py

Source: Data and visualizations are courtesy of the Environmental Data Application (EDA)
(https://visualization.osdr.nasa.gov/eda/). Version: not displayed on the site (accessed 14 Nov 2026).
