import { useState } from 'react'
import './AutoLoadSettings.css'

/**
 * Settings panel for auto-load configuration.
 * Allows users to customize auto-load behavior.
 */
export default function AutoLoadSettings({ 
  enabled,
  onEnabledChange,
  settings,
  onSettingsChange,
  onClose
}) {
  const [localSettings, setLocalSettings] = useState(settings || {
    thresholdPercent: 0.8,
    timeBeforeEndSeconds: 5,
    segmentDurationDays: 365,
    segmentPoints: 100,
    maxPoints: 10000
  })

  const handleSave = () => {
    onSettingsChange(localSettings)
    onClose()
  }

  const handleReset = () => {
    const defaults = {
      thresholdPercent: 0.8,
      timeBeforeEndSeconds: 5,
      segmentDurationDays: 365,
      segmentPoints: 100,
      maxPoints: 10000
    }
    setLocalSettings(defaults)
    onSettingsChange(defaults)
  }

  return (
    <div className="auto-load-settings-overlay" onClick={onClose}>
      <div className="auto-load-settings-panel" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h3>🔄 Auto-Load Settings</h3>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="settings-content">
          {/* Enable/Disable */}
          <div className="setting-group">
            <label className="setting-toggle">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => onEnabledChange(e.target.checked)}
              />
              <span className="toggle-label">Enable Auto-Load</span>
            </label>
            <p className="setting-description">
              Automatically load more trajectory data as animation progresses
            </p>
          </div>

          <div className="settings-divider" />

          {/* Trigger Settings */}
          <div className="setting-group">
            <h4>Trigger Conditions</h4>
            
            <div className="setting-item">
              <label>
                <span className="setting-label">Threshold</span>
                <span className="setting-value">{(localSettings.thresholdPercent * 100).toFixed(0)}%</span>
              </label>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={localSettings.thresholdPercent}
                onChange={(e) => setLocalSettings({
                  ...localSettings,
                  thresholdPercent: parseFloat(e.target.value)
                })}
                disabled={!enabled}
              />
              <p className="setting-hint">
                Load next segment when {(localSettings.thresholdPercent * 100).toFixed(0)}% through current segment
              </p>
            </div>

            <div className="setting-item">
              <label>
                <span className="setting-label">Time Buffer</span>
                <span className="setting-value">{localSettings.timeBeforeEndSeconds}s</span>
              </label>
              <input
                type="range"
                min="1"
                max="15"
                step="1"
                value={localSettings.timeBeforeEndSeconds}
                onChange={(e) => setLocalSettings({
                  ...localSettings,
                  timeBeforeEndSeconds: parseInt(e.target.value)
                })}
                disabled={!enabled}
              />
              <p className="setting-hint">
                Load when {localSettings.timeBeforeEndSeconds} seconds remain at current speed
              </p>
            </div>
          </div>

          <div className="settings-divider" />

          {/* Segment Settings */}
          <div className="setting-group">
            <h4>Segment Configuration</h4>
            
            <div className="setting-item">
              <label>
                <span className="setting-label">Duration</span>
                <span className="setting-value">{localSettings.segmentDurationDays} days</span>
              </label>
              <input
                type="range"
                min="30"
                max="1000"
                step="30"
                value={localSettings.segmentDurationDays}
                onChange={(e) => setLocalSettings({
                  ...localSettings,
                  segmentDurationDays: parseInt(e.target.value)
                })}
                disabled={!enabled}
              />
              <p className="setting-hint">
                Each segment covers {(localSettings.segmentDurationDays / 365.25).toFixed(1)} years
              </p>
            </div>

            <div className="setting-item">
              <label>
                <span className="setting-label">Points per Segment</span>
                <span className="setting-value">{localSettings.segmentPoints}</span>
              </label>
              <input
                type="range"
                min="50"
                max="500"
                step="50"
                value={localSettings.segmentPoints}
                onChange={(e) => setLocalSettings({
                  ...localSettings,
                  segmentPoints: parseInt(e.target.value)
                })}
                disabled={!enabled}
              />
              <p className="setting-hint">
                Higher values = smoother trajectory, slower loading
              </p>
            </div>
          </div>

          <div className="settings-divider" />

          {/* Memory Management */}
          <div className="setting-group">
            <h4>Memory Management</h4>
            
            <div className="setting-item">
              <label>
                <span className="setting-label">Max Points</span>
                <span className="setting-value">{localSettings.maxPoints.toLocaleString()}</span>
              </label>
              <input
                type="range"
                min="5000"
                max="50000"
                step="5000"
                value={localSettings.maxPoints}
                onChange={(e) => setLocalSettings({
                  ...localSettings,
                  maxPoints: parseInt(e.target.value)
                })}
                disabled={!enabled}
              />
              <p className="setting-hint">
                Older points are removed when limit is reached (sliding window)
              </p>
            </div>
          </div>
        </div>

        <div className="settings-footer">
          <button className="button-secondary" onClick={handleReset}>
            Reset to Defaults
          </button>
          <button className="button-primary" onClick={handleSave}>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}
