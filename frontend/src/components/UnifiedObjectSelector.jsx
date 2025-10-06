import { useState, useEffect } from 'react'
import { fetchComets, fetchObjectsBatch } from '../api'
import './UnifiedObjectSelector.css'

const CATEGORIES = [
  { value: 'all', label: 'All Comets', color: '#888888' },
  { value: 'neo', label: 'Near-Earth Objects', color: '#FF4444' },
  { value: 'jupiter', label: 'Jupiter Family', color: '#4444FF' },
  { value: 'long_period', label: 'Long Period', color: '#44FF44' },
  { value: 'oort_cloud', label: 'Oort Cloud', color: '#FFFF44' },
  { value: 'hyperbolic', label: 'Hyperbolic', color: '#FF8844' }
]

function UnifiedObjectSelector({
  multiMode,
  onToggleMode,
  selectedObject,
  onSelectObject,
  selectedObjects,
  onSelectMultiple,
  onFetchMultiple,
  onClearSelection
}) {
  const [category, setCategory] = useState('all')
  const [objects, setObjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [limit, setLimit] = useState(50)

  useEffect(() => {
    loadObjects()
  }, [category, limit, multiMode])

  const loadObjects = async () => {
    try {
      setLoading(true)
      setError(null)
      
      let data
      if (category === 'all' || !multiMode) {
        // Load regular comet list
        data = await fetchComets({ limit })
        setObjects(data.comets || [])
      } else {
        // Load filtered objects by category
        data = await fetchObjectsBatch({ category, limit })
        setObjects(data.objects || [])
      }
    } catch (err) {
      console.error('Error loading objects:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleObjectClick = (obj) => {
    if (multiMode) {
      // Multi-select mode
      const isSelected = selectedObjects.some(s => s.designation === obj.designation)
      if (isSelected) {
        onSelectMultiple(selectedObjects.filter(s => s.designation !== obj.designation))
      } else {
        onSelectMultiple([...selectedObjects, obj])
      }
    } else {
      // Single select mode
      onSelectObject(obj)
    }
  }

  const handleSelectAll = () => {
    const validObjects = objects.filter(obj => obj.orbital_elements)
    onSelectMultiple(validObjects)
  }

  const handleClearAll = () => {
    if (multiMode) {
      onClearSelection()
    } else {
      onSelectObject(null)
    }
  }

  const getCategoryColor = (cat) => {
    const category = CATEGORIES.find(c => c.value === cat)
    return category ? category.color : '#888888'
  }

  const isObjectSelected = (obj) => {
    if (multiMode) {
      return selectedObjects.some(s => s.designation === obj.designation)
    } else {
      return selectedObject?.designation === obj.designation
    }
  }

  return (
    <div className="unified-selector">
      <div className="selector-header">
        <h3>🔭 {multiMode ? 'Select Objects' : 'Select Comet'}</h3>
        <button
          className={`mode-toggle ${multiMode ? 'multi' : 'single'}`}
          onClick={onToggleMode}
          title={multiMode ? 'Switch to single mode' : 'Switch to multi mode'}
        >
          {multiMode ? '📊 Multi' : '🎯 Single'}
        </button>
      </div>

      {multiMode && (
        <>
          <div className="category-selector">
            <label>Category:</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="selection-info">
            <span className="selection-count">
              {selectedObjects.length} selected
            </span>
            <div className="action-buttons-inline">
              <button 
                onClick={onFetchMultiple} 
                disabled={selectedObjects.length === 0} 
                className="btn-small btn-primary"
              >
                Fetch
              </button>
              <button onClick={handleSelectAll} disabled={loading} className="btn-small">
                All
              </button>
              <button onClick={handleClearAll} disabled={selectedObjects.length === 0} className="btn-small">
                Clear
              </button>
            </div>
          </div>
        </>
      )}

      {loading && <div className="loading-indicator">Loading...</div>}
      {error && <div className="error-message">Error: {error}</div>}

      <div className="objects-list">
        {objects.map(obj => {
          const isSelected = isObjectSelected(obj)
          const hasElements = obj.orbital_elements !== null
          
          return (
            <div
              key={obj.designation}
              className={`object-item ${isSelected ? 'selected' : ''} ${!hasElements ? 'disabled' : ''}`}
              onClick={() => hasElements && handleObjectClick(obj)}
              style={{
                borderLeft: multiMode ? `4px solid ${getCategoryColor(category)}` : 'none'
              }}
            >
              {multiMode && (
                <div className="object-checkbox">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    disabled={!hasElements}
                    readOnly
                  />
                </div>
              )}
              <div className="object-info">
                <div className="object-name">
                  {obj.orbit_type ? `${obj.orbit_type}/` : ''}{obj.designation || obj.name}
                </div>
                {obj.orbital_elements && (
                  <div className="object-details">
                    <span>e: {obj.orbital_elements.eccentricity.toFixed(3)}</span>
                    <span>q: {obj.orbital_elements.perihelion_distance.toFixed(2)} AU</span>
                    {obj.orbital_elements.period_years && (
                      <span>P: {obj.orbital_elements.period_years.toFixed(1)} yr</span>
                    )}
                  </div>
                )}
                {!hasElements && (
                  <div className="object-details error">No orbital elements</div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {objects.length === 0 && !loading && (
        <div className="no-objects">
          No objects found
        </div>
      )}
    </div>
  )
}

export default UnifiedObjectSelector
