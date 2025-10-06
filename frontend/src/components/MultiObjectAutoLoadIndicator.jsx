import './MultiObjectAutoLoadIndicator.css'

/**
 * Visual indicator for multi-object auto-load status.
 * Shows per-object loading state and aggregate statistics.
 */
export default function MultiObjectAutoLoadIndicator({ 
  enabled,
  loadingStates = {},
  selectedObjects = [],
  activeLoads = 0,
  queuedLoads = 0,
  totalSegmentsLoaded = 0
}) {
  if (!enabled || selectedObjects.length === 0) {
    return null
  }

  const hasAnyActivity = activeLoads > 0 || queuedLoads > 0 || totalSegmentsLoaded > 0

  return (
    <div className="multi-auto-load-indicator">
      <div className="indicator-header">
        <span className="indicator-icon">🔄</span>
        <span className="indicator-title">Multi Auto-Load</span>
        <span className={`indicator-status ${activeLoads > 0 ? 'loading' : 'ready'}`}>
          {activeLoads > 0 ? `Loading ${activeLoads}` : 'Active'}
        </span>
      </div>

      {/* Aggregate stats */}
      {hasAnyActivity && (
        <div className="aggregate-stats">
          {totalSegmentsLoaded > 0 && (
            <div className="stat-item">
              <span className="stat-label">Total Segments:</span>
              <span className="stat-value">{totalSegmentsLoaded}</span>
            </div>
          )}
          {queuedLoads > 0 && (
            <div className="stat-item">
              <span className="stat-label">Queued:</span>
              <span className="stat-value">{queuedLoads}</span>
            </div>
          )}
        </div>
      )}

      {/* Per-object status */}
      <div className="objects-list">
        {selectedObjects.map(obj => {
          const state = loadingStates[obj.designation] || {}
          const hasActivity = state.isLoading || state.segmentsLoaded > 0 || state.error

          if (!hasActivity) return null

          return (
            <div key={obj.designation} className="object-status">
              <div className="object-name">{obj.designation}</div>
              <div className="object-indicators">
                {state.isLoading && (
                  <span className="loading-spinner" title="Loading...">⏳</span>
                )}
                {state.segmentsLoaded > 0 && !state.isLoading && (
                  <span className="segments-badge" title={`${state.segmentsLoaded} segments loaded`}>
                    +{state.segmentsLoaded}
                  </span>
                )}
                {state.error && (
                  <span className="error-indicator" title={state.error}>⚠️</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Show message if no activity yet */}
      {!hasAnyActivity && (
        <div className="no-activity-message">
          Monitoring {selectedObjects.length} object{selectedObjects.length > 1 ? 's' : ''}...
        </div>
      )}
    </div>
  )
}
