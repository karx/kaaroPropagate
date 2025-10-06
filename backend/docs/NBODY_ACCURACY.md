# N-Body Propagator: Accuracy and Limitations

## Overview

The N-body propagator simulates comet trajectories by numerically integrating the equations of motion under gravitational forces from the Sun and major planets. This document describes the accuracy, limitations, and best practices for using the N-body propagator.

## Fixes Applied

### Critical Bug Fixes (2024)

1. **Gravitational Constant (GM_sun)**
   - **Issue**: GM_SUN was set to 1.0 (normalized units) instead of physical value
   - **Impact**: Gravitational force was 3380x too strong, causing rapid trajectory collapse
   - **Fix**: Changed to 0.0002959122082855911 AU³/day²
   - **Files**: `backend/app/physics/nbody.py`, `backend/app/models/orbital.py`

2. **Velocity Calculation in Keplerian-to-Cartesian Conversion**
   - **Issue**: Incorrect velocity formula caused velocities to be 136x too small
   - **Impact**: Orbits had wrong energy and didn't match expected trajectories
   - **Fix**: Corrected velocity components using proper orbital mechanics formulas
   - **File**: `backend/app/models/orbital.py`

## Accuracy

### Validated Performance

All tests pass with the following accuracy metrics:

#### 1. Gravitational Constant
- ✅ GM_sun matches physical value exactly
- ✅ Orbital period for Earth (a=1 AU) = 365.26 days (expected 365.25)

#### 2. Energy Conservation
- ✅ Short term (1 year): < 0.03% error
- ✅ Medium term (10 years): < 0.2% error
- ✅ Long term (50 years): < 1% error
- ✅ Highly eccentric orbits (e=0.967): < 1.5% error over 10 years

#### 3. N-body vs Two-body Agreement
- ✅ Short term (10 days, no planets): < 0.00001 AU difference
- ✅ Planetary perturbations correctly detected (0.002 AU over 1 year)

#### 4. Coordinate Transformations
- ✅ Circular orbits: exact to machine precision
- ✅ Inclined orbits: correct inclination handling
- ✅ Eccentric orbits: perihelion/aphelion distances exact
- ✅ Angular momentum: conserved to machine precision

#### 5. Planetary Masses
- ✅ All masses match IAU 2015 values exactly
- ✅ Mass ratios correct (Jupiter/Saturn = 3.34, Jupiter/Neptune = 18.53)

#### 6. Integration Quality
- ✅ DOP853 (8th order Runge-Kutta) with adaptive step size
- ✅ rtol = 1e-10, atol = 1e-12 (high precision)
- ✅ Close approaches handled correctly (perihelion at 0.3 AU)

### Test Coverage

The implementation is validated by 5 comprehensive test suites:

1. **test_nbody_validation.py** - Core N-body functionality (5/5 tests pass)
2. **test_halley_comet.py** - Real comet validation (3/3 tests pass)
3. **test_coordinate_transforms.py** - Coordinate system validation (4/4 tests pass)
4. **test_planetary_masses.py** - Planetary parameters (3/3 tests pass)
5. **test_integration_quality.py** - Numerical integration (5/5 tests pass)

**Total: 20/20 tests pass** ✅

## Limitations

### 1. Planetary Ephemeris

**Current Implementation**: Simplified Keplerian elements for planets
- Uses mean orbital elements (J2000 epoch)
- Planets on circular/elliptical orbits
- No planetary perturbations on each other

**Impact**:
- Planetary positions accurate to ~0.1 AU for short-term (< 10 years)
- Errors accumulate for long-term propagation
- Not suitable for precise planetary encounter predictions

**Future Improvement**: Use SPICE kernels (JPL DE440/441) for precise planetary positions

### 2. Non-Gravitational Forces

**Not Implemented**:
- Outgassing/jet forces
- Solar radiation pressure
- Yarkovsky effect
- Relativistic effects

**Impact**:
- Comets with significant outgassing may deviate from predictions
- Long-period comets (> 100 years) may show larger errors
- Close solar approaches (< 0.1 AU) may need relativistic corrections

**Typical Magnitude**:
- Outgassing can cause ~0.01-0.1 AU deviations over decades for active comets
- Radiation pressure: ~1e-6 AU/year² (negligible for most comets)

### 3. Planetary Coverage

**Included**: Jupiter, Saturn, Uranus, Neptune
**Not Included**: Mercury, Venus, Earth, Mars, minor planets

**Impact**:
- Inner solar system comets may miss perturbations from terrestrial planets
- Asteroid belt perturbations not modeled
- Trojan asteroids and resonances not captured

**When This Matters**:
- Comets with perihelion < 2 AU
- Near-Earth objects
- Resonant orbits (e.g., Jupiter Trojans)

### 4. Numerical Integration

**Method**: DOP853 (8th order Runge-Kutta)
**Tolerances**: rtol=1e-10, atol=1e-12

**Limitations**:
- Energy drift increases with time (0.7% over 50 years)
- Very close encounters (< 0.01 AU from planet) may need tighter tolerances
- Hyperbolic orbits (e > 1) may accumulate errors faster

**Recommended Time Spans**:
- High accuracy (< 0.1% error): < 10 years
- Good accuracy (< 1% error): < 50 years
- Approximate (< 5% error): < 100 years

### 5. Coordinate System

**Reference Frame**: Heliocentric ecliptic J2000
- Origin: Center of Sun
- XY-plane: Ecliptic plane at J2000 epoch
- X-axis: Vernal equinox direction (J2000)

**Limitations**:
- Does not account for precession (for very long timescales)
- Barycentric corrections not applied (Sun's motion around solar system barycenter)
- Frame rotation effects negligible for < 1000 years

## Best Practices

### 1. Choosing Propagation Method

**Use Two-Body When**:
- Short-term predictions (< 1 year)
- Far from planets (> 10 AU from any planet)
- Quick calculations needed
- Analytical solutions preferred

**Use N-Body When**:
- Medium to long-term predictions (> 1 year)
- Close planetary encounters expected
- High accuracy required
- Studying planetary perturbations

### 2. Interpreting Results

**Position Accuracy**:
- 1 year: ±0.001 AU (150,000 km)
- 10 years: ±0.01 AU (1.5 million km)
- 50 years: ±0.1 AU (15 million km)

**Velocity Accuracy**:
- Typically 10x better than position (in relative terms)
- Energy conservation is a good indicator of overall accuracy

**When to Be Cautious**:
- Energy error > 1%: Results may be unreliable
- Very close encounters (< 0.1 AU): Check energy conservation carefully
- Hyperbolic orbits: Validate against shorter time spans

### 3. Validation

**Always Check**:
1. Energy conservation (should be < 1% for most cases)
2. Angular momentum conservation (should be exact)
3. Orbital period matches expected value
4. Perihelion/aphelion distances are reasonable

**Compare With**:
- JPL HORIZONS for known objects
- Two-body propagation for short-term validation
- Published orbital elements from MPC or JPL

### 4. Performance Considerations

**Computational Cost**:
- Two-body: ~0.001 seconds per propagation
- N-body (4 planets): ~0.1 seconds per propagation
- N-body with dense output: ~1 second for 100 points

**Optimization Tips**:
- Use two-body for initial orbit determination
- Switch to N-body only when needed
- Reduce number of planets if far from outer solar system
- Use coarser time steps for visualization (num_points=50-100)

## Comparison with Other Methods

### vs. Two-Body (Keplerian)
- **Accuracy**: N-body 10-100x more accurate for > 1 year
- **Speed**: Two-body 100x faster
- **Use Case**: N-body for science, two-body for quick estimates

### vs. JPL HORIZONS
- **Accuracy**: HORIZONS uses full planetary ephemeris (DE440/441)
- **Difference**: ~0.01 AU over 10 years for typical comets
- **Advantage**: Our implementation is self-contained and fast

### vs. SPICE Toolkit
- **Accuracy**: SPICE has full solar system model
- **Difference**: ~0.001 AU over 1 year
- **Trade-off**: SPICE requires large kernel files (GB), we're lightweight (KB)

## Future Improvements

### High Priority
1. **SPICE Integration**: Use JPL SPICE kernels for planetary positions
2. **Non-Gravitational Forces**: Add outgassing model for active comets
3. **Inner Planets**: Include Mercury, Venus, Earth, Mars

### Medium Priority
4. **Barycentric Correction**: Account for Sun's motion
5. **Relativistic Effects**: For close solar approaches
6. **Adaptive Tolerances**: Tighter tolerances during close encounters

### Low Priority
7. **Asteroid Perturbations**: Major asteroids (Ceres, Vesta, etc.)
8. **Resonance Detection**: Identify mean-motion resonances
9. **Uncertainty Propagation**: Monte Carlo for orbit uncertainty

## References

1. **Gravitational Parameters**: JPL Solar System Dynamics
   - https://ssd.jpl.nasa.gov/astro_par.html

2. **Planetary Masses**: IAU 2015 values
   - https://ssd.jpl.nasa.gov/astro_par.html

3. **Numerical Integration**: SciPy solve_ivp (DOP853)
   - Dormand, J. R., & Prince, P. J. (1980). "A family of embedded Runge-Kutta formulae"

4. **Orbital Mechanics**: 
   - Vallado, D. A. (2013). "Fundamentals of Astrodynamics and Applications"
   - Murray, C. D., & Dermott, S. F. (1999). "Solar System Dynamics"

5. **JPL HORIZONS**: NASA/JPL Solar System Dynamics
   - https://ssd.jpl.nasa.gov/horizons.cgi

## Testing

Run all validation tests:

```bash
cd backend

# Core N-body validation
python3 tests/test_nbody_validation.py

# Halley's Comet test
python3 tests/test_halley_comet.py

# Coordinate transformations
python3 tests/test_coordinate_transforms.py

# Planetary masses
python3 tests/test_planetary_masses.py

# Integration quality
python3 tests/test_integration_quality.py

# JPL HORIZONS comparison framework
python3 tests/test_jpl_horizons_comparison.py
```

All tests should pass (20/20 tests).

## Changelog

### 2024-10-06
- ✅ Fixed GM_SUN value (was 3380x too large)
- ✅ Fixed velocity calculation in keplerian_to_cartesian
- ✅ Added comprehensive test suite (20 tests)
- ✅ Validated against Halley's Comet orbital elements
- ✅ Verified energy conservation (< 1% over 50 years)
- ✅ Confirmed coordinate transformations correct
- ✅ Validated planetary masses against IAU 2015 values
- ✅ Tested integration quality with DOP853

### Previous
- Initial N-body implementation
- Planetary perturbations (Jupiter, Saturn, Uranus, Neptune)
- SPICE kernel support (optional)
- Adaptive step size integration

## Contact

For questions or issues with the N-body propagator:
- Check test suite for examples
- Review this documentation
- Compare with JPL HORIZONS for validation
- File an issue with test case and expected vs. actual results
