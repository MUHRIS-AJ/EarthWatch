"""EarthWatch: NASA EONET + USGS read-only natural-event intelligence."""
from __future__ import annotations
from datetime import datetime, timezone
import re
from transport import request_json, SourceError

SERVICES = ["EarthWatch"]
NASA = "https://eonet.gsfc.nasa.gov/api/v3/events"
USGS = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"

def _event_nasa(item):
    geo = (item.get("geometry") or [{}])[-1]
    categories = [x.get("title") for x in (item.get("categories") or []) if x.get("title")]
    return {
        "id": "nasa:" + str(item.get("id", "")),
        "title": str(item.get("title") or "Unnamed natural event"),
        "category": ", ".join(categories) or "Natural event",
        "updated": geo.get("date"),
        "coordinates": geo.get("coordinates") if geo.get("type") == "Point" else None,
        "source_url": item.get("link") or "https://eonet.gsfc.nasa.gov/",
        "provider": "NASA EONET",
        "status": item.get("closed") and "closed" or "open"
    }

def _event_usgs(item):
    props = item.get("properties") or {}
    coords = (item.get("geometry") or {}).get("coordinates") or []
    millis = props.get("time")
    stamp = datetime.fromtimestamp(millis/1000, tz=timezone.utc).isoformat() if isinstance(millis,(int,float)) else None
    return {
        "id": "usgs:" + str(item.get("id", "")),
        "title": str(props.get("title") or "Earthquake"),
        "category": "Earthquake",
        "updated": stamp,
        "magnitude": props.get("mag"),
        "coordinates": coords[:2] if len(coords) >= 2 else None,
        "source_url": props.get("url") or "https://earthquake.usgs.gov/",
        "provider": "USGS",
        "status": str(props.get("status") or "reported")
    }

def collect():
    # Source Agent: two independent, documented US public data sources.
    events, errors = [], []
    try:
        data = request_json(NASA, {"status": "open", "limit": 40})
        events.extend(_event_nasa(x) for x in data.get("events", []) if isinstance(x, dict))
    except SourceError as exc:
        errors.append("NASA EONET: "+str(exc))
    try:
        data = request_json(USGS)
        events.extend(_event_usgs(x) for x in data.get("features", [])[:100] if isinstance(x, dict))
    except SourceError as exc:
        errors.append("USGS: "+str(exc))
    if len(errors) == 2:
        raise SourceError("All event sources unavailable: " + "; ".join(errors))
    return events, errors

def run(query: str, service: str = "EarthWatch"):
    if service not in SERVICES or not isinstance(query, str) or not 2 <= len(query.strip()) <= 120:
        raise ValueError("Select EarthWatch and enter 2–120 search characters (or 'all').")
    # Analysis Agent: filtered matching of official descriptions; no LLM inference.
    events, warnings = collect()
    keyword = query.strip().lower()
    if keyword != "all":
        matches = [e for e in events if keyword in (e["title"]+" "+e["category"]).lower()]
    else:
        matches = events
    # Verification Agent: accept only entries with provider IDs and HTTP(S) source references.
    sourced = [e for e in matches if e["id"].split(":")[-1] and str(e["source_url"]).startswith("https://")]
    sourced.sort(key=lambda e:e["updated"] or "", reverse=True)
    # Report Agent: no location predictions, no safety instructions and no fabricated alerts.
    return {
        "project":"EarthWatch", "query":query, "match_count":len(sourced),
        "events":sourced[:30], "source_errors":warnings,
        "source_catalog":[NASA,USGS],
        "agents":["SourceAgent: NASA+USGS","AnalysisAgent: category matching","VerificationAgent: provider+source URL","ReportAgent: evidence-linked summary"],
        "limitations":["Historical or ongoing events, not predictions.",
            "Not an official emergency warning or operational safety system.",
            "Source records may be delayed, incomplete or subsequently revised."]
    }

if __name__ == "__main__":
    import argparse, json
    ap=argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default="all")
    a=ap.parse_args()
    try: print(json.dumps(run(a.query), indent=2))
    except (SourceError,ValueError) as exc: ap.exit(2,str(exc)+"\n")
