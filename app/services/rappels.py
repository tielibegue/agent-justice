from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.echeance import Echeance
from app.models.notification import Notification
from app.models.utilisateur import Utilisateur
from app.services.email import envoyer_email

DELAI_RAPPEL_JOURS = 7


def notifier_echeances_proches(db: Session) -> int:
    """Crée une notification (et envoie un email) pour chaque échéance non accomplie
    arrivant dans les 7 jours, une seule fois par utilisateur et par échéance.
    Retourne le nombre de notifications créées."""
    maintenant = datetime.utcnow()
    limite = maintenant + timedelta(days=DELAI_RAPPEL_JOURS)

    echeances = db.query(Echeance).filter(
        Echeance.date_echeance >= maintenant,
        Echeance.date_echeance <= limite,
        Echeance.accomplie == False
    ).all()
    if not echeances:
        return 0

    utilisateurs = db.query(Utilisateur).filter(Utilisateur.est_actif == True).all()
    creees = 0

    for echeance in echeances:
        deja_notifies = {
            n.utilisateur_id for n in
            db.query(Notification.utilisateur_id).filter(Notification.echeance_id == echeance.id)
        }
        date_txt = echeance.date_echeance.strftime("%d/%m/%Y %H:%M")
        affaire = echeance.affaire
        titre = f"Échéance proche : {echeance.titre}"
        message = (
            f"L'échéance « {echeance.titre} » de l'affaire {affaire.numero} ({affaire.titre}) "
            f"arrive le {date_txt} (UTC)."
        )

        for utilisateur in utilisateurs:
            if utilisateur.id in deja_notifies:
                continue
            db.add(Notification(
                utilisateur_id=utilisateur.id,
                titre=titre,
                message=message,
                echeance_id=echeance.id
            ))
            # Commit avant l'envoi : un échec SMTP ne doit pas provoquer de doublons
            db.commit()
            creees += 1
            envoyer_email(
                utilisateur.email,
                f"[Agent-Justice] {titre}",
                f"Bonjour {utilisateur.username},\n\n{message}\n\n— Agent-Justice"
            )

    return creees
