from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESEARCH_FILE = PROJECT_ROOT / "outputs" / "research_results.json"
VERIFICATION_FILE = PROJECT_ROOT / "outputs" / "verification_sample.json"
FINAL_FILE = PROJECT_ROOT / "outputs" / "final_results.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    research_results = load_json(RESEARCH_FILE)
    verification_records = load_json(VERIFICATION_FILE)

    verification_by_id = {
        str(record["id"]): record
        for record in verification_records
        if record.get("human_verified") is True
    }

    final_results = []

    for result in research_results:
        result_id = str(result.get("id"))

        verified = verification_by_id.get(result_id)

        if verified:
            corrections = verified.get(
                "human_corrections",
                {},
            )

            for field, corrected_value in corrections.items():
                result[field] = corrected_value

            result["human_verified"] = True
            result["human_corrections"] = corrections
            result["human_notes"] = verified.get(
                "human_notes",
                "",
            )

            result["verification_status"] = "human-verified"

        else:
            result["human_verified"] = False
            result["human_corrections"] = {}
            result["human_notes"] = ""
            result["verification_status"] = "agent-only"

        final_results.append(result)

    save_json(FINAL_FILE, final_results)

    verified_count = sum(
        1
        for result in final_results
        if result.get("human_verified") is True
    )

    print("Verification corrections applied.")
    print(f"Total results: {len(final_results)}")
    print(f"Human-verified results: {verified_count}")
    print(f"Saved to: {FINAL_FILE}")


if __name__ == "__main__":
    main()