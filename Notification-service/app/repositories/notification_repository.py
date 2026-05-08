from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.models.notification import Notification
from app.schemas.notification_schema import NotificationCreate
from datetime import datetime, timezone

class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[Notification]:
        return self.db.query(Notification).order_by(Notification.dateEnvoi.desc()).all()

    def find_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def find_non_lues(self) -> list[Notification]:
        return self.db.query(Notification).filter(Notification.lu == False).all()

    def save(self, notification: NotificationCreate) -> Notification:
        db_notification = Notification(
            message=notification.message,
            dateEnvoi=datetime.now(timezone.utc),
            lu=False
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def update_lu(self, notification: Notification) -> Notification:
        notification.lu = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def delete(self, notification: Notification) -> None:
        self.db.delete(notification)
        self.db.commit()