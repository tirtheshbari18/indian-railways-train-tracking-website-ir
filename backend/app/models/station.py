from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from backend.app.database import Base

class Station(Base):
    __tablename__ = "stations"

    code = Column(String(10), primary_key=True, index=True)  # e.g. "NDLS"
    name = Column(String(100), nullable=False, index=True)    # e.g. "New Delhi"
    division = Column(String(50), nullable=True)             # e.g. "Delhi"
    zone = Column(String(20), nullable=True, index=True)     # e.g. "NR", "WR", "CR"
    state = Column(String(50), nullable=True)                # e.g. "Delhi"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    platforms_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
