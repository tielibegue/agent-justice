from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.client import Client
from app.models.affaire import Affaire, StatutAffaire
from app.models.echeance import Echeance
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    # Statistiques des clients
    total_clients = db.query(Client).count()
    
    # Statistiques des affaires
    total_affaires = db.query(Affaire).count()
    affaires_par_statut = {}
    for statut in StatutAffaire:
        count = db.query(Affaire).filter(Affaire.statut == statut).count()
        affaires_par_statut[statut.value] = count
    
    # Statistiques des échéances
    total_echeances = db.query(Echeance).count()
    echeances_accomplies = db.query(Echeance).filter(Echeance.accomplie == True).count()
    echeances_en_attente = db.query(Echeance).filter(Echeance.accomplie == False).count()
    
    # Échéances prochains 7 jours
    maintenant = datetime.utcnow()
    dans_7_jours = maintenant + timedelta(days=7)
    echeances_proches = db.query(Echeance).filter(
        Echeance.date_echeance >= maintenant,
        Echeance.date_echeance <= dans_7_jours,
        Echeance.accomplie == False
    ).count()
    
    # Échéances en retard
    echeances_en_retard = db.query(Echeance).filter(
        Echeance.date_echeance < maintenant,
        Echeance.accomplie == False
    ).count()
    
    # Échéances à venir (30 jours)
    dans_30_jours = maintenant + timedelta(days=30)
    echeances_30_jours = db.query(Echeance).filter(
        Echeance.date_echeance >= maintenant,
        Echeance.date_echeance <= dans_30_jours,
        Echeance.accomplie == False
    ).all()
    
    # Dernières affaires créées
    dernieres_affaires = db.query(Affaire).order_by(Affaire.date_creation.desc()).limit(5).all()
    
    # Derniers clients
    derniers_clients = db.query(Client).order_by(Client.date_creation.desc()).limit(5).all()
    
    return {
        "clients": {
            "total": total_clients
        },
        "affaires": {
            "total": total_affaires,
            "par_statut": affaires_par_statut
        },
        "echeances": {
            "total": total_echeances,
            "accomplies": echeances_accomplies,
            "en_attente": echeances_en_attente,
            "prochaines_7_jours": echeances_proches,
            "en_retard": echeances_en_retard
        },
        "echeances_30_jours": [
            {
                "id": e.id,
                "titre": e.titre,
                "date_echeance": e.date_echeance.isoformat(),
                "affaire_id": e.affaire_id
            }
            for e in echeances_30_jours
        ],
        "dernieres_affaires": [
            {
                "id": a.id,
                "numero": a.numero,
                "titre": a.titre,
                "statut": a.statut.value,
                "date_ouverture": a.date_ouverture.isoformat()
            }
            for a in dernieres_affaires
        ],
        "derniers_clients": [
            {
                "id": c.id,
                "nom": c.nom,
                "prenom": c.prenom,
                "email": c.email
            }
            for c in derniers_clients
        ]
    }
