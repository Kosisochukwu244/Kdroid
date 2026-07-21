"""
Thin wrapper around the Cyberwave SDK for the UGV Beast twin.

Keeps all direct SDK calls in one place so the rest of Kdroid doesn't need
to know Cyberwave's API shape. If the SDK's method names change, this is
the only file that should need edits.

Confirmed against cyberwave==0.6.0 by hands-on testing against the real
Beast (not guessed) — see docs/ROADMAP.md Phase 0 notes:
  - cw.twin(asset_id, twin_id=..., environment_id=...) — singular, and
    needs the catalog ASSET uuid (not a "vendor/slug" string) plus the
    specific twin_id/environment_id for YOUR twin. Get these via
    `cyberwave twin show <your-twin-uuid>`.
  - Camera lives on the twin itself (twin.camera), not a separate twin.
  - stop() is NOT a flat method on the twin — it's twin.locomotion.stop().
    move_forward/move_backward/turn_left/turn_right are "burst" commands
    that already stop themselves after `duration` seconds (default 1.0s),
    so explicit stop() is mainly for interrupting a burst early.
  - get_frame(source="local") reads directly from the USB camera via
    OpenCV on the Pi — independent of the cloud WebRTC streaming service,
    useful if that service isn't set up yet.
"""
from __future__ import annotations

from cyberwave import Cyberwave

from kdroid.config import config


class BeastController:
    def __init__(self, simulate: bool = False):
        self._cw = Cyberwave()
        self._twin = self._cw.twin(
            config.cyberwave_asset_id,
            twin_id=config.cyberwave_twin_id,
            environment_id=config.cyberwave_environment_id,
        )
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
        """Interrupts an in-progress movement burst early."""
        self._twin.locomotion.stop()

    # -- camera ---------------------------------------------------------
    def get_frame_path(self, source: str = "local") -> str:
        """
        Captures one frame and returns a filesystem path to the saved JPEG.

        source options:
          - "local"       — direct USB camera read via OpenCV on the Pi.
                             Independent of any cloud streaming service.
          - "cloud"        — platform's stored latest-frame (only option
                             available in simulation runtime mode).
          - "remote_edge"  — MQTT take_photo round-trip via the edge driver.
          - "zenoh"        — subscribe-based, for high-frequency local pipes.

        Default is "local" since that's the one proven to work without
        depending on the (currently blocked) cyberwave-camera WebRTC setup.
        """
        return self._twin.camera.get_frame(format="path", source=source)

    # -- human handoff ----------------------------------------------------
    def hand_to_human(self) -> None:
        """Useful for demos/testing: let a human drive from the dashboard."""
        self._twin.use_controller("keyboard")

    def hand_to_code(self) -> None:
        self._twin.use_controller("code")


if __name__ == "__main__":
    # Quick manual smoke test: python -m kdroid.robot_control
    beast = BeastController(simulate=True)
    beast.move_forward(0.3)
    beast.turn_left(0.5)
    beast.stop()
    print("Smoke test complete (simulation).")
