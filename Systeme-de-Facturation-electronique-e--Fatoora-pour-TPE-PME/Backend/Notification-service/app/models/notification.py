from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.database import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(String(255), nullable=False)
    dateEnvoi = Column(DateTime, default=datetime.utcnow)
    lu = Column(Boolean, default=False)