# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/app" --shell "/sbin/nologin" --uid "${UID}" assistant

USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=assistant:assistant . .

# (Optional) Download assets at build time – removed to avoid missing env-vars
# RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
