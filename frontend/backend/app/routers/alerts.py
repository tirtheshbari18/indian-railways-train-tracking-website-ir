from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.alert import ServiceAlertResponse, ServiceAlertCreate, ServiceAlertUpdate
from backend.app.services.alert_service import (
    get_active_alerts,
    get_alert_by_id,
    create_alert,
    update_alert,
    delete_alert
)
from backend.app.services.auth import require_admin_user
from backend.app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Service Alerts"])

@router.get("", response_model=List[ServiceAlertResponse])
def list_alerts(
    train_number: Optional[str] = Query(None, description="Filter by affected train number"),
    station_code: Optional[str] = Query(None, description="Filter by affected station code"),
    alert_type: Optional[str] = Query(None, description="delay, cancellation, diversion, weather, etc."),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_active_alerts(
        db,
        train_number=train_number,
        station_code=station_code,
        alert_type=alert_type,
        limit=limit
    )

@router.get("/{alert_id}", response_model=ServiceAlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("", response_model=ServiceAlertResponse, status_code=status.HTTP_201_CREATED)
def post_alert(
    alert_in: ServiceAlertCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return create_alert(db, alert_in)

@router.put("/{alert_id}", response_model=ServiceAlertResponse)
def put_alert(
    alert_id: int,
    alert_in: ServiceAlertUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return update_alert(db, alert_id, alert_in)

@router.delete("/{alert_id}")
def remove_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    delete_alert(db, alert_id)
    return {"message": f"Alert {alert_id} deleted."}
