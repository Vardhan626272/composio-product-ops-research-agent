from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = PROJECT_ROOT / "outputs" / "research_results.json"


def evaluate_quality(result: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []

    status = result.get("status")
    confidence = result.get("confidence")
    pages_found = result.get("pages_found", 0)
    evidence_urls = result.get("evidence_urls", [])
    auth_methods = result.get("auth_methods", [])
    api_type = result.get("api_type")
    credential_path = result.get("credential_path")
    mcp_available = result.get("mcp_available")
    buildability = result.get("buildability")

    if status != "success":
        issues.append("Research pipeline did not complete successfully.")

    if pages_found == 0:
        issues.append("No usable source pages were retrieved.")
    elif pages_found == 1:
        issues.append(
            "Only one source page was retrieved; cross-check recommended."
        )

    if not evidence_urls:
        issues.append("No evidence URLs were recorded.")

    if not auth_methods:
        issues.append(
            "Authentication methods were not established from the evidence."
        )

    if credential_path == "unknown":
        issues.append("Credential acquisition path is unknown.")

    if mcp_available is False:
        issues.append(
            "MCP availability was not established as true; manual verification may be required."
        )

    if api_type in {None, "Unknown"}:
        issues.append("Public API type is unknown.")

    if buildability == "uncertain":
        issues.append("Buildability could not be determined confidently.")

    if confidence == "high":
        if pages_found < 2:
            issues.append(
                "Confidence is high despite having fewer than two evidence pages."
            )

        if not auth_methods:
            issues.append(
                "Confidence is high despite missing authentication evidence."
            )

        if credential_path == "unknown":
            issues.append(
                "Confidence is high despite an unknown credential path."
            )

    needs_human_verification = bool(
        result.get("needs_human_verification", False)
    )

    if issues:
        needs_human_verification = True

    if status != "success":
        quality_status = "failed"
    elif confidence == "high" and not issues:
        quality_status = "pass"
    else:
        quality_status = "review"

    return {
        "quality_status": quality_status,
        "quality_issues": issues,
        "needs_human_verification": needs_human_verification,
        "quality_score": max(0, 100 - (len(issues) * 10)),
    }


def main() -> None:
    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"Loaded {len(results)} research results.\n")

    for result in results:
        quality = evaluate_quality(result)

        print("=" * 70)
        print(f"App: {result.get('app')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Pages found: {result.get('pages_found')}")
        print(f"Quality status: {quality['quality_status']}")
        print(f"Quality score: {quality['quality_score']}")
        print(
            f"Human verification needed: "
            f"{quality['needs_human_verification']}"
        )

        if quality["quality_issues"]:
            print("Issues:")
            for issue in quality["quality_issues"]:
                print(f"  - {issue}")

    print("\n" + "=" * 70)
    print("Quality-gate evaluation complete.")


if __name__ == "__main__":
    main()