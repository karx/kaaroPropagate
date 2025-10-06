# Comet Trajectory Visualization System

An interactive 3D solar system viewer that accurately plots the positions and future trajectories of all known comets using real astronomical data.

## Features

- **Real Data**: Ingests data from Minor Planet Center (MPC) with 1,141 comets
- **Accurate Physics**: Choose between fast two-body or accurate N-body propagation with planetary perturbations
- **SPICE Integration**: Uses JPL DE440 ephemeris for high-precision planetary positions
- **3D Visualization**: Interactive WebGL-based solar system viewer with planetary orbits
- **Method Comparison**: Switch between two-body and N-body methods to see the difference
- **Detailed Information**: View orbital parameters and trajectory statistics

## Project Status

✅ **Phase 2 Complete!** - N-body propagation with SPICE integration

- [x] Technical design and architecture
- [x] Project structure setup
- [x] Data ingestion module (MPC parser) - 1,141 comets loaded
- [x] Orbital propagation engine - Two-body and N-body methods ✨
- [x] SPICE integration - JPL DE440 ephemeris for planetary positions ✨
- [x] Integration testing - All tests passing
- [x] Backend API - FastAPI with method selection endpoint ✨
- [x] Frontend visualization - React + Three.js with planetary orbits ✨
- [x] Method comparison UI - Toggle between two-body and N-body ✨

🚀 **Live Demo**: [Frontend](https://5173--0199ad84-7027-76e5-80a1-b3d96a8105a5.us-east-1-01.gitpod.dev) | [API](https://8000--0199ad84-7027-76e5-80a1-b3d96a8105a5.us-east-1-01.gitpod.dev)

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip and npm

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Architecture

The system consists of three main layers:

1. **Data Ingestion**: Downloads and parses astronomical data from MPC and JPL
2. **Physics Engine**: Calculates orbital mechanics and propagates trajectories
3. **Visualization**: Renders 3D solar system with interactive controls

See [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) for detailed architecture documentation.

## Development Phases

### Phase 1: MVP ✅
- MPC data parser
- Basic two-body orbital propagation
- CLI testing interface

### Phase 2: Core Engine ✅
- Custom N-body propagator with DOP853 integrator
- Planetary perturbations (Jupiter, Saturn, Uranus, Neptune)
- JPL SPICE kernel support with DE440 ephemeris
- Method selection API endpoint

### Phase 3: Visualization ✅
- FastAPI backend with trajectory endpoints
- React + Three.js frontend
- Interactive 3D viewer with planetary orbits
- Method comparison UI

### Phase 4: Advanced Features (Future)
- Non-gravitational forces (radiation pressure, outgassing)
- Performance optimization and caching
- Search and filtering by orbital parameters
- Time animation controls

## Data Sources

- **Minor Planet Center**: https://www.minorplanetcenter.net/
- **JPL Small-Body Database**: https://ssd.jpl.nasa.gov/
- **JPL HORIZONS**: https://ssd.jpl.nasa.gov/horizons/

## License

MIT License - See LICENSE file for details

## Contributing

This is a learning project. Contributions and suggestions are welcome!

## Documentation

- [Technical Design](TECHNICAL_DESIGN.md) - Architecture and implementation details
- [API Documentation](docs/API.md) - Backend API reference (coming soon)
- [Physics Guide](docs/PHYSICS.md) - Orbital mechanics explanation (coming soon)
- [User Guide](docs/USER_GUIDE.md) - How to use the application (coming soon)
