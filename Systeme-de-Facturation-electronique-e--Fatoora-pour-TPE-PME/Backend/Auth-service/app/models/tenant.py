import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan       = Column(String, default="starter")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)