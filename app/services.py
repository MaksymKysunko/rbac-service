import base64
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from typing import Optional
from fastapi import Header, Depends, HTTPException

from app.db import SessionLocal
from app.core.config import (ALG, JWKS_URL, RBAC_AUDIENCE, IDP_ISS)
import logging


_jwks_cache: Optional[dict] = None


def _b64url_to_bytes(val: str) -> bytes:
    rem = len(val) % 4
    if rem:
        val += "=" * (4 - rem)
    return base64.urlsafe_b64decode(val.encode("utf-8"))


def _load_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        logging.info("[rbac] loading JWKS from %s", JWKS_URL)
        resp = requests.get(JWKS_URL, timeout=5)
        logging.info("[rbac] JWKS response: %s %s", resp.status_code, resp.text[:200])
        if resp.status_code != 200:
            logging.error("[rbac] Failed to fetch JWKS: %s %s", resp.status_code, resp.text)
            raise HTTPException(500, "cannot fetch jwks")
        _jwks_cache = resp.json()
        logging.info("[rbac] JWKS loaded with %d keys", len(_jwks_cache.get("keys", [])))
    return _jwks_cache


def verify_bearer(auth: Optional[str]) -> dict:
    if not auth or not auth.startswith("Bearer "):
        logging.warning("[rbac] verify_bearer: missing or malformed Authorization header: %r", auth)
        raise HTTPException(401, "missing bearer")

    token = auth.split(" ", 1)[1].strip()
    logging.info("[rbac] verify_bearer: got bearer token len=%d", len(token))

    # заголовок токена без перевірки підпису
    try:
        unverified_header = jwt.get_unverified_header(token)
        logging.info(
            "[rbac] verify_bearer: unverified header kid=%r alg=%r",
            unverified_header.get("kid"),
            unverified_header.get("alg"),
        )
    except Exception:
        logging.exception("[rbac] verify_bearer: failed to parse unverified header")
        raise HTTPException(401, "invalid token")

    # payload без перевірки (для логів)
    try:
        unverified_payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_aud": False},
            algorithms=[ALG],
        )
        logging.info(
            "[rbac] verify_bearer: unverified payload sub=%r aud=%r role=%r",
            unverified_payload.get("sub"),
            unverified_payload.get("aud"),
            unverified_payload.get("role"),
        )
    except Exception:
        logging.exception("[rbac] verify_bearer: cannot decode unverified payload")

    kid = unverified_header.get("kid")
    if not kid:
        logging.warning("[rbac] verify_bearer: token without kid")
        raise HTTPException(401, "missing kid")

    jwks = _load_jwks()
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)

    if not key:
        logging.warning("[rbac] verify_bearer: kid %r not found in JWKS, refreshing cache", kid)
        global _jwks_cache
        _jwks_cache = None
        jwks = _load_jwks()
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)

    if not key:
        logging.error("[rbac] verify_bearer: unknown kid=%r even after JWKS refresh", kid)
        raise HTTPException(401, "unknown kid")

    try:
        n_bytes = _b64url_to_bytes(key["n"])
        e_bytes = _b64url_to_bytes(key["e"])

        n = int.from_bytes(n_bytes, "big")
        e = int.from_bytes(e_bytes, "big")

        pub = rsa.RSAPublicNumbers(e, n).public_key()
        pub_pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        logging.info(
            "[rbac] verify_bearer: decoding JWT with expected audience=%r",
            RBAC_AUDIENCE,
        )

        claims = jwt.decode(
            token,
            pub_pem,
            algorithms=[ALG],
            audience=RBAC_AUDIENCE,
            options={"verify_iss": False},
        )

        logging.info(
            "[rbac] verify_bearer: token validated OK: sub=%r aud=%r role=%r",
            claims.get("sub"),
            claims.get("aud"),
            claims.get("role"),
        )
    except Exception:
        logging.exception("[rbac] verify_bearer: token validation failed")
        raise HTTPException(401, "invalid token")

    return claims

def get_claims(authorization: Optional[str] = Header(default=None)) -> dict:
    """Як у профайлі: дістати і провалідати JWT, повернути claims."""
    return verify_bearer(authorization)


def require_role(*allowed_roles: str):
    """
    Залежність для перевірки ролі.
    Приклад: Depends(require_role("boss"))
    """
    def _dep(claims: dict = Depends(get_claims)) -> dict:
        role = claims.get("role")
        if role not in allowed_roles:
            raise HTTPException(403, "forbidden")
        return claims

    return _dep


def get_principal(claims: dict = Depends(get_claims)) -> dict:
    """
    Спеціалізована залежність для RBAC:
    повертає dict з user_id (sub) і role.
    """
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(401, "token missing sub")

    try:
        uid = int(sub)
    except ValueError:
        raise HTTPException(401, "invalid subject in token")

    role = claims.get("role")
    if not role:
        raise HTTPException(401, "token missing role")

    return {"user_id": uid, "role": role}