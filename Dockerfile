# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

# don’t write .pyc files, flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# create a non‑root user
ARG UID=10001
RUN adduser --disabled-password --gecos "" \
      --home "/home/appuser" \
      --shell "/sbin/nologin" \
      --uid "${UID}" appuser

# install any C‑build dependencies
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

USER appuser
WORKDIR /home/appuser

# install your Python dependencies
COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir -r requirements.txt

# copy in your agent code
COPY . .

# (optional) download models at build time
RUN python minimal_assistant.py download-files

# default entrypoint + command
ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
