from app.core.config import JWKS_URL, ALG, BACKEND_AUDIENCE, IDP_ISS
from fastapi_microkit.auth import AuthSettings, build_auth_dependencies

settings = AuthSettings(
    jwks_url=JWKS_URL,
    algorithm=ALG,
    audience=BACKEND_AUDIENCE,
    issuer=IDP_ISS
)

get_claims, get_principal, require_role = build_auth_dependencies(settings)
