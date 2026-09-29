import os
import uuid
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur

# Configuration JWT (surcharger SECRET_KEY en production)
SECRET_KEY = os.getenv("SECRET_KEY", "changez-moi-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Identifiants (jti) des jetons révoqués par /logout, conservés jusqu'à leur expiration
_jetons_revoques: dict[str, datetime] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, mot_de_passe_hash: str) -> bool:
    return pwd_context.verify(password, mot_de_passe_hash)


def create_access_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire, "jti": uuid.uuid4().hex}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def revoke_token(payload: dict):
    maintenant = datetime.utcnow()
    # Purger les jetons déjà expirés
    for jti, expire in list(_jetons_revoques.items()):
        if expire < maintenant:
            del _jetons_revoques[jti]
    _jetons_revoques[payload["jti"]] = datetime.utcfromtimestamp(payload["exp"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Utilisateur:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expirée",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    if payload.get("jti") in _jetons_revoques:
        raise credentials_exception

    username = payload.get("sub")
    utilisateur = db.query(Utilisateur).filter(Utilisateur.username == username).first()
    if not utilisateur or not utilisateur.est_actif:
        raise credentials_exception
    return utilisateur
