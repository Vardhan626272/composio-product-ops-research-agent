"""
Legacy single-app smoke test.

The production 100-app research pipeline is:
    src/batch_research.py

This file is retained only as a small Gemini/web-search smoke test.
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing")

client = genai.Client(api_key=api_key)

prompt = """
Research Salesforce using current public web information.

Return:
1. What Salesforce does in one sentence.
2. Authentication methods documented for its public APIs.
3. Whether API credentials can be obtained self-serve, and any important plan/admin restrictions.
4. Main public API type(s) and approximate breadth.
5. Whether Salesforce currently documents an MCP server.
6. The most important evidence URLs.

Prefer official Salesforce documentation. Distinguish clearly between facts and uncertainty.
"""

response = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=prompt,
    tools=[{"type": "google_search"}],
)

print(response.output_text)
