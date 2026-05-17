FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && python -m playwright install --with-deps chromium

COPY scraper.py /app/scraper.py

CMD ["python", "scraper.py"]
