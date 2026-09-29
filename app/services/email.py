import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

# Configuration SMTP via variables d'environnement
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "agent-justice@localhost")
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() in ("1", "true", "yes")


def email_configure() -> bool:
    return bool(SMTP_HOST)


def envoyer_email(destinataire: str, sujet: str, contenu: str) -> bool:
    """Envoie un email texte. Retourne False si SMTP n'est pas configuré ou en cas d'échec."""
    if not email_configure():
        logger.info("SMTP non configuré, email non envoyé à %s : %s", destinataire, sujet)
        return False

    message = EmailMessage()
    message["From"] = SMTP_FROM
    message["To"] = destinataire
    message["Subject"] = sujet
    message.set_content(contenu)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            if SMTP_TLS:
                smtp.starttls()
            if SMTP_USER:
                smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(message)
        return True
    except (smtplib.SMTPException, OSError) as e:
        logger.error("Échec de l'envoi de l'email à %s : %s", destinataire, e)
        return False
