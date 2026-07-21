"""
Local-first storage for scouting results.

Every capture gets written here FIRST, before any attempt to sync to
Cyberwave or the farmer dashboard — so a dropped connection in the field
never loses a reading. This is plain files on the Pi's SD card:
  ~/kdroid_data/
    images/<capture_id>.jpg
    results/<capture_id>.json

Deliberately not a database for v1 — flat files are trivial to inspect by
hand over SSH, trivial to rsync/copy off the SD card, and there's no
schema migration to worry about while the format is still changing.
Revisit as SQLite (see config.local_db_path) once the record shape is
stable and you actually need to query across many captures.
"""
from __future__ import annotations

import json
import shutil
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from kdroid.config import config


@dataclass
class ScoutRecord:
    capture_id: str
    timestamp: float
    row: Optional[int]
    plant_index: Optional[int]
    crop: str
    status: str                    # "healthy" | "diseased" | "unknown" (parse failure)
    disease_guess: Optional[str]
    ripeness: str                  # "ripe" | "unripe" | "not_applicable"
    confidence: str                # "high" | "medium" | "low"
    notes: str
    soil_moisture_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    image_path: Optional[str] = None
    synced_to_cyberwave: bool = False


class LocalStore:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or config.local_data_dir)
        self.images_dir = self.base_dir / "images"
        self.results_dir = self.base_dir / "results"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def new_capture_id(self) -> str:
        return f"{int(time.time())}-{uuid.uuid4().hex[:8]}"

    def save_image(self, capture_id: str, source_frame_path: str) -> str:
        """Copies a captured frame (from BeastController.get_frame_path)
        into permanent local storage. Returns the new path."""
        dest = self.images_dir / f"{capture_id}.jpg"
        shutil.copy(source_frame_path, dest)
        return str(dest)

    def save_result(self, record: ScoutRecord) -> str:
        dest = self.results_dir / f"{record.capture_id}.json"
        with open(dest, "w") as f:
            json.dump(asdict(record), f, indent=2)
        return str(dest)

    def list_unsynced(self) -> list[ScoutRecord]:
        """Records not yet pushed to Cyberwave/dashboard — for catch-up
        sync once connectivity is back."""
        unsynced = []
        for result_file in sorted(self.results_dir.glob("*.json")):
            with open(result_file) as f:
                data = json.load(f)
            if not data.get("synced_to_cyberwave", False):
                unsynced.append(ScoutRecord(**data))
        return unsynced

    def mark_synced(self, capture_id: str) -> None:
        result_file = self.results_dir / f"{capture_id}.json"
        with open(result_file) as f:
            data = json.load(f)
        data["synced_to_cyberwave"] = True
        with open(result_file, "w") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Smoke test: python -m kdroid.local_store
    store = LocalStore()
    cid = store.new_capture_id()
    record = ScoutRecord(
        capture_id=cid,
        timestamp=time.time(),
        row=1,
        plant_index=1,
        crop=config.crop_name,
        status="healthy",
        disease_guess=None,
        ripeness="ripe",
        confidence="high",
        notes="Test record, no real image attached.",
    )
    print("Saved result to:", store.save_result(record))
    print("Unsynced records:", store.list_unsynced())
