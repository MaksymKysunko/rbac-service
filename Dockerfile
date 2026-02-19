# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install microkit-python
COPY microkit-python /tmp/microkit-python
RUN pip install --no-cache-dir /tmp/microkit-python

# Install service dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    pydantic \
    psycopg2-binary \
    pyjwt \
    cryptography \
    requests \
    prometheus-client \
    pytest \
    pytest-asyncio \
    requests-mock \
    pytest-mock

# Stage 2: Tester
FROM builder AS tester
WORKDIR /app
COPY rbac-service/app ./app
COPY rbac-service/tests ./tests
RUN python -m pytest tests && touch .tests-passed

# Stage 3: Final
FROM python:3.12-slim

WORKDIR /app

# Ensure tests passed before proceeding to final image
COPY --from=tester /app/.tests-passed ./.tests-passed

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy only the installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy service code
COPY rbac-service/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
