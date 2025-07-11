import os
from dotenv import load_dotenv

load_dotenv()  # legge fiscoai/.env in locale; nei deploy usi vere env-vars

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY non trovato: aggiungilo al tuo .env (openssl rand -hex 32)"
    )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ──────────────────────────────────────────────
# 2) Import di terze parti
# ──────────────────────────────────────────────
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError             # python-jose[cryptography]
from passlib.context import CryptContext   # passlib[bcrypt]
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from sqlmodel import select

# ──────────────────────────────────────────────
# 3) Import interni al progetto
# ──────────────────────────────────────────────
from services.db import get_session
from models.user import User, UserCreate

# ──────────────────────────────────────────────
# 4) Helpers bcrypt & OAuth2
# ──────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ──────────────────────────────────────────────
# 5) CRUD utenti
# ──────────────────────────────────────────────
def create_user(data: UserCreate) -> User:
    """Registra un nuovo utente con password criptata."""
    with next(get_session()) as session:
        # Evita doppie email
        if session.exec(select(User).where(User.email == data.email)).first():
            raise HTTPException(status_code=400, detail="Email già registrata")

        user = User(
            email=data.email,
            hashed_password=_hash_password(data.password),
            role="user",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def authenticate(email: str, password: str) -> Optional[User]:
    """Ritorna User se la password è corretta, altrimenti None."""
    with next(get_session()) as session:
        user = session.exec(select(User).where(User.email == email)).first()
    if user and _verify_password(password, user.hashed_password):
        return user
    return None


# ──────────────────────────────────────────────
# 6) JWT utility
# ──────────────────────────────────────────────
def create_access_token(
    sub: str, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode = {"sub": sub, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dipendenza FastAPI per proteggere endpoint:
    - legge Authorization: Bearer <token>
    - decodifica e valida JWT
    - carica oggetto User dal DB
    """
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token non valido o scaduto",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    with next(get_session()) as session:
        user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise cred_exc
    return user