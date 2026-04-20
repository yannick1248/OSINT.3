# Build this image from the repository root so that both ./backend and
# ./osint_omega are in the build context:
#   docker build -f backend/Dockerfile -t osint-omega-backend .
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

COPY osint_omega /opt/osint_omega
COPY backend/pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install -e /opt/osint_omega \
 && pip install -e ".[dev]"

COPY backend/app ./app
COPY backend/tests ./tests

EXPOSE 8000
CMD ["uvicorn", "app.presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
