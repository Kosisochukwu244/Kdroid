# Roadmap

Built in phases so there's always a working demo, even if later phases slip.
Each phase should end with something you can show, not just code that
compiles.

## Phase 0 — Bring-up (first 1–2 days)

Goal: prove the Beast talks to Cyberwave at all.

- [ ] Install `cyberwave` SDK on the Pi, run `cyberwave --help`
- [ ] `cyberwave pair` the Beast, confirm it shows up as a twin in the
      Cyberwave dashboard
- [ ] Move the robot forward/turn from a Python one-liner using the SDK
- [ ] Start the camera twin, confirm you can view the stream live
- [ ] Test the same movement code against `cw.affect("simulation")` in the
      Playground, confirm parity with live

**Exit criteria:** you can drive the Beast and see its camera feed through
Cyberwave, from your own script, in both sim and live.

## Phase 1 — Manual scouting loop (days 3–5)

Goal: prove the perception pipeline before automating movement.

- [ ] Manually position the robot at a plant, grab a frame, upload it
- [ ] Build one Cyberwave workflow in Studio: Call-Model node with a plant
      health prompt, wired to a VLM from the catalog
- [ ] Trigger it manually via `workflow_trigger.py`, confirm you get back a
      sensible plant-health read
- [ ] Log the result (even just to a local JSON file)

**Exit criteria:** point the camera at a real plant, run one command, get a
plant-health assessment back.

## Phase 2 — Deterministic waypoints (days 6–9)

Goal: automate "go here, look, log it" without SLAM.

- [ ] Print/stake AprilTags at 3–5 test plant positions
- [ ] `waypoint_manager.py`: detect tags, map tag ID → plant metadata
- [ ] Wire proximity trigger → `workflow_trigger.py` automatically
- [ ] `scripts/run_scout_loop.py`: robot moves through a fixed route, stops
      and scans at each tag, resumes

**Exit criteria:** robot autonomously visits N marked plants in one run and
produces N logged assessments, unattended.

## Phase 3 — Sensor fusion (days 10–12)

Goal: combine vision with cheap ground-truth sensors.

- [ ] ESP32 reads soil moisture + temp/humidity, relayed to Pi
- [ ] `sensor_bridge.py` pushes readings to Cyberwave telemetry
- [ ] Fusion step pairs nearest sensor reading with each visual assessment
- [ ] Sanity-check fused output against a manual inspection of the same
      plants

**Exit criteria:** a single record per plant that combines what the camera
saw with what the soil sensor measured.

## Phase 4 — Farmer dashboard (days 13–16)

Goal: make the output usable by someone who isn't reading logs.

- [ ] Minimal dashboard (row/plant grid, status color, trend over visits)
- [ ] Local-first sync: buffer results offline, push when connected
- [ ] Plain-language summaries instead of raw model text

**Exit criteria:** a non-technical person can look at the dashboard and know
which plants need attention.

## Phase 5 — Field pilot + polish (remaining time)

- [ ] Run a real multi-row session end to end
- [ ] Basic weatherproofing pass on the electronics bay
- [ ] Record demo footage
- [ ] Write up results, known limitations, next steps for the cohort/comp
      submission

## Explicitly out of scope for v1

- Full SLAM / dense mapping — revisit only if AprilTag waypointing proves
  insufficient at scale
- Multi-robot fleet coordination
- On-device model training (use Cyberwave's catalog/fine-tuning instead)
