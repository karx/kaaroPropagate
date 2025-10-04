# Phase 2: Advanced Physics Engine

## Overview

Phase 2 focuses on improving the accuracy and capabilities of the orbital propagation engine by integrating professional-grade libraries and implementing N-body perturbations.

## Goals

1. ✅ **Integrate Poliastro** - Professional orbital mechanics library
2. ✅ **JPL SPICE Support** - High-precision planetary ephemerides  
3. ✅ **N-Body Perturbations** - Include planetary gravitational effects
4. ✅ **REST API Foundation** - Design API structure for Phase 3

## Why These Improvements?

### Current Limitations (Two-Body Model)
- Only considers Sun-comet gravitational interaction
- Ignores planetary perturbations (especially Jupiter)
- Accuracy degrades over time
- Not suitable for close planetary encounters

### Phase 2 Improvements
- **Poliastro**: Battle-tested orbital mechanics with multiple propagators
- **SPICE**: NASA's standard for planetary positions (used by JPL HORIZONS)
- **N-Body**: Account for Jupiter, Saturn, and other planets
- **Better Accuracy**: Suitable for long-term predictions

## Implementation Plan

### Task 1: Install and Test Poliastro

**Goal**: Verify Poliastro works with our data

```bash
pip install poliastro astropy
```

**Test Script** (`backend/test_poliastro.py`):
```python
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
from astropy import units as u
from astropy.time import Time

# Create test orbit
orbit = Orbit.from_classical(
    Sun,
    a=3.5 * u.AU,
    ecc=0.65 * u.one,
    inc=45 * u.deg,
    raan=90 * u.deg,
    argp=180 * u.deg,
    nu=0 * u.deg,
    epoch=Time("2024-01-01")
)

# Propagate
orbit_later = orbit.propagate(365 * u.day)
print(f"Position: {orbit_later.r}")
```

### Task 2: Create Poliastro Adapter

**File**: `backend/app/physics/poliastro_adapter.py`

**Purpose**: Bridge between our data structures and Poliastro

```python
from poliastro.twobody import Orbit
from poliastro.bodies import Sun
from astropy import units as u
from astropy.time import Time
from ..models.orbital import KeplerianElements, StateVector

def keplerian_to_poliastro(elements: KeplerianElements) -> Orbit:
    """Convert our KeplerianElements to Poliastro Orbit."""
    # Implementation
    pass

def poliastro_to_state_vector(orbit: Orbit) -> StateVector:
    """Convert Poliastro Orbit to our StateVector."""
    # Implementation
    pass
```

### Task 3: Implement N-Body Propagator

**File**: `backend/app/physics/nbody.py`

**Features**:
- Use Poliastro's numerical propagators (Cowell, etc.)
- Include perturbations from major planets
- Configurable accuracy vs. speed

```python
from poliastro.twobody.propagation import cowell
from poliastro.core.perturbations import J2_perturbation, third_body

class NBodyPropagator:
    """
    N-body propagator using Poliastro.
    
    Includes gravitational perturbations from major planets.
    """
    
    def __init__(self, elements: KeplerianElements, 
                 perturbing_bodies: list = None):
        """
        Args:
            elements: Initial orbital elements
            perturbing_bodies: List of bodies to include (default: Jupiter, Saturn)
        """
        pass
    
    def propagate(self, time: float) -> StateVector:
        """Propagate with N-body perturbations."""
        pass
```

### Task 4: SPICE Kernel Support

**File**: `backend/app/data/spice_loader.py`

**Purpose**: Load and use JPL SPICE kernels for planetary positions

```python
import spiceypy as spice

class SPICEKernelManager:
    """
    Manages SPICE kernel loading and planetary ephemerides.
    """
    
    def __init__(self, kernel_dir: Path):
        """Load required SPICE kernels."""
        self.kernel_dir = kernel_dir
        self.load_kernels()
    
    def load_kernels(self):
        """Load planetary ephemeris kernels."""
        # Load DE440 or DE441 kernel
        # Load leap seconds kernel
        pass
    
    def get_planet_position(self, planet: str, time: float) -> np.ndarray:
        """Get planet position at given time."""
        pass
```

**Required Kernels** (download from NAIF):
- `de440.bsp` or `de441.bsp` - Planetary ephemerides
- `naif0012.tls` - Leap seconds
- `pck00010.tpc` - Physical constants

### Task 5: REST API Design

**File**: `backend/app/api/routes.py`

**Endpoints**:

```python
from fastapi import FastAPI, Query
from typing import List

app = FastAPI(title="Comet Trajectory API")

@app.get("/comets")
async def list_comets(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    orbit_type: str = Query(None)
):
    """List all comets with pagination."""
    pass

@app.get("/comets/{designation}")
async def get_comet(designation: str):
    """Get detailed information about a specific comet."""
    pass

@app.get("/comets/{designation}/trajectory")
async def get_trajectory(
    designation: str,
    start_time: float,
    end_time: float,
    num_points: int = Query(100, le=1000),
    method: str = Query("twobody", regex="^(twobody|nbody)$")
):
    """Calculate comet trajectory over time range."""
    pass

@app.get("/comets/{designation}/position")
async def get_position(
    designation: str,
    time: float,
    method: str = Query("twobody")
):
    """Get comet position at specific time."""
    pass
```

### Task 6: Integration Testing

**File**: `backend/test_phase2.py`

**Tests**:
1. Poliastro adapter conversions
2. N-body propagation accuracy
3. SPICE kernel loading
4. API endpoint responses
5. Performance benchmarks

**Validation**:
- Compare results with Phase 1 two-body propagator
- Verify N-body gives different (more accurate) results
- Check against JPL HORIZONS for known comets

## File Structure (Phase 2 Additions)

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py         ← NEW: REST API endpoints
│   ├── data/
│   │   └── spice_loader.py   ← NEW: SPICE kernel manager
│   └── physics/
│       ├── nbody.py          ← NEW: N-body propagator
│       └── poliastro_adapter.py  ← NEW: Poliastro bridge
├── data/
│   └── kernels/              ← NEW: SPICE kernels directory
│       ├── de440.bsp
│       ├── naif0012.tls
│       └── pck00010.tpc
├── test_phase2.py            ← NEW: Phase 2 tests
└── test_poliastro.py         ← NEW: Poliastro verification
```

## Dependencies to Add

Update `backend/requirements.txt`:

```txt
# Existing
numpy>=1.24.0
scipy>=1.11.0
requests>=2.31.0

# Phase 2 additions
poliastro>=0.17.0
astropy>=5.3.0
spiceypy>=6.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.4.0
```

## Testing Strategy

### Unit Tests
- Poliastro adapter conversions (both directions)
- SPICE kernel loading and queries
- N-body propagator initialization

### Integration Tests
- End-to-end trajectory calculation
- API endpoint responses
- Data format consistency

### Validation Tests
- Compare with Phase 1 two-body results
- Verify N-body perturbations are significant for Jupiter-family comets
- Check against JPL HORIZONS for Halley's Comet

### Performance Tests
- Benchmark two-body vs. N-body propagation
- Measure API response times
- Profile memory usage

## Expected Results

### Accuracy Improvements
- **Short-term (< 1 year)**: Similar to two-body
- **Medium-term (1-10 years)**: Noticeable improvement for Jupiter-family comets
- **Long-term (> 10 years)**: Significant improvement, especially near planets

### Performance
- **Two-body**: ~1ms per trajectory point (unchanged)
- **N-body**: ~10-100ms per trajectory point (acceptable for API)
- **Caching**: Reduce repeated calculations

## Success Criteria

Phase 2 is complete when:

1. ✅ Poliastro successfully integrated
2. ✅ N-body propagator working with planetary perturbations
3. ✅ SPICE kernels loaded and planetary positions accurate
4. ✅ REST API designed and documented
5. ✅ All tests passing
6. ✅ Validation against HORIZONS shows improved accuracy

## Timeline

- **Day 1**: Install Poliastro, create adapter, basic tests
- **Day 2**: Implement N-body propagator, SPICE loader
- **Day 3**: Design and implement REST API
- **Day 4**: Integration testing, validation, documentation

## Next Phase Preview

**Phase 3** will use the Phase 2 API to build:
- React frontend with Three.js visualization
- Interactive 3D solar system
- Real-time trajectory updates via WebSocket
- User controls for time, selection, and viewing

## Resources

### Documentation
- [Poliastro Docs](https://docs.poliastro.space/)
- [Astropy Time](https://docs.astropy.org/en/stable/time/)
- [SPICE Toolkit](https://naif.jpl.nasa.gov/naif/toolkit.html)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Data Sources
- [NAIF SPICE Kernels](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/)
- [JPL HORIZONS](https://ssd.jpl.nasa.gov/horizons/)
- [MPC Comet Data](https://www.minorplanetcenter.net/iau/MPCORB/)

### Validation
- [JPL HORIZONS Web Interface](https://ssd.jpl.nasa.gov/horizons/app.html)
- Compare with known comet trajectories
- Check perihelion passages against observations
