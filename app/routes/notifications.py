from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification
from app.models.utilisateur import Utilisateur
from app.schemas import NotificationResponse
from app.security import get_current_user
from app.services.rappels import notifier_echeances_proches

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    lue: bool = None,
    utilisateur: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.utilisateur_id == utilisateur.id)

    # Filtrage lues / non lues
    if lue is not None:
        query = query.filter(Notification.lue == lue)

    notifications = query.order_by(Notification.date_creation.desc()).offset(skip).limit(limit).all()
    return notifications


@router.post("/verifier")
def verifier_echeances(
    utilisateur: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Déclenchement manuel de la vérification des échéances proches
    return {"notifications_creees": notifier_echeances_proches(db)}


@router.put("/lire-tout", status_code=204)
def mark_all_read(
    utilisateur: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.utilisateur_id == utilisateur.id,
        Notification.lue == False
    ).update({Notification.lue: True})
    db.commit()
    return None


@router.put("/{notification_id}/lue", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    utilisateur: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.utilisateur_id == utilisateur.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")

    notification.lue = True
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    utilisateur: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.utilisateur_id == utilisateur.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")

    db.delete(notification)
    db.commit()
    return None
