# -------- Builder: resolve & lock --------
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.in ./
RUN python -m pip install -U pip setuptools wheel pip-tools \
 && pip-compile --generate-hashes -o requirements.txt requirements.in

# -------- Final image: install from lock --------
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
 && pip install --require-hashes --no-deps -r requirements.txt \
 && pip check

COPY . .

EXPOSE 5000
ENV FLASK_ENV=production
CMD ["python", "app.py"]