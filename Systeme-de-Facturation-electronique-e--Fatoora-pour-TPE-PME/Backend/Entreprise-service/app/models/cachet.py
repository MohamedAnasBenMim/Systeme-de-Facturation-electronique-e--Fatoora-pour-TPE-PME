
import uuid
from sqlalchemy import Column, String, ForeignKey, LargeBinary, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Cachet(Base):
    __tablename__ = "cachets"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)
    image_data   = Column(LargeBinary, nullable=False)        # image stockée en binaire
    image_mime   = Column(String(50), nullable=False)         # ex: image/png
    nom          = Column(String(100), nullable=True)         # label optionnel
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    entreprise = relationship("Entreprise", back_populates="cachet")
