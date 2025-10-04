# Quick Start Guide

Get the Comet Trajectory Visualization System running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Internet connection (to download comet data)

## Installation

### 1. Clone or Navigate to Project

```bash
cd /workspaces/workspaces
```

### 2. Install Dependencies

```bash
cd backend
pip install numpy scipy requests
```

That's it! Only 3 dependencies for Phase 1.

## Running the System

### Option 1: Run Integration Tests (Recommended)

This will download data, parse comets, and calculate trajectories:

```bash
python test_phase1.py
```

**Expected Output:**
```
============================================================
  PHASE 1 INTEGRATION TEST
============================================================

✅ TEST 1: Data Ingestion
   - Downloaded 209KB of MPC data
   - Parsed 1,141 comet orbits

✅ TEST 2: Catalog Building
   - Catalog created with 1,141 comets

✅ TEST 3: Orbital Propagation
   - Successfully propagated test comet

✅ TEST 4: Multiple Comet Propagation
   - 5 comets propagated over 2 years

✅ TEST 5: Search Functionality
   - Search functionality working

============================================================
  PHASE 1 COMPLETE
============================================================

✅ All tests passed!
```

### Option 2: Interactive Python

```python
# Start Python
python

# Import modules
from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc
from app.physics.propagator import TwoBodyPropagator

# Load comet data (downloads if needed)
print("Loading comet data...")
mpc_elements = load_mpc_data()
print(f"Loaded {len(mpc_elements)} comets")

# Build catalog
catalog = build_catalog_from_mpc(mpc_elements)

# Get a comet
comet = catalog.comets[0]
print(f"\nComet: {comet}")
print(f"  Perihelion: {comet.elements.perihelion_distance:.3f} AU")
print(f"  Eccentricity: {comet.elements.eccentricity:.4f}")

# Calculate trajectory
propagator = TwoBodyPropagator(comet.elements)
positions, times = propagator.get_trajectory(
    start_time=comet.elements.epoch,
    end_time=comet.elements.epoch + 365.25,  # 1 year
    num_points=50
)

print(f"\nCalculated {len(positions)} trajectory points")
print(f"First position: {positions[0]}")
print(f"Last position: {positions[-1]}")
```

### Option 3: Test Individual Modules

```bash
# Test data ingestion
python -m app.data.ingestion

# Test orbital mechanics
python -m app.models.orbital

# Test propagator
python -m app.physics.propagator
```

## Example Usage

### Find Periodic Comets

```python
from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc

# Load data
mpc_elements = load_mpc_data()
catalog = build_catalog_from_mpc(mpc_elements)

# Filter periodic comets
periodic = catalog.filter_periodic()
print(f"Found {len(periodic)} periodic comets")

# Show first 5
for comet in periodic[:5]:
    print(f"  {comet}")
    if comet.elements.eccentricity < 1.0:
        period_years = comet.elements.orbital_period / 365.25
        print(f"    Period: {period_years:.2f} years")
```

### Calculate Comet Position at Specific Time

```python
from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc
from app.physics.propagator import calculate_orbital_position
import numpy as np

# Load data
mpc_elements = load_mpc_data()
catalog = build_catalog_from_mpc(mpc_elements)

# Get a comet
comet = catalog.comets[0]

# Calculate position 100 days from epoch
time = comet.elements.epoch + 100
position = calculate_orbital_position(comet.elements, time)

print(f"Comet: {comet}")
print(f"Position at day 100:")
print(f"  X: {position[0]:.3f} AU")
print(f"  Y: {position[1]:.3f} AU")
print(f"  Z: {position[2]:.3f} AU")
print(f"  Distance from Sun: {np.linalg.norm(position):.3f} AU")
```

### Search for Specific Comet

```python
from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc

# Load data
mpc_elements = load_mpc_data()
catalog = build_catalog_from_mpc(mpc_elements)

# Search by name
results = catalog.search_by_name("Halley")
print(f"Found {len(results)} comets matching 'Halley'")

for comet in results:
    print(f"  {comet.full_name}")
```

### Compare Two Comets

```python
from app.data.ingestion import load_mpc_data
from app.core.integration import build_catalog_from_mpc
import numpy as np

# Load data
mpc_elements = load_mpc_data()
catalog = build_catalog_from_mpc(mpc_elements)

# Get two comets
comet1 = catalog.comets[0]
comet2 = catalog.comets[1]

print(f"Comet 1: {comet1}")
print(f"  Perihelion: {comet1.elements.perihelion_distance:.3f} AU")
print(f"  Eccentricity: {comet1.elements.eccentricity:.4f}")
print(f"  Inclination: {np.degrees(comet1.elements.inclination):.1f}°")

print(f"\nComet 2: {comet2}")
print(f"  Perihelion: {comet2.elements.perihelion_distance:.3f} AU")
print(f"  Eccentricity: {comet2.elements.eccentricity:.4f}")
print(f"  Inclination: {np.degrees(comet2.elements.inclination):.1f}°")
```

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   └── integration.py      # MPC → Keplerian conversion
│   ├── data/
│   │   └── ingestion.py        # Download and parse MPC data
│   ├── models/
│   │   ├── comet.py            # Comet data model
│   │   └── orbital.py          # Orbital elements
│   └── physics/
│       └── propagator.py       # Trajectory calculation
├── data/
│   └── CometEls.txt            # Downloaded MPC data (auto-created)
├── test_phase1.py              # Integration tests
└── requirements.txt            # Dependencies
```

## Common Issues

### Issue: "Module not found"

**Solution**: Make sure you're in the `backend` directory:
```bash
cd backend
python test_phase1.py
```

### Issue: "pip: command not found"

**Solution**: Use `pip3` instead:
```bash
pip3 install numpy scipy requests
```

### Issue: Download fails

**Solution**: Check internet connection and try again:
```python
from app.data.ingestion import download_mpc_data
download_mpc_data(force=True)  # Force re-download
```

### Issue: Parsing errors

**Solution**: These are normal for some special entries (fragments, etc.). The system handles them gracefully and continues parsing.

## Next Steps

### Learn More
- Read [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) for architecture details
- Read [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) for test results
- Read [PHASE2_PLAN.md](PHASE2_PLAN.md) for future plans

### Explore the Code
- `app/data/ingestion.py` - See how MPC data is parsed
- `app/models/orbital.py` - Learn about orbital mechanics
- `app/physics/propagator.py` - Understand trajectory calculation

### Contribute
- Add more test cases
- Improve documentation
- Optimize performance
- Add new features

### Phase 2 (Coming Soon)
- Install Poliastro: `pip install poliastro astropy spiceypy`
- Implement N-body propagation
- Build REST API
- Add SPICE kernel support

## Performance Tips

### Speed Up Data Loading
```python
# First run: downloads data
mpc_elements = load_mpc_data()

# Subsequent runs: uses cached file
mpc_elements = load_mpc_data()  # Fast!
```

### Reduce Trajectory Points
```python
# High resolution (slow)
positions, times = propagator.get_trajectory(
    start_time, end_time, num_points=1000
)

# Low resolution (fast)
positions, times = propagator.get_trajectory(
    start_time, end_time, num_points=50
)
```

### Filter Before Processing
```python
# Process only periodic comets
periodic = catalog.filter_periodic()
for comet in periodic:
    # Process...
    pass
```

## Troubleshooting

### Enable Debug Output

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code
from app.data.ingestion import load_mpc_data
mpc_elements = load_mpc_data()
```

### Check Data File

```bash
# Verify data file exists
ls -lh backend/data/CometEls.txt

# View first few lines
head backend/data/CometEls.txt

# Count comets
wc -l backend/data/CometEls.txt
```

### Verify Installation

```python
import numpy
import scipy
import requests

print(f"NumPy version: {numpy.__version__}")
print(f"SciPy version: {scipy.__version__}")
print(f"Requests version: {requests.__version__}")
```

## Getting Help

### Documentation
- [README.md](README.md) - Project overview
- [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) - Architecture
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design

### Code Examples
- [test_phase1.py](backend/test_phase1.py) - Integration tests
- Module `__main__` blocks - Self-contained examples

### Resources
- [MPC Format](https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html)
- [Orbital Mechanics](https://en.wikipedia.org/wiki/Orbital_elements)
- [NumPy Documentation](https://numpy.org/doc/)

## Summary

You now have a working comet trajectory system! You can:

✅ Download real comet data from MPC  
✅ Parse 1,141+ comet orbital elements  
✅ Calculate accurate trajectories  
✅ Search and filter comets  
✅ Analyze orbital parameters  

**Next**: Explore the code, run examples, and prepare for Phase 2!

---

**Questions?** Check the documentation or examine the test files for more examples.
