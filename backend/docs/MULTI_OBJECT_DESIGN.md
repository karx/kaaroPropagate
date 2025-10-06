# Multi-Object Visualization Design

## Overview

Design for enabling simultaneous visualization of multiple comets, asteroids, and small bodies including Near-Earth Objects (NEOs), Kuiper Belt Objects (KBOs), and Oort Cloud comets.

## Current Catalog Analysis

From our existing MPC catalog (1,141 objects):

| Category | Count | Criteria |
|----------|-------|----------|
| Near-Earth Objects | 144 | q < 1.3 AU |
| Jupiter Family | 466 | 2 < T < 20 years |
| Long Period | 32 | T > 200 years |
| Oort Cloud | 148 | a > 10,000 AU |
| Hyperbolic | 104 | e > 1 |
| Kuiper Belt | 0* | a > 30 AU, e < 0.2 |

*Note: MPC comet catalog doesn't include many KBOs. Need to integrate asteroid data.

## Data Sources

### 1. Current: MPC Comet Catalog
- **Source**: https://www.minorplanetcenter.net/iau/MPCORB/CometEls.txt
- **Coverage**: ~1,141 comets
- **Includes**: NEOs, Jupiter family, long-period, Oort cloud comets
- **Status**: ✅ Already integrated

### 2. Proposed: JPL SBDB API
- **Source**: https://ssd-api.jpl.nasa.gov/sbdb.api
- **Coverage**: All known asteroids and comets
- **Includes**: NEOs, MBAs, KBOs, TNOs, Centaurs
- **Features**: Physical parameters, close approach data, discovery info
- **Status**: 🔄 To be integrated

### 3. Proposed: JPL Small-Body Database Query
- **Source**: https://ssd-api.jpl.nasa.gov/sbdb_query.api
- **Coverage**: Filtered queries (e.g., all NEOs, all KBOs)
- **Use case**: Bulk retrieval of specific object types
- **Status**: 🔄 To be integrated

## Architecture Design

### 1. Object Categories

```python
class ObjectCategory(Enum):
    NEO = "neo"                    # Near-Earth Objects (q < 1.3 AU)
    ATIRA = "atira"                # a < 1.0 AU, Q < 0.983 AU
    ATEN = "aten"                  # a < 1.0 AU, Q > 0.983 AU
    APOLLO = "apollo"              # a > 1.0 AU, q < 1.017 AU
    AMOR = "amor"                  # 1.017 < q < 1.3 AU
    
    JUPITER_FAMILY = "jupiter"     # 2 < T < 20 years
    HALLEY_TYPE = "halley"         # 20 < T < 200 years
    LONG_PERIOD = "long_period"    # T > 200 years
    
    MAIN_BELT = "main_belt"        # 2.0 < a < 3.2 AU
    KUIPER_BELT = "kuiper_belt"    # 30 < a < 50 AU, e < 0.2
    SCATTERED_DISK = "scattered"   # a > 50 AU or e > 0.2
    OORT_CLOUD = "oort_cloud"      # a > 10,000 AU
    
    CENTAUR = "centaur"            # 5.2 < a < 30 AU
    TROJAN = "trojan"              # Jupiter/Neptune Trojans
    HYPERBOLIC = "hyperbolic"      # e > 1.0
```

### 2. Multi-Object Query API

#### Endpoint: GET `/api/objects/batch`

Query multiple objects by category, filters, or explicit list.

**Query Parameters:**
```
categories: List[ObjectCategory]  # Filter by categories
limit: int = 100                  # Max objects to return
q_min: float = None               # Min perihelion distance
q_max: float = None               # Max perihelion distance
a_min: float = None               # Min semi-major axis
a_max: float = None               # Max semi-major axis
e_max: float = 1.0                # Max eccentricity
period_min: float = None          # Min period (years)
period_max: float = None          # Max period (years)
designations: List[str] = None    # Explicit list of designations
```

**Response:**
```json
{
  "total": 144,
  "objects": [
    {
      "designation": "K03T120",
      "name": "K03T120",
      "category": "neo",
      "orbital_elements": {...},
      "physical_properties": {...}
    },
    ...
  ]
}
```

#### Endpoint: POST `/api/trajectories/batch`

Calculate trajectories for multiple objects simultaneously.

**Request Body:**
```json
{
  "designations": ["1P", "2P", "9P"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "num_points": 100,
  "method": "nbody",
  "parallel": true
}
```

**Response:**
```json
{
  "trajectories": {
    "1P": {
      "designation": "1P",
      "points": [...],
      "calculation_time_ms": 1234
    },
    "2P": {...},
    "9P": {...}
  },
  "total_time_ms": 3456,
  "method": "nbody"
}
```

### 3. Performance Optimization

#### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

def calculate_trajectories_parallel(
    comets: List[Comet],
    start_time: float,
    end_time: float,
    num_points: int,
    method: str = "nbody"
) -> Dict[str, List[StateVector]]:
    """Calculate trajectories for multiple comets in parallel."""
    
    def calculate_single(comet: Comet):
        if method == "nbody":
            propagator = NBodyPropagator(comet.elements)
        else:
            propagator = TwoBodyPropagator(comet.elements)
        
        return comet.designation, propagator.propagate_range(
            start_time, end_time, num_points
        )
    
    # Use thread pool for I/O-bound operations
    # Use process pool for CPU-bound N-body calculations
    executor_class = ProcessPoolExecutor if method == "nbody" else ThreadPoolExecutor
    max_workers = min(multiprocessing.cpu_count(), len(comets))
    
    with executor_class(max_workers=max_workers) as executor:
        results = dict(executor.map(calculate_single, comets))
    
    return results
```

#### Caching Strategy
```python
from functools import lru_cache
import hashlib

class TrajectoryCache:
    """Cache computed trajectories to avoid recomputation."""
    
    def __init__(self, max_size_mb: int = 500):
        self.cache = {}
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
    
    def get_key(self, designation: str, start: float, end: float, 
                points: int, method: str) -> str:
        """Generate cache key."""
        data = f"{designation}:{start}:{end}:{points}:{method}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[List[StateVector]]:
        """Retrieve from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, trajectory: List[StateVector]):
        """Store in cache with LRU eviction."""
        # Implement LRU eviction if needed
        self.cache[key] = trajectory
```

### 4. Frontend Integration

#### Multi-Object Selection UI
```typescript
interface ObjectFilter {
  categories: ObjectCategory[];
  qMin?: number;
  qMax?: number;
  aMin?: number;
  aMax?: number;
  limit: number;
}

interface MultiObjectVisualization {
  objects: CometData[];
  trajectories: Map<string, TrajectoryPoint[]>;
  colors: Map<string, string>;  // Color coding by category
  visibility: Map<string, boolean>;  // Toggle individual objects
}

// Color scheme by category
const CATEGORY_COLORS = {
  neo: '#FF4444',        // Red - dangerous
  jupiter: '#4444FF',    // Blue - short period
  long_period: '#44FF44', // Green - long period
  kuiper_belt: '#FF44FF', // Magenta - distant
  oort_cloud: '#FFFF44', // Yellow - very distant
  hyperbolic: '#FF8844'  // Orange - interstellar
};
```

#### Performance Considerations
- **Level of Detail (LOD)**: Reduce trajectory points for distant objects
- **Culling**: Don't render objects outside view frustum
- **Instancing**: Use GPU instancing for rendering many objects
- **Progressive Loading**: Load and render in batches

### 5. Database Schema Extensions

```sql
-- Add category classification
ALTER TABLE comets ADD COLUMN category VARCHAR(50);
ALTER TABLE comets ADD COLUMN subcategory VARCHAR(50);

-- Add physical properties
ALTER TABLE comets ADD COLUMN absolute_magnitude FLOAT;
ALTER TABLE comets ADD COLUMN diameter_km FLOAT;
ALTER TABLE comets ADD COLUMN albedo FLOAT;

-- Add discovery/observation metadata
ALTER TABLE comets ADD COLUMN discovery_date DATE;
ALTER TABLE comets ADD COLUMN last_observation DATE;
ALTER TABLE comets ADD COLUMN num_observations INT;

-- Create indexes for filtering
CREATE INDEX idx_category ON comets(category);
CREATE INDEX idx_perihelion ON comets(perihelion_distance);
CREATE INDEX idx_semi_major_axis ON comets(semi_major_axis);
CREATE INDEX idx_period ON comets(period_years);
```

## Implementation Plan

### Phase 1: Backend Infrastructure (Current Sprint)
1. ✅ Add object categorization logic
2. ✅ Implement batch trajectory calculation
3. ✅ Add parallel processing support
4. ✅ Create multi-object API endpoints
5. ✅ Add caching layer

### Phase 2: Data Integration
1. 🔄 Integrate JPL SBDB API for asteroids
2. 🔄 Add Kuiper Belt Objects from MPC
3. 🔄 Enhance metadata (physical properties)
4. 🔄 Add discovery/observation data

### Phase 3: Frontend Visualization
1. 🔄 Multi-object selection UI
2. 🔄 Category filtering controls
3. 🔄 Color coding by category
4. 🔄 Performance optimization (LOD, culling)
5. 🔄 Legend and object labels

### Phase 4: Advanced Features
1. 🔄 Close approach detection
2. 🔄 Orbital resonance visualization
3. 🔄 Family grouping (e.g., comet fragments)
4. 🔄 Time-based filtering (active comets)

## API Examples

### Get all NEOs
```bash
curl "http://localhost:8000/api/objects/batch?categories=neo&limit=100"
```

### Get Kuiper Belt Objects
```bash
curl "http://localhost:8000/api/objects/batch?categories=kuiper_belt&a_min=30&a_max=50&e_max=0.2"
```

### Calculate trajectories for multiple comets
```bash
curl -X POST "http://localhost:8000/api/trajectories/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "designations": ["1P", "2P", "9P", "67P"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "num_points": 100,
    "method": "nbody",
    "parallel": true
  }'
```

### Get objects by explicit list
```bash
curl "http://localhost:8000/api/objects/batch?designations=1P,2P,9P,67P,81P"
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Single trajectory (two-body) | < 10ms | Fast Keplerian |
| Single trajectory (N-body) | < 100ms | With 4 planets |
| Batch 10 objects (two-body) | < 50ms | Parallel |
| Batch 10 objects (N-body) | < 500ms | Parallel, 4 cores |
| Batch 100 objects (two-body) | < 200ms | Parallel |
| Frontend render 100 objects | 60 FPS | With LOD |
| Cache hit rate | > 80% | For repeated queries |

## Data Volume Estimates

| Category | Estimated Count | Source |
|----------|----------------|--------|
| NEOs | ~30,000 | JPL CNEOS |
| Main Belt Asteroids | ~1,000,000 | MPC |
| Jupiter Family Comets | ~500 | MPC |
| Long Period Comets | ~4,000 | MPC |
| Kuiper Belt Objects | ~3,000 | MPC |
| Centaurs | ~500 | MPC |
| Total Small Bodies | ~1,040,000 | Combined |

**Practical Limits:**
- Visualize: 100-1,000 objects simultaneously
- Calculate: 10,000 trajectories in batch
- Store: Full catalog with metadata

## Security & Rate Limiting

```python
from fastapi import Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/trajectories/batch")
@limiter.limit("10/minute")  # Limit expensive batch calculations
async def batch_trajectories(
    request: BatchTrajectoryRequest,
    remote_addr: str = Depends(get_remote_address)
):
    # Limit number of objects per request
    if len(request.designations) > 100:
        raise HTTPException(400, "Maximum 100 objects per batch request")
    
    # Limit time span for N-body
    if request.method == "nbody":
        days = (request.end_date - request.start_date).days
        if days > 3650:  # 10 years
            raise HTTPException(400, "N-body limited to 10 years")
    
    # Calculate trajectories...
```

## Testing Strategy

1. **Unit Tests**: Individual object categorization
2. **Integration Tests**: Batch trajectory calculation
3. **Performance Tests**: Parallel processing benchmarks
4. **Load Tests**: 100+ simultaneous objects
5. **Accuracy Tests**: Compare with JPL HORIZONS

## Documentation

- API documentation (OpenAPI/Swagger)
- Object category definitions
- Performance characteristics
- Usage examples
- Visualization best practices

## Future Enhancements

1. **Real-time Updates**: WebSocket for live trajectory updates
2. **Collision Detection**: Identify potential close approaches
3. **Orbital Families**: Group related objects (e.g., comet fragments)
4. **Historical Orbits**: Show past positions
5. **Prediction Uncertainty**: Visualize orbit uncertainty ellipses
6. **Mobile Optimization**: Reduced data for mobile clients
7. **Export Formats**: CSV, JSON, KML for external tools
