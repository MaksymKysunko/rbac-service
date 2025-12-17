from app.core.config import JWKS_URL, ALG, BACKEND_AUDIENCE
from club_shared.auth.settings import AuthSettings
from club_shared.auth.deps import build_auth_deps

settings = AuthSettings(
    jwks_url=JWKS_URL,
    algorithm=ALG,
    audience=BACKEND_AUDIENCE,
)

get_claims, get_principal, require_role = build_auth_deps(settings)
