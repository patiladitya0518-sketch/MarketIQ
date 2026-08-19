from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.auth import get_db, get_current_user
from schemas.auth import UserRegister, UserLogin, Token
from services.auth_service import create_user, authenticate_user
from services.jwt_service import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================================================
# REGISTER
# ==========================================================

@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    """

    new_user = create_user(db, user)

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    return {
        "success": True,
        "message": "User registered successfully.",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
        },
    }


# ==========================================================
# LOGIN
# ==========================================================

@router.post("/login", response_model=Token)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login user and return JWT token.
    """

    db_user = authenticate_user(
        db,
        user.email,
        user.password,
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ==========================================================
# CURRENT USER
# ==========================================================

@router.get("/me")
def get_me(
    current_user=Depends(get_current_user),
):
    """
    Get currently logged-in user.
    """

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "profile_image": current_user.profile_image,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }