import sys
import os

# Ensure project root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Indicate Vercel environment
os.environ["VERCEL"] = "1"

# Import the FastAPI application
from backend.app.main import app

# Ensure database tables and initial seed data exist upon serverless cold start
try:
    from backend.app.database import engine, Base, SessionLocal
    from backend.app.seeds.seed_data import seed_database
    from backend.app.models.station import Station

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Station).count()
        if count == 0:
            seed_database(db)
    finally:
        db.close()
except Exception as e:
    print(f"Warning during cold-start database init: {e}")
