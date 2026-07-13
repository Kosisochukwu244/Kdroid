# Reference projects

Prior art worth reading before/while building. None of these should be
copied wholesale — the point is to reuse validated patterns and avoid
re-discovering their dead ends.

## Roamie / "Principessa Robi" (UGV Beast + Cyberwave)
- Repo: https://github.com/OguzhanKirik/cyberwave
- Closest analog to Kdroid: a UGV Beast that streams camera frames through
  the Cyberwave SDK, localizes with monocular ORB-SLAM3, and triggers a
  VLM-based Cyberwave workflow at each plant to assess health, with results
  delivered to email/dashboard.
- Useful: their `AddWaypoint` / `TriggerWorkflow` service pattern, and their
  documented upload → PATCH Call-Model node → POST trigger workflow
  sequence — this is the template `workflow_trigger.py` is based on.
- Useful cautionary notes from their README: monocular SLAM drift, ~2Hz
  camera frame rate over the Cyberwave upload path, no confirmed LiDAR/IMU
  on their Beast unit. This is exactly why Kdroid uses AprilTags instead of
  SLAM for localization.

## Jupyter Rover UGV Beast
- Repo: https://github.com/RisorseArtificiali/jupyter-rover
- A catalog of self-contained notebooks for the Beast covering camera
  calibration, AprilTag localization, YOLOv8 obstacle detection, autonomous
  patrol, and a VLA pipeline. Worth checking their AprilTag notebook
  directly before writing `waypoint_manager.py` from scratch.

## buildPARITY (Pi 5 + D500 Lidar rover, Cyberwave)
- Repo: https://github.com/swilcock0/cyberwave-learning
- Tiered autonomy pattern: safety-critical reflexes handled locally via
  ROS2 + Nav2, mission-level decisions driven by cloud VLA models through
  Cyberwave Edge Core. Relevant if Kdroid ever needs an obstacle-avoidance
  layer on top of the waypoint loop.

## Hedon (custom UGV, Cyberwave + ROS2)
- Repo: https://github.com/EdyVision/hedon-robotics
- Example of fusing multiple sensor streams (camera, mic, biosignals) into
  a single behavioral decision loop on a Raspberry Pi over ROS2 + Cyberwave
  SDK — same shape as Kdroid's planned vision + soil-sensor fusion step,
  just a different sensor mix.
