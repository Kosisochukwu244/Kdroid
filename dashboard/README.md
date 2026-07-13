# Kdroid dashboard (Phase 4)

Not started yet — this is a placeholder so the repo structure reflects the
full architecture from day one.

## Intent

Turn fused vision + sensor records into something a farmer can actually use:
a per-row, per-plant grid with a status color and trend over visits, in
plain language rather than raw model output.

## Planned approach

- Local-first: read from `kdroid_local.sqlite3` so it works without live
  connectivity; sync to/from Cyberwave's stored telemetry when available.
- Keep it simple for v1 — a lightweight web view (Flask, matching the
  pattern the Beast's own web app already uses) is enough; no need for a
  heavier framework for a competition demo.
- Consider reusing the Google Apps Script / spreadsheet-backed dashboard
  pattern if a zero-install option is preferable for a non-technical
  end user in early pilots.

## Data contract (draft)

Each record the dashboard reads should look roughly like:

```json
{
  "plant_id": "row1-plant2",
  "timestamp": "2026-07-20T09:15:00Z",
  "visual_flag": "possible early blight",
  "soil_moisture_pct": 22.5,
  "temperature_c": 29.1,
  "humidity_pct": 61.0,
  "summary": "Leaves show early discoloration; soil moisture is low — likely drought stress, not disease."
}
```

Finalize this once Phase 3 fusion logic exists.
