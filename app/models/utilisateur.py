from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    est_actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relations
    notifications = relationship("Notification", back_populates="utilisateur", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Utilisateur {self.username}>"
