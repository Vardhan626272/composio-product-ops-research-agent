from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VERIFICATION_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "verification_sample.json"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "verification_report.json"
)


def load_verification_sample() -> list[dict[str, Any]]:
    with VERIFICATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "verification_sample.json must contain a JSON list."
        )

    return data


def compare_agent_and_human(
    record: dict[str, Any],
) -> dict[str, Any]:

    agent_result = record.get(
        "agent_result",
        {},
    )

    human_corrections = record.get(
        "human_corrections",
        {},
    )

    corrected_fields = []

    for field, human_value in human_corrections.items():
        agent_value = agent_result.get(field)

        if agent_value != human_value:
            corrected_fields.append(
                {
                    "field": field,
                    "agent_value": agent_value,
                    "human_value": human_value,
                }
            )

    return {
        "id": str(record.get("id", "")),
        "app": record.get("app"),
        "human_verified": (
            record.get("human_verified") is True
        ),
        "agent_confidence": record.get(
            "agent_confidence"
        ),
        "corrected_field_count": len(
            corrected_fields
        ),
        "corrected_fields": corrected_fields,
        "human_notes": record.get(
            "human_notes",
            "",
        ),
    }


def build_report(
    records: list[dict[str, Any]],
) -> dict[str, Any]:

    verification_results = [
        compare_agent_and_human(record)
        for record in records
    ]

    verified_results = [
        result
        for result in verification_results
        if result["human_verified"] is True
    ]

    apps_with_corrections = [
        result
        for result in verified_results
        if result["corrected_field_count"] > 0
    ]

    total_recorded_field_corrections = sum(
        result["corrected_field_count"]
        for result in verified_results
    )

    return {
        "verification_method": (
            "Manual review of selected agent outputs "
            "against first-party documentation."
        ),
        "sample_size": len(records),
        "fully_human_verified_apps": len(
            verified_results
        ),
        "apps_with_recorded_corrections": len(
            apps_with_corrections
        ),
        "total_recorded_field_corrections": (
            total_recorded_field_corrections
        ),
        "accuracy_claim": (
            "No overall percentage accuracy is claimed "
            "because the current sample does not verify "
            "every field for every sampled app."
        ),
        "verification_results": verification_results,
    }


def save_report(
    report: dict[str, Any],
) -> None:

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:

    records = load_verification_sample()

    report = build_report(records)

    save_report(report)

    print("Verification report generated.")
    print(f"Sample size: {report['sample_size']}")
    print(
        "Fully human-verified apps: "
        f"{report['fully_human_verified_apps']}"
    )
    print(
        "Apps with recorded corrections: "
        f"{report['apps_with_recorded_corrections']}"
    )
    print(
        "Total recorded field corrections: "
        f"{report['total_recorded_field_corrections']}"
    )
    print(f"Saved to: {REPORT_FILE}")

    print("\nVerified apps:")

    for result in report["verification_results"]:
        if result["human_verified"]:
            print(
                f"  - {result['app']}: "
                f"{result['corrected_field_count']} correction(s)"
            )


if __name__ == "__main__":
    main()