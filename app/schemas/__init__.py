from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# Schémas Client
class ClientBase(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    adresse: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True


class ClientWithAffaires(ClientResponse):
    affaires: List["AffaireResponse"] = []


# Schémas Affaire
class AffaireBase(BaseModel):
    numero: str
    titre: str
    description: Optional[str] = None
    client_id: int


class AffaireCreate(AffaireBase):
    pass


class AffaireUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    client_id: Optional[int] = None


class AffaireResponse(AffaireBase):
    id: int
    statut: str
    date_ouverture: datetime
    date_cloture: Optional[datetime] = None
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True


class AffaireWithEcheances(AffaireResponse):
    echeances: List["EcheanceResponse"] = []


# Schémas Echeance
class EcheanceBase(BaseModel):
    titre: str
    description: Optional[str] = None
    date_echeance: datetime
    affaire_id: int


class EcheanceCreate(EcheanceBase):
    pass


class EcheanceUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    date_echeance: Optional[datetime] = None
    accomplie: Optional[bool] = None


class EcheanceResponse(EcheanceBase):
    id: int
    accomplie: bool
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True


# Schémas Document
class DocumentUpdate(BaseModel):
    nom: Optional[str] = None
    affaire_id: Optional[int] = None


class DocumentResponse(BaseModel):
    id: int
    nom: str
    type_mime: Optional[str] = None
    taille: int
    affaire_id: int
    date_creation: datetime

    class Config:
        from_attributes = True


# Schémas Utilisateur
class UtilisateurCreate(BaseModel):
    username: str
    email: str
    password: str


class UtilisateurResponse(BaseModel):
    id: int
    username: str
    email: str
    est_actif: bool
    date_creation: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schémas Notification
class NotificationResponse(BaseModel):
    id: int
    titre: str
    message: str
    lue: bool
    echeance_id: Optional[int] = None
    date_creation: datetime

    class Config:
        from_attributes = True


# Résoudre les références circulaires
ClientWithAffaires.model_rebuild()
AffaireWithEcheances.model_rebuild()
