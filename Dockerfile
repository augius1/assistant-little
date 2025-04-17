# syntax=docker/dockerfile:1
FROM python:3.13.1-slim

#–– Avoid .pyc, unbuffered logs ––
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#–– Create a non-root user “assistant” with home at /home/appuser ––
ARG UID=10001
RUN adduser --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    assistant  \
 && chown -R assistant:assistant /home/appuser

#–– Install C build deps as root ––
USER root
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

#–– Switch to the non-root user ––
USER assistant
WORKDIR /home/appuser

#–– Install Python deps globally (no --user) ––
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

#–– Copy in your agent code ––
COPY --chown=assistant:assistant . .

#–– (Optional) pre-download assets at build time ––
RUN python minimal_assistant.py download-files

ENTRYPOINT ["python", "minimal_assistant.py"]
CMD ["dev"]
