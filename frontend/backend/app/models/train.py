from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(10), unique=True, index=True, nullable=False)  # e.g. "12951"
    train_name = Column(String(150), nullable=False, index=True)               # e.g. "Mumbai Tejas Rajdhani Express"
    train_type = Column(String(50), nullable=False, default="Superfast")       # "Rajdhani", "Vande Bharat", etc.
    source_station_code = Column(String(10), ForeignKey("stations.code"), nullable=False, index=True)
    destination_station_code = Column(String(10), ForeignKey("stations.code"), nullable=False, index=True)
    running_days = Column(String(20), nullable=False, default="1111111")        # "Mon,Tue,Wed..." or "1111111"
    total_distance_km = Column(Float, nullable=False, default=0.0)
    duration_minutes = Column(Integer, nullable=False, default=0)
    classes = Column(JSON, nullable=True, default=list)                         # ["1A", "2A", "3A"]
    pantry_car = Column(Boolean, default=True)
    return_train_number = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_station = relationship("Station", foreign_keys=[source_station_code])
    destination_station = relationship("Station", foreign_keys=[destination_station_code])
    stops = relationship("Stop", back_populates="train", order_by="Stop.stop_sequence", cascade="all, delete-orphan")
