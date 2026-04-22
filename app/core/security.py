import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()
security = HTTPBearer()

SECRET_KEY =  os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRY_DAYS = os.getenv("ACCESS_TOKEN_EXPIRY_DAYS")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password:str) -> str:
    return pwd_context.hash(password)



def verify_password(plain:str, hashed:str):
    return pwd_context.verify(plain, hash=hashed)



def create_access_token(user_role: str, user_id:int):
    payload = {
        "sub":str(user_id),
        "role": user_role,
        "exp":datetime.now() + timedelta(days=int(ACCESS_TOKEN_EXPIRY_DAYS))
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return decode_token(credentials.credentials)


def require_role(role: str):
    def check_role(payload: dict = Depends(get_current_user)):
        if payload.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires '{role}' role"
            )
        return payload
    return check_role
