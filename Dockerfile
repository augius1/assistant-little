# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/home/appuser" --shell "/sbin/nologin" --uid "${UID}" assistant

RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /home/appuser

COPY requirements.txt .
RUN python -m pip install - user - no-cache-dir -r requirements.txt

COPY . .
RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
