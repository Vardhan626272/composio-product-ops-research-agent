from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class ResearchPage:
    url: str
    text: str
    method: str


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)


def fetch_with_requests(url: str) -> ResearchPage | None:
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        response.raise_for_status()

        text = clean_html(response.text)

        if len(text) < 500:
            return None

        return ResearchPage(
            url=response.url,
            text=text,
            method="requests",
        )

    except requests.RequestException:
        return None


def fetch_with_browser(url: str) -> ResearchPage | None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                )
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            page.wait_for_timeout(3000)

            text = page.locator("body").inner_text()
            final_url = page.url

            browser.close()

        if len(text.strip()) < 500:
            return None

        return ResearchPage(
            url=final_url,
            text=text.strip(),
            method="playwright",
        )

    except Exception as exc:
        print(f"Browser fallback failed for {url}: {exc}")
        return None


def research_url(url: str) -> ResearchPage | None:
    print(f"Trying requests: {url}")

    result = fetch_with_requests(url)

    if result:
        print(
            f"Success with requests: "
            f"{result.url} ({len(result.text)} chars)"
        )
        return result

    print(f"Requests failed or returned insufficient text: {url}")
    print("Trying Playwright browser fallback...")

    result = fetch_with_browser(url)

    if result:
        print(
            f"Success with Playwright: "
            f"{result.url} ({len(result.text)} chars)"
        )
        return result

    return None


def research_candidates(urls: list[str]) -> list[ResearchPage]:
    """
    Try all candidate URLs and collect every usable documentation page.

    This is intentionally different from the earlier implementation:
    we do not stop after the first successful page.
    """

    pages: list[ResearchPage] = []

    for url in urls:
        result = research_url(url)

        if result:
            pages.append(result)

    return pages