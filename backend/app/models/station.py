from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from backend.app.database import Base

class Station(Base):
    __tablename__ = "stations"

    code = Column(String(10), primary_key=True, index=True)  # e.g. "NDLS"
    name = Column(String(100), nullable=False, index=True)    # e.g. "New Delhi"
    state = Column(String(50), nullable=True)                # e.g. "Delhi", "Maharashtra"
    district = Column(String(50), nullable=True)             # e.g. "Palghar", "Mumbai Suburban"
    division = Column(String(50), nullable=True, index=True) # e.g. "Mumbai WR", "Delhi"
    zone = Column(String(20), nullable=True, index=True)     # e.g. "WR", "CR", "NR"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String(30), default="Regular", index=True)  # "Junction", "Terminal", "Suburban", "Regular", "Halt"
    platforms_count = Column(Integer, default=1)
    facilities = Column(JSON, nullable=True, default=list)   # ["Waiting Room", "Wi-Fi", "Food Court"]
    operational_status = Column(String(20), default="Operational") # "Operational", "Remodeling"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
