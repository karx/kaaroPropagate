# Comet Trajectory Visualization System

An interactive 3D solar system viewer that accurately plots the positions and future trajectories of all known comets using real astronomical data.

## Features

- **Real Data**: Ingests data from Minor Planet Center (MPC) and JPL Small-Body Database
- **Accurate Physics**: Implements orbital propagation with two-body and N-body models
- **3D Visualization**: Interactive WebGL-based solar system viewer
- **Time Travel**: Scrub through time to see past and future comet positions
- **Detailed Information**: View orbital parameters and physical characteristics

## Project Status

✅ **Web UI Complete!** - See [WEB_UI_COMPLETE.md](WEB_UI_COMPLETE.md) for details

- [x] Technical design and architecture
- [x] Project structure setup
- [x] Data ingestion module (MPC parser) - 1,141 comets loaded
- [x] Orbital propagation engine - Two-body propagation working
- [x] Integration testing - All tests passing
- [x] Backend API - FastAPI with REST endpoints ✨
- [x] Frontend visualization - React + Three.js 3D viewer ✨

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

### Phase 1: MVP (Current)
- MPC data parser
- Basic two-body orbital propagation
- CLI testing interface

### Phase 2: Core Engine
- Poliastro integration
- N-body perturbations
- JPL SPICE kernel support

### Phase 3: Visualization
- FastAPI backend
- React + Three.js frontend
- Interactive 3D viewer

### Phase 4: Advanced Features
- Non-gravitational forces
- Performance optimization
- Search and filtering

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
