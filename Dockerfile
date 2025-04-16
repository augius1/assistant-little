# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

#–– Environment: no .pyc files, unbuffered logs ––
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#–– Create a non‑root user “appuser” with home at /home/appuser ––
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/home/appuser" --shell "/sbin/nologin" --uid "${UID}" appuser

#–– Install C build‑deps (for any native pip packages) as root ––
USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

#–– Switch to non‑root user and set working directory ––
USER appuser
WORKDIR /home/appuser

#–– Install Python dependencies globally (do not use --user) ––
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

#–– Copy your agent code (with proper ownership) ––
COPY --chown=appuser:appuser . .

#–– Download assets at build time (optional – if needed, otherwise run at startup) ––
RUN python minimal_assistant.py download-files

#–– Set the default entrypoint & command ––
ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
