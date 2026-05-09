from sqlalchemy import Column, Integer, String
from app.db.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    matricule_fiscal = Column(String(50), nullable=True, unique=True, index=True)

    def __repr__(self):
        return f"<Client id={self.id} email={self.email}>"