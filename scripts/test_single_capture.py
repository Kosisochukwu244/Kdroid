"""
Manual, one-shot test of the full capture -> classify -> save loop, with
NO automation (no waypoints, no route). Point the camera at a real pepper
plant/fruit yourself and run this.

This is deliberately the very first thing to get working end-to-end,
before wiring up AprilTags or a route — validates every other piece of
the pipeline first.

Usage:
    python scripts/test_single_capture.py
"""
from __future__ import annotations

import json
import time

from kdroid.robot_control import BeastController
from kdroid.workflow_trigger import WorkflowTrigger
from kdroid.local_store import LocalStore, ScoutRecord
from kdroid.config import config


def parse_vlm_response(raw_text: str) -> dict:
    """
    VLMs don't always return perfectly clean JSON even when asked to.
    Strip to the outermost {...} before parsing, and fail soft rather
    than crashing the whole loop on a bad response.
    """
    try:
        start = raw_text.index("{")
        end = raw_text.rindex("}") + 1
        return json.loads(raw_text[start:end])
    except (ValueError, json.JSONDecodeError):
        return {
            "status": "unknown",
            "disease_guess": None,
            "ripeness": "not_applicable",
            "confidence": "low",
            "notes": f"Could not parse model response: {raw_text[:200]}",
        }


def main():
    print(f"Connecting to Beast (live mode), crop target: {config.crop_name}...")
    beast = BeastController(simulate=False)
    store = LocalStore()

    input("Point the camera at a pepper plant/fruit, then press Enter to capture...")

    frame_path = beast.get_frame_path(source="local")
    print(f"Captured frame: {frame_path}")

    print("Triggering Cyberwave workflow for VLM assessment...")
    trigger = WorkflowTrigger()
    with open(frame_path, "rb") as f:
        frame_bytes = f.read()
    result = trigger.trigger(frame_bytes)
    print(f"Workflow run: {result.run_uuid}")

    # TODO: once workflow_trigger.py can retrieve the actual model output
    # (currently it only returns a run_uuid — see the TODO there about
    # polling the run status), replace this placeholder with the real
    # response text before parsing.
    raw_response = input(
        "Paste the model's raw text response here (temporary manual step "
        "until run-status polling is wired up): "
    )
    parsed = parse_vlm_response(raw_response)

    capture_id = store.new_capture_id()
    saved_image_path = store.save_image(capture_id, frame_path)

    record = ScoutRecord(
        capture_id=capture_id,
        timestamp=time.time(),
        row=None,
        plant_index=None,
        crop=config.crop_name,
        status=parsed.get("status", "unknown"),
        disease_guess=parsed.get("disease_guess"),
        ripeness=parsed.get("ripeness", "not_applicable"),
        confidence=parsed.get("confidence", "low"),
        notes=parsed.get("notes", ""),
        image_path=saved_image_path,
    )
    result_path = store.save_result(record)

    print("\n--- Result ---")
    print(f"Status:     {record.status}")
    print(f"Disease:    {record.disease_guess}")
    print(f"Ripeness:   {record.ripeness}")
    print(f"Confidence: {record.confidence}")
    print(f"Notes:      {record.notes}")
    print(f"\nSaved image:  {saved_image_path}")
    print(f"Saved record: {result_path}")


if __name__ == "__main__":
    main()
