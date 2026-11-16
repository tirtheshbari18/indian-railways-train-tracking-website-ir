import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.routers import auth, trains, stations, tracking, alerts, admin, saved
from backend.app.seeds.seed_data import seed_database
from backend.app.models.station import Station

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if database needs seeding
        count = db.query(Station).count()
        if count == 0:
            seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# Indian Railways Train Tracking & Passenger Information System API
Architecture built for enterprise railway operational monitoring inspired by CRIS (Centre for Railway Information Systems) and RailTel.

### Key Capabilities:
- **Train Schedules & Timetables**: Search by Train Number, Name, Route (Source to Destination), or passing station.
- **Station Live Boards**: Real-time arrival and departure telemetry with platform sourcing and delay metrics.
- **Interactive Route Tracking**: Stop-by-stop sequencing, geospatial coordinates, and live GPS estimation.
- **Provider Adapter Architecture**: Pluggable support for Simulated Feeds, External NTES/RailTel REST APIs, and strict Null/Unavailable fallback.
- **Admin Management Console**: Bulk CSV/JSON import with 2-step validation, audit logging, and service alert broadcasting.
- **RBAC Security**: JWT tokens with Passenger and Admin roles.
    """,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers with both /api/v1 and /v1 for Vercel Serverless compatibility
for prefix in [settings.API_V1_STR, "/v1"]:
    app.include_router(auth.router, prefix=prefix)
    app.include_router(trains.router, prefix=prefix)
    app.include_router(stations.router, prefix=prefix)
    app.include_router(tracking.router, prefix=prefix)
    app.include_router(alerts.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
    app.include_router(saved.router, prefix=prefix)

@app.get("/api/health", tags=["System Health"])
@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": settings.DATABASE_URL.split("://")[0],
        "active_provider": settings.TRACKING_PROVIDER
    }

@app.get("/api", tags=["System Info"])
def api_info():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "health": "/api/health",
            "trains": "/api/v1/trains",
            "stations": "/api/v1/stations",
            "tracking": "/api/v1/tracking",
            "alerts": "/api/v1/alerts",
            "admin": "/api/v1/admin"
        }
    }

# Mount static frontend build if present (checks both root 'dist' and 'frontend/dist')
root_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dist"))
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
dist_path = root_dist if os.path.exists(root_dist) else (frontend_dist if os.path.exists(frontend_dist) else None)

if dist_path and os.path.exists(dist_path):
    assets_dir = os.path.join(dist_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Don't intercept API routes or docs
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_candidate = os.path.join(dist_path, full_path)
        if os.path.isfile(file_candidate):
            return FileResponse(file_candidate)
        return FileResponse(os.path.join(dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
