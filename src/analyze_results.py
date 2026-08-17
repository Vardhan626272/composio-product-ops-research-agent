from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FINAL_FILE = PROJECT_ROOT / "outputs" / "final_results.json"
REPORT_FILE = PROJECT_ROOT / "outputs" / "patterns_report.json"


def load_results() -> list[dict]:
    with FINAL_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def count_list_values(results, field):
    counter = Counter()

    for result in results:
        for value in result.get(field, []) or []:
            counter[value] += 1

    return counter


def main():
    results = load_results()

    total = len(results)

    categories = Counter(
        r.get("category", "Unknown")
        for r in results
    )

    auth_methods = count_list_values(
        results,
        "auth_methods",
    )

    credential_paths = Counter(
        r.get("credential_path", "unknown")
        for r in results
    )

    api_types = Counter(
        r.get("api_type", "Unknown")
        for r in results
    )

    api_breadth = Counter(
        r.get("api_breadth", "unknown")
        for r in results
    )

    buildability = Counter(
        r.get("buildability", "uncertain")
        for r in results
    )

    quality_status = Counter(
        r.get("quality_status", "unknown")
        for r in results
    )

    confidence = Counter(
        r.get("confidence", "unknown")
        for r in results
    )

    mcp_count = sum(
        1
        for r in results
        if r.get("mcp_available") is True
    )

    human_verification_count = sum(
        1
        for r in results
        if r.get("needs_human_verification") is True
    )

    pages_distribution = Counter(
        r.get("pages_found", 0)
        for r in results
    )

    blockers = Counter(
        r.get("main_blocker")
        for r in results
        if r.get("main_blocker")
    )

    category_summary = defaultdict(
        lambda: {
            "apps": 0,
            "agent_ready": 0,
            "buildable_with_setup": 0,
            "blocked": 0,
            "uncertain": 0,
            "mcp": 0,
        }
    )

    for result in results:
        category = result.get(
            "category",
            "Unknown",
        )

        summary = category_summary[category]

        summary["apps"] += 1

        build = result.get(
            "buildability"
        )

        if build == "agent-ready":
            summary["agent_ready"] += 1
        elif build == "buildable-with-setup":
            summary["buildable_with_setup"] += 1
        elif build == "blocked":
            summary["blocked"] += 1
        else:
            summary["uncertain"] += 1

        if result.get("mcp_available") is True:
            summary["mcp"] += 1

    report = {
        "total_apps": total,

        "headline_metrics": {
            "mcp_available": mcp_count,
            "mcp_percentage": round(
                100 * mcp_count / total,
                1,
            ) if total else 0,

            "human_verification_flagged": human_verification_count,
            "human_verification_percentage": round(
                100 * human_verification_count / total,
                1,
            ) if total else 0,
        },

        "authentication": dict(auth_methods),

        "credential_path": dict(credential_paths),

        "api_type": dict(api_types),

        "api_breadth": dict(api_breadth),

        "buildability": dict(buildability),

        "quality_status": dict(quality_status),

        "confidence": dict(confidence),

        "pages_found": dict(pages_distribution),

        "blockers": dict(blockers),

        "categories": dict(categories),

        "category_summary": dict(category_summary),
    }

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

    print("=" * 70)
    print("100-APP PATTERN ANALYSIS")
    print("=" * 70)

    print(f"\nTotal apps: {total}")

    print("\nAuthentication:")
    for key, value in auth_methods.most_common():
        print(f"  {key}: {value}")

    print("\nCredential path:")
    for key, value in credential_paths.most_common():
        print(f"  {key}: {value}")

    print("\nAPI type:")
    for key, value in api_types.most_common():
        print(f"  {key}: {value}")

    print("\nAPI breadth:")
    for key, value in api_breadth.most_common():
        print(f"  {key}: {value}")

    print("\nBuildability:")
    for key, value in buildability.most_common():
        print(f"  {key}: {value}")

    print("\nMCP:")
    print(f"  Available: {mcp_count}/{total}")

    print("\nQuality:")
    for key, value in quality_status.most_common():
        print(f"  {key}: {value}")

    print("\nHuman verification flags:")
    print(f"  {human_verification_count}/{total}")

    print("\nTop blockers:")
    for key, value in blockers.most_common(10):
        print(f"  {key}: {value}")

    print("\nCategory summary:")
    for category, summary in category_summary.items():
        print(
            f"  {category}: "
            f"{summary['apps']} apps, "
            f"{summary['agent_ready']} agent-ready, "
            f"{summary['buildable_with_setup']} setup, "
            f"{summary['blocked']} blocked, "
            f"{summary['uncertain']} uncertain, "
            f"{summary['mcp']} MCP"
        )

    print(
        f"\nSaved report to:\n{REPORT_FILE}"
    )


if __name__ == "__main__":
    main()