from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas import UtilisateurCreate, UtilisateurResponse, Token
from app.security import (
    hash_password, verify_password, create_access_token, decode_token,
    revoke_token, get_current_user, oauth2_scheme
)

router = APIRouter()


@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(utilisateur: UtilisateurCreate, request: Request, db: Session = Depends(get_db)):
    # Le premier compte peut être créé librement ; les suivants nécessitent d'être connecté
    if db.query(Utilisateur).count() > 0:
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            raise HTTPException(status_code=403, detail="Inscription fermée : un utilisateur connecté doit créer votre compte")
        get_current_user(auth[7:], db)

    if len(utilisateur.password) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")

    existing = db.query(Utilisateur).filter(
        (Utilisateur.username == utilisateur.username) |
        (Utilisateur.email == utilisateur.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur ou cet email est déjà utilisé")

    db_utilisateur = Utilisateur(
        username=utilisateur.username,
        email=utilisateur.email,
        mot_de_passe_hash=hash_password(utilisateur.password)
    )
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Connexion par nom d'utilisateur ou email
    utilisateur = db.query(Utilisateur).filter(
        (Utilisateur.username == form_data.username) |
        (Utilisateur.email == form_data.username)
    ).first()
    if not utilisateur or not verify_password(form_data.password, utilisateur.mot_de_passe_hash):
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not utilisateur.est_actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    return Token(access_token=create_access_token(utilisateur.username))


@router.post("/logout", status_code=204)
def logout(token: str = Depends(oauth2_scheme), utilisateur: Utilisateur = Depends(get_current_user)):
    revoke_token(decode_token(token))
    return None


@router.get("/me", response_model=UtilisateurResponse)
def me(utilisateur: Utilisateur = Depends(get_current_user)):
    return utilisateur
