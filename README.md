# Composio Product Ops Intern — 100-App Research Agent

Research agent and case study built for the Composio Product Ops Intern take-home assignment.

The system researches 100 apps and captures authentication, credential access, API surface, MCP availability, buildability, evidence, and verification signals. It then analyzes cross-app patterns and generates a self-contained HTML case study.

## Case Study

**Live case study:**  
https://Vardhan626272.github.io/composio-product-ops-research-agent/

**Source repository:**  
https://github.com/Vardhan626272/composio-product-ops-research-agent

---

## What the Agent Does

For each of the 100 apps, the pipeline attempts to determine:

- Category and what the app does
- Authentication method(s)
- Credential acquisition path
- API type and approximate breadth
- MCP availability
- Agent buildability
- Main blocker
- Evidence URLs and summaries
- Confidence and quality signals
- Human-verification requirements

The pipeline then aggregates the results to identify patterns across the full research set.

---

## Final Research Snapshot

| Metric | Result |
|---|---:|
| Apps researched | 100 |
| Successful research records | 100 |
| MCP available | 41 |
| Agent-ready | 25 |
| Buildable with setup | 28 |
| Blocked | 2 |
| Uncertain | 45 |
| Human verification flagged | 89 |
| Human verified | 3 |
| Quality pass | 11 |
| Quality review | 89 |

### Main patterns

- REST is the dominant API type: 70/100 apps.
- Broad API surfaces are common: 63/100 apps.
- OAuth and token-based authentication dominate the research set.
- Credential-path information is a major source of uncertainty.
- 89/100 records were flagged for human verification.
- The most common blocker was unclear API authentication.
- Productivity and Project Management produced the strongest agent-ready share.
- Data, SEO and Scraping also showed strong agent-building potential.
- Finance and AI/Research categories contained more gated or uncertain cases.

These findings are based on the agent's collected research and should be interpreted together with the verification results.

---

## Verification

Verification was treated as a separate step rather than assuming that the first research pass was correct.

The current pipeline includes:

1. Automated research and evidence collection
2. Candidate URL validation
3. Quality checks
4. Verification sampling
5. Human review and correction fields
6. Pattern analysis from the resulting dataset

Three records were explicitly human-verified in the current run:

- HubSpot
- Salesforce Commerce Cloud
- Paygent Connect

The pipeline intentionally exposes uncertainty instead of presenting unverified results as fully accurate.

---

## Pipeline

```text
100-app input
     |
     v
Research agent
     |
     +--> URL / source discovery
     |
     +--> Web research
     |
     +--> Evidence extraction
     |
     v
Candidate results
     |
     v
Validation + quality gates
     |
     v
Verification / human review
     |
     v
Final results
     |
     +--> Pattern analysis
     |
     +--> HTML case study
