# Cyberwave workflow: plant health assessment

This workflow is built in **Cyberwave Studio**, not as a code file — Studio
workflows are visual/low-code. This doc specs out what to build so it's
reproducible and reviewable, and records the workflow ID once created.

## Nodes

1. **Trigger** — HTTP/API trigger, fired by `workflow_trigger.py`
2. **Call-Model** — VLM node
   - Model: pick a vision-capable model from the Cyberwave catalog (start
     with whatever general-purpose VLM is available; revisit once you can
     compare outputs against a plant-specific model if one exists in the
     catalog)
   - Input: `image_url` (patched per-run by `workflow_trigger.py`),
     `prompt` (patched per-run — see `config.default_prompt` for the
     default, or a per-waypoint override)
   - Output: structured or free-text health assessment
3. **Output/Delivery** — where the result goes. For Phase 1, use
   Cyberwave's built-in dashboard/email delivery to validate the pipeline
   fast. For Phase 4, replace/add a webhook to Kdroid's own dashboard
   backend so results land in the farmer-facing view instead of (or in
   addition to) Cyberwave's default delivery.

## Prompt — pepper, structured JSON (v1 target crop)

Ask for structured JSON, not free text — makes downstream parsing (local
storage, dashboard, fusion with sensor data) trivial instead of needing to
regex a paragraph.

> You are inspecting a pepper plant/fruit for a farmer. Respond with ONLY
> a JSON object, no other text, matching this schema:
> `{"status": "healthy" | "diseased", "disease_guess": string or null (name
> the most likely disease/pest if status is diseased, else null),
> "ripeness": "ripe" | "unripe" | "not_applicable" (use not_applicable if
> no fruit is visible, only leaves/stem), "confidence": "high" | "medium" |
> "low", "notes": short plain-language explanation, 1 sentence max}`

This matches `config.default_prompt` in `src/kdroid/config.py` — keep them
in sync if you tune the wording.

**Validate against real pepper disease signs once the basic pipeline
works** — common ones worth mentioning explicitly in a v2 prompt if the
generic version isn't specific enough: bacterial spot, anthracnose,
Cercospora leaf spot, blossom end rot, pepper mosaic virus. Adding named
diseases to the prompt tends to improve VLM accuracy over a fully generic
"any disease" ask.

**Parsing note:** VLMs don't always perfectly honor "JSON only" — build in
a fallback for when the response has extra text wrapped around the JSON
(strip to the outermost `{...}` before parsing) or fails to parse at all
(store status as `"unknown"` rather than crashing the scouting loop).

## Once built

- [ ] Record the workflow UUID here: `CYBERWAVE_WORKFLOW_ID = <fill in>`
- [ ] Confirm it also matches `.env` / `CYBERWAVE_WORKFLOW_ID`
- [ ] Run one manual trigger via `python -m kdroid.workflow_trigger
      <test_image.jpg>` and sanity-check the output before wiring it into
      the automated loop
