import './AutoLoadIndicator.css'

/**
 * Visual indicator for auto-load status.
 * Shows loading progress, segments loaded, and errors.
 */
export default function AutoLoadIndicator({ 
  enabled, 
  isLoading, 
  loadProgress, 
  segmentsLoaded, 
  error,
  trajectory 
}) {
  if (!enabled) {
    return null
  }

  const totalPoints = trajectory?.trajectory?.length || 0
  const hasData = totalPoints > 0

  return (
    <div className="auto-load-indicator">
      <div className="indicator-header">
        <span className="indicator-icon">🔄</span>
        <span className="indicator-title">Auto-Load</span>
        <span className={`indicator-status ${isLoading ? 'loading' : 'ready'}`}>
          {isLoading ? 'Loading...' : 'Active'}
        </span>
      </div>

      {isLoading && (
        <div className="loading-bar-container">
          <div 
            className="loading-bar" 
            style={{ width: `${loadProgress}%` }}
          />
        </div>
      )}

      <div className="indicator-stats">
        {segmentsLoaded > 0 && (
          <div className="stat-item">
            <span className="stat-label">Segments:</span>
            <span className="stat-value">{segmentsLoaded}</span>
          </div>
        )}
        
        {hasData && (
          <div className="stat-item">
            <span className="stat-label">Points:</span>
            <span className="stat-value">{totalPoints.toLocaleString()}</span>
          </div>
        )}
      </div>

      {error && (
        <div className="indicator-error">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
        </div>
      )}

      {!isLoading && !error && segmentsLoaded > 0 && (
        <div className="indicator-success">
          ✅ {segmentsLoaded} segment{segmentsLoaded > 1 ? 's' : ''} loaded
        </div>
      )}
    </div>
  )
}
