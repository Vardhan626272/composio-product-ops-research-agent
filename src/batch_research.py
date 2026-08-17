from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from analyzer import analyze_app
from quality_gate import evaluate_quality
from run_state import load_state, mark_completed, mark_failed, save_state
from url_candidates import URL_CANDIDATES
from web_research import research_candidates


PROJECT_ROOT = Path(__file__).resolve().parent.parent

APPS_FILE = PROJECT_ROOT / "data" / "apps.csv"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "research_results.json"

# Retry only the three apps that previously failed.
RETRY_IDS = {"44", "84", "85"}


def load_apps() -> list[dict]:
    with APPS_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def load_existing_results() -> list[dict]:
    if not OUTPUT_FILE.exists():
        return []

    with OUTPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_results(results: list[dict]) -> None:
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )


def build_evidence(pages) -> str:
    sections = []

    for index, page in enumerate(
        pages,
        start=1,
    ):
        sections.append(
            f"""
--- SOURCE {index} ---
URL: {page.url}
Retrieval method: {page.method}

CONTENT:
{page.text[:12000]}
"""
        )

    return "\n".join(sections)


def research_one_app(app_row: dict) -> dict:
    app = app_row["app"]
    category = app_row["category"]
    app_id = str(app_row["id"])

    candidates = URL_CANDIDATES.get(
        app,
        [],
    )

    print("\n" + "=" * 70)
    print(f"Researching: {app}")
    print(f"ID: {app_id}")
    print(f"Category: {category}")
    print(f"Candidate URLs: {len(candidates)}")

    pages = research_candidates(candidates)

    if not pages:
        print("No usable documentation pages found.")

        return {
            **app_row,
            "status": "fetch_failed",
            "error": "No candidate URL returned usable content.",
            "pages_found": 0,
            "quality_status": "failed",
            "quality_score": 0,
            "quality_issues": [
                "No usable documentation pages were retrieved."
            ],
            "needs_human_verification": True,
        }

    print(
        f"Usable documentation pages: "
        f"{len(pages)}"
    )

    source_urls = [
        page.url
        for page in pages
    ]

    retrieval_methods = [
        page.method
        for page in pages
    ]

    combined_evidence = build_evidence(
        pages
    )

    print(
        f"Total evidence characters: "
        f"{len(combined_evidence)}"
    )

    print(
        "Analyzing combined evidence with Gemini..."
    )

    try:
        result = analyze_app(
            app=app,
            category=category,
            source_urls=source_urls,
            source_text=combined_evidence,
        )

        output = result.model_dump()

        output["id"] = app_id
        output["status"] = "success"
        output["source_urls_used"] = source_urls
        output["retrieval_methods"] = retrieval_methods
        output["pages_found"] = len(pages)

        quality = evaluate_quality(
            output
        )

        output.update(
            quality
        )

        print("Analysis successful.")
        print(
            f"Quality: "
            f"{quality['quality_status']} "
            f"({quality['quality_score']}/100)"
        )

        if quality["quality_issues"]:
            print("Quality issues:")

            for issue in quality[
                "quality_issues"
            ]:
                print(
                    f"  - {issue}"
                )

        return output

    except Exception as exc:
        print(
            f"Analysis failed: {exc}"
        )

        return {
            **app_row,
            "status": "analysis_failed",
            "source_urls_used": source_urls,
            "retrieval_methods": retrieval_methods,
            "pages_found": len(pages),
            "error": str(exc),
            "quality_status": "failed",
            "quality_score": 0,
            "quality_issues": [
                f"Analysis failed: {exc}"
            ],
            "needs_human_verification": True,
        }


def main() -> None:
    apps = load_apps()
    existing_results = load_existing_results()
    state = load_state()

    results_by_id = {
        str(result.get("id")): result
        for result in existing_results
        if result.get("id") is not None
    }

    retry_apps = [
        app
        for app in apps
        if str(app["id"]) in RETRY_IDS
    ]

    print(
        f"Retrying {len(retry_apps)} previously failed app(s)."
    )

    for index, app_row in enumerate(
        retry_apps,
        start=1,
    ):
        app_id = str(
            app_row["id"]
        )

        print(
            f"\nProgress: "
            f"{index}/{len(retry_apps)}"
        )

        result = research_one_app(
            app_row
        )

        results_by_id[app_id] = result

        results = sorted(
            results_by_id.values(),
            key=lambda item: int(
                item.get("id", 0)
            ),
        )

        save_results(
            results
        )

        if result.get("status") == "success":
            mark_completed(
                state,
                app_id
            )
        else:
            mark_failed(
                state,
                app_id
            )

        save_state(
            state
        )

        if index < len(retry_apps):
            time.sleep(3)

    print("\n" + "=" * 70)
    print("FAILED-APP RETRY COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()