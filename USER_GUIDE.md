# Comet Trajectory Visualization Tool - User Guide

## Overview

The Comet Trajectory Visualization Tool is an interactive 3D application for visualizing and analyzing comet trajectories in our solar system. It combines real astronomical data with advanced orbital mechanics to provide accurate, real-time simulations of comet paths and planetary positions.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Features](#features)
4. [Visualization Modes](#visualization-modes)
5. [Controls and Navigation](#controls-and-navigation)
6. [Understanding the Data](#understanding-the-data)
7. [Advanced Features](#advanced-features)
8. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### Accessing the Application

The application runs in your web browser and consists of two main components:
- **Backend API**: Runs on port 8000 (handles data and calculations)
- **Frontend UI**: Runs on port 5173 (the visual interface)

### First Launch

When you first open the application:
1. The system loads comet data from the Minor Planet Center (MPC)
2. The first comet is automatically selected
3. Its trajectory is calculated and displayed in 3D space
4. Planets are positioned at their current orbital locations

---

## Interface Overview

### Main Layout

The interface is divided into three main sections:

```
┌─────────────────────────────────────────────────────────┐
│  🌠 Comet Trajectory Visualization                      │
├──────────────┬──────────────────────────┬───────────────┤
│              │                          │               │
│  Left Panel  │    3D Visualization      │  Right Panel  │
│              │                          │               │
│  - Object    │    - Solar System        │  - Comet Info │
│    Selector  │    - Trajectories        │  - Physics    │
│  - Controls  │    - Planets             │    Data       │
│              │    - Animations          │               │
│              │                          │               │
└──────────────┴──────────────────────────┴───────────────┘
│                 Animation Controls                      │
└─────────────────────────────────────────────────────────┘
```

### Left Panel

**Unified Object Selector**
- Toggle between Single Mode (🎯) and Multi Mode (📊)
- Search and select comets from the catalog
- Filter by category in multi-mode
- View selection count and controls

**Trajectory Parameters**
- **Days**: Duration of trajectory (30-3650 days)
- **Points**: Number of calculation points (50-500)
- **Method**: 
  - Two-Body: Fast Keplerian orbit
  - N-Body: Includes planetary perturbations
- **Compare Methods**: View both methods simultaneously (single mode only)

### Center Panel (3D Visualization)

**Celestial Objects**
- ☀️ **Sun**: Central star with procedural texture
- 🪐 **Planets**: All 8 planets with realistic textures and orbits
- ☄️ **Comets**: Selected objects with trajectory paths

**Visual Elements**
- Orbital paths (elliptical orbits)
- Current position markers
- Trajectory trails
- Velocity vectors (green arrows)
- Perihelion markers (yellow - closest point to Sun)
- Aphelion markers (blue - farthest point from Sun)

### Right Panel

**Comet Information**
- Name and designation
- Orbital type (Periodic, Hyperbolic, etc.)
- Orbital elements (semi-major axis, eccentricity, etc.)
- Perihelion distance and date

**Physics Data** (Single Mode)
- Current distance from Sun
- Current velocity
- Legend for visual markers

### Bottom Panel

**Animation Controls**
- ▶️ Play/⏸️ Pause button
- Timeline scrubber (drag to any point in time)
- Speed controls (0.5x, 1x, 2x, 5x)
- Time display (days and years from epoch)

---

## Features

### 1. Single Object Mode

**Purpose**: Detailed analysis of individual comets

**How to Use**:
1. Ensure "Single Mode" is active (🎯 button)
2. Click on any comet in the list
3. The trajectory is automatically calculated and displayed
4. Use animation controls to see motion over time

**What You See**:
- Complete orbital path
- Current position marker (colored sphere with glow)
- Velocity vector (green arrow showing direction and speed)
- Perihelion point (yellow marker)
- Aphelion point (blue marker)
- Trail showing path traveled

**Key Features**:
- Real-time physics data
- Method comparison (Two-Body vs N-Body)
- Detailed orbital information
- Animation with time synchronization

### 2. Multi-Object Mode

**Purpose**: Compare multiple comets simultaneously

**How to Use**:
1. Click the mode toggle to switch to "Multi Mode" (📊)
2. Select category filter (optional)
3. Check boxes next to comets you want to visualize
4. Click "Fetch" to load trajectories
5. Each object gets a unique color

**What You See**:
- Multiple trajectory paths in different colors
- Legend showing object names and colors
- All objects animate synchronously
- Shared timeline

**Key Features**:
- Up to 50+ objects simultaneously
- Category filtering (NEO, Jupiter Family, etc.)
- Batch trajectory calculation
- Color-coded visualization
- Selection management (All, Clear buttons)

### 3. Planet Visualization

**Real-Time Positions**:
- Planets move along their actual orbits
- Positions calculated using Keplerian orbital mechanics
- Synchronized with trajectory time

**Visual Details**:
- Procedural textures for each planet
- Saturn's rings
- Atmosphere effects for gas giants
- Elliptical orbit paths
- Realistic sizes (scaled for visibility)

**Planets Included**:
- ☿️ Mercury (rocky, cratered)
- ♀️ Venus (bright, smooth)
- 🌍 Earth (blue, moderate roughness)
- ♂️ Mars (red, rocky)
- ♃ Jupiter (banded gas giant with Great Red Spot)
- ♄ Saturn (pale with iconic rings)
- ♅ Uranus (cyan ice giant)
- ♆ Neptune (deep blue ice giant)

---

## Visualization Modes

### Two-Body Method

**Description**: Simplified Keplerian orbit calculation

**Characteristics**:
- Fast computation
- Assumes only Sun's gravity
- Ideal for short-term predictions
- Smooth, elliptical orbits

**Best For**:
- Quick visualization
- Short time periods (< 1 year)
- Educational purposes
- Initial exploration

**Visual Indicator**: Green badge "⚡ Two-Body"

### N-Body Method

**Description**: Advanced calculation including planetary perturbations

**Characteristics**:
- Slower computation
- Includes Jupiter and Saturn's gravity
- More accurate for long-term predictions
- May show orbital perturbations

**Best For**:
- Scientific accuracy
- Long time periods (> 1 year)
- Close planetary encounters
- Research applications

**Visual Indicator**: Purple badge "🌌 N-Body"

### Comparison Mode

**Purpose**: See differences between methods

**How to Use**:
1. Select a comet in Single Mode
2. Check "Compare Methods" box
3. Two trajectories appear:
   - Cyan: Primary method
   - Yellow: Comparison method

**What to Look For**:
- Divergence over time
- Effect of planetary perturbations
- Accuracy differences
- Orbital stability

---

## Controls and Navigation

### 3D View Controls

**Mouse Controls**:
- **Left Click + Drag**: Rotate view around Sun
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Double Click**: Reset view

**Touch Controls** (mobile):
- **One Finger**: Rotate
- **Two Fingers**: Pan and zoom

**Keyboard Shortcuts**:
- `Space`: Play/Pause animation
- `←/→`: Step backward/forward in time
- `R`: Reset camera view

### Animation Controls

**Timeline Scrubber**:
- Drag the slider to jump to any point in time
- Shows current position along trajectory
- Updates all visual elements in real-time

**Speed Controls**:
- **0.5x**: Slow motion (good for detailed observation)
- **1x**: Normal speed
- **2x**: Fast forward
- **5x**: Very fast (good for long orbits)

**Play/Pause**:
- Click to start/stop animation
- Animation loops automatically
- All objects move synchronously

### Parameter Controls

**Days Slider**:
- Adjusts trajectory duration
- Range: 30 to 3650 days (10 years)
- Longer periods show more of the orbit
- Automatically recalculates trajectory

**Points Slider**:
- Controls calculation resolution
- Range: 50 to 500 points
- More points = smoother curves
- Higher values = slower calculation

**Method Selector**:
- Choose between Two-Body and N-Body
- Changes apply immediately
- Affects all future calculations

---

## Understanding the Data

### Orbital Elements

**Semi-Major Axis (a)**:
- Average distance from Sun
- Measured in AU (Astronomical Units)
- 1 AU = Earth-Sun distance

**Eccentricity (e)**:
- Shape of orbit
- 0 = perfect circle
- 0-1 = ellipse
- >1 = hyperbolic (escape trajectory)

**Inclination (i)**:
- Tilt of orbit relative to Earth's orbit
- Measured in degrees
- 0° = same plane as Earth

**Perihelion Distance (q)**:
- Closest approach to Sun
- Critical for comet activity
- Measured in AU

**Orbital Period**:
- Time to complete one orbit
- Calculated from semi-major axis
- Shown in years and days

### Physics Data

**Distance from Sun**:
- Real-time distance in AU
- Changes as comet moves
- Minimum at perihelion
- Maximum at aphelion

**Velocity**:
- Speed along trajectory
- Measured in AU/day
- Faster near perihelion
- Slower near aphelion

**Days from Epoch**:
- Time since reference date
- Used for position calculation
- Shown in animation controls

### Visual Markers

**Perihelion (Yellow)**:
- Closest point to Sun
- Comet is fastest here
- Often brightest point
- Small yellow sphere

**Aphelion (Blue)**:
- Farthest point from Sun
- Comet is slowest here
- Often dimmest point
- Small blue sphere

**Velocity Vector (Green)**:
- Shows direction of motion
- Arrow length indicates speed
- Always tangent to orbit
- Updates in real-time

---

## Advanced Features

### Batch Trajectory Calculation

**Purpose**: Efficiently calculate multiple trajectories

**How It Works**:
1. Select multiple objects in Multi Mode
2. Click "Fetch" button
3. Backend calculates all trajectories in parallel
4. Results cached for performance

**Performance**:
- Parallel processing for speed
- Caching reduces redundant calculations
- Handles 50+ objects smoothly
- Progress indicator during loading

### Category Filtering

**Available Categories**:
- **All Comets**: Complete catalog
- **Near-Earth Objects (NEO)**: q < 1.3 AU
- **Jupiter Family**: Short period, influenced by Jupiter
- **Long Period**: Orbital period > 200 years
- **Oort Cloud**: Very long period comets
- **Hyperbolic**: Escape trajectories (e > 1)

**How to Use**:
1. Switch to Multi Mode
2. Select category from dropdown
3. List updates automatically
4. Select objects to visualize

### Time Synchronization

**Feature**: All objects move together in time

**Benefits**:
- Compare relative positions
- See planetary encounters
- Understand orbital resonances
- Analyze close approaches

**Implementation**:
- Shared time index across all objects
- Synchronized animation frame
- Consistent epoch reference
- Real-time position updates

### Procedural Textures

**Sun**:
- Radial gradient (white to orange)
- Solar flares and spots
- Emissive glow effect
- Rotating surface

**Rocky Planets**:
- Impact craters (80 spots)
- Surface variation (40 light spots)
- Bump mapping for depth
- Realistic roughness

**Gas Giants**:
- Horizontal bands (15-25)
- Wave patterns
- Jupiter's Great Red Spot
- Atmosphere glow

**Comets**:
- Icy/rocky texture
- Dark spots for detail
- Emissive glow
- Tail effect (future feature)

---

## Tips and Best Practices

### Performance Optimization

**For Smooth Animation**:
- Use fewer points (100-200) for real-time animation
- Limit multi-object mode to 10-20 objects
- Close other browser tabs
- Use hardware acceleration if available

**For Detailed Analysis**:
- Use more points (300-500) for static views
- Pause animation when examining details
- Use single object mode for precision
- Enable method comparison for accuracy checks

### Visualization Tips

**Camera Positioning**:
- Start with default view (slightly above ecliptic plane)
- Zoom out to see outer planets
- Zoom in for inner solar system detail
- Use pan to center on specific objects

**Color Interpretation**:
- Brighter colors = more recent trajectory segments
- Faded colors = older trajectory segments
- Unique colors in multi-mode for easy identification
- Consistent colors for planets

**Time Selection**:
- Use scrubber for specific dates
- Play animation for motion understanding
- Pause at perihelion for closest approach
- Speed up for long-period comets

### Scientific Use

**Accuracy Considerations**:
- Two-Body: ±0.1 AU for short periods
- N-Body: ±0.01 AU for medium periods
- Longer predictions = lower accuracy
- Planetary encounters need N-Body method

**Data Validation**:
- Compare with JPL HORIZONS for verification
- Check orbital elements against MPC data
- Use method comparison to assess uncertainty
- Note epoch date for position calculations

**Research Applications**:
- Close approach analysis
- Orbital evolution studies
- Resonance identification
- Trajectory planning

### Troubleshooting

**Trajectory Not Showing**:
- Check if object has valid orbital elements
- Verify time range includes perihelion
- Try refreshing the page
- Check browser console for errors

**Slow Performance**:
- Reduce number of points
- Limit objects in multi-mode
- Close other applications
- Try different browser

**Animation Stuttering**:
- Pause and resume animation
- Reduce animation speed
- Clear browser cache
- Check system resources

**Planets Not Moving**:
- Verify animation is playing
- Check time range is changing
- Ensure trajectory is loaded
- Try reloading the page

---

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `Space` | Play/Pause animation |
| `←` | Step backward in time |
| `→` | Step forward in time |
| `R` | Reset camera view |
| `+` | Zoom in |
| `-` | Zoom out |
| `1-5` | Set animation speed (1=0.5x, 5=5x) |
| `M` | Toggle mode (Single/Multi) |
| `C` | Toggle method comparison |
| `Esc` | Clear selection |

---

## API Endpoints Reference

For developers and advanced users:

### Comet Data
- `GET /comets` - List all comets
- `GET /comets/{designation}` - Get specific comet
- `GET /comets/{designation}/trajectory` - Calculate trajectory
- `GET /comets/{designation}/position` - Get position at time

### Multi-Object
- `GET /api/objects/batch` - Get multiple objects
- `POST /api/trajectories/batch` - Calculate batch trajectories

### Planets
- `GET /api/planets/positions` - Get planet positions at time

### Statistics
- `GET /statistics` - Catalog statistics
- `GET /metrics` - Performance metrics

---

## Technical Specifications

### Coordinate System
- **Reference Frame**: Heliocentric ecliptic (J2000)
- **Units**: Astronomical Units (AU) and days
- **Epoch**: J2000.0 (JD 2451545.0)

### Calculation Methods
- **Two-Body**: Keplerian orbit propagation
- **N-Body**: Numerical integration with planetary perturbations
- **Planets**: Simplified Keplerian elements

### Data Sources
- **Comet Data**: Minor Planet Center (MPC)
- **Orbital Elements**: J2000 epoch
- **Planet Data**: NASA JPL ephemerides

### Browser Requirements
- Modern browser with WebGL support
- Minimum 4GB RAM recommended
- Hardware acceleration enabled
- JavaScript enabled

---

## Version Information

**Current Version**: 2.2

**Recent Updates**:
- Unified object selector
- Real-time planet positions
- Procedural textures
- Fixed orbital speeds
- Improved UI/UX
- Multi-object animation
- Performance optimizations

**Known Limitations**:
- Maximum 50 objects in multi-mode
- Accuracy decreases for very long periods
- No comet tail visualization (yet)
- Limited to major planets

---

## Support and Feedback

For questions, issues, or feature requests:
- Check the troubleshooting section
- Review the API documentation
- Examine browser console for errors
- Report issues with detailed descriptions

---

## Credits

**Developed by**: Ona AI Assistant
**Data Sources**: Minor Planet Center, NASA JPL
**Technologies**: React, Three.js, FastAPI, Python
**Orbital Mechanics**: Keplerian elements, N-body integration

---

*Last Updated: 2025-10-06*
*Version: 2.2*
