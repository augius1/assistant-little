# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

# Avoid .pyc, unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install C build deps as root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working dir and copy requirements early
WORKDIR /app
COPY requirements.txt .

# Install dependencies as root (so they're visible system-wide)
RUN python -m pip install --no-cache-dir -r requirements.txt

# Create non-root user after pip install
ARG UID=10001
RUN adduser --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    assistant  \
 && mkdir -p /home/appuser && chown -R assistant:assistant /home/appuser

# Copy in your code after switching user
USER assistant
COPY --chown=assistant:assistant . .

# Run script (still as assistant, but deps are installed globally)
RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
