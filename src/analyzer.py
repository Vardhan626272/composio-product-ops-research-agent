import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from models import AppResearch
from research_prompt import RESEARCH_PROMPT


load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing from .env")


client = genai.Client(api_key=api_key)


MODEL_NAME = "gemini-3.5-flash-lite"


def analyze_app(
    app: str,
    category: str,
    source_urls: list[str],
    source_text: str,
) -> AppResearch:
    """
    Analyze supplied documentation for one application.

    The model is explicitly instructed to use only the supplied evidence.
    """

    prompt = f"""
{RESEARCH_PROMPT}

TARGET APP:
{app}

CATEGORY:
{category}

SOURCE URLS:
{json.dumps(source_urls, indent=2)}

SOURCE DOCUMENTATION TEXT:
{source_text[:30000]}

Additional instructions:
- Use only the supplied documentation text and URLs.
- Do not rely on unstated background knowledge.
- Do not invent authentication, pricing, MCP, or API details.
- When evidence is insufficient, explicitly represent the uncertainty.
- Return ONLY valid JSON matching the AppResearch schema.
"""

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AppResearch.model_json_schema(),
                },
            )

            if not response.text:
                raise RuntimeError(
                    f"Gemini returned an empty response for {app}"
                )

            data = json.loads(response.text)

            return AppResearch.model_validate(data)

        except errors.ServerError as exc:
            # Temporary service-side errors such as HTTP 503.
            if attempt == max_attempts:
                raise

            wait_seconds = 5 * attempt

            print(
                f"Gemini server error on attempt "
                f"{attempt}/{max_attempts}: {exc}"
            )
            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

        except errors.APIError as exc:
            # Handle transient rate-limit responses separately.
            status_code = getattr(exc, "code", None)

            if status_code == 429 and attempt < max_attempts:
                wait_seconds = 10 * attempt

                print(
                    f"Gemini rate limit on attempt "
                    f"{attempt}/{max_attempts}."
                )
                print(
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)
                continue

            raise

        except (json.JSONDecodeError, ValueError) as exc:
            # Structured output problems are usually not fixed by retrying,
            # but one retry can recover from a transient malformed response.
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Gemini returned invalid structured output for "
                    f"{app}: {exc}"
                ) from exc

            wait_seconds = 2 * attempt

            print(
                f"Invalid structured response on attempt "
                f"{attempt}/{max_attempts}: {exc}"
            )
            print(
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Gemini analysis failed after {max_attempts} attempts for {app}"
    )


if __name__ == "__main__":
    from web_research import research_candidates

    test_urls = [
        "https://docs.github.com/en/rest",
        "https://docs.github.com/en/rest/authentication",
    ]

    print("Fetching GitHub documentation...")
    pages = research_candidates(test_urls)

    if not pages:
        raise RuntimeError("Could not retrieve GitHub documentation.")

    source_urls = [page.url for page in pages]

    evidence_sections = []

    for index, page in enumerate(pages, start=1):
        evidence_sections.append(
            f"""
--- SOURCE {index} ---
URL: {page.url}
Retrieval method: {page.method}

CONTENT:
{page.text[:12000]}
"""
        )

    combined_evidence = "\n".join(evidence_sections)

    print(
        f"Fetched {len(pages)} source page(s), "
        f"{len(combined_evidence)} evidence characters."
    )

    print("Sending documentation to Gemini...")

    result = analyze_app(
        app="GitHub",
        category="Developer, Infra and Data platforms",
        source_urls=source_urls,
        source_text=combined_evidence,
    )

    print("\nAnalysis result:\n")
    print(result.model_dump_json(indent=2))