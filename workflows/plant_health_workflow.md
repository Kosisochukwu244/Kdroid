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

## Suggested prompt (starting point, iterate on real leaves)

> Assess this plant's health. Note any visible signs of disease, pest
> damage, wilting, discoloration, or nutrient deficiency. If the plant
> looks healthy, say so plainly. Keep the assessment to 2–3 sentences.

Tune this against your actual target crop (cassava/maize per your local
context) — a generic prompt will be less accurate than one that mentions
the crop and common local disease signs (e.g. cassava mosaic, cassava
bacterial blight) once you've validated the general pipeline works.

## Once built

- [ ] Record the workflow UUID here: `CYBERWAVE_WORKFLOW_ID = <fill in>`
- [ ] Confirm it also matches `.env` / `CYBERWAVE_WORKFLOW_ID`
- [ ] Run one manual trigger via `python -m kdroid.workflow_trigger
      <test_image.jpg>` and sanity-check the output before wiring it into
      the automated loop
