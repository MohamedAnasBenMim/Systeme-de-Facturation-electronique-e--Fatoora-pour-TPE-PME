from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification_schema import NotificationCreate, NotificationResponse
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)

@router.get("/", response_model=List[NotificationResponse])
def get_all(service: NotificationService = Depends(get_service)):
    return service.get_all()

@router.get("/non-lues", response_model=List[NotificationResponse])
def get_non_lues(service: NotificationService = Depends(get_service)):
    return service.get_non_lues()

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_by_id(notification_id: int, service: NotificationService = Depends(get_service)):
    return service.get_by_id(notification_id)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create(payload: NotificationCreate, service: NotificationService = Depends(get_service)):
    return service.create(payload)

@router.put("/{notification_id}/lire", response_model=NotificationResponse)
def marquer_comme_lue(notification_id: int, service: NotificationService = Depends(get_service)):
    return service.marquer_comme_lue(notification_id)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(notification_id: int, service: NotificationService = Depends(get_service)):
    service.delete(notification_id)