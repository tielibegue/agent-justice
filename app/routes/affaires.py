from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.affaire import Affaire, StatutAffaire
from app.schemas import AffaireCreate, AffaireUpdate, AffaireResponse, AffaireWithEcheances

router = APIRouter()


@router.get("/", response_model=List[AffaireResponse])
def list_affaires(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    statut: str = None,
    client_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Affaire)
    
    # Recherche par numéro ou titre
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Affaire.numero.ilike(search_term)) |
            (Affaire.titre.ilike(search_term))
        )
    
    # Filtrage par statut
    if statut:
        query = query.filter(Affaire.statut == statut)
    
    # Filtrage par client
    if client_id:
        query = query.filter(Affaire.client_id == client_id)
    
    affaires = query.offset(skip).limit(limit).all()
    return affaires


@router.get("/{affaire_id}", response_model=AffaireWithEcheances)
def get_affaire(affaire_id: int, db: Session = Depends(get_db)):
    affaire = db.query(Affaire).filter(Affaire.id == affaire_id).first()
    if not affaire:
        raise HTTPException(status_code=404, detail="Affaire non trouvée")
    return affaire


@router.post("/", response_model=AffaireResponse, status_code=201)
def create_affaire(affaire: AffaireCreate, db: Session = Depends(get_db)):
    # Vérifier si le numéro existe déjà
    existing = db.query(Affaire).filter(Affaire.numero == affaire.numero).first()
    if existing:
        raise HTTPException(status_code=400, detail="Une affaire avec ce numéro existe déjà")
    
    db_affaire = Affaire(**affaire.model_dump())
    db.add(db_affaire)
    db.commit()
    db.refresh(db_affaire)
    return db_affaire


@router.put("/{affaire_id}", response_model=AffaireResponse)
def update_affaire(affaire_id: int, affaire: AffaireUpdate, db: Session = Depends(get_db)):
    db_affaire = db.query(Affaire).filter(Affaire.id == affaire_id).first()
    if not db_affaire:
        raise HTTPException(status_code=404, detail="Affaire non trouvée")
    
    for key, value in affaire.model_dump(exclude_unset=True).items():
        setattr(db_affaire, key, value)
    
    db.commit()
    db.refresh(db_affaire)
    return db_affaire


@router.delete("/{affaire_id}", status_code=204)
def delete_affaire(affaire_id: int, db: Session = Depends(get_db)):
    db_affaire = db.query(Affaire).filter(Affaire.id == affaire_id).first()
    if not db_affaire:
        raise HTTPException(status_code=404, detail="Affaire non trouvée")
    
    db.delete(db_affaire)
    db.commit()
    return None
