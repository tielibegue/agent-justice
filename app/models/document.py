from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Integer as SqlInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False)
    chemin_fichier = Column(String(500), nullable=False)
    type_mime = Column(String(100))
    taille = Column(SqlInteger)  # en bytes
    affaire_id = Column(Integer, ForeignKey("affaires.id"), nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # Relations
    affaire = relationship("Affaire", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.nom}>"
