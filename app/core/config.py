# app/core/config.py
import os

ALG = "RS256"
JWKS_URL = os.getenv("JWKS_URL", "http://idp-service/.well-known/jwks.json")
IDP_ISS = os.getenv("IDP_ISS", "club-idp")

PROFILE_AUDIENCE = os.getenv("PROFILE_AUDIENCE", "profile")
RBAC_AUDIENCE = os.getenv("RBAC_AUDIENCE", "rbac")
