# app/core/config.py
import os

ALG = "RS256"
JWKS_URL = os.getenv("JWKS_URL", "http://idp:8000/.well-known/jwks.json")
IDP_ISS = os.getenv("IDP_ISS", "club-idp")
BACKEND_AUDIENCE = os.getenv("BACKEND_AUDIENCE", "club-api")
