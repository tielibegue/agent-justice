from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    lue = Column(Boolean, default=False)
    # Échéance à l'origine de la notification (évite les rappels en double)
    echeance_id = Column(Integer, ForeignKey("echeances.id"), nullable=True, index=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relations
    utilisateur = relationship("Utilisateur", back_populates="notifications")
    echeance = relationship("Echeance", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.titre}>"
