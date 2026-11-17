from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.train import (
    TrainResponse,
    TrainDetailResponse,
    TrainCreate,
    TrainUpdate
)
from backend.app.services.train_service import (
    search_trains,
    get_train_by_number,
    create_train,
    update_train,
    delete_train
)
from backend.app.services.auth import require_admin_user
from backend.app.models.user import User

router = APIRouter(prefix="/trains", tags=["Trains"])

@router.get("")
def get_trains(
    query: Optional[str] = Query(None, description="Search by train number, name, or 'Source to Dest'"),
    source: Optional[str] = Query(None, description="Source station code or name"),
    destination: Optional[str] = Query(None, description="Destination station code or name"),
    station: Optional[str] = Query(None, description="Passing/halting station code or name"),
    train_type: Optional[str] = Query(None, description="Rajdhani, Vande Bharat, Shatabdi, etc."),
    category: Optional[str] = Query(None, description="MEMU, DEMU, Local, Superfast, Express, Passenger, Special, etc."),
    day: Optional[str] = Query(None, description="Running day e.g. Mon, Tue"),
    is_special: Optional[bool] = Query(None, description="Filter festival/holiday special trains"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    trains, total = search_trains(
        db,
        query=query,
        source=source,
        destination=destination,
        station=station,
        train_type=train_type,
        category=category,
        day=day,
        is_special=is_special,
        limit=limit,
        offset=offset
    )
    items = [TrainResponse.model_validate(t) for t in trains]
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1
    }

@router.get("/{train_number}", response_model=TrainDetailResponse)
def get_train(train_number: str, db: Session = Depends(get_db)):
    train = get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train '{train_number}' not found.")
    return train

@router.post("", response_model=TrainDetailResponse, status_code=status.HTTP_201_CREATED)
def add_train(
    train_in: TrainCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return create_train(db, train_in)

@router.put("/{train_number}", response_model=TrainDetailResponse)
def edit_train(
    train_number: str,
    train_in: TrainUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return update_train(db, train_number, train_in)

@router.delete("/{train_number}")
def remove_train(
    train_number: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    delete_train(db, train_number)
    return {"message": f"Train '{train_number}' deleted successfully."}
