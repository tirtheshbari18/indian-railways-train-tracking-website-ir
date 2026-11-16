from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from backend.app.database import Base

class ServiceAlert(Base):
    __tablename__ = "service_alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False, default="maintenance")  # "delay", "cancellation", "diversion", "special", "fog"
    severity = Column(String(20), nullable=False, default="warning")        # "info", "warning", "critical"
    description = Column(Text, nullable=False)
    affected_train_numbers = Column(JSON, nullable=True, default=list)      # ["12951", "12002"]
    affected_station_codes = Column(JSON, nullable=True, default=list)      # ["NDLS", "CNB"]
    active_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    active_to = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
