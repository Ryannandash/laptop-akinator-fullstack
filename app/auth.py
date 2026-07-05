import os
import time
import jwt
from passlib.context import CryptContext
from fastapi import Header, HTTPException

SECRET_KEY = os.environ.get("JWT_SECRET", "ganti-dengan-secret-yang-aman")
ALGORITHM = "HS256"
EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 hari

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": time.time() + EXPIRE_SECONDS}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def get_current_user_id(authorization: str = Header(default=None)) -> str:
    """Dependency wajib login. Mengharapkan header Authorization: Bearer <token>"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak ditemukan")
    token = authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token tidak valid atau kedaluwarsa")
    return user_id


def get_optional_user_id(authorization: str = Header(default=None)):
    """Dependency untuk endpoint yang bisa dipakai guest maupun user login."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    return decode_token(token)
