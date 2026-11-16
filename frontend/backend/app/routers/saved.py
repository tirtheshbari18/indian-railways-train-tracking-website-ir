from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.saved import SavedTrain
from backend.app.models.train import Train
from backend.app.schemas.train import TrainResponse
from backend.app.services.auth import require_current_user

router = APIRouter(prefix="/saved-trains", tags=["Saved Trains"])

@router.get("", response_model=List[TrainResponse])
def get_user_saved_trains(db: Session = Depends(get_db), current_user: User = Depends(require_current_user)):
    saved = (
        db.query(SavedTrain)
        .filter(SavedTrain.user_id == current_user.id)
        .join(Train, SavedTrain.train_id == Train.id)
        .options(
            joinedload(SavedTrain.train).joinedload(Train.source_station),
            joinedload(SavedTrain.train).joinedload(Train.destination_station)
        )
        .all()
    )
    return [s.train for s in saved if s.train]

@router.post("/{train_number}", status_code=status.HTTP_201_CREATED)
def save_train(train_number: str, db: Session = Depends(get_db), current_user: User = Depends(require_current_user)):
    num = train_number.strip().upper()
    train = db.query(Train).filter(Train.train_number == num).first()
    if not train:
        raise HTTPException(status_code=404, detail=f"Train '{train_number}' not found.")

    existing = db.query(SavedTrain).filter(SavedTrain.user_id == current_user.id, SavedTrain.train_id == train.id).first()
    if existing:
        return {"message": "Train already in saved list", "train_number": num}

    saved = SavedTrain(user_id=current_user.id, train_id=train.id)
    db.add(saved)
    db.commit()
    return {"message": "Train saved successfully", "train_number": num}

@router.delete("/{train_number}")
def unsave_train(train_number: str, db: Session = Depends(get_db), current_user: User = Depends(require_current_user)):
    num = train_number.strip().upper()
    train = db.query(Train).filter(Train.train_number == num).first()
    if not train:
        raise HTTPException(status_code=404, detail=f"Train '{train_number}' not found.")

    saved = db.query(SavedTrain).filter(SavedTrain.user_id == current_user.id, SavedTrain.train_id == train.id).first()
    if saved:
        db.delete(saved)
        db.commit()
    return {"message": "Train removed from saved list", "train_number": num}
