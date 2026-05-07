from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.db.database import Base

class CompteurDocument(Base):
    __tablename__ = "compteurs_documents"

    id             = Column(Integer, primary_key=True, index=True)
    type_doc       = Column(String(10), nullable=False)   # DEV | BC | BL | FAC
    annee          = Column(Integer, nullable=False)
    dernier_numero = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("type_doc", "annee", name="uq_compteur_type_annee"),
    )