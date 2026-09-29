from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.client import Client
from app.schemas import ClientCreate, ClientUpdate, ClientResponse, ClientWithAffaires

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Client)
    
    # Recherche par nom, prénom ou email
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.nom.ilike(search_term)) |
            (Client.prenom.ilike(search_term)) |
            (Client.email.ilike(search_term))
        )
    
    clients = query.offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientWithAffaires)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    existing = db.query(Client).filter(Client.email == client.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un client avec cet email existe déjà")
    
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client: ClientUpdate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    for key, value in client.model_dump(exclude_unset=True).items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    db.delete(db_client)
    db.commit()
    return None
