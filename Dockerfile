# Use an official Python image
FROM python:3.10-slim

# Install system deps...
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /home/appuser

# Copy requirements and install _as root_ into /usr/local/
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir -r requirements.txt

# Now create and switch to a non‑root user
RUN adduser --disabled-password --gecos "" \
    --home "/home/appuser" --shell "/sbin/nologin" \
    --uid "10001" assistant
USER assistant

# Copy app code and run your download command
COPY --chown=assistant:assistant . .
RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
