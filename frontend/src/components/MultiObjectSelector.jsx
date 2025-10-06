import { useState, useEffect } from 'react'
import { fetchObjectsBatch } from '../api'
import './MultiObjectSelector.css'

const CATEGORIES = [
  { value: 'neo', label: 'Near-Earth Objects (NEOs)', color: '#FF4444' },
  { value: 'jupiter', label: 'Jupiter Family', color: '#4444FF' },
  { value: 'long_period', label: 'Long Period', color: '#44FF44' },
  { value: 'oort_cloud', label: 'Oort Cloud', color: '#FFFF44' },
  { value: 'hyperbolic', label: 'Hyperbolic', color: '#FF8844' }
]

function MultiObjectSelector({ onObjectsSelected, selectedObjects = [] }) {
  const [category, setCategory] = useState('neo')
  const [objects, setObjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [limit, setLimit] = useState(20)
  
  // Custom filters
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [qMax, setQMax] = useState('')
  const [periodMin, setPeriodMin] = useState('')
  const [periodMax, setPeriodMax] = useState('')

  useEffect(() => {
    loadObjects()
  }, [category, limit])

  const loadObjects = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params = {
        category,
        limit
      }
      
      // Add custom filters if advanced mode
      if (showAdvanced) {
        if (qMax) params.qMax = parseFloat(qMax)
        if (periodMin) params.periodMin = parseFloat(periodMin)
        if (periodMax) params.periodMax = parseFloat(periodMax)
      }
      
      const data = await fetchObjectsBatch(params)
      setObjects(data.objects || [])
    } catch (err) {
      console.error('Error loading objects:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleObject = (obj) => {
    const isSelected = selectedObjects.some(s => s.designation === obj.designation)
    
    if (isSelected) {
      onObjectsSelected(selectedObjects.filter(s => s.designation !== obj.designation))
    } else {
      onObjectsSelected([...selectedObjects, obj])
    }
  }

  const handleSelectAll = () => {
    const validObjects = objects.filter(obj => obj.orbital_elements)
    onObjectsSelected(validObjects)
  }

  const handleClearAll = () => {
    onObjectsSelected([])
  }

  const getCategoryColor = (cat) => {
    const category = CATEGORIES.find(c => c.value === cat)
    return category ? category.color : '#888888'
  }

  return (
    <div className="multi-object-selector">
      <div className="selector-header">
        <h3>Multi-Object Selection</h3>
        <div className="selection-count">
          {selectedObjects.length} selected
        </div>
      </div>

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

      <div className="limit-selector">
        <label>Limit:</label>
        <input
          type="number"
          value={limit}
          onChange={(e) => setLimit(parseInt(e.target.value))}
          min="1"
          max="100"
        />
      </div>

      <div className="advanced-toggle">
        <button onClick={() => setShowAdvanced(!showAdvanced)}>
          {showAdvanced ? '▼' : '▶'} Advanced Filters
        </button>
      </div>

      {showAdvanced && (
        <div className="advanced-filters">
          <div className="filter-row">
            <label>Max Perihelion (AU):</label>
            <input
              type="number"
              value={qMax}
              onChange={(e) => setQMax(e.target.value)}
              placeholder="e.g., 1.3"
              step="0.1"
            />
          </div>
          <div className="filter-row">
            <label>Period Range (years):</label>
            <input
              type="number"
              value={periodMin}
              onChange={(e) => setPeriodMin(e.target.value)}
              placeholder="Min"
              step="1"
            />
            <input
              type="number"
              value={periodMax}
              onChange={(e) => setPeriodMax(e.target.value)}
              placeholder="Max"
              step="1"
            />
          </div>
          <button onClick={loadObjects} className="apply-filters-btn">
            Apply Filters
          </button>
        </div>
      )}

      <div className="action-buttons">
        <button onClick={handleSelectAll} disabled={loading}>
          Select All
        </button>
        <button onClick={handleClearAll} disabled={selectedObjects.length === 0}>
          Clear All
        </button>
        <button onClick={loadObjects} disabled={loading}>
          Refresh
        </button>
      </div>

      {loading && <div className="loading">Loading objects...</div>}
      {error && <div className="error">Error: {error}</div>}

      <div className="objects-list">
        {objects.map(obj => {
          const isSelected = selectedObjects.some(s => s.designation === obj.designation)
          const hasElements = obj.orbital_elements !== null
          
          return (
            <div
              key={obj.designation}
              className={`object-item ${isSelected ? 'selected' : ''} ${!hasElements ? 'disabled' : ''}`}
              onClick={() => hasElements && handleToggleObject(obj)}
              style={{
                borderLeft: `4px solid ${getCategoryColor(category)}`
              }}
            >
              <div className="object-checkbox">
                <input
                  type="checkbox"
                  checked={isSelected}
                  disabled={!hasElements}
                  readOnly
                />
              </div>
              <div className="object-info">
                <div className="object-designation">
                  {obj.designation || obj.name}
                </div>
                {obj.orbital_elements && (
                  <div className="object-details">
                    q: {obj.orbital_elements.perihelion_distance?.toFixed(2)} AU
                    {obj.orbital_elements.period_years && (
                      <> • P: {obj.orbital_elements.period_years.toFixed(1)} yr</>
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
          No objects found for this category
        </div>
      )}
    </div>
  )
}

export default MultiObjectSelector
