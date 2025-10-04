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
          <div className="info-grid">
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
        <h3>ℹ️ About</h3>
        <p className="info-text">
          This visualization shows the comet's trajectory calculated using 
          two-body orbital mechanics. The cyan line represents the comet's path, 
          and the magenta sphere shows its current position at epoch.
        </p>
        <p className="info-text">
          Data source: Minor Planet Center (MPC)
        </p>
      </div>
    </div>
  )
}
