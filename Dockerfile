FROM python:3.11-slim

RUN pip install --no-cache-dir playwright \
    && playwright install --with-deps chromium

EXPOSE 3000

CMD ["python", "-m", "playwright", "run-server", "--port", "3000", "--host", "0.0.0.0"]
