from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    message: str

class NotificationUpdate(BaseModel):
    lu: Optional[bool] = None

class NotificationResponse(BaseModel):
    id: int
    message: str
    dateEnvoi: datetime
    lu: bool

    class Config:
        from_attributes = True