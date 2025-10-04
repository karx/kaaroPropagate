# System Architecture

## Overview

The Comet Trajectory Visualization System is built with a modular, layered architecture that separates concerns and allows for independent development and testing of each component.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                        (Phase 3 - Future)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   3D Viewer  │  │   Controls   │  │   Information Panel  │  │
│  │  (Three.js)  │  │  (Time, Sel) │  │   (Comet Details)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    REST API / WebSocket
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (Phase 2)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  REST Routes │  │  WebSocket   │  │   Response Cache     │  │
│  │   (FastAPI)  │  │   Handlers   │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│                        (Phase 1 ✅)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Integration Layer                        │  │
│  │  • MPC → Keplerian Conversion                            │  │
│  │  • Catalog Building                                       │  │
│  │  • Data Validation                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Models    │  │   Physics    │  │   Data Access        │  │
│  │              │  │              │  │                      │  │
│  │ • Comet      │  │ • Propagator │  │ • MPC Parser         │  │
│  │ • Orbital    │  │ • N-Body     │  │ • SPICE Loader       │  │
│  │ • Catalog    │  │ • Forces     │  │ • JPL Client         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │     MPC      │  │  JPL SPICE   │  │   JPL Small-Body     │  │
│  │  CometEls    │  │   Kernels    │  │     Database         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. Data Sources Layer

**Purpose**: External data providers

**Components**:
- **MPC (Minor Planet Center)**: Comet orbital elements
- **JPL SPICE Kernels**: High-precision planetary ephemerides
- **JPL Small-Body Database**: Additional comet data and parameters

**Status**: ✅ MPC integration complete

### 2. Data Access Layer

**Purpose**: Download, parse, and cache external data

**Components**:
- **MPC Parser** (`app/data/ingestion.py`): ✅ Complete
  - Downloads CometEls.txt
  - Parses 80-column format
  - Handles 1,141+ comets
  
- **SPICE Loader** (`app/data/spice_loader.py`): 🔄 Phase 2
  - Loads planetary ephemeris kernels
  - Provides planetary positions
  
- **JPL Client** (`app/data/jpl_client.py`): 🔄 Future
  - Queries JPL Small-Body Database API
  - Fetches additional comet parameters

**Status**: MPC parser complete, others planned

### 3. Business Logic Layer

**Purpose**: Core application logic and computations

#### Models (`app/models/`)
- **`orbital.py`**: ✅ Complete
  - `KeplerianElements`: Orbital parameters
  - `StateVector`: Position and velocity
  - Coordinate transformations
  
- **`comet.py`**: ✅ Complete
  - `Comet`: Complete comet data
  - `CometCatalog`: Searchable collection

#### Physics Engine (`app/physics/`)
- **`propagator.py`**: ✅ Complete (Two-body)
  - `TwoBodyPropagator`: Keplerian orbits
  - `AdaptivePropagator`: Variable step size
  - Trajectory calculation
  
- **`nbody.py`**: 🔄 Phase 2
  - N-body perturbations
  - Planetary gravitational effects
  
- **`nongrav.py`**: 🔄 Phase 4
  - Non-gravitational forces
  - Comet outgassing models

#### Integration (`app/core/`)
- **`integration.py`**: ✅ Complete
  - MPC → Keplerian conversion
  - Catalog building
  - Data validation

**Status**: Phase 1 complete, Phase 2 planned

### 4. API Layer

**Purpose**: Expose functionality via REST API

**Components**:
- **REST Routes** (`app/api/routes.py`): 🔄 Phase 2
  - `/comets` - List comets
  - `/comets/{id}` - Get comet details
  - `/comets/{id}/trajectory` - Calculate trajectory
  - `/comets/{id}/position` - Get position at time
  
- **WebSocket Handlers** (`app/api/websocket.py`): 🔄 Phase 3
  - Real-time trajectory updates
  - Live position streaming
  
- **Response Cache** (`app/core/cache.py`): 🔄 Phase 4
  - Cache computed trajectories
  - Reduce redundant calculations

**Status**: Planned for Phase 2-3

### 5. User Interface Layer

**Purpose**: Interactive 3D visualization

**Components**:
- **3D Viewer** (Three.js): 🔄 Phase 3
  - Solar system scene
  - Comet trajectories
  - Camera controls
  
- **Controls** (React): 🔄 Phase 3
  - Time scrubbing
  - Comet selection
  - View settings
  
- **Information Panel** (React): 🔄 Phase 3
  - Comet details
  - Orbital parameters
  - Statistics

**Status**: Planned for Phase 3

## Data Flow

### Phase 1 (Current): Command-Line Interface

```
1. User runs test_phase1.py
2. System downloads MPC data
3. Parser extracts orbital elements
4. Integration layer converts to Keplerian
5. Catalog is built
6. User selects comet
7. Propagator calculates trajectory
8. Results displayed in terminal
```

### Phase 2-3 (Future): Web Application

```
1. User opens web browser
2. Frontend loads React app
3. App requests comet list from API
4. Backend queries catalog
5. Frontend displays comet list
6. User selects comet
7. Frontend requests trajectory
8. Backend calculates with N-body propagator
9. Trajectory sent via WebSocket
10. Three.js renders 3D visualization
11. User interacts with controls
12. Frontend requests updated positions
13. Backend streams real-time updates
```

## Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                      test_phase1.py                          │
│                    (Integration Tests)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────┐
                            │                 │
                            ▼                 ▼
┌──────────────────────────────┐   ┌──────────────────────────┐
│   app.data.ingestion         │   │  app.core.integration    │
│   • load_mpc_data()          │   │  • mpc_to_keplerian()    │
│   • parse_mpc_file()         │   │  • build_catalog()       │
└──────────────────────────────┘   └──────────────────────────┘
                            │                 │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  app.models.orbital  │  │ app.models.comet │  │ app.physics.     │
│  • KeplerianElements │  │ • Comet          │  │   propagator     │
│  • StateVector       │  │ • CometCatalog   │  │ • TwoBody        │
│  • Transformations   │  │                  │  │   Propagator     │
└──────────────────────┘  └──────────────────┘  └──────────────────┘
```

## Design Patterns

### 1. Adapter Pattern
**Used in**: `app/core/integration.py`

Converts external MPC format to internal Keplerian representation.

```python
def mpc_to_keplerian(mpc: MPCOrbitalElements) -> KeplerianElements:
    """Adapter: MPC format → Internal format"""
    pass
```

### 2. Factory Pattern
**Used in**: `app/models/comet.py`

Creates comet objects from various sources.

```python
@classmethod
def from_mpc(cls, mpc_elements: MPCOrbitalElements) -> Comet:
    """Factory: Create Comet from MPC data"""
    pass
```

### 3. Strategy Pattern
**Used in**: `app/physics/propagator.py`

Different propagation strategies (two-body, N-body, etc.).

```python
class Propagator(ABC):
    @abstractmethod
    def propagate(self, time: float) -> StateVector:
        pass

class TwoBodyPropagator(Propagator):
    def propagate(self, time: float) -> StateVector:
        # Two-body implementation
        pass

class NBodyPropagator(Propagator):
    def propagate(self, time: float) -> StateVector:
        # N-body implementation
        pass
```

### 4. Repository Pattern
**Used in**: `app/models/comet.py`

CometCatalog acts as a repository for comet data.

```python
class CometCatalog:
    def get_by_designation(self, designation: str) -> Optional[Comet]:
        pass
    
    def search_by_name(self, query: str) -> List[Comet]:
        pass
    
    def filter_periodic(self) -> List[Comet]:
        pass
```

## Technology Choices

### Phase 1 (Current)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.12 | Scientific computing ecosystem |
| Numerics | NumPy | Fast array operations |
| Math | SciPy | Scientific algorithms |
| HTTP | Requests | Simple, reliable |
| Testing | Custom | Lightweight for MVP |

### Phase 2 (Planned)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Orbital Mechanics | Poliastro | Professional-grade, well-tested |
| Astronomy | Astropy | Industry standard |
| Ephemerides | SPICEYPY | NASA's toolkit |
| API | FastAPI | Modern, fast, auto-docs |
| Server | Uvicorn | ASGI server |

### Phase 3 (Planned)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | React | Component-based, popular |
| 3D Graphics | Three.js | WebGL abstraction |
| State | React Hooks | Simple, modern |
| HTTP Client | Axios | Promise-based |
| Build | Vite | Fast, modern |

## Scalability Considerations

### Current Limitations
- Single-threaded computation
- No caching
- In-memory data storage
- Synchronous API (future)

### Future Improvements

#### Phase 2
- Async API with FastAPI
- Response caching
- Database for comet data (optional)

#### Phase 3
- WebSocket for real-time updates
- Client-side caching
- Progressive loading

#### Phase 4
- Parallel trajectory computation
- Distributed caching (Redis)
- CDN for static assets
- Database indexing

## Security Considerations

### Current
- No authentication (local use only)
- No sensitive data
- Read-only operations

### Future (Production)
- API rate limiting
- Input validation
- CORS configuration
- HTTPS only
- Authentication (optional)
- Logging and monitoring

## Testing Strategy

### Unit Tests
- Individual function testing
- Mock external dependencies
- Edge case coverage

### Integration Tests
- End-to-end data flow
- Multiple component interaction
- Real data validation

### Performance Tests
- Benchmark propagation speed
- Memory usage profiling
- API response times

### Validation Tests
- Compare with JPL HORIZONS
- Known comet trajectories
- Accuracy metrics

## Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────────┐
│                      Load Balancer                       │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Backend    │    │   Backend    │    │   Backend    │
│  Instance 1  │    │  Instance 2  │    │  Instance 3  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │    Redis     │
                    │    Cache     │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │  (Optional)  │
                    └──────────────┘
```

## Monitoring and Observability (Future)

- **Logging**: Structured logs with context
- **Metrics**: Request rates, response times, error rates
- **Tracing**: Distributed tracing for API calls
- **Alerting**: Automated alerts for errors
- **Dashboards**: Real-time system health

## Conclusion

The architecture is designed to be:
- **Modular**: Independent components
- **Testable**: Clear interfaces
- **Scalable**: Can grow with demand
- **Maintainable**: Clean code, good docs
- **Extensible**: Easy to add features

Phase 1 establishes a solid foundation that can support the advanced features planned for future phases.
