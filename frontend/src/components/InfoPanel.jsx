import './InfoPanel.css'

export default function InfoPanel({ comet, trajectory }) {
  if (!comet) {
    return (
      <div className="info-panel">
        <div className="info-section">
          <h3>No comet selected</h3>
          <p>Select a comet from the list to view details</p>
        </div>
      </div>
    )
  }

  const elements = comet.orbital_elements

  return (
    <div className="info-panel">
      <div className="info-section">
        <h3>📊 Comet Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Designation:</span>
            <span className="info-value">{comet.designation}</span>
          </div>
          
          {comet.name && comet.name !== comet.designation && (
            <div className="info-item">
              <span className="info-label">Name:</span>
              <span className="info-value">{comet.name}</span>
            </div>
          )}
          
          <div className="info-item">
            <span className="info-label">Type:</span>
            <span className="info-value">
              {comet.orbit_type === 'P' ? 'Periodic' : 
               comet.orbit_type === 'C' ? 'Long-period' : 
               comet.orbit_type}
            </span>
          </div>
          
          {comet.periodic_number && (
            <div className="info-item">
              <span className="info-label">Number:</span>
              <span className="info-value">{comet.periodic_number}P</span>
            </div>
          )}
        </div>
      </div>

      {elements && (
        <div className="info-section">
          <h3>🌌 Orbital Elements</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Semi-major axis (a):</span>
              <span className="info-value">{elements.semi_major_axis.toFixed(3)} AU</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">Eccentricity (e):</span>
              <span className="info-value">{elements.eccentricity.toFixed(4)}</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">Inclination (i):</span>
              <span className="info-value">{elements.inclination_deg.toFixed(2)}°</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">Perihelion (q):</span>
              <span className="info-value">{elements.perihelion_distance.toFixed(3)} AU</span>
            </div>
            
            {elements.aphelion_distance && elements.aphelion_distance !== Infinity && (
              <div className="info-item">
                <span className="info-label">Aphelion (Q):</span>
                <span className="info-value">{elements.aphelion_distance.toFixed(3)} AU</span>
              </div>
            )}
            
            {elements.period_years && (
              <div className="info-item">
                <span className="info-label">Period:</span>
                <span className="info-value">{elements.period_years.toFixed(2)} years</span>
              </div>
            )}
          </div>
        </div>
      )}

      {trajectory && (
        <div className="info-section">
          <h3>📈 Trajectory Info</h3>
          
          <div className="data-source-badge">
            <div className="badge-header">
              <span className="badge-icon">🔬</span>
              <span className="badge-title">Data Source</span>
            </div>
            <div className="badge-content">
              <div className="badge-item">
                <strong>Orbital Elements:</strong> Minor Planet Center (MPC)
              </div>
              <div className="badge-item">
                <strong>Epoch:</strong> {new Date((trajectory.start_time - 2440587.5) * 86400000).toLocaleDateString()}
              </div>
              <div className="badge-item">
                <strong>Calculation:</strong> {trajectory.method === 'twobody' ? 'Two-Body Keplerian' : 'N-Body with Perturbations'}
              </div>
              <div className="badge-item">
                <strong>Status:</strong> <span className="calculated-badge">CALCULATED</span>
              </div>
            </div>
          </div>
          
          <div className="info-grid">
            {trajectory.method && (
              <div className="info-item">
                <span className="info-label">Method:</span>
                <span className="info-value">
                  {trajectory.method === 'twobody' ? 'Two-Body' : 'N-Body'}
                </span>
              </div>
            )}
            
            <div className="info-item">
              <span className="info-label">Time span:</span>
              <span className="info-value">{trajectory.days} days</span>
            </div>
            
            <div className="info-item">
              <span className="info-label">Data points:</span>
              <span className="info-value">{trajectory.points}</span>
            </div>
            
            {trajectory.trajectory && trajectory.trajectory.length > 0 && (
              <>
                <div className="info-item">
                  <span className="info-label">Min distance:</span>
                  <span className="info-value">
                    {Math.min(...trajectory.trajectory.map(p => p.distance_from_sun)).toFixed(3)} AU
                  </span>
                </div>
                
                <div className="info-item">
                  <span className="info-label">Max distance:</span>
                  <span className="info-value">
                    {Math.max(...trajectory.trajectory.map(p => p.distance_from_sun)).toFixed(3)} AU
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="info-section">
        <h3>ℹ️ Understanding the Data</h3>
        
        <div className="help-box">
          <div className="help-title">📊 What You're Seeing</div>
          <p className="info-text">
            The visualization shows the <strong>calculated trajectory</strong> of the comet 
            based on its orbital elements from the Minor Planet Center (MPC). The position 
            at epoch (reference time) is the most accurate, with uncertainty increasing 
            over time.
          </p>
        </div>

        <div className="help-box">
          <div className="help-title">🔬 Calculation Methods</div>
          <p className="info-text">
            <strong>Two-Body:</strong> Fast Keplerian orbit assuming only Sun's gravity. 
            Good for short-term predictions (&lt;1 year). Calculation time: ~2ms.
          </p>
          <p className="info-text">
            <strong>N-Body:</strong> Includes gravitational effects from Jupiter, Saturn, 
            Uranus, and Neptune. More accurate for long-term predictions. 
            Calculation time: ~1-2s.
          </p>
        </div>

        <div className="help-box">
          <div className="help-title">⚠️ Accuracy Notes</div>
          <p className="info-text">
            • Orbital elements are from MPC observations<br/>
            • Two-body accuracy decreases beyond 1 year<br/>
            • N-body includes major planets only<br/>
            • Non-gravitational forces (outgassing) not included<br/>
            • Use comparison mode to see the difference
          </p>
        </div>

        <p className="info-text" style={{ marginTop: '12px', fontSize: '11px', color: '#888' }}>
          Data: Minor Planet Center (MPC) • Ephemeris: JPL DE440 • Validated: Energy conservation &lt;1e-6
        </p>
      </div>
    </div>
  )
}
