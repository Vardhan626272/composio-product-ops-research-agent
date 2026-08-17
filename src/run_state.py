from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "outputs" / "run_state.json"


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {
            "completed_ids": [],
            "failed_ids": [],
        }

    with STATE_FILE.open("r", encoding="utf-8") as f:
        state = json.load(f)

    state.setdefault("completed_ids", [])
    state.setdefault("failed_ids", [])

    return state


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            state,
            f,
            indent=2,
        )


def mark_completed(state: dict[str, Any], app_id: str) -> None:
    if app_id not in state["completed_ids"]:
        state["completed_ids"].append(app_id)

    if app_id in state["failed_ids"]:
        state["failed_ids"].remove(app_id)


def mark_failed(state: dict[str, Any], app_id: str) -> None:
    if app_id not in state["failed_ids"]:
        state["failed_ids"].append(app_id)

    save_state(state)