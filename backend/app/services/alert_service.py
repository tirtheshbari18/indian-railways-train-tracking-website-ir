from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from backend.app.models.alert import ServiceAlert
from backend.app.schemas.alert import ServiceAlertCreate, ServiceAlertUpdate

def get_active_alerts(
    db: Session,
    train_number: Optional[str] = None,
    station_code: Optional[str] = None,
    alert_type: Optional[str] = None,
    limit: int = 50
) -> List[ServiceAlert]:
    now = datetime.utcnow()
    q = db.query(ServiceAlert).filter(
        ServiceAlert.is_active == True,
        or_(ServiceAlert.active_to == None, ServiceAlert.active_to >= now)
    )

    if alert_type:
        q = q.filter(ServiceAlert.alert_type == alert_type.strip())

    alerts = q.order_by(ServiceAlert.created_at.desc()).limit(limit).all()

    # Filter by train or station if specified
    if train_number or station_code:
        filtered = []
        tn = train_number.strip().upper() if train_number else None
        sc = station_code.strip().upper() if station_code else None
        for a in alerts:
            match = False
            if tn and a.affected_train_numbers and tn in [x.upper() for x in a.affected_train_numbers]:
                match = True
            if sc and a.affected_station_codes and sc in [x.upper() for x in a.affected_station_codes]:
                match = True
            # If alert applies broadly (empty affected lists), include it as general notice
            if not a.affected_train_numbers and not a.affected_station_codes:
                match = True
            if match:
                filtered.append(a)
        return filtered

    return alerts

def get_alert_by_id(db: Session, alert_id: int) -> Optional[ServiceAlert]:
    return db.query(ServiceAlert).filter(ServiceAlert.id == alert_id).first()

def create_alert(db: Session, data: ServiceAlertCreate) -> ServiceAlert:
    alert = ServiceAlert(
        title=data.title.strip(),
        alert_type=data.alert_type,
        severity=data.severity,
        description=data.description.strip(),
        affected_train_numbers=data.affected_train_numbers or [],
        affected_station_codes=data.affected_station_codes or [],
        active_from=data.active_from or datetime.utcnow(),
        active_to=data.active_to,
        is_active=data.is_active
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def update_alert(db: Session, alert_id: int, data: ServiceAlertUpdate) -> ServiceAlert:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Service alert not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(alert, k, v)
    db.commit()
    db.refresh(alert)
    return alert

def delete_alert(db: Session, alert_id: int) -> bool:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Service alert not found")
    db.delete(alert)
    db.commit()
    return True
