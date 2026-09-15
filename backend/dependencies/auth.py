from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.session import SessionLocal
from services.jwt_service import verify_access_token
from models.user import User


security = HTTPBearer()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# GET CURRENT AUTHENTICATED USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Resolve the currently authenticated MarketIQ user.

    The JWT normally contains:
        user_id -> database user ID
        sub     -> user email

    We first try user_id.

    If the user_id stored inside an older JWT does not exist
    in the database, we fall back to the email stored in
    the JWT.

    This prevents stale tokens from causing:
        401 User not found
    when the email still belongs to a valid user.
    """

    token = credentials.credentials

    # --------------------------------------------------------
    # VERIFY TOKEN
    # --------------------------------------------------------

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    # --------------------------------------------------------
    # READ JWT CLAIMS
    # --------------------------------------------------------

    user_id = payload.get("user_id")
    email = payload.get("sub")

    if not user_id and not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    # --------------------------------------------------------
    # FIRST: FIND USER BY USER ID
    # --------------------------------------------------------

    user = None

    if user_id:
        user = (
            db.query(User)
            .filter(
                User.id == str(user_id)
            )
            .first()
        )

    # --------------------------------------------------------
    # SECOND: FALL BACK TO EMAIL
    # --------------------------------------------------------

    if user is None and email:
        user = (
            db.query(User)
            .filter(
                User.email == str(email).lower()
            )
            .first()
        )

    # --------------------------------------------------------
    # USER STILL NOT FOUND
    # --------------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    # --------------------------------------------------------
    # CHECK ACCOUNT STATUS
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    return user