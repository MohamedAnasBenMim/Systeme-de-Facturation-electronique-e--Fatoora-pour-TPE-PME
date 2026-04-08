from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role     = Column(String(50), default="USER")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    