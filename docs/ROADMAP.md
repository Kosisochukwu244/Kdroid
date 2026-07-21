# Roadmap

Built in phases so there's always a working demo, even if later phases slip.
Each phase should end with something you can show, not just code that
compiles.

## Phase 0 — Bring-up ✅ mostly done

Goal: prove the Beast talks to Cyberwave at all.

- [x] Stop the default `ugv_rpi/app.py` program (was holding the camera +
      serial port) — killed process + disabled its `@reboot` cron entry
- [x] `pip install cyberwave` in a venv (`pip install --break-system-packages`
      or a venv is required on Bookworm — system Python is externally managed)
- [x] Install the Cyberwave CLI separately (`curl ... | bash`) — this is a
      DIFFERENT tool from the pip package, only the CLI has `pair`/`login`
- [x] `cyberwave login` + `sudo cyberwave pair` — installs
      `cyberwave-edge-core` as a systemd service, auto-detects the USB
      camera, links to your `ugv-live` twin
- [x] Move the robot live from a Python script — confirmed working:
      `cw.twin(asset_id, twin_id=..., environment_id=...)`, then
      `beast.move_forward(...)` etc.
- [ ] Camera **live streaming to the dashboard** specifically — blocked on
      access to a private `cyberwave-edge-python` repo (separate service
      from edge-core). Not required for the core pipeline — see Phase 1.

**Exit criteria met** for movement + basic SDK connectivity. Streaming to
the dashboard UI is a nice-to-have for demos, not a blocker — frame
*capture* for the VLM pipeline uses `source="local"`, which reads the USB
camera directly via OpenCV and doesn't depend on the blocked service at all.

## Phase 1 — Manual single-shot capture (pepper) — START HERE NOW

Goal: prove the full perception pipeline on ONE frame, no automation, no
waypoints, no route — before building anything else.

- [ ] Build one Cyberwave workflow in Studio: Call-Model node using the
      pepper prompt in `workflows/plant_health_workflow.md`, wired to a
      vision-capable model from the catalog. Record the workflow UUID into
      `.env` as `CYBERWAVE_WORKFLOW_ID`.
- [ ] Run `python scripts/test_single_capture.py` — point the camera at a
      real pepper plant/fruit, capture a frame via `source="local"`,
      trigger the workflow, save the result + image to `~/kdroid_data/`
- [ ] Confirm the JSON output actually parses (status/disease_guess/
      ripeness/confidence/notes) — iterate on the prompt in
      `config.default_prompt` if the model isn't following the schema
- [ ] Test against a few different real conditions: healthy leaf, a fruit
      showing early rot/discoloration if you have one, ripe vs. unripe
      fruit — see if the categories actually distinguish correctly
- [ ] Note: `workflow_trigger.py` currently only returns a `run_uuid`, not
      the model's actual text response — you'll need to check the result
      either in the Cyberwave dashboard's workflow run history, or extend
      `WorkflowTrigger` to poll the run status endpoint for the output.
      This is the next real code task once the manual test proves the
      concept works at all.

**Exit criteria:** point the camera at a real pepper plant, run one
command, get back a parsed healthy/diseased + ripe/unripe read, saved
locally to the SD card.

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
