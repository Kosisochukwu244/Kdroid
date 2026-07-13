"""
AprilTag-based waypoint detection. This replaces SLAM-based localization
(see ARCHITECTURE.md for why) with a deterministic tag-ID lookup.

Each tag staked in the field maps to a known (row, plant_index, prompt).
When the robot's camera sees a tag close/large enough in frame, that's
treated as "arrived at this plant" and a workflow trigger fires, with a
per-tag cooldown so lingering near a tag doesn't spam triggers.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import cv2
import numpy as np


@dataclass
class Waypoint:
    tag_id: int
    row: int
    plant_index: int
    prompt: str
    last_triggered: float = field(default=0.0)


class WaypointManager:
    def __init__(self, cooldown_s: float = 60.0, min_tag_area_px: int = 4000):
        """
        min_tag_area_px is a crude proxy for "close enough to trigger" —
        a tag filling more of the frame means the robot is nearer to it.
        Calibrate this against your actual tag size and mount height
        during Phase 2 field testing; don't trust the default.
        """
        self.cooldown_s = cooldown_s
        self.min_tag_area_px = min_tag_area_px
        self.waypoints: dict[int, Waypoint] = {}

        # Standard AprilTag dictionary; swap to a different family if your
        # printed tags use one (e.g. DICT_APRILTAG_25h9)
        self._aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        self._aruco_params = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(self._aruco_dict, self._aruco_params)

    def register_waypoint(self, tag_id: int, row: int, plant_index: int, prompt: str) -> None:
        self.waypoints[tag_id] = Waypoint(tag_id, row, plant_index, prompt)

    def check_frame(self, frame: np.ndarray) -> Waypoint | None:
        """
        Runs tag detection on a frame. Returns the Waypoint that should
        trigger, or None if nothing is ready to fire (not in view, too far,
        or still in cooldown).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._detector.detectMarkers(gray)

        if ids is None:
            return None

        now = time.monotonic()
        for tag_corners, tag_id_arr in zip(corners, ids):
            tag_id = int(tag_id_arr[0])
            waypoint = self.waypoints.get(tag_id)
            if waypoint is None:
                continue

            area = cv2.contourArea(tag_corners[0])
            if area < self.min_tag_area_px:
                continue  # tag visible but robot still too far away

            if now - waypoint.last_triggered < self.cooldown_s:
                continue  # already triggered recently

            waypoint.last_triggered = now
            return waypoint

        return None
