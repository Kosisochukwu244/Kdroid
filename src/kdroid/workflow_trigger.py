"""
Fires a Cyberwave workflow (VLM plant-health assessment) with the current
camera frame and a prompt.

The upload -> patch Call-Model node -> trigger sequence below is modeled on
the pattern documented in the Roamie reference project (see
docs/reference-projects.md), NOT copied from official Cyberwave API docs
that we've directly confirmed. Treat the request shapes here as a starting
point: validate them against your own API key and
docs.cyberwave.com/technology/components/apis in Phase 1, before relying on
this for the automated loop in Phase 2.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from kdroid.config import config

CYBERWAVE_API_BASE = "https://api.cyberwave.com/api/v1"  # TODO: confirm base URL


@dataclass
class WorkflowResult:
    run_uuid: str
    prompt: str
    triggered_at: float


class WorkflowTrigger:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {"Authorization": f"Bearer {config.cyberwave_api_key}"}
        )

    def _upload_frame(self, frame_bytes: bytes) -> str:
        """
        Uploads a JPEG frame to Cyberwave storage, returns an image URL.
        TODO: confirm the actual upload endpoint/response shape.
        """
        resp = self._session.post(
            f"{CYBERWAVE_API_BASE}/storage/upload",
            files={"file": ("frame.jpg", frame_bytes, "image/jpeg")},
        )
        resp.raise_for_status()
        return resp.json()["url"]

    def _patch_call_model_node(self, image_url: str, prompt: str) -> None:
        """
        Points the workflow's Call-Model node at this image + prompt before
        triggering. TODO: confirm node-patch endpoint/payload shape.
        """
        resp = self._session.patch(
            f"{CYBERWAVE_API_BASE}/workflows/{config.cyberwave_workflow_id}/nodes/call-model",
            json={"image_url": image_url, "prompt": prompt},
        )
        resp.raise_for_status()

    def trigger(self, frame_bytes: bytes, prompt: str | None = None) -> WorkflowResult:
        prompt = prompt or config.default_prompt

        image_url = self._upload_frame(frame_bytes)
        self._patch_call_model_node(image_url, prompt)

        resp = self._session.post(
            f"{CYBERWAVE_API_BASE}/workflows/{config.cyberwave_workflow_id}/trigger"
        )
        resp.raise_for_status()
        run_uuid = resp.json()["run_uuid"]

        return WorkflowResult(run_uuid=run_uuid, prompt=prompt, triggered_at=time.time())


if __name__ == "__main__":
    # Manual smoke test: trigger the workflow once against a saved test
    # image, to validate the API shape before wiring it into the full loop.
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m kdroid.workflow_trigger <path_to_test_image.jpg>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        image_bytes = f.read()

    trigger = WorkflowTrigger()
    result = trigger.trigger(image_bytes)
    print(f"Triggered workflow run {result.run_uuid}")
