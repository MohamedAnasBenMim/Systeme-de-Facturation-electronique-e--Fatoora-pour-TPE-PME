from sqlalchemy.orm import Session
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification_schema import NotificationCreate, NotificationResponse
from app.exceptions.http_exceptions import NotificationNotFoundException
from typing import List

class NotificationService:

    def __init__(self, db: Session):
        self.repository = NotificationRepository(db)

    def get_all(self) -> List[NotificationResponse]:
        return self.repository.find_all()

    def get_by_id(self, notification_id: int) -> NotificationResponse:
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(notification_id)
        return notification

    def get_non_lues(self) -> List[NotificationResponse]:
        return self.repository.find_non_lues()

    def create(self, notification: NotificationCreate) -> NotificationResponse:
        return self.repository.save(notification)

    def marquer_comme_lue(self, notification_id: int) -> NotificationResponse:
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(notification_id)
        return self.repository.update_lu(notification)

    def delete(self, notification_id: int) -> None:
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(notification_id)
        self.repository.delete(notification)