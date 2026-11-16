from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Stop(Base):
    __tablename__ = "stops"
    __table_args__ = (
        UniqueConstraint("train_id", "stop_sequence", name="uq_train_stop_sequence"),
    )

    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id", ondelete="CASCADE"), nullable=False, index=True)
    station_code = Column(String(10), ForeignKey("stations.code"), nullable=False, index=True)
    stop_sequence = Column(Integer, nullable=False)               # 1, 2, 3...
    arrival_time = Column(String(10), nullable=True)             # "HH:MM" e.g. "16:55", null for origin
    departure_time = Column(String(10), nullable=True)           # "HH:MM" e.g. "17:00", null for destination
    halt_minutes = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    day_number = Column(Integer, default=1)
    platform = Column(String(10), nullable=True)                 # Scheduled platform e.g. "1", "16"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    train = relationship("Train", back_populates="stops")
    station = relationship("Station")
