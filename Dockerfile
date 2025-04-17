# Use an official Python image
FROM python:3.10-slim

# System-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# Add the assistant user first
# ---------------------------
RUN adduser --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "10001" assistant && \
    mkdir -p /home/appuser && \
    chown -R assistant:assistant /home/appuser

# Switch to assistant user
USER assistant
WORKDIR /home/appuser

# ---------------------------
# Set environment variables
# ---------------------------
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/home/appuser/.local/lib/python3.10/site-packages:$PYTHONPATH"

# ---------------------------
# Copy and install dependencies
# ---------------------------
COPY --chown=assistant:assistant requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

# Copy the rest of your app
COPY --chown=assistant:assistant . .

# ---------------------------
# Run your startup command
# ---------------------------
RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
