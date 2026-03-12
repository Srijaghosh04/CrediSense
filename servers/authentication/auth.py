import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from dotenv import load_dotenv

load_dotenv()

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")

security = HTTPBearer()


async def verify_token(request: Request) -> dict:
    """
    Verify the Supabase JWT token from the Authorization header.
    Returns the decoded user payload if valid.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1]

    if not SUPABASE_JWT_SECRET:
        print("WARNING: SUPABASE_JWT_SECRET not set. Skipping authentication.")
        return {"sub": "dev-user", "email": "dev@localhost"}

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please login again.")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_user_id(user: dict) -> str:
    """Extract user ID from decoded JWT payload."""
    return user.get("sub", "")


def get_user_email(user: dict) -> str:
    """Extract user email from decoded JWT payload."""
    return user.get("email", "")
