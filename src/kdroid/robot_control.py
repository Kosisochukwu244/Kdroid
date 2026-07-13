"""
Thin wrapper around the Cyberwave SDK for the UGV Beast twin.

Keeps all direct SDK calls in one place so the rest of Kdroid doesn't need
to know Cyberwave's API shape. If the SDK's method names change, this is
the only file that should need edits.

Phase 0 goal: everything in this file should work against both
`cw.affect("simulation")` and `cw.affect("live")` with no code changes.
"""
from __future__ import annotations

from cyberwave import Cyberwave

from kdroid.config import config


class BeastController:
    def __init__(self, simulate: bool = False):
        self._cw = Cyberwave()
        self._twin = self._cw.twins(config.cyberwave_twin_slug)
        self._camera = self._cw.twins("camera")
        if simulate:
            self._cw.affect("simulation")
        else:
            self._cw.affect("live")

    # -- movement -----------------------------------------------------
    def move_forward(self, meters: float) -> None:
        self._twin.move_forward(meters)

    def move_backward(self, meters: float) -> None:
        self._twin.move_backward(meters)

    def turn_left(self, radians: float) -> None:
        self._twin.turn_left(radians)

    def turn_right(self, radians: float) -> None:
        self._twin.turn_right(radians)

    def stop(self) -> None:
        self._twin.stop()

    # -- camera ---------------------------------------------------------
    def start_camera_stream(self) -> None:
        self._camera.start_streaming()

    def get_latest_frame(self):
        """
        Returns the most recent camera frame.

        TODO: confirm the exact accessor on the camera twin object (e.g.
        `.latest_frame()` vs a subscribed callback) against current SDK
        docs — this is a best guess pending hands-on testing.
        """
        return self._camera.latest_frame()

    # -- human handoff ----------------------------------------------------
    def hand_to_human(self) -> None:
        """Useful for demos/testing: let a human drive from the dashboard."""
        self._twin.use_controller("keyboard")

    def hand_to_code(self) -> None:
        self._twin.use_controller("code")


if __name__ == "__main__":
    # Quick manual smoke test: python -m kdroid.robot_control
    beast = BeastController(simulate=True)
    beast.start_camera_stream()
    beast.move_forward(0.3)
    beast.turn_left(0.5)
    beast.stop()
    print("Smoke test complete (simulation).")
