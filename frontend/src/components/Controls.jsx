import './Controls.css'

export default function Controls({
  comets,
  selectedComet,
  onCometSelect,
  days,
  onDaysChange,
  points,
  onPointsChange
}) {
  return (
    <div className="controls">
      <div className="controls-section">
        <h3>🔭 Select Comet</h3>
        <div className="comet-list">
          {comets.map((comet) => (
            <button
              key={comet.designation}
              className={`comet-item ${selectedComet?.designation === comet.designation ? 'active' : ''}`}
              onClick={() => onCometSelect(comet)}
            >
              <div className="comet-name">
                {comet.orbit_type}/{comet.designation}
              </div>
              {comet.orbital_elements && (
                <div className="comet-details">
                  <span>e: {comet.orbital_elements.eccentricity.toFixed(3)}</span>
                  <span>q: {comet.orbital_elements.perihelion_distance.toFixed(2)} AU</span>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="controls-section">
        <h3>⏱️ Time Range</h3>
        <div className="control-group">
          <label>
            Days: {days}
            <input
              type="range"
              min="30"
              max="3650"
              step="30"
              value={days}
              onChange={(e) => onDaysChange(Number(e.target.value))}
            />
          </label>
          <div className="control-hint">
            {(days / 365.25).toFixed(1)} years
          </div>
        </div>

        <div className="control-group">
          <label>
            Points: {points}
            <input
              type="range"
              min="20"
              max="500"
              step="10"
              value={points}
              onChange={(e) => onPointsChange(Number(e.target.value))}
            />
          </label>
          <div className="control-hint">
            Trajectory resolution
          </div>
        </div>
      </div>

      <div className="controls-section">
        <h3>🎮 Controls</h3>
        <div className="help-text">
          <p><strong>Rotate:</strong> Left click + drag</p>
          <p><strong>Pan:</strong> Right click + drag</p>
          <p><strong>Zoom:</strong> Scroll wheel</p>
        </div>
      </div>
    </div>
  )
}
