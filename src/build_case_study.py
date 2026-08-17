from __future__ import annotations

import json
from collections import Counter
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

FINAL_RESULTS = ROOT / "outputs" / "final_results.json"
PATTERNS = ROOT / "outputs" / "patterns_report.json"
VERIFICATION = ROOT / "outputs" / "verification_report.json"
VERIFICATION_SAMPLE = ROOT / "outputs" / "verification_sample.json"

OUTPUT = ROOT / "outputs" / "composio_product_ops_case_study.html"

# Replace these after your GitHub repo and deployment are ready.
SOURCE_REPO_URL = "REPLACE_WITH_GITHUB_REPO_URL"
LIVE_APP_URL = "REPLACE_WITH_LIVE_CASE_STUDY_URL"


def pct(value: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{100 * value / total:.1f}%"


def bar_row(label: str, value: int, total: int) -> str:
    width = 0 if not total else 100 * value / total

    return f"""
    <div class="metric-row">
      <div class="metric-label">{escape(label)}</div>
      <div class="bar">
        <div class="bar-fill" style="width:{width:.1f}%"></div>
      </div>
      <div class="metric-value">{value}</div>
    </div>
    """


def normalize_auth_methods(methods: list[str] | None) -> str:
    if not methods:
        return "Unknown"

    normalized = set()

    for raw in methods:
        value = raw.lower().strip()

        if "oauth" in value:
            normalized.add("OAuth")

        if any(
            token in value
            for token in [
                "api key",
                "api keys",
                "api token",
                "api tokens",
                "access token",
                "personal access token",
                "bearer token",
                "private integration token",
                "private app access token",
                "developer token",
                "global api key",
                "static api token",
                "client credentials",
                "service key",
            ]
        ):
            normalized.add("API key/token")

        if "basic" in value:
            normalized.add("Basic")

        if "service account" in value:
            normalized.add("Service account")

        if "jwt" in value:
            normalized.add("JWT")

        if any(
            token in value
            for token in [
                "login",
                "browser",
                "sso",
                "google",
                "microsoft",
            ]
        ):
            normalized.add("User/SSO")

    if not normalized:
        normalized.add("Other")

    return ", ".join(sorted(normalized))


def evidence_link(url: str) -> str:
    safe_url = escape(url, quote=True)
    label = escape(url)

    return (
        f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">'
        f"{label}</a>"
    )


def main() -> None:
    with FINAL_RESULTS.open(
        "r",
        encoding="utf-8",
    ) as f:
        results = json.load(f)

    with PATTERNS.open(
        "r",
        encoding="utf-8",
    ) as f:
        patterns = json.load(f)

    with VERIFICATION.open(
        "r",
        encoding="utf-8",
    ) as f:
        verification = json.load(f)

    with VERIFICATION_SAMPLE.open(
        "r",
        encoding="utf-8",
    ) as f:
        verification_sample = json.load(f)

    total = len(results)

    buildability = patterns["buildability"]
    credential = patterns["credential_path"]
    api_type = patterns["api_type"]

    mcp_count = patterns["headline_metrics"]["mcp_available"]

    review_count = patterns["headline_metrics"][
        "human_verification_flagged"
    ]

    verified_apps = verification[
        "fully_human_verified_apps"
    ]

    recorded_corrections = verification[
        "total_recorded_field_corrections"
    ]

    pass_results = [
        r for r in results
        if r.get("quality_status") == "pass"
    ]

    review_results = [
        r for r in results
        if r.get("quality_status") != "pass"
    ]

    # ---------------------------------------------------------
    # Authentication normalization
    # ---------------------------------------------------------

    auth_counter = Counter()

    for result in results:
        normalized = normalize_auth_methods(
            result.get("auth_methods")
        )
        auth_counter[normalized] += 1

    # ---------------------------------------------------------
    # Category rows
    # ---------------------------------------------------------

    category_rows = ""

    for category, summary in patterns[
        "category_summary"
    ].items():

        category_rows += f"""
        <tr>
          <td>{escape(category)}</td>
          <td>{summary["apps"]}</td>
          <td>{summary["agent_ready"]}</td>
          <td>{summary["buildable_with_setup"]}</td>
          <td>{summary["blocked"]}</td>
          <td>{summary["uncertain"]}</td>
          <td>{summary["mcp"]}</td>
        </tr>
        """

    # ---------------------------------------------------------
    # Full 100-app table
    # ---------------------------------------------------------

    app_rows = ""

    for result in results:

        app_id = escape(
            str(result.get("id", ""))
        )

        app = escape(
            result.get("app", "")
        )

        category = escape(
            result.get("category", "")
        )

        auth = escape(
            normalize_auth_methods(
                result.get("auth_methods")
            )
        )

        credential_path = escape(
            str(
                result.get(
                    "credential_path",
                    "unknown",
                )
            )
        )

        api = escape(
            str(
                result.get(
                    "api_type",
                    "Unknown",
                )
            )
        )

        mcp = (
            '<span class="tag yes">Yes</span>'
            if result.get("mcp_available") is True
            else '<span class="tag no">No</span>'
        )

        build = escape(
            str(
                result.get(
                    "buildability",
                    "uncertain",
                )
            )
        )

        confidence = escape(
            str(
                result.get(
                    "confidence",
                    "unknown",
                )
            )
        )

        quality = escape(
            str(
                result.get(
                    "quality_status",
                    "unknown",
                )
            )
        )

        urls = result.get(
            "source_urls_used",
            result.get(
                "evidence_urls",
                [],
            ),
        )

        if urls:
            evidence = "<br>".join(
                evidence_link(url)
                for url in urls[:3]
            )
        else:
            evidence = "No usable source"

        app_rows += f"""
        <tr>
          <td>{app_id}</td>
          <td><strong>{app}</strong></td>
          <td>{category}</td>
          <td>{auth}</td>
          <td>{credential_path}</td>
          <td>{api}</td>
          <td>{mcp}</td>
          <td>{build}</td>
          <td>{confidence}</td>
          <td>{quality}</td>
          <td>{evidence}</td>
        </tr>
        """

    # ---------------------------------------------------------
    # Review sample
    # ---------------------------------------------------------

    review_rows = ""

    for result in review_results[:20]:

        issues = result.get(
            "quality_issues",
            [],
        )

        issues_html = "<br>".join(
            escape(issue)
            for issue in issues[:3]
        )

        review_rows += f"""
        <tr>
          <td>{escape(str(result.get("id", "")))}</td>
          <td>{escape(result.get("app", ""))}</td>
          <td>{escape(str(result.get("confidence", "unknown")))}</td>
          <td>{result.get("quality_score", 0)}</td>
          <td>{issues_html}</td>
        </tr>
        """

    # ---------------------------------------------------------
    # Verified examples
    # ---------------------------------------------------------

    verified_rows = ""

    for record in verification_sample:

        if record.get("human_verified") is not True:
            continue

        corrected_count = 0

        for field, human_value in record.get(
            "human_corrections",
            {},
        ).items():

            agent_value = record.get(
                "agent_result",
                {},
            ).get(field)

            if agent_value != human_value:
                corrected_count += 1

        verified_rows += f"""
        <tr>
          <td>{escape(record.get("app", ""))}</td>
          <td>{escape(str(record.get("agent_confidence", "")))}</td>
          <td>{corrected_count}</td>
          <td>{escape(record.get("human_notes", ""))}</td>
        </tr>
        """

    # ---------------------------------------------------------
    # Top blockers
    # ---------------------------------------------------------

    top_blockers = list(
        patterns["blockers"].items()
    )[:10]

    blocker_rows = ""

    for blocker, count in top_blockers:
        blocker_rows += f"""
        <tr>
          <td>{escape(str(blocker))}</td>
          <td>{count}</td>
        </tr>
        """

    # ---------------------------------------------------------
    # HTML
    # ---------------------------------------------------------

    html = f"""<!doctype html>
<html lang="en">

<head>

<meta charset="utf-8">

<meta
  name="viewport"
  content="width=device-width, initial-scale=1"
>

<title>
Composio Product Ops Intern — 100-App Research Agent
</title>

<style>

:root {{
  --bg: #0b1020;
  --panel: #121a2e;
  --panel2: #18223b;
  --text: #edf3ff;
  --muted: #aab7d0;
  --accent: #6ea8fe;
  --accent2: #7ee787;
  --warn: #ffcc66;
  --danger: #ff7b72;
  --line: #2b3959;
}}

* {{
  box-sizing: border-box;
}}

html {{
  scroll-behavior: smooth;
}}

body {{
  margin: 0;
  background:
    linear-gradient(
      180deg,
      #09101f,
      #0b1020 40%,
      #0d1326
    );
  color: var(--text);
  font-family:
    Inter,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  line-height: 1.5;
}}

a {{
  color: #a8c7ff;
}}

.container {{
  max-width: 1450px;
  margin: 0 auto;
  padding: 38px 24px 80px;
}}

.hero {{
  background:
    linear-gradient(
      135deg,
      #172544,
      #10192e
    );
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 34px;
  margin-bottom: 22px;
}}

.eyebrow {{
  color: var(--accent2);
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-size: 13px;
}}

h1 {{
  font-size: 42px;
  line-height: 1.08;
  margin: 10px 0 14px;
}}

h2 {{
  font-size: 24px;
  margin: 0 0 16px;
}}

h3 {{
  font-size: 17px;
  margin: 0 0 10px;
}}

.lead {{
  color: var(--muted);
  font-size: 17px;
  max-width: 1050px;
}}

.actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}}

.action {{
  display: inline-block;
  border: 1px solid var(--line);
  background: var(--panel);
  padding: 9px 14px;
  border-radius: 9px;
  text-decoration: none;
  color: var(--text);
  font-size: 13px;
}}

.grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 22px;
}}

.card {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 20px;
}}

.big {{
  font-size: 31px;
  font-weight: 800;
}}

.small {{
  color: var(--muted);
  font-size: 13px;
}}

section {{
  background: rgba(18, 26, 46, .92);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 26px;
  margin-top: 22px;
}}

.insight-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}}

.insight {{
  background: var(--panel2);
  border-radius: 16px;
  padding: 18px;
}}

.metric-row {{
  display: grid;
  grid-template-columns: 220px 1fr 50px;
  align-items: center;
  gap: 12px;
  margin: 10px 0;
}}

.metric-label {{
  color: var(--muted);
  font-size: 14px;
}}

.bar {{
  height: 10px;
  background: #263452;
  border-radius: 999px;
  overflow: hidden;
}}

.bar-fill {{
  height: 100%;
  background:
    linear-gradient(
      90deg,
      var(--accent),
      #9b8cff
    );
  border-radius: 999px;
}}

.metric-value {{
  text-align: right;
  font-weight: 700;
}}

.workflow {{
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}}

.step {{
  background: var(--panel2);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 15px;
  font-size: 13px;
}}

.step strong {{
  display: block;
  color: var(--accent2);
  margin-bottom: 6px;
}}

.callout {{
  border-left: 4px solid var(--warn);
  padding: 14px 18px;
  background: #211c0e;
  border-radius: 8px;
  color: #f4e6b5;
  margin-top: 18px;
}}

.success {{
  border-left-color: var(--accent2);
  background: #102219;
  color: #ccefd7;
}}

.danger {{
  border-left-color: var(--danger);
  background: #261415;
  color: #ffd2d0;
}}

.table-wrap {{
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 14px;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  min-width: 1050px;
}}

th,
td {{
  text-align: left;
  border-bottom: 1px solid var(--line);
  padding: 9px 8px;
  vertical-align: top;
}}

th {{
  position: sticky;
  top: 0;
  background: #111a2f;
  color: var(--muted);
  font-weight: 700;
  z-index: 1;
}}

tr:hover td {{
  background: rgba(110, 168, 254, .04);
}}

.tag {{
  display: inline-block;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}}

.yes {{
  background: #123a25;
  color: #9df0b5;
}}

.no {{
  background: #321a1a;
  color: #ffaaa5;
}}

.note {{
  color: var(--muted);
  font-size: 12px;
}}

footer {{
  color: var(--muted);
  font-size: 12px;
  margin-top: 28px;
}}

@media (max-width: 1000px) {{

  .grid,
  .insight-grid {{
    grid-template-columns: 1fr 1fr;
  }}

  .workflow {{
    grid-template-columns: 1fr 1fr 1fr;
  }}
}}

@media (max-width: 650px) {{

  .grid,
  .insight-grid {{
    grid-template-columns: 1fr;
  }}

  .workflow {{
    grid-template-columns: 1fr;
  }}

  h1 {{
    font-size: 32px;
  }}

  .metric-row {{
    grid-template-columns: 130px 1fr 40px;
  }}
}}

</style>

</head>

<body>

<div class="container">

  <div class="hero">

    <div class="eyebrow">
      Composio • Product Ops Intern
    </div>

    <h1>
      Researching 100 app integrations with an evidence-first agent
    </h1>

    <div class="lead">
      I built a reproducible pipeline that retrieves first-party developer
      documentation, extracts evidence, classifies every app against one
      schema, quality-checks the output, and routes weak findings to human
      verification.
    </div>

    <div class="actions">
      <a
        class="action"
        href="{SOURCE_REPO_URL}"
        target="_blank"
        rel="noopener noreferrer"
      >
        Source repository
      </a>

      <a
        class="action"
        href="{LIVE_APP_URL}"
        target="_blank"
        rel="noopener noreferrer"
      >
        Live case study
      </a>
    </div>

    <div class="grid">

      <div class="card">
        <div class="big">100</div>
        <div class="small">apps researched</div>
      </div>

      <div class="card">
        <div class="big">{mcp_count}</div>
        <div class="small">
          apps with MCP evidence ({pct(mcp_count, total)})
        </div>
      </div>

      <div class="card">
        <div class="big">{buildability.get("agent-ready", 0)}</div>
        <div class="small">agent-ready</div>
      </div>

      <div class="card">
        <div class="big">
          {buildability.get("buildable-with-setup", 0)}
        </div>
        <div class="small">
          buildable with setup
        </div>
      </div>

    </div>

  </div>

  <section>

    <h2>
      Executive summary
    </h2>

    <div class="insight-grid">

      <div class="insight">

        <h3>
          REST dominates
        </h3>

        <div class="big">
          {api_type.get("REST", 0)}
        </div>

        <div class="small">
          of 100 apps were classified as REST-only.
        </div>

      </div>

      <div class="insight">

        <h3>
          Authentication is the biggest evidence gap
        </h3>

        <div class="big">
          {credential.get("unknown", 0)}
        </div>

        <div class="small">
          credential paths remain unknown in the first-pass dataset.
        </div>

      </div>

      <div class="insight">

        <h3>
          The pipeline is intentionally conservative
        </h3>

        <div class="big">
          {review_count}
        </div>

        <div class="small">
          apps were flagged for review instead of being treated as
          confidently solved.
        </div>

      </div>

    </div>

  </section>

  <section>

    <h2>
      What I built
    </h2>

    <div class="workflow">

      <div class="step">
        <strong>1. Input</strong>
        100-app CSV containing category and official documentation hints.
      </div>

      <div class="step">
        <strong>2. Retrieval</strong>
        Official URLs first; requests first and Playwright fallback.
      </div>

      <div class="step">
        <strong>3. Evidence</strong>
        HTML cleaned into text with source URLs preserved.
      </div>

      <div class="step">
        <strong>4. Agent</strong>
        Gemini 3.5 Flash-Lite produces schema-constrained JSON.
      </div>

      <div class="step">
        <strong>5. Quality gate</strong>
        Thin or contradictory evidence is flagged automatically.
      </div>

      <div class="step">
        <strong>6. Human loop</strong>
        Selected weak cases are manually checked and corrections are stored.
      </div>

    </div>

    <div class="callout success">

      Composio SDK connectivity and tool discovery were successfully tested.
      The Composio Browser Tool itself returned HTTP 403 because execution was
      disabled by the administrator, so the final web-research path used
      direct retrieval plus a local Playwright fallback. This limitation is
      disclosed rather than hidden.
    </div>

  </section>

  <section>

    <h2>
      Key patterns
    </h2>

    <h3>
      Credential path
    </h3>

    {bar_row(
        "Self-serve free",
        credential.get("self-serve-free", 0),
        total,
    )}

    {bar_row(
        "Self-serve trial",
        credential.get("self-serve-trial", 0),
        total,
    )}

    {bar_row(
        "Admin approval",
        credential.get("admin-approval-required", 0),
        total,
    )}

    {bar_row(
        "Partner gated",
        credential.get("partner-gated", 0),
        total,
    )}

    {bar_row(
        "Unknown",
        credential.get("unknown", 0),
        total,
    )}

    <h3 style="margin-top:24px;">
      Buildability
    </h3>

    {bar_row(
        "Agent-ready",
        buildability.get("agent-ready", 0),
        total,
    )}

    {bar_row(
        "Buildable with setup",
        buildability.get("buildable-with-setup", 0),
        total,
    )}

    {bar_row(
        "Blocked",
        buildability.get("blocked", 0),
        total,
    )}

    {bar_row(
        "Uncertain",
        buildability.get("uncertain", 0),
        total,
    )}

    <h3 style="margin-top:24px;">
      Normalized authentication patterns
    </h3>

    <div class="table-wrap">

      <table>

        <thead>
          <tr>
            <th>Canonical auth bucket</th>
            <th>Apps</th>
          </tr>
        </thead>

        <tbody>

          {
            "".join(
              f"<tr><td>{escape(name)}</td><td>{count}</td></tr>"
              for name, count
              in auth_counter.most_common()
            )
          }

        </tbody>

      </table>

    </div>

  </section>

  <section>

    <h2>
      Human verification: first pass vs. checked result
    </h2>

    <div class="grid">

      <div class="card">
        <div class="big">
          {verified_apps}
        </div>
        <div class="small">
          fully human-verified apps
        </div>
      </div>

      <div class="card">
        <div class="big">
          {recorded_corrections}
        </div>
        <div class="small">
          recorded field corrections
        </div>
      </div>

      <div class="card">
        <div class="big">
          {len(pass_results)}
        </div>
        <div class="small">
          first-pass quality passes
        </div>
      </div>

      <div class="card">
        <div class="big">
          {review_count}
        </div>
        <div class="small">
          first-pass review flags
        </div>
      </div>

    </div>

    <div class="callout">

      The sample is not presented as a statistically valid 100-app accuracy
      benchmark. It is a targeted verification loop designed to expose
      real misses and show how human review changes the output.
    </div>

    <div class="table-wrap">

      <table>

        <thead>

          <tr>
            <th>App</th>
            <th>Agent confidence</th>
            <th>Corrections</th>
            <th>What human review found</th>
          </tr>

        </thead>

        <tbody>

          {verified_rows}

        </tbody>

      </table>

    </div>

  </section>

  <section>

    <h2>
      Top blockers
    </h2>

    <div class="table-wrap">

      <table>

        <thead>
          <tr>
            <th>Blocker</th>
            <th>Count</th>
          </tr>
        </thead>

        <tbody>
          {blocker_rows}
        </tbody>

      </table>

    </div>

    <div class="callout danger">

      The strongest recurring blocker was not a missing API. It was missing
      evidence about authentication and credential acquisition. That is where
      a stronger discovery loop would provide the most leverage.
    </div>

  </section>

  <section>

    <h2>
      Category-level matrix
    </h2>

    <div class="table-wrap">

      <table>

        <thead>

          <tr>
            <th>Category</th>
            <th>Apps</th>
            <th>Agent-ready</th>
            <th>Setup</th>
            <th>Blocked</th>
            <th>Uncertain</th>
            <th>MCP</th>
          </tr>

        </thead>

        <tbody>

          {category_rows}

        </tbody>

      </table>

    </div>

  </section>

  <section>

    <h2>
      Full 100-app research matrix
    </h2>

    <p class="note">
      Evidence URLs are clickable. “Unknown” and “Review” are intentional
      states: the agent did not invent an answer when the retrieved evidence
      did not support one.
    </p>

    <div class="table-wrap">

      <table>

        <thead>

          <tr>
            <th>ID</th>
            <th>App</th>
            <th>Category</th>
            <th>Auth</th>
            <th>Credential path</th>
            <th>API</th>
            <th>MCP</th>
            <th>Buildability</th>
            <th>Confidence</th>
            <th>Quality</th>
            <th>Evidence</th>
          </tr>

        </thead>

        <tbody>

          {app_rows}

        </tbody>

      </table>

    </div>

  </section>

  <section>

    <h2>
      Known research limitations
    </h2>

    <ul>

      <li>
        Composio Browser Tool execution was unavailable in the assessment
        environment (HTTP 403), so local Playwright was used as the fallback.
      </li>

      <li>
        Fixed URL candidates are useful but imperfect; some pages redirected,
        returned thin content, or required a browser.
      </li>

      <li>
        Authentication labels were normalized for the summary view, while
        the underlying final records retain the original agent evidence.
      </li>

      <li>
        Some apps require deeper targeted evidence research before their
        credential path or MCP status should be considered final.
      </li>

    </ul>

  </section>

  <section>

    <h2>
      What I would build next
    </h2>

    <div class="insight-grid">

      <div class="insight">
        <h3>
          Targeted evidence discovery
        </h3>
        Automatically search specifically for authentication, API access,
        pricing, developer onboarding, and MCP pages when the first pass
        leaves those fields unresolved.
      </div>

      <div class="insight">
        <h3>
          Evidence-aware second pass
        </h3>
        Trigger a targeted re-research loop only for missing fields rather
        than rerunning the entire app research task.
      </div>

      <div class="insight">
        <h3>
          Better taxonomy
        </h3>
        Canonicalize authentication mechanisms and blockers before producing
        aggregate portfolio-level insights.
      </div>

    </div>

  </section>

  <footer>

    Composio Product Ops Intern take-home •
    100-app research pipeline •
    Evidence-first and human-verified where required.

  </footer>

</div>

</body>
</html>
"""

    OUTPUT.write_text(
        html,
        encoding="utf-8",
    )

    print(
        f"Case study generated:\n{OUTPUT}"
    )


if __name__ == "__main__":
    main()