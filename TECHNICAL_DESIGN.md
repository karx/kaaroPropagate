# Comet Trajectory Visualization System - Technical Design

## Project Overview
Interactive 3D solar system viewer for visualizing comet trajectories using real astronomical data.

## Technical Stack

### Backend & Computation (Python)

#### Core Libraries
- **Python 3.10+**: Primary language for data processing and orbital mechanics
- **NumPy**: Numerical computations and array operations
- **Poliastro**: Orbital mechanics library for propagation and coordinate transformations
- **Astropy**: Astronomical calculations, time handling, and coordinate systems
- **SPICEYPY**: Python wrapper for NASA's SPICE toolkit (JPL ephemeris data)

#### Data Processing
- **Pandas**: Data manipulation and CSV/text file parsing
- **Requests**: HTTP client for downloading data from MPC and JPL
- **BeautifulSoup4**: HTML parsing if needed for web scraping

### Frontend & Visualization

#### Option A: Web-Based (Recommended for MVP)
- **Three.js**: WebGL-based 3D rendering library
- **React**: UI framework for controls and information panels
- **FastAPI**: Python backend API server
- **WebSocket**: Real-time data streaming for trajectory updates

#### Option B: Desktop Application
- **PyQt6** or **Tkinter**: GUI framework
- **VTK** or **Mayavi**: 3D visualization toolkit
- **Matplotlib**: 2D plotting for orbital elements

**Decision: Start with Web-Based (Option A)** for better accessibility and modern UI capabilities.

### Data Sources

#### Primary Sources
1. **Minor Planet Center (MPC)**
   - URL: https://www.minorplanetcenter.net/iau/MPCORB/CometEls.txt
   - Format: MPC 80-column format
   - Contains: Orbital elements for all known comets
   - Update frequency: Daily

2. **JPL Small-Body Database**
   - URL: https://ssd.jpl.nasa.gov/tools/sbdb_query.html
   - API: https://ssd-api.jpl.nasa.gov/doc/sbdb.html
   - Format: JSON API responses
   - Contains: Detailed orbital data, physical parameters

3. **JPL HORIZONS System**
   - URL: https://ssd.jpl.nasa.gov/horizons/
   - Format: SPICE SPK kernels (binary ephemeris)
   - Contains: High-precision position data

#### Planetary Data
- **JPL DE440/DE441**: Planetary ephemerides (via SPICE)
- Built-in Poliastro solar system bodies

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  3D Viewer   │  │   Controls   │  │  Info Panel  │  │
│  │  (Three.js)  │  │   (Time,     │  │  (Comet      │  │
│  │              │  │   Selection) │  │   Details)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                    WebSocket / REST API
                            │
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  API Routes  │  │  Propagation │  │  Data Cache  │  │
│  │              │  │    Engine    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              Data Ingestion Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  MPC Parser  │  │  JPL Client  │  │ SPICE Loader │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Initialization**:
   - Download MPC CometEls.txt
   - Parse orbital elements
   - Load planetary ephemerides (SPICE kernels)

2. **Propagation**:
   - User selects time range
   - Backend calculates positions using Poliastro
   - Apply perturbations (N-body, non-gravitational forces)
   - Return trajectory points to frontend

3. **Visualization**:
   - Three.js renders solar system
   - Plot comet trajectories as curves
   - Update camera and controls based on user input

## MPC 80-Column Format

### Format Specification
```
Columns  Format  Description
1-4      I4      Periodic comet number
5        A1      Orbit type (C/P/D/X/I/A)
6-12     A7      Provisional designation
14-18    I5      Year of perihelion passage
19-20    I2      Month of perihelion passage
21-29    F9.6    Day of perihelion passage (TT)
30-38    F9.6    Perihelion distance (AU)
39-47    F9.7    Orbital eccentricity
48-56    F9.5    Argument of perihelion (degrees)
57-65    F9.5    Longitude of ascending node (degrees)
66-74    F9.5    Inclination (degrees)
75-79    I5      Year of epoch for elements
80       A1      Reference
```

### Example Entry
```
    CJ95 O1   1997 04 01.2334  0.914409 0.9951418  130.5890  282.9478   89.4002 1997 0
```

## Orbital Mechanics Implementation

### Phase 1: Two-Body Problem (Keplerian Orbits)
- Use classical orbital elements (a, e, i, Ω, ω, M)
- Convert to state vectors (position, velocity)
- Propagate using Kepler's equation
- Fast computation, suitable for initial visualization

### Phase 2: N-Body Perturbations
- Include gravitational effects from Sun, Jupiter, Saturn, Uranus, Neptune
- Use numerical integration (RK4, RK45, or DOP853)
- Poliastro's `propagate()` with perturbations

### Phase 3: Non-Gravitational Forces
- Model comet outgassing: F = A * r^(-n) * (1 + cos(θ))
- Marsden's non-gravitational parameters (A1, A2, A3)
- Requires specialized physics model

## Coordinate Systems

### Input: Orbital Elements (Heliocentric)
- Semi-major axis (a) or perihelion distance (q)
- Eccentricity (e)
- Inclination (i)
- Longitude of ascending node (Ω)
- Argument of perihelion (ω)
- Mean anomaly (M) or time of perihelion (T)

### Output: Cartesian Coordinates (Heliocentric Ecliptic J2000)
- X, Y, Z positions in AU
- Standard reference frame for visualization

### Transformations
- Astropy: Coordinate frame conversions
- Poliastro: Orbital elements ↔ state vectors

## Performance Considerations

### Optimization Strategies
1. **Caching**: Pre-compute trajectories for common time ranges
2. **LOD (Level of Detail)**: Reduce trajectory resolution for distant objects
3. **Web Workers**: Offload calculations to background threads
4. **Lazy Loading**: Load comet data on-demand
5. **Spatial Indexing**: Octree for efficient object culling

### Target Performance
- Load time: < 5 seconds for initial data
- Frame rate: 60 FPS for 3D rendering
- Trajectory calculation: < 1 second for 100 comets over 10 years

## Development Phases

### Phase 1: MVP (Data Ingestion & Basic Propagation)
**Duration**: 2-3 days
- MPC data parser
- Orbital element data structure
- Two-body propagation
- Simple CLI output

**Deliverables**:
- `data_ingestion.py`: MPC parser
- `orbital_elements.py`: Data classes
- `propagator.py`: Two-body solver
- `test_phase1.py`: Unit tests

### Phase 2: Core Engine
**Duration**: 3-4 days
- Poliastro integration
- JPL SPICE kernel support
- N-body propagation
- Multi-comet handling

**Deliverables**:
- `engine.py`: Main propagation engine
- `spice_loader.py`: SPICE kernel interface
- `perturbations.py`: N-body models
- API design document

### Phase 3: Visualization & UI
**Duration**: 4-5 days
- FastAPI backend
- React + Three.js frontend
- 3D solar system scene
- Interactive controls

**Deliverables**:
- `backend/`: FastAPI application
- `frontend/`: React application
- Deployment configuration
- User documentation

### Phase 4: Optimization & Advanced Features
**Duration**: 2-3 days
- Non-gravitational forces
- Performance optimization
- Time-scrubbing
- Search functionality

**Deliverables**:
- `nongrav.py`: Non-gravitational force models
- Performance benchmarks
- Feature documentation

## Testing Strategy

### Unit Tests
- Data parsing accuracy
- Orbital element conversions
- Propagation algorithms

### Integration Tests
- End-to-end data flow
- API endpoints
- Frontend-backend communication

### Validation Tests
- Compare results with JPL HORIZONS
- Known comet trajectories (e.g., Halley's Comet)
- Accuracy metrics

## Dependencies

### Python (requirements.txt)
```
numpy>=1.24.0
poliastro>=0.17.0
astropy>=5.3.0
spiceypy>=6.0.0
pandas>=2.0.0
requests>=2.31.0
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
pydantic>=2.4.0
python-multipart>=0.0.6
```

### JavaScript (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "three": "^0.158.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "axios": "^1.6.0"
  }
}
```

## File Structure

```
comet-viz/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py        # API endpoints
│   │   │   └── websocket.py     # WebSocket handlers
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration
│   │   │   └── cache.py         # Caching layer
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py     # MPC parser
│   │   │   ├── jpl_client.py    # JPL API client
│   │   │   └── spice_loader.py  # SPICE interface
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── comet.py         # Comet data model
│   │   │   └── orbital.py       # Orbital elements
│   │   └── physics/
│   │       ├── __init__.py
│   │       ├── propagator.py    # Propagation engine
│   │       ├── perturbations.py # N-body forces
│   │       └── nongrav.py       # Non-gravitational forces
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_ingestion.py
│   │   ├── test_propagator.py
│   │   └── test_api.py
│   ├── data/                    # Downloaded data files
│   │   ├── CometEls.txt
│   │   └── kernels/             # SPICE kernels
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── SolarSystem.jsx  # Three.js scene
│   │   │   ├── Controls.jsx     # UI controls
│   │   │   └── InfoPanel.jsx    # Comet details
│   │   ├── hooks/
│   │   │   └── useWebSocket.js  # WebSocket hook
│   │   └── utils/
│   │       └── api.js           # API client
│   ├── package.json
│   └── README.md
├── docs/
│   ├── API.md                   # API documentation
│   ├── PHYSICS.md               # Orbital mechanics details
│   └── USER_GUIDE.md            # User manual
├── scripts/
│   ├── download_data.py         # Data download script
│   └── validate_results.py      # Validation against HORIZONS
├── .gitignore
├── README.md
└── TECHNICAL_DESIGN.md          # This file
```

## Next Steps

1. ✅ Create project structure
2. ✅ Document technical design
3. → Implement Phase 1: Data ingestion
4. → Implement Phase 1: Propagation engine
5. → Test Phase 1 with sample data
6. → Begin Phase 2 planning
