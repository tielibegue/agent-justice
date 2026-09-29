from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class StatutAffaire(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    SUSPENDUE = "suspendue"
    CLOTUREE = "cloturee"


class Affaire(Base):
    __tablename__ = "affaires"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    statut = Column(Enum(StatutAffaire), default=StatutAffaire.OUVERTE)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    date_ouverture = Column(DateTime, default=datetime.utcnow)
    date_cloture = Column(DateTime, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    client = relationship("Client", back_populates="affaires")
    echeances = relationship("Echeance", back_populates="affaire", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="affaire", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="affaire", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Affaire {self.numero}: {self.titre}>"
