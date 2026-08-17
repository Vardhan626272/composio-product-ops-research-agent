from pydantic import BaseModel, Field
from typing import Literal


class AppResearch(BaseModel):
    app: str
    category: str
    what_it_does: str = Field(description="One-line description of the app's primary purpose.")

    auth_methods: list[str] = Field(
        description="Authentication methods documented by the app."
    )

    credential_path: Literal[
        "self-serve-free",
        "self-serve-trial",
        "paid-plan-required",
        "admin-approval-required",
        "partner-gated",
        "contact-sales",
        "unknown",
    ]

    api_type: Literal[
        "REST",
        "GraphQL",
        "REST+GraphQL",
        "SDK-only",
        "CLI",
        "No-public-API-found",
        "Other",
        "Unknown",
    ]

    api_breadth: Literal[
        "broad",
        "moderate",
        "narrow",
        "unknown",
    ]

    mcp_available: bool
    mcp_evidence: str | None = None

    buildability: Literal[
        "agent-ready",
        "buildable-with-setup",
        "blocked",
        "uncertain",
    ]

    main_blocker: str | None = None

    evidence_urls: list[str] = Field(
        description="URLs supporting the findings. Prefer official documentation."
    )

    evidence_summary: list[str] = Field(
        description="Short explanation of what each evidence source proves."
    )

    confidence: Literal[
        "high",
        "medium",
        "low",
    ]

    needs_human_verification: bool
    verification_note: str | None = None