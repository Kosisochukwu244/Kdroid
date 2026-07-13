"""
Phase 2 entrypoint: drives a fixed route, checks for AprilTag waypoints at
each step, and fires a Cyberwave workflow when a waypoint is reached.

This is deliberately simple — a hardcoded route, not a planner. Extend once
Phase 2's exit criteria (autonomous multi-plant scouting run) is met.

Usage:
    python scripts/run_scout_loop.py --sim     # dry run in Cyberwave Playground
    python scripts/run_scout_loop.py           # live, on real hardware
"""
from __future__ import annotations

import argparse
import time

from kdroid.robot_control import BeastController
from kdroid.waypoint_manager import WaypointManager
from kdroid.workflow_trigger import WorkflowTrigger
from kdroid.config import config

# TODO: replace with your real field layout once tags are staked.
ROUTE = [
    {"action": "forward", "meters": 1.0},
    {"action": "check_waypoint"},
    {"action": "forward", "meters": 1.0},
    {"action": "check_waypoint"},
    {"action": "turn_left", "radians": 1.57},
    {"action": "forward", "meters": 1.0},
    {"action": "check_waypoint"},
]

# TODO: replace with your real tag IDs / plant metadata.
WAYPOINTS = [
    {"tag_id": 0, "row": 1, "plant_index": 1, "prompt": config.default_prompt},
    {"tag_id": 1, "row": 1, "plant_index": 2, "prompt": config.default_prompt},
    {"tag_id": 2, "row": 2, "plant_index": 1, "prompt": config.default_prompt},
]


def run(simulate: bool) -> None:
    beast = BeastController(simulate=simulate)
    beast.start_camera_stream()

    waypoints = WaypointManager(cooldown_s=config.waypoint_cooldown_s)
    for wp in WAYPOINTS:
        waypoints.register_waypoint(**wp)

    workflow = WorkflowTrigger()

    for step in ROUTE:
        if step["action"] == "forward":
            beast.move_forward(step["meters"])
        elif step["action"] == "turn_left":
            beast.turn_left(step["radians"])
        elif step["action"] == "check_waypoint":
            frame = beast.get_latest_frame()
            hit = waypoints.check_frame(frame)
            if hit:
                print(f"Waypoint hit: row {hit.row}, plant {hit.plant_index}")
                # TODO: encode `frame` to JPEG bytes before passing along —
                # left as a stub since encoding depends on the frame format
                # the SDK returns.
                result = workflow.trigger(frame_bytes=frame, prompt=hit.prompt)
                print(f"  -> workflow run {result.run_uuid}")
        time.sleep(0.5)  # let the robot settle before the next check

    beast.stop()
    print("Route complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action="store_true", help="run against Cyberwave Playground sim")
    args = parser.parse_args()
    run(simulate=args.sim)
