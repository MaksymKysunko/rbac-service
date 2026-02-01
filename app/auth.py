from app.core.config import JWKS_URL, ALG, BACKEND_AUDIENCE, IDP_ISS
from club_shared.auth.settings import AuthSettings
from club_shared.auth.deps import build_auth_deps

settings = AuthSettings(
    jwks_url=JWKS_URL,
    algorithm=ALG,
    audience=BACKEND_AUDIENCE,
    issuer=IDP_ISS
)

get_claims, get_principal, require_role = build_auth_deps(settings)
