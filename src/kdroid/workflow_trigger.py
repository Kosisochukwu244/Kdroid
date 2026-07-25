"""
Fires a Cyberwave workflow (VLM plant-health assessment) with the current
camera frame and a prompt.

The trigger-with-inputs + poll-for-result pattern below is modeled on the
Roamie reference project (see docs/reference-projects.md), NOT copied from
official Cyberwave API docs that we've directly confirmed. Treat the
request/response shapes here as a starting point: validate them against
docs.cyberwave.com/technology/components/apis before relying on this for
the automated loop in Phase 2.
"""
from __future__ import annotations

import base64
import time
from dataclasses import dataclass

import requests

from kdroid.config import config

CYBERWAVE_API_BASE = "https://api.cyberwave.com/api/v1"  # TODO: confirm base URL

# TODO: confirm actual terminal/failure state strings from a real response —
# these are guesses based on common workflow-engine conventions.
TERMINAL_SUCCESS_STATES = {"completed", "succeeded"}
TERMINAL_FAILURE_STATES = {"failed", "error"}


@dataclass
class WorkflowResult:
    run_uuid: str
    prompt: str
    triggered_at: float
    raw_response: str  # the Call-Model node's actual text output


class WorkflowTrigger:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {"Authorization": f"Bearer {config.cyberwave_api_key}"}
        )

    def _trigger_run(self, frame_bytes: bytes, prompt: str) -> str:
        """
        Fires the workflow with the frame + prompt passed directly as node
        inputs — no upload step needed now that Call-Model accepts
        image_bytes inline.
        TODO: confirm the trigger endpoint's expected input-mapping shape;
        this assumes an `inputs` dict keyed by the node's input names.
        """
        encoded_image = base64.b64encode(frame_bytes).decode("ascii")
        resp = self._session.post(
            f"{CYBERWAVE_API_BASE}/workflows/{config.cyberwave_workflow_id}/trigger",
            json={
                "inputs": {
                    "image_bytes": encoded_image,
                    "prompt": prompt,
                }
            },
        )
        resp.raise_for_status()
        return resp.json()["run_uuid"]

    def _poll_for_result(
        self, run_uuid: str, timeout_s: float = 30.0, poll_interval_s: float = 2.0
    ) -> str:
        """
        Polls the workflow run status until it completes, then returns the
        Call-Model node's raw text output.
        TODO: confirm the run-status endpoint path and response shape
        (state field name, output field name/location) against real API
        responses — this is a best-guess structure.
        """
        elapsed = 0.0
        while elapsed < timeout_s:
            resp = self._session.get(
                f"{CYBERWAVE_API_BASE}/workflows/runs/{run_uuid}"
            )
            resp.raise_for_status()
            status = resp.json()

            state = status.get("state")
            if state in TERMINAL_SUCCESS_STATES:
                # TODO: confirm where the Call-Model output actually lands
                # in this payload — top-level "output", or nested under
                # a node-keyed results dict.
                return status["output"]
            if state in TERMINAL_FAILURE_STATES:
                raise RuntimeError(f"Workflow run {run_uuid} failed: {status.get('error')}")

            time.sleep(poll_interval_s)
            elapsed += poll_interval_s

        raise TimeoutError(f"Workflow run {run_uuid} did not complete in {timeout_s}s")

    def trigger(self, frame_bytes: bytes, prompt: str | None = None) -> WorkflowResult:
        prompt = prompt or config.default_prompt

        run_uuid = self._trigger_run(frame_bytes, prompt)
        raw_response = self._poll_for_result(run_uuid)

        return WorkflowResult(
            run_uuid=run_uuid,
            prompt=prompt,
            triggered_at=time.time(),
            raw_response=raw_response,
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m kdroid.workflow_trigger <path_to_test_image.jpg>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        image_bytes = f.read()

    trigger = WorkflowTrigger()
    result = trigger.trigger(image_bytes)
    print(f"Workflow run {result.run_uuid} completed.")
    print(f"Raw response:\n{result.raw_response}")