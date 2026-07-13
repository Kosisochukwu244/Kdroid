# Architecture

## Design goals

- **Deterministic localization over SLAM.** A comparable Cyberwave/Beast
  project ("Roamie", see `docs/reference-projects.md`) used monocular
  ORB-SLAM3 for waypoint localization and documented real drift and low
  frame-rate issues on this exact hardware. Kdroid avoids that failure mode
  by using AprilTag fiducials staked at each plant/row position instead.
  Trade-off: requires physically placing markers in the field, but it's
  drift-free, cheap, and fast to implement.
- **Push inference to Cyberwave, not a local model server.** The host
  controller (Pi) doesn't need to run its own VLM. Cyberwave's model catalog
  and workflow engine take the frame + prompt and return a result, so the
  Pi's job is orchestration (movement, tag detection, triggering), not
  inference.
- **Fuse vision with cheap sensors.** A VLM's read of "leaves look wilted" is
  ambiguous — could be drought stress or root rot. Pairing it with soil
  moisture from the ESP32 disambiguates cheaply.
- **Local-first data path.** Rural field connectivity is not guaranteed.
  Scouting runs should buffer results locally (SQLite) and sync to the
  dashboard/Cyberwave cloud opportunistically, not block on a live
  connection.

## Component breakdown

### `robot_control.py`
Wraps the Cyberwave SDK twin for the Beast. Responsible for:
- Pairing/connecting to the twin (`cw.twins("waveshare/ugv-beast")` —
  confirm exact catalog slug once the twin is provisioned; Beast may need to
  be registered as a custom twin if not yet in the public catalog).
- Movement primitives for row traversal (forward/turn), and a `use_controller`
  hook so the robot can be handed to a human via the Cyberwave dashboard
  during testing/demo without touching code.
- Switching between `cw.affect("simulation")` and `cw.affect("live")` so the
  scouting loop can be dry-run in the Playground sim before field use.

### `waypoint_manager.py`
- Runs AprilTag detection (OpenCV `cv2.aruco`) on the live camera frame.
- Maintains a lookup of tag ID → (row, plant index, prompt).
- Debounces triggers with a cooldown so idling near a tag doesn't spam the
  workflow.
- **Open question:** does the Cyberwave SDK expose camera frames at a rate
  usable for real-time tag detection on the Pi, or should tag detection run
  on the ESP32/local frame buffer before frames are uploaded to Cyberwave?
  Confirm against `docs.cyberwave.com/technology/components/sdk` — the
  Roamie project saw only ~2Hz over the Cyberwave-uploaded stream, which
  may be fine for tag detection (robot moves slowly) but worth validating
  early.

### `workflow_trigger.py`
- On a waypoint trigger: grabs the current frame, uploads it, and fires a
  Cyberwave workflow with the plant-specific prompt.
- Mirrors the pattern documented in the Roamie repo: upload frame → PATCH the
  workflow's Call-Model node with the image URL + prompt → POST to trigger
  the workflow run. Treat this as a starting guess, not confirmed API —
  verify exact endpoint shape against current Cyberwave API docs once you
  have API key access, since this was reverse-engineered from a community
  project rather than official docs.
- Also exposes a manual trigger path (no waypoint needed) for
  testing/demoing the VLM call in isolation.

### `sensor_bridge.py`
- ESP32 sub-controller publishes soil moisture / temperature / humidity over
  its existing serial link to the Pi (already how the Beast's dual-controller
  setup works for motor/IMU data).
- Bridge relays those readings to Cyberwave as twin telemetry (SDK supports
  MQTT-based telemetry streaming) so they live alongside camera-triggered
  events on the same timeline.

### Fusion + dashboard (phase 3–4, not yet built)
- A small service reads the VLM result + nearest-in-time sensor reading and
  writes a single structured record (`plant_id, timestamp, visual_flag,
  soil_moisture, temp, humidity, plain_language_summary`).
- Dashboard reads from local SQLite (offline-safe) and/or Cyberwave's stored
  telemetry (when synced), and renders a per-row, per-plant view over time
  rather than a raw model transcript.

## Known risks / things to validate early

1. **Camera frame rate through the Cyberwave upload path.** Confirm this
   doesn't bottleneck tag detection or the field-scouting pace.
2. **Whether Beast is a first-class Cyberwave twin or needs custom
   registration.** Check the digital twin catalog before assuming
   `cw.twins("waveshare/ugv-beast")` works out of the box.
3. **Outdoor weatherproofing.** The Beast chassis is not waterproof; dew and
   soil moisture are a given in a field. Plan a basic enclosure for the
   driver board bay before extended outdoor testing.
4. **Workflow trigger API shape.** As noted above, unconfirmed — first task
   in Phase 1.
