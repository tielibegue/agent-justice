from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.echeance import Echeance
from app.schemas import EcheanceCreate, EcheanceUpdate, EcheanceResponse

router = APIRouter()


@router.get("/", response_model=List[EcheanceResponse])
def list_echeances(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    affaire_id: int = None,
    accomplie: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Echeance)
    
    # Recherche par titre
    if search:
        search_term = f"%{search}%"
        query = query.filter(Echeance.titre.ilike(search_term))
    
    # Filtrage par affaire
    if affaire_id:
        query = query.filter(Echeance.affaire_id == affaire_id)
    
    # Filtrage par statut d'accomplissement
    if accomplie is not None:
        query = query.filter(Echeance.accomplie == accomplie)
    
    echeances = query.offset(skip).limit(limit).all()
    return echeances


@router.get("/{echeance_id}", response_model=EcheanceResponse)
def get_echeance(echeance_id: int, db: Session = Depends(get_db)):
    echeance = db.query(Echeance).filter(Echeance.id == echeance_id).first()
    if not echeance:
        raise HTTPException(status_code=404, detail="Échéance non trouvée")
    return echeance


@router.post("/", response_model=EcheanceResponse, status_code=201)
def create_echeance(echeance: EcheanceCreate, db: Session = Depends(get_db)):
    db_echeance = Echeance(**echeance.model_dump())
    db.add(db_echeance)
    db.commit()
    db.refresh(db_echeance)
    return db_echeance


@router.put("/{echeance_id}", response_model=EcheanceResponse)
def update_echeance(echeance_id: int, echeance: EcheanceUpdate, db: Session = Depends(get_db)):
    db_echeance = db.query(Echeance).filter(Echeance.id == echeance_id).first()
    if not db_echeance:
        raise HTTPException(status_code=404, detail="Échéance non trouvée")
    
    for key, value in echeance.model_dump(exclude_unset=True).items():
        setattr(db_echeance, key, value)
    
    db.commit()
    db.refresh(db_echeance)
    return db_echeance


@router.delete("/{echeance_id}", status_code=204)
def delete_echeance(echeance_id: int, db: Session = Depends(get_db)):
    db_echeance = db.query(Echeance).filter(Echeance.id == echeance_id).first()
    if not db_echeance:
        raise HTTPException(status_code=404, detail="Échéance non trouvée")
    
    db.delete(db_echeance)
    db.commit()
    return None
