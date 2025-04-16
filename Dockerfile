# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

#–– Environment: no .pyc files, unbuffered logs ––
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#–– Create a non‑root user “assistant” with home at /app ––
ARG UID=10001
RUN adduser --disabled-password --gecos "" \
      --home "/app" \
      --shell "/sbin/nologin" \
      --uid "${UID}" assistant

#–– Install C build‑deps (for any native pip packages) as root ––
USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

#–– Install Python dependencies globally (without --user) ––
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

#–– Copy your agent code and set proper ownership ––
COPY --chown=assistant:assistant . .

#–– We’ll pull models at runtime, not build time ––

#–– Set the default entrypoint & command ––
ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
