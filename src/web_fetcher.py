import requests
from bs4 import BeautifulSoup


def fetch_page(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)


def fetch_with_fallback(urls: list[str]) -> tuple[str | None, str | None]:
    """
    Try several candidate URLs and return the first successful result.

    Returns:
        (url_used, extracted_text)
    """
    for url in urls:
        try:
            text = fetch_page(url)

            if len(text) >= 500:
                return url, text

        except requests.RequestException:
            continue

    return None, None