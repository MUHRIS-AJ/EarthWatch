# EarthWatch · Public natural-event explorer

Live on-demand reader for [NASA EONET](https://eonet.gsfc.nasa.gov/docs/v3) and [USGS earthquake GeoJSON](https://earthquake.usgs.gov/earthquakes/feed/v1.0/). A read-only data tool, **not** an emergency warning service or prediction engine.

Pipeline: SourceAgent (NASA + USGS) → AnalysisAgent (keyword/category filter) → VerificationAgent (provider IDs and source URLs) → ReportAgent (JSON events) → human review.

### Run
```bash
python core.py all
python core.py earthquake
python dashboard.py --port 8765
python -m unittest discover -s tests -v
```
Open http://localhost:8765 for the interactive browser UI.
FastMCP: `pip install -r requirements.txt && python server.py` (stdio) or `fastmcp run server.py:mcp --transport http --port 8000`.

If either upstream fails, the available provider can still supply a partial report with warnings. If both fail, an explicit error is returned. There is **no ongoing alert subscription, official warning, hazard forecast, or LLM agent**.
