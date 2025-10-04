# Comet Visualization Backend

Python backend for comet trajectory calculation and data processing.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes and WebSocket handlers
│   ├── core/         # Configuration and caching
│   ├── data/         # Data ingestion (MPC, JPL, SPICE)
│   ├── models/       # Data models (Comet, OrbitalElements)
│   └── physics/      # Propagation engine and physics models
├── tests/            # Unit and integration tests
└── data/             # Downloaded data files (not in git)
```

## Running Tests

```bash
pytest
pytest --cov=app tests/  # With coverage
```

## Development

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

## Phase 1 Goals

- [x] Project structure
- [ ] MPC data parser
- [ ] Orbital element data model
- [ ] Two-body propagation engine
- [ ] CLI testing interface
