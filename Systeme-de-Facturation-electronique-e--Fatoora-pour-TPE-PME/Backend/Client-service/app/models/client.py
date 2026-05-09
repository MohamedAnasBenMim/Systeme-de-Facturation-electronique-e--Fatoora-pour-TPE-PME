import enum
from sqlalchemy import Boolean, Column, Enum as SAEnum, Integer, String
from app.db.database import Base


class TypeClient(str, enum.Enum):
    PARTICULIER = "PARTICULIER"
    ENTREPRISE = "ENTREPRISE"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    telephone = Column(String(20), nullable=True, unique=True, index=True)
    adresse = Column(String(255), nullable=True)
    matricule_fiscal = Column(String(50), nullable=True, unique=True, index=True)
    type_client = Column(SAEnum(TypeClient), nullable=False, default=TypeClient.PARTICULIER, index=True)
    secteur = Column(String(100), nullable=True, index=True)
    tags = Column(String(255), nullable=True)  
    niveau = Column(String(20), nullable=False, default="STANDARD", index=True)  # STANDARD | VIP
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self):
        return f"<Client id={self.id} email={self.email}>"
