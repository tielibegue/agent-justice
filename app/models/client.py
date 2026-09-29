from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True)
    telephone = Column(String(20))
    adresse = Column(Text)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    affaires = relationship("Affaire", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.prenom} {self.nom}>"
