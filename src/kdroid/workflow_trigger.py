"""
Runs GPT-5.4 (via Cyberwave's ML model catalog) directly against a captured
camera frame for VLM plant-health assessment.

Originally built around triggering a Cyberwave *workflow* via a generic
HTTP /trigger endpoint — that approach was abandoned after inspecting the
workflow's generated edge-worker code (Studio > workflow > "Python worker"
tab), which showed the actual mechanism is a synchronous SDK call:
    client.mlmodels.run(model_uuid, prompt=..., image=..., image_url=...)
This bypasses the workflow/trigger/execution-target system entirely and
calls the model directly, mirroring exactly what the generated worker does
for its Call-Model node. See docs/ROADMAP.md Phase 1 notes for the full
debugging trail that led here (Manual trigger has no image payload path,
Camera Frame trigger requires edge deployment we didn't get working today).
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from cyberwave import Cyberwave

from kdroid.config import config

# GPT-5.4's model UUID in Cyberwave's catalog, confirmed from the
# generated worker code for the image-classification workflow.
GPT_5_4_MODEL_UUID = "b46f01c6-be38-4936-806b-cf398329e96c"


@dataclass
class WorkflowResult:
    run_uuid: str
    prompt: str
    triggered_at: float
    raw_response: str  # the model's raw text output


class WorkflowTrigger:
    def __init__(self):
        self._cw = Cyberwave()

    def trigger(self, frame_bytes: bytes, prompt: str | None = None) -> WorkflowResult:
        prompt = prompt or config.default_prompt

        result = self._cw.mlmodels.run(
            GPT_5_4_MODEL_UUID,
            prompt=prompt,
            image=frame_bytes,
            image_url=None,
        )

        return WorkflowResult(
            run_uuid=getattr(result, "workload_uuid", ""),
            prompt=prompt,
            triggered_at=time.time(),
            raw_response=result.output,
        )


if __name__ == "__main__":
    # Manual smoke test: python -m kdroid.workflow_trigger <path_to_test_image.jpg>
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m kdroid.workflow_trigger <path_to_test_image.jpg>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        image_bytes = f.read()

    trigger = WorkflowTrigger()
    result = trigger.trigger(image_bytes)
    print(f"Model call complete (workload_uuid={result.run_uuid})")
    print(f"Raw response:\n{result.raw_response}")