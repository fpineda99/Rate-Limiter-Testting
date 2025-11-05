FROM python:3.12-slim

WORKDIR /app

COPY Template-2.py .

RUN pip install --no-cache-dir aiohttp requests

ENTRYPOINT ["python", "Template-2.py"]
