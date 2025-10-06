# Multi-Object API Documentation

## Overview

The Multi-Object API enables simultaneous visualization and trajectory calculation for multiple comets, asteroids, and small bodies. This includes Near-Earth Objects (NEOs), Jupiter-family comets, long-period comets, and Oort Cloud objects.

## Current Catalog

**Total Objects**: 1,141 comets from MPC catalog

| Category | Count | Criteria |
|----------|-------|----------|
| Near-Earth Objects | 144 | q < 1.3 AU |
| Jupiter Family | 466 | 2 < T < 20 years |
| Long Period | 32 | T > 200 years |
| Oort Cloud | 148 | a > 10,000 AU |
| Hyperbolic | 104 | e > 1.0 |

## API Endpoints

### 1. Get Multiple Objects

**Endpoint**: `GET /api/objects/batch`

Query multiple objects by filters or explicit designation list.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `designations` | string | Comma-separated list of designations | `1P,2P,9P` |
| `category` | string | Filter by category | `neo`, `jupiter`, `long_period`, `oort_cloud` |
| `q_min` | float | Minimum perihelion distance (AU) | `0.5` |
| `q_max` | float | Maximum perihelion distance (AU) | `1.3` |
| `a_min` | float | Minimum semi-major axis (AU) | `30` |
| `a_max` | float | Maximum semi-major axis (AU) | `50` |
| `e_max` | float | Maximum eccentricity | `0.2` |
| `period_min` | float | Minimum period (years) | `2` |
| `period_max` | float | Maximum period (years) | `20` |
| `limit` | int | Maximum objects to return (1-1000) | `100` |

#### Examples

**Get specific comets by designation:**
```bash
curl "http://localhost:8000/api/objects/batch?designations=J96R020,J98V24S,J99XC0N"
```

**Get all NEOs (perihelion < 1.3 AU):**
```bash
curl "http://localhost:8000/api/objects/batch?q_max=1.3&limit=100"
```

**Get Jupiter-family comets (2-20 year period):**
```bash
curl "http://localhost:8000/api/objects/batch?period_min=2&period_max=20&limit=50"
```

**Get Kuiper Belt region objects (30-50 AU):**
```bash
curl "http://localhost:8000/api/objects/batch?a_min=30&a_max=50&e_max=0.2&limit=50"
```

**Get Oort Cloud candidates (a > 10,000 AU):**
```bash
curl "http://localhost:8000/api/objects/batch?a_min=10000&limit=50"
```

#### Response Format

```json
{
  "total": 144,
  "returned": 10,
  "limit": 10,
  "objects": [
    {
      "designation": "J99R28O",
      "name": "J99R28O",
      "orbit_type": "P",
      "periodic_number": null,
      "is_periodic": false,
      "is_hyperbolic": false,
      "orbital_elements": {
        "semi_major_axis": 3.4249,
        "eccentricity": 0.6722,
        "inclination_deg": 7.5672,
        "perihelion_distance": 1.1228,
        "epoch": 2460979.3038,
        "period_days": 2315.05,
        "period_years": 6.34
      }
    },
    ...
  ]
}
```

### 2. Calculate Batch Trajectories

**Endpoint**: `POST /api/trajectories/batch`

Calculate trajectories for multiple objects in parallel.

#### Request Body

```json
{
  "designations": ["J96R020", "J98V24S", "J99XC0N"],
  "start_date": "2024-01-01",  // Optional
  "end_date": "2024-12-31",    // Optional
  "days": 365,                  // Alternative to end_date
  "num_points": 100,
  "method": "twobody",          // or "nbody"
  "parallel": true
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `designations` | array | Yes | List of object designations (max 100) |
| `start_date` | string | No | Start date (ISO format) |
| `end_date` | string | No | End date (ISO format) |
| `days` | int | No | Number of days from epoch (default: 365) |
| `num_points` | int | Yes | Number of trajectory points (10-1000) |
| `method` | string | Yes | `twobody` or `nbody` |
| `parallel` | bool | No | Enable parallel processing (default: true) |

#### Examples

**Calculate trajectories for 3 comets (two-body):**
```bash
curl -X POST "http://localhost:8000/api/trajectories/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "designations": ["J96R020", "J98V24S", "J99XC0N"],
    "days": 365,
    "num_points": 100,
    "method": "twobody",
    "parallel": true
  }'
```

**Calculate N-body trajectories for 4 comets:**
```bash
curl -X POST "http://localhost:8000/api/trajectories/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "designations": ["J96R020", "J98V24S", "J99XC0N", "K00R020"],
    "days": 730,
    "num_points": 100,
    "method": "nbody",
    "parallel": true
  }'
```

#### Response Format

```json
{
  "trajectories": {
    "J96R020": {
      "designation": "J96R020",
      "points": [
        {
          "time": 2461207.7238,
          "position": {"x": 2.514, "y": 0.607, "z": -0.052},
          "velocity": {"x": -0.012, "y": 0.015, "z": -0.001}
        },
        ...
      ],
      "calculation_time_ms": 5.2
    },
    "J98V24S": {...},
    "J99XC0N": {...}
  },
  "errors": {
    "K01K050": "No orbital elements"
  },
  "not_found": [],
  "statistics": {
    "total_objects": 4,
    "successful": 3,
    "failed": 1,
    "cache_hits": 0,
    "cache_misses": 4,
    "total_time_ms": 28.5,
    "avg_calc_time_ms": 7.1,
    "method": "twobody",
    "parallel": true
  }
}
```

## Performance

### Benchmarks

Tested on 4-core system:

| Scenario | Objects | Method | Time | Speedup |
|----------|---------|--------|------|---------|
| Single comet | 1 | two-body | ~1ms | - |
| Single comet | 1 | N-body | ~30ms | - |
| Batch 10 comets | 10 | two-body | ~10ms | ~10x |
| Batch 10 comets | 10 | N-body | ~300ms | ~10x |
| Batch 4 comets | 4 | N-body | ~130ms | ~4x |

### Parallel Processing

- **Two-body**: Uses ThreadPoolExecutor (I/O-bound)
- **N-body**: Uses ProcessPoolExecutor (CPU-bound)
- **Auto-scaling**: Workers = min(CPU cores, number of objects)
- **Cache**: Trajectories cached to avoid recomputation

### Limits

- **Max objects per request**: 100
- **Max trajectory points**: 1,000
- **Max time span (N-body)**: 10 years (3,650 days)
- **Rate limit**: 10 batch requests per minute

## Object Categories

### Near-Earth Objects (NEOs)

Objects with perihelion distance < 1.3 AU.

**Subcategories:**
- **Atira**: a < 1.0 AU, Q < 0.983 AU
- **Aten**: a < 1.0 AU, Q > 0.983 AU
- **Apollo**: a > 1.0 AU, q < 1.017 AU
- **Amor**: 1.017 < q < 1.3 AU

**Query:**
```bash
curl "http://localhost:8000/api/objects/batch?q_max=1.3&limit=100"
```

### Jupiter-Family Comets

Short-period comets with 2 < T < 20 years.

**Query:**
```bash
curl "http://localhost:8000/api/objects/batch?period_min=2&period_max=20&limit=100"
```

### Long-Period Comets

Comets with T > 200 years.

**Query:**
```bash
curl "http://localhost:8000/api/objects/batch?period_min=200&limit=100"
```

### Oort Cloud Objects

Very distant objects with a > 10,000 AU.

**Query:**
```bash
curl "http://localhost:8000/api/objects/batch?a_min=10000&limit=100"
```

### Hyperbolic Objects

Objects with e > 1.0 (interstellar visitors).

**Query:**
```bash
curl "http://localhost:8000/api/objects/batch?category=hyperbolic&limit=100"
```

## Use Cases

### 1. Visualize All NEOs

```javascript
// Fetch all NEOs
const response = await fetch('/api/objects/batch?q_max=1.3&limit=100');
const data = await response.json();

// Calculate trajectories
const trajResponse = await fetch('/api/trajectories/batch', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    designations: data.objects.map(o => o.designation),
    days: 365,
    num_points: 100,
    method: 'twobody',
    parallel: true
  })
});

const trajectories = await trajResponse.json();
// Render in 3D visualization
```

### 2. Compare Jupiter-Family Comets

```bash
# Get Jupiter-family comets
curl "http://localhost:8000/api/objects/batch?period_min=2&period_max=20&limit=10" \
  | jq '.objects[].designation' \
  | xargs -I {} curl -X POST "http://localhost:8000/api/trajectories/batch" \
    -H "Content-Type: application/json" \
    -d '{"designations": ["{}"], "days": 365, "num_points": 100, "method": "nbody"}'
```

### 3. Study Oort Cloud Distribution

```python
import requests

# Get Oort Cloud objects
response = requests.get('http://localhost:8000/api/objects/batch', params={
    'a_min': 10000,
    'limit': 50
})

objects = response.json()['objects']

# Analyze distribution
import matplotlib.pyplot as plt
import numpy as np

a_values = [obj['orbital_elements']['semi_major_axis'] for obj in objects]
e_values = [obj['orbital_elements']['eccentricity'] for obj in objects]

plt.scatter(a_values, e_values)
plt.xlabel('Semi-major axis (AU)')
plt.ylabel('Eccentricity')
plt.title('Oort Cloud Objects')
plt.xscale('log')
plt.show()
```

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "detail": "Maximum 100 objects per batch request"
}
```

**404 Not Found**
```json
{
  "detail": "No comets found. Not found: ['INVALID1', 'INVALID2']"
}
```

**503 Service Unavailable**
```json
{
  "detail": "Catalog not loaded"
}
```

### Partial Success

The batch endpoint returns partial results if some objects fail:

```json
{
  "trajectories": {
    "J96R020": {...},
    "J98V24S": {...}
  },
  "errors": {
    "K01K050": "No orbital elements",
    "INVALID": "Comet not found"
  },
  "not_found": ["INVALID"],
  "statistics": {
    "successful": 2,
    "failed": 2
  }
}
```

## Caching

Trajectories are automatically cached to improve performance:

- **Cache key**: `{designation}:{start}:{end}:{points}:{method}`
- **Cache hit rate**: Typically > 80% for repeated queries
- **Cache size**: Unlimited (in-memory)
- **Cache invalidation**: Automatic on server restart

**Check cache statistics:**
```bash
curl "http://localhost:8000/metrics"
```

## Best Practices

### 1. Use Appropriate Method

- **Two-body**: Fast, good for short-term (< 1 year) or distant objects
- **N-body**: Accurate, needed for close planetary encounters

### 2. Batch Similar Objects

Group objects by:
- Time span requirements
- Accuracy needs (two-body vs N-body)
- Visualization context

### 3. Optimize Point Count

- **Visualization**: 50-100 points sufficient
- **Analysis**: 100-500 points
- **High precision**: 500-1000 points

### 4. Use Parallel Processing

Always enable `parallel: true` for batch requests with > 2 objects.

### 5. Handle Partial Failures

Always check the `errors` field in batch responses and handle gracefully.

## Future Enhancements

### Planned Features

1. **WebSocket streaming**: Real-time trajectory updates
2. **Collision detection**: Identify close approaches
3. **Orbital families**: Group related objects
4. **Export formats**: CSV, JSON, KML
5. **Mobile optimization**: Reduced data payloads
6. **Advanced filtering**: By discovery date, observation count, etc.

### Data Sources

1. **JPL SBDB API**: Add asteroids and physical properties
2. **MPC asteroid catalog**: Expand to 1M+ objects
3. **Kuiper Belt Objects**: Dedicated TNO catalog
4. **Real-time updates**: Sync with MPC daily updates

## Support

For issues or questions:
- Check API documentation: `/docs`
- View metrics: `/metrics`
- Check health: `/health`
- Review logs for errors

## Examples Repository

Complete examples available at:
- Python: `examples/python/multi_object.py`
- JavaScript: `examples/javascript/multi_object.js`
- Jupyter Notebook: `examples/notebooks/multi_object_analysis.ipynb`
