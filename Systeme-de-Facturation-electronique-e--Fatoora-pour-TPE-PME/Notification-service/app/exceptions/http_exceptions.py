from fastapi import HTTPException, status

class NotificationNotFoundException(HTTPException):
    def __init__(self, notification_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification avec l'id '{notification_id}' introuvable"
        )

class NotificationCreateException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la création de la notification"
        )