from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from app.database import get_db
from app.models.document import Document
from app.models.affaire import Affaire

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.get("/")
async def list_documents(affaire_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if affaire_id:
        query = query.filter(Document.affaire_id == affaire_id)
    return query.all()


@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return document


@router.post("/upload")
async def upload_document(
    affaire_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Vérifier que l'affaire existe
    affaire = db.query(Affaire).filter(Affaire.id == affaire_id).first()
    if not affaire:
        raise HTTPException(status_code=404, detail="Affaire non trouvée")

    # Créer le dossier d'upload si nécessaire
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Sauvegarder le fichier
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Créer l'entrée en base de données
    document = Document(
        nom=file.filename,
        chemin_fichier=file_path,
        type_mime=file.content_type,
        taille=os.path.getsize(file_path),
        affaire_id=affaire_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/download/{document_id}")
async def download_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if not os.path.exists(document.chemin_fichier):
        raise HTTPException(status_code=404, detail="Fichier non trouvé sur le disque")
    return FileResponse(
        path=document.chemin_fichier,
        filename=document.nom,
        media_type=document.type_mime
    )


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")

    # Supprimer le fichier du disque
    if os.path.exists(document.chemin_fichier):
        os.remove(document.chemin_fichier)

    # Supprimer l'entrée en base
    db.delete(document)
    db.commit()
    return {"message": "Document supprimé"}
