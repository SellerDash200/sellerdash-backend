import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

CLERK_DOMAIN = os.getenv("CLERK_DOMAIN")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")

if not CLERK_DOMAIN or not CLERK_AUDIENCE:
    raise RuntimeError("CLERK_DOMAIN and CLERK_AUDIENCE must be set")

CLERK_ISSUER = f"https://{CLERK_DOMAIN}"
JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"

jwk_client = PyJWKClient(JWKS_URL)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token).key

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE,
            issuer=CLERK_ISSUER,
            leeway=30,
        )

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

