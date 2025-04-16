# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

# don’t write .pyc files, flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non‑root user
ARG UID=10001
RUN adduser --disabled-password --gecos "" \
      --home "/home/appuser" \
      --shell "/sbin/nologin" \
      --uid "${UID}" appuser

# Install any C‑build dependencies
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /home/appuser

# Install your Python dependencies
COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir -r requirements.txt

# Copy in your agent code
COPY . .

# (Optional) Download models at build time
RUN python minimal_assistant.py download-files

# Set the default entrypoint and command
ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
