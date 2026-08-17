from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = PROJECT_ROOT / "outputs" / "research_results.json"
VERIFICATION_FILE = PROJECT_ROOT / "outputs" / "verification_sample.json"


# These are the fields the human reviewer must explicitly verify.
FIELDS_TO_VERIFY = [
    "auth_methods",
    "credential_path",
    "api_type",
    "api_breadth",
    "mcp_available",
    "buildability",
    "main_blocker",
]


def build_verification_sample(
    sample_size: int = 2,
) -> list[dict]:
    """
    Select a small sample of successful research results for manual review.

    Priority:
    1. Results already flagged for human verification.
    2. Results with lower confidence.
    3. Remaining successful results.
    """

    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        results = json.load(f)

    successful = [
        result
        for result in results
        if result.get("status") == "success"
    ]

    flagged = [
        result
        for result in successful
        if result.get("needs_human_verification") is True
    ]

    low_confidence = [
        result
        for result in successful
        if result.get("confidence") in {"low", "medium"}
        and result not in flagged
    ]

    remaining = [
        result
        for result in successful
        if result not in flagged and result not in low_confidence
    ]

    ordered = flagged + low_confidence + remaining

    sample = ordered[:sample_size]

    verification_records = []

    for result in sample:
        verification_records.append(
            {
                "id": result.get("id"),
                "app": result.get("app"),
                "category": result.get("category"),
                "source_urls": result.get(
                    "source_urls_used",
                    result.get("evidence_urls", []),
                ),
                "agent_result": {
                    field: result.get(field)
                    for field in FIELDS_TO_VERIFY
                },
                "agent_confidence": result.get("confidence"),
                "agent_needs_human_verification": result.get(
                    "needs_human_verification"
                ),
                "human_verified": False,
                "human_corrections": {},
                "human_notes": "",
            }
        )

    return verification_records


def save_sample(records: list[dict]) -> None:
    VERIFICATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with VERIFICATION_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    sample = build_verification_sample(sample_size=2)

    save_sample(sample)

    print(f"Created verification sample with {len(sample)} app(s).")
    print(f"Saved to: {VERIFICATION_FILE}")

    print("\nApps selected for manual verification:")

    for record in sample:
        print(
            f"- {record['app']} "
            f"(confidence={record['agent_confidence']})"
        )


if __name__ == "__main__":
    main()