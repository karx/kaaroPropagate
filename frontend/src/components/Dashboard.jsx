import { useState, useEffect } from 'react'
import './Dashboard.css'

export default function Dashboard({ onBack }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('https://8000--0199ad84-7027-76e5-80a1-b3d96a8105a5.us-east-1-01.gitpod.dev/dashboard')
      const result = await response.json()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchDashboardData()
    }, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>⚠️ Error Loading Dashboard</h2>
        <p>{error}</p>
        <button onClick={fetchDashboardData}>Retry</button>
      </div>
    )
  }

  if (!data) return null

  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy': return '#4ade80'
      case 'degraded': return '#fbbf24'
      case 'unhealthy': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getHealthIcon = (status) => {
    switch (status) {
      case 'healthy': return '✅'
      case 'degraded': return '⚠️'
      case 'unhealthy': return '❌'
      default: return '❓'
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>🔭 System Monitoring Dashboard</h1>
          <p className="dashboard-subtitle">Real-time API metrics and health status</p>
        </div>
        <div className="dashboard-controls">
          {onBack && (
            <button onClick={onBack} className="back-btn">
              ← Back to Visualization
            </button>
          )}
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (5s)
          </label>
          <button onClick={fetchDashboardData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* System Health */}
      <div className="dashboard-section">
        <h2>System Health</h2>
        <div className="health-grid">
          <div className="health-card" style={{ borderColor: getHealthColor(data.health.status) }}>
            <div className="health-icon">{getHealthIcon(data.health.status)}</div>
            <div className="health-info">
              <div className="health-label">Overall Status</div>
              <div className="health-value" style={{ color: getHealthColor(data.health.status) }}>
                {data.health.status.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="health-card">
            <div className="health-icon">📚</div>
            <div className="health-info">
              <div className="health-label">Catalog</div>
              <div className="health-value">
                {data.health.catalog_loaded ? `${data.health.catalog_size} comets` : 'Not loaded'}
              </div>
            </div>
          </div>

          <div className="health-card">
            <div className="health-icon">🛰️</div>
            <div className="health-info">
              <div className="health-label">SPICE Kernels</div>
              <div className="health-value">
                {data.health.spice_available ? 'Available' : 'Unavailable'}
              </div>
            </div>
          </div>

          <div className="health-card">
            <div className="health-icon">⏰</div>
            <div className="health-info">
              <div className="health-label">Last Updated</div>
              <div className="health-value timestamp">
                {new Date(data.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="dashboard-section">
        <h2>Key Performance Indicators</h2>
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-value">{data.kpis.total_requests.toLocaleString()}</div>
            <div className="kpi-label">Total Requests</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-value">{data.kpis.total_calculations.toLocaleString()}</div>
            <div className="kpi-label">Trajectory Calculations</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-value">{data.kpis.total_errors.toLocaleString()}</div>
            <div className="kpi-label">Total Errors</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-value" style={{ color: data.kpis.error_rate_percent > 5 ? '#ef4444' : '#4ade80' }}>
              {data.kpis.error_rate_percent}%
            </div>
            <div className="kpi-label">Error Rate</div>
          </div>
        </div>
      </div>

      {/* Calculation Performance */}
      <div className="dashboard-section">
        <h2>Calculation Performance</h2>
        <div className="performance-grid">
          <div className="performance-card">
            <h3>Two-Body Method</h3>
            <div className="performance-stats">
              <div className="stat-row">
                <span className="stat-label">Count:</span>
                <span className="stat-value">{data.calculations.twobody.count}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Percentage:</span>
                <span className="stat-value">{data.calculations.twobody.percentage}%</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Avg Time:</span>
                <span className="stat-value highlight">{data.calculations.twobody.avg_time_ms} ms</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Total Time:</span>
                <span className="stat-value">{data.calculations.twobody.total_time_s} s</span>
              </div>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill twobody"
                style={{ width: `${data.calculations.twobody.percentage}%` }}
              ></div>
            </div>
          </div>

          <div className="performance-card">
            <h3>N-Body Method</h3>
            <div className="performance-stats">
              <div className="stat-row">
                <span className="stat-label">Count:</span>
                <span className="stat-value">{data.calculations.nbody.count}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Percentage:</span>
                <span className="stat-value">{data.calculations.nbody.percentage}%</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Avg Time:</span>
                <span className="stat-value highlight">{data.calculations.nbody.avg_time_ms} ms</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Total Time:</span>
                <span className="stat-value">{data.calculations.nbody.total_time_s} s</span>
              </div>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill nbody"
                style={{ width: `${data.calculations.nbody.percentage}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Request Distribution */}
      <div className="dashboard-section">
        <h2>Request Distribution</h2>
        <div className="request-list">
          {Object.entries(data.requests.by_endpoint)
            .sort((a, b) => b[1] - a[1])
            .map(([endpoint, count]) => (
              <div key={endpoint} className="request-item">
                <div className="request-endpoint">{endpoint}</div>
                <div className="request-count">{count}</div>
                <div className="request-bar">
                  <div 
                    className="request-bar-fill"
                    style={{ width: `${(count / data.requests.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Recent Errors */}
      {data.errors.total > 0 && (
        <div className="dashboard-section">
          <h2>Recent Errors</h2>
          <div className="errors-summary">
            <div className="error-types">
              {Object.entries(data.errors.by_type).map(([type, count]) => (
                <div key={type} className="error-type-badge">
                  <span className="error-type-name">{type}</span>
                  <span className="error-type-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
          {data.errors.recent.length > 0 && (
            <div className="error-list">
              {data.errors.recent.map((error, idx) => (
                <div key={idx} className="error-item">
                  <div className="error-header">
                    <span className="error-type">{error.type}</span>
                    <span className="error-time">
                      {new Date(error.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="error-message">{error.message}</div>
                  {error.details && Object.keys(error.details).length > 0 && (
                    <div className="error-details">
                      {Object.entries(error.details).map(([key, value]) => (
                        <span key={key} className="error-detail">
                          {key}: {value}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
