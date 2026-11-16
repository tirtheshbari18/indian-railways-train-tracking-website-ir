# RailTrack India | Indian Railways Live Train Tracking & Passenger Information Portal

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC.svg)](https://tailwindcss.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9+-199900.svg)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-Proprietary%20Portfolio-amber.svg)]()

> A portfolio-grade, production-quality Indian Railways train tracking and passenger information web application designed to demonstrate full-stack engineering, geospatial mapping, and data provenance capabilities relevant to organizations such as **CRIS** (Centre for Railway Information Systems), **RailTel Corporation of India**, and **RDSO** (Research Designs and Standards Organisation).

---

## 1. Executive Summary & Purpose

RailTrack India provides passenger-facing and administrative railway operations tools:
- **Instant Search**: Search by Train Number (e.g., `12951`, `22436`), Train Name (e.g., `Rajdhani`, `Vande Bharat`), Source/Destination station pairs (e.g., `MMCT` to `NDLS`), or passing junction.
- **Stop-by-Stop Route Timetable**: View sequential halts, arrival/departure schedules, scheduled halt durations, platform assignments, and day counts.
- **Geospatial Route Map**: Interactive Leaflet / OpenStreetMap mapping of the entire rail track with station markers, popups, and live train position tracking.
- **Station Live Telemetry Board**: Real-time arrival and departure boards for over 25+ major Indian junctions with platform confirmation badges.
- **Data Provenance & Ethical Disclosure**: Explicitly distinguishes **Verified NTES Telemetry**, **Demo Simulation Feeds**, and **Static Scheduled Timetables**. Adheres strictly to the rule: *Never fabricate live positions or platforms; show "Live Data Unavailable" when no verified provider feed exists*.
- **Admin Management Console**: Two-stage CSV/JSON bulk import engine with schema validation, error inspection, sample templates, and audit logging.

---

## 2. System Architecture

The application adopts a modular, decoupled full-stack architecture:

```
+------------------------------------------------------------------------+
|                     Client Tier (React 18 + Vite)                      |
|  - Tailwind CSS IR Theme (IR Navy Blue, Maroon, Saffron Amber)         |
|  - Interactive Leaflet Geospatial Maps & Route Polyline                |
|  - Role-Based Views (Passenger Portal & Administrator Console)         |
+-----------------------------------+------------------------------------+
                                    | REST API Calls (JWT Bearer Token)
                                    v
+------------------------------------------------------------------------+
|                     Backend Tier (Python FastAPI)                      |
|  - Pydantic v2 Input/Output Validation & Serialization                 |
|  - JWT Authentication & RBAC Authorization (Admin vs Passenger)        |
|  - SQLAlchemy 2.0 ORM with Dialect Support (SQLite / PostgreSQL)       |
|  - Alembic Schema Migrations                                           |
+-----------------------------------+------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+--------------------------------+          +--------------------------------+
|   Tracking Provider Adapter    |          |    Persistent Storage Tier     |
| - MockDemoProvider (Simulation)|          | - PostgreSQL 15 / SQLite 3     |
| - ExternalApiProvider (NTES)   |          | - Stations, Trains, Stops      |
| - NullProvider (Offline/None)  |          | - Service Alerts & Audit Trail |
+--------------------------------+          +--------------------------------+
```

### Pluggable Tracking Provider Interface

```python
class TrainTrackingProvider(ABC):
    @abstractmethod
    def get_live_status(self, train: Train, stops: List[Stop], journey_date: Optional[str]) -> LiveStatusResponse:
        pass
    
    @abstractmethod
    def get_station_live_board(self, station: Station, stops: List[Stop]) -> Dict[str, List[StationLiveBoardItem]]:
        pass
```

1. **`MockDemoProvider`**: Generates realistic telemetry (speed, halt delay, GPS track interpolation) for portfolio showcase. Explicitly tagged as `demo_simulation`.
2. **`ExternalApiProvider`**: Connects to official or licensed Indian Railways APIs (CRIS NTES, RailTel Open Data, RapidAPI IRCTC). Tagged as `verified_live_feed`.
3. **`NullProvider`**: Activated when no live gateway is configured. Returns static scheduled timetables and explicitly tags status as `unavailable` with zero fabricated telemetry.

---

## 3. Database Schema

The database is designed with high normalization, foreign key constraints, and performance indexes:

| Table | Description | Key Columns |
|---|---|---|
| `users` | User accounts and credentials | `id` (PK), `username` (UK), `email` (UK), `hashed_password`, `role` (`admin`/`passenger`), `is_active`, `created_at` |
| `stations` | Indian Railways station network | `code` (PK, e.g. `NDLS`), `name`, `division`, `zone` (e.g. `NR`, `WR`), `state`, `latitude`, `longitude`, `platforms_count` |
| `trains` | Express and passenger train services | `id` (PK), `train_number` (UK), `train_name`, `train_type`, `source_station_code` (FK), `destination_station_code` (FK), `running_days`, `total_distance_km`, `duration_minutes`, `classes` (JSON), `pantry_car` (bool) |
| `stops` | Sequential timetable stop sequence | `id` (PK), `train_id` (FK), `station_code` (FK), `stop_sequence`, `arrival_time`, `departure_time`, `halt_minutes`, `distance_km`, `day_number`, `platform`, Unique(`train_id`, `stop_sequence`) |
| `service_alerts`| Network disruptions & advisories | `id` (PK), `title`, `alert_type`, `severity`, `description`, `affected_train_numbers` (JSON), `affected_station_codes` (JSON), `active_from`, `active_to`, `is_active` |
| `audit_logs` | Operations and import security log | `id` (PK), `user_id` (FK), `username`, `action`, `entity_type`, `entity_id`, `details` (JSON), `ip_address`, `created_at` |
| `saved_trains` | Passenger bookmark preferences | `id` (PK), `user_id` (FK), `train_id` (FK), Unique(`user_id`, `train_id`) |

---

## 4. REST API Endpoints

### Authentication & Profile (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Register passenger account
- `POST /api/v1/auth/login` — OAuth2 password form login
- `POST /api/v1/auth/login/json` — JSON body login (returns JWT token)
- `GET /api/v1/auth/me` — Authenticated profile and role check

### Trains & Schedules (`/api/v1/trains`)
- `GET /api/v1/trains` — Paginated search with filters (`query`, `source`, `destination`, `station`, `train_type`, `day`, `page`, `limit`)
- `GET /api/v1/trains/{train_number}` — Complete train overview with ordered timetable halts
- `POST /api/v1/trains` — Create train (Admin only)
- `PUT /api/v1/trains/{train_number}` — Update train metadata (Admin only)
- `DELETE /api/v1/trains/{train_number}` — Delete train (Admin only)

### Stations & Live Boards (`/api/v1/stations`)
- `GET /api/v1/stations` — Search stations with query, zone (`NR`, `WR`, `CR`, etc.), and state
- `GET /api/v1/stations/{station_code}` — Station details and platform counts
- `GET /api/v1/stations/{station_code}/live-board` — Real-time arrivals & departures board with platform sourcing

### Live Telemetry Tracking (`/api/v1/tracking`)
- `GET /api/v1/tracking/train/{train_number}/live` — Live status, delay, speed, and GPS coordinates
- `GET /api/v1/tracking/provider-info` — Active tracking provider metadata and feed state

### Service Alerts & Advisories (`/api/v1/alerts`)
- `GET /api/v1/alerts` — Active bulletins (fog speed limits, track work, special rakes)
- `POST /api/v1/alerts` — Publish new operational advisory (Admin only)

### Admin Console & Bulk Ingestion (`/api/v1/admin`)
- `GET /api/v1/admin/stats` — Operations KPI metrics
- `POST /api/v1/admin/import/validate` — Stage 1 dry-run CSV/JSON validator
- `POST /api/v1/admin/import/execute` — Stage 2 atomic database ingestion with audit log entry
- `GET /api/v1/admin/import/template/{entity}` — Download sample CSV or JSON templates
- `GET /api/v1/admin/audit-logs` — Audit log history

---

## 5. Seeded Showcase Data

The application comes pre-loaded with realistic Indian Railways records:
- **25 Major Junctions**: `NDLS` (New Delhi), `MMCT` (Mumbai Central), `CSMT` (Mumbai CSMT), `HWH` (Howrah), `MAS` (Chennai Central), `SBC` (Bengaluru), `PNBE` (Patna), `GKP` (Gorakhpur), `BSB` (Varanasi), `CNB` (Kanpur Central), `AGC` (Agra Cantt), `BPL` (Bhopal), `RKMP` (Rani Kamlapati), `BRC` (Vadodara), `ST` (Surat), `KOTA` (Kota), `RTM` (Ratlam), `ADI` (Ahmedabad), `PRYJ` (Prayagraj), `DDU` (Deen Dayal Upadhyaya), `MYS` (Mysuru), `TVC` (Thiruvananthapuram).
- **Flagship Express Trains**:
  - `12951 / 12952`: Mumbai Tejas Rajdhani Express (`MMCT` <-> `NDLS` via `ST`, `BRC`, `RTM`, `KOTA`)
  - `22436 / 22435`: Vande Bharat Express (`NDLS` <-> `BSB` via `CNB`, `PRYJ`)
  - `12002`: New Delhi - Rani Kamlapati (Bhopal) Shatabdi Express (`NDLS` <-> `RKMP` via `AGC`, `GWL`, `VGLJ`, `BPL`)
  - `12301`: Howrah - New Delhi Rajdhani Express (via `Gaya`, `DDU`, `PRYJ`, `CNB`)
  - `20607`: Chennai - Mysuru Vande Bharat Express (`MAS` <-> `MYS` via `KJM`, `SBC`)
  - `12009`: Mumbai - Ahmedabad Shatabdi Express (`MMCT` <-> `ADI` via `BVI`, `ST`, `BRC`)

---

## 6. Local Setup & Execution Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### Windows PowerShell Quickstart (Out-of-the-Box)

#### 1. Configure Environment
```powershell
# Copy environment configuration
Copy-Item .env.example .env
```

#### 2. Run Database Seeding & Pytest Test Suite
```powershell
# Initialize and seed database
python -m backend.app.seeds.seed_data

# Execute unit and integration tests (17 tests)
python -m pytest backend/tests -v
```

#### 3. Run FastAPI Backend
```powershell
# Start FastAPI application on port 8000
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger Documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 4. Run Vite Frontend Development Server (In a separate terminal)
```powershell
cd frontend
npm run dev
```
Open your browser at: [http://localhost:5173](http://localhost:5173)

*(Note: Since the production build is also pre-compiled into `frontend/dist`, visiting [http://127.0.0.1:8000](http://127.0.0.1:8000) will directly serve the full application through FastAPI even without Vite running!)*

---

## 7. Pre-Configured Demo Credentials

For instant evaluator sign-in, use the one-click demo login buttons on the `/login` screen or the following credentials:

| Role | Username | Password | Privileges |
|---|---|---|---|
| **Administrator** | `admin` | `RailAdmin@2026` | Full administrative console, CSV/JSON bulk import, broadcast service alerts, view security audit trails |
| **Passenger** | `passenger` | `Passenger@2026` | Public tracking, station live boards, route timeline, bookmark/save favourite trains |

---

## 8. Docker Deployment

To launch the multi-container stack with PostgreSQL, FastAPI, and Nginx:

```bash
docker-compose up --build -d
```
- **Web App**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: Port `5432`

---

## 9. CSV & JSON Import Specifications

Sample template files are provided in `sample_data/`:
1. `stations_sample.csv` / `stations_sample.json`
2. `trains_sample.csv` / `trains_sample.json`
3. `timetables_sample.csv` / `timetables_sample.json`

### Import Rules & Integrity
- **Stage 1 (Validation)**: Performs row-by-row checks without committing. Validates coordinates ($\text{lat} \in [-90, 90]$, $\text{lng} \in [-180, 180]$), 24-hour time formats (`HH:MM`), station code existence, and sequence uniqueness. Returns detailed row-level errors and previews.
- **Stage 2 (Execution)**: Upserts records in an atomic transaction and automatically logs an audit event (`IMPORT_STATIONS`, `IMPORT_TRAINS`, `IMPORT_TIMETABLES`) with the admin user ID and client IP address.

---

## 10. Limitations & Future Roadmap

### Current Limitations
- Live GPS tracking for demo trains is generated by `MockDemoProvider` using deterministic telemetry (since official CRIS NTES production feeds require secure VPN peering within Indian Railways intranet).
- Platform numbers are displayed with explicit source indicators (`Scheduled`, `Verified Live`, `Estimated`).

### Future Roadmap
1. **Direct RailTel / CRIS NTES Gateway Integration**: Complete HTTPS mutual TLS certificate handshake adapter for live production streams.
2. **Coach Layout & Rake Composition**: Dynamic display of locomotive, luggage vans, and coach sequence (e.g., LHB rake sequence `H1-A1-A2-B1...`).
3. **PNR Status Verification Adapter**: Integration with IRCTC reservation inquiry systems.
4. **Offline Mobile PWA**: IndexedDB caching of static timetables for passengers with limited connectivity onboard trains.
