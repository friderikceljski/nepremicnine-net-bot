# nepremicnine-net-bot

Starter scraper for nepremicnine.net search results.

## What it extracts
From each `div.property-details` listing on the target URL:
- property name (`a.url-title-d[title]`)
- price
- size in m2

## Run locally
```bash
python -m pip install -r requirements.txt
python scraper.py --method all
```

Methods:
- `requests` (fast first try)
- `playwright` (fallback for dynamic pages)
- `all` (default: tries requests, then playwright)

## Run with Docker Compose
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```
