# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

#–– Environment: no .pyc files, unbuffered logs ––
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/assistant/.local/bin:$PATH

#–– Create a non‑root user “assistant” with home at /app ––
ARG UID=10001
RUN adduser --disabled-password --gecos "" \
      --home "/app" \
      --shell "/sbin/nologin" \
      --uid "${UID}" assistant

#–– Install C build‑deps (for any native pip packages) ––
USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

#–– Switch to non‑root ––
USER assistant
WORKDIR /app

#–– Install Python deps into ~/.local ––
COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir -r requirements.txt

#–– Copy your agent code ––
COPY --chown=assistant:assistant . .

#–– NO build‑time download of models ––
#    We’ll pull at startup instead.

#–– Entrypoint & default command ––
ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
