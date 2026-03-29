# Stage 1: Builder
FROM la-familia-base AS builder

WORKDIR /app

# Stage 2: Tester
FROM builder AS tester
WORKDIR /app
COPY rbac-service/app ./app
COPY rbac-service/tests ./tests
RUN python -m pytest tests && touch .tests-passed

# Stage 3: Final
FROM la-familia-base

WORKDIR /app

# Ensure tests passed before proceeding to final image
COPY --from=tester /app/.tests-passed ./.tests-passed

# Copy service code
COPY rbac-service/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
