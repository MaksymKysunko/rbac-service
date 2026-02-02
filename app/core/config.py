# app/core/config.py
import os

ALG = "RS256"
JWKS_URL = os.getenv("JWKS_URL", "http://idp:8000/.well-known/jwks.json")
IDP_ISS = os.getenv("IDP_ISS", "http://idp:8000")
BACKEND_AUDIENCE = os.getenv("BACKEND_AUDIENCE", "club-api")

DB_URL = os.getenv("DB_URL", "postgresql://rbac:rbac@db:5432/rbac")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "change-me")
