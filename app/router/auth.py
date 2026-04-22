from fastapi import APIRouter, Depends, HTTPException, Response, status
from schemas.pydantic_models import UserCreate, UserLogin, TokenResponse, UserResponse
from schemas.models import User
from sqlalchemy.orm import Session
from core.security import hash_password, verify_password, create_access_token, require_role
from core.database import get_db


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username = payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role = payload.role
    )
    
    
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user_id=user.id, user_role=user.role)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user_id=user.id, user_role=user.role)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
def admin_route():
    return {"message": "welcome admin"}
