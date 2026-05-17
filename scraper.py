from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://www.nepremicnine.net/oglasi-prodaja/ljubljana-okolica/posest/zazidljiva/cena-od-100000-do-200000-eur,velikost-od-1000-do-2000-m2/"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
PRICE_RE = re.compile(r"\b\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?\s*EUR\b", re.IGNORECASE)
SIZE_RE = re.compile(r"\b\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?\s*m2\b", re.IGNORECASE)


@dataclass
class Property:
    name: str
    price: str
    size_m2: str


def _first_match(regex: re.Pattern[str], text: str) -> str:
    match = regex.search(text)
    return match.group(0).strip() if match else ""


def parse_properties_from_html(html: str) -> List[Property]:
    soup = BeautifulSoup(html, "html.parser")
    properties: List[Property] = []

    for details in soup.select("div.property-details"):
        if not isinstance(details, Tag):
            continue

        title_anchor = details.select_one("a.url-title-d[title]")
        if not isinstance(title_anchor, Tag):
            continue

        raw_text = " ".join(details.stripped_strings)
        title = title_anchor.get("title", "")
        name = " ".join(title).strip() if isinstance(title, list) else str(title).strip()
        price = _first_match(PRICE_RE, raw_text)
        size_m2 = _first_match(SIZE_RE, raw_text)

        if name:
            properties.append(Property(name=name, price=price, size_m2=size_m2))

    return properties


def fetch_with_requests(url: str) -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.text


def fetch_with_playwright(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(url, wait_until="networkidle", timeout=60_000)
        html = page.content()
        browser.close()
        return html


def scrape(url: str, methods: Iterable[str]) -> List[Property]:
    errors = []

    for method in methods:
        try:
            html = fetch_with_requests(url) if method == "requests" else fetch_with_playwright(url)
            properties = parse_properties_from_html(html)
            if properties:
                return properties
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{method}: {exc}")

    details = " | ".join(errors) if errors else "No properties found"
    raise RuntimeError(f"Scraping failed. {details}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Starter scraper for nepremicnine.net")
    parser.add_argument("--url", default=URL, help="Target URL to scrape")
    parser.add_argument(
        "--method",
        choices=["requests", "playwright", "all"],
        default="all",
        help="Scraping method to use",
    )
    args = parser.parse_args()

    methods = ["requests", "playwright"] if args.method == "all" else [args.method]

    try:
        properties = scrape(args.url, methods)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps([asdict(item) for item in properties], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
