from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Echeance(Base):
    __tablename__ = "echeances"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    date_echeance = Column(DateTime, nullable=False)
    accomplie = Column(Boolean, default=False)
    affaire_id = Column(Integer, ForeignKey("affaires.id"), nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    affaire = relationship("Affaire", back_populates="echeances")
    notifications = relationship("Notification", back_populates="echeance", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Echeance {self.titre} - {self.date_echeance}>"
