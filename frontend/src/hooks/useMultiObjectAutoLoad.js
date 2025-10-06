import { useState, useEffect, useRef, useCallback } from 'react'
import { continueTrajectory } from '../api'

/**
 * Custom hook for automatic trajectory loading in multi-object mode.
 * 
 * Manages auto-load for multiple objects simultaneously with:
 * - Per-object loading state
 * - Queue-based loading with concurrent limit
 * - Independent trigger monitoring
 * - Memory management per object
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} Multi-object auto-load state and controls
 */
export function useMultiObjectAutoLoad({
  enabled = false,
  batchTrajectories = {},
  selectedObjects = [],
  currentTimeIndex = 0,
  animationSpeed = 1,
  animationPlaying = false,
  method = 'twobody',
  segmentDurationDays = 365,
  segmentPoints = 100,
  thresholdPercent = 0.8,
  timeBeforeEndSeconds = 5,
  maxPointsPerObject = 10000,
  maxConcurrentLoads = 2,
  onTrajectoriesUpdate = null,
  onError = null
} = {}) {
  
  // Per-object loading states
  const [loadingStates, setLoadingStates] = useState({})
  
  // Loading queue
  const [loadingQueue, setLoadingQueue] = useState([])
  const activeLoadsRef = useRef(new Set())
  
  // Track which objects are currently loading
  const loadingRef = useRef({})
  
  // Initialize loading states for all selected objects
  useEffect(() => {
    const newStates = {}
    selectedObjects.forEach(obj => {
      if (!loadingStates[obj.designation]) {
        newStates[obj.designation] = {
          isLoading: false,
          segmentsLoaded: 0,
          error: null,
          lastLoadTime: 0
        }
      } else {
        newStates[obj.designation] = loadingStates[obj.designation]
      }
    })
    
    // Remove states for objects no longer selected
    const selectedDesignations = new Set(selectedObjects.map(o => o.designation))
    Object.keys(loadingStates).forEach(designation => {
      if (selectedDesignations.has(designation)) {
        newStates[designation] = loadingStates[designation]
      }
    })
    
    setLoadingStates(newStates)
  }, [selectedObjects])
  
  // Check if an object should trigger auto-load
  const shouldTriggerLoad = useCallback((designation) => {
    if (!enabled || !animationPlaying) return false
    
    const trajectory = batchTrajectories[designation]
    if (!trajectory || !trajectory.trajectory) return false
    
    const state = loadingStates[designation]
    if (state?.isLoading) return false
    
    const totalPoints = trajectory.trajectory.length
    if (totalPoints === 0) return false
    
    // Threshold-based trigger
    const progressPercent = currentTimeIndex / totalPoints
    if (progressPercent >= thresholdPercent) {
      return true
    }
    
    // Time-based trigger
    const pointsRemaining = totalPoints - currentTimeIndex
    const secondsRemaining = pointsRemaining / animationSpeed
    if (secondsRemaining <= timeBeforeEndSeconds) {
      return true
    }
    
    return false
  }, [
    enabled,
    batchTrajectories,
    currentTimeIndex,
    animationSpeed,
    animationPlaying,
    thresholdPercent,
    timeBeforeEndSeconds,
    loadingStates
  ])
  
  // Add object to loading queue
  const queueLoad = useCallback((designation) => {
    setLoadingQueue(prev => {
      if (prev.includes(designation)) return prev
      console.log(`[Multi-Auto-Load] Queuing ${designation}`)
      return [...prev, designation]
    })
  }, [])
  
  // Load next segment for a specific object
  const loadSegmentForObject = useCallback(async (designation) => {
    const trajectory = batchTrajectories[designation]
    
    if (!trajectory) {
      console.error(`[Multi-Auto-Load] No trajectory found for ${designation}`)
      setLoadingStates(prev => ({
        ...prev,
        [designation]: {
          ...prev[designation],
          error: 'Trajectory not found'
        }
      }))
      return
    }
    
    if (!trajectory.final_state) {
      console.error(`[Multi-Auto-Load] No final_state for ${designation}`, trajectory)
      setLoadingStates(prev => ({
        ...prev,
        [designation]: {
          ...prev[designation],
          error: 'Missing final_state'
        }
      }))
      return
    }
    
    // Mark as loading
    loadingRef.current[designation] = true
    activeLoadsRef.current.add(designation)
    setLoadingStates(prev => ({
      ...prev,
      [designation]: {
        ...prev[designation],
        isLoading: true,
        error: null
      }
    }))
    
    try {
      console.log(`[Multi-Auto-Load] Loading segment for ${designation}`)
      
      const data = await continueTrajectory(
        trajectory.final_state,
        segmentDurationDays,
        segmentPoints,
        method
      )
      
      console.log(`[Multi-Auto-Load] Received ${data.trajectory.length} points for ${designation}`)
      
      // Calculate days_from_epoch for new points
      const originalEpoch = trajectory.start_time || trajectory.trajectory[0]?.time
      const newTrajectoryWithEpoch = data.trajectory.map(point => ({
        ...point,
        days_from_epoch: point.time - originalEpoch
      }))
      
      // Update the specific trajectory in the batch
      if (onTrajectoriesUpdate) {
        const updatedTrajectory = {
          ...trajectory,
          trajectory: [...trajectory.trajectory, ...newTrajectoryWithEpoch],
          final_state: data.final_state,
          continuation_info: {
            ...trajectory.continuation_info,
            segments_loaded: (trajectory.continuation_info?.segments_loaded || 0) + 1,
            total_points: trajectory.trajectory.length + newTrajectoryWithEpoch.length
          }
        }
        
        // Apply memory management (sliding window)
        if (updatedTrajectory.trajectory.length > maxPointsPerObject) {
          const pointsToRemove = updatedTrajectory.trajectory.length - maxPointsPerObject
          updatedTrajectory.trajectory = updatedTrajectory.trajectory.slice(pointsToRemove)
          console.log(`[Multi-Auto-Load] Trimmed ${pointsToRemove} points for ${designation}`)
        }
        
        // Update the batch with the new trajectory
        const updatedBatch = {
          ...batchTrajectories,
          [designation]: updatedTrajectory
        }
        
        onTrajectoriesUpdate(updatedBatch)
      }
      
      // Update loading state
      setLoadingStates(prev => ({
        ...prev,
        [designation]: {
          isLoading: false,
          segmentsLoaded: (prev[designation]?.segmentsLoaded || 0) + 1,
          error: null,
          lastLoadTime: Date.now()
        }
      }))
      
      console.log(`[Multi-Auto-Load] Successfully loaded segment for ${designation}`)
      
    } catch (error) {
      console.error(`[Multi-Auto-Load] Failed to load segment for ${designation}:`, error)
      
      setLoadingStates(prev => ({
        ...prev,
        [designation]: {
          ...prev[designation],
          isLoading: false,
          error: error.message || 'Failed to load segment'
        }
      }))
      
      if (onError) {
        onError(designation, error)
      }
    } finally {
      loadingRef.current[designation] = false
      activeLoadsRef.current.delete(designation)
    }
  }, [
    batchTrajectories,
    segmentDurationDays,
    segmentPoints,
    method,
    maxPointsPerObject,
    onTrajectoriesUpdate,
    onError
  ])
  
  // Process loading queue
  useEffect(() => {
    if (loadingQueue.length === 0) return
    if (activeLoadsRef.current.size >= maxConcurrentLoads) return
    
    // Get next item from queue
    const designation = loadingQueue[0]
    
    // Remove from queue
    setLoadingQueue(prev => prev.slice(1))
    
    // Start loading
    loadSegmentForObject(designation)
  }, [loadingQueue, maxConcurrentLoads, loadSegmentForObject])
  
  // Monitor all objects and queue loads as needed
  useEffect(() => {
    if (!enabled || !animationPlaying) return
    
    selectedObjects.forEach(obj => {
      if (shouldTriggerLoad(obj.designation)) {
        queueLoad(obj.designation)
      }
    })
  }, [enabled, animationPlaying, selectedObjects, shouldTriggerLoad, queueLoad, currentTimeIndex])
  
  // Manual trigger for specific object
  const triggerLoadForObject = useCallback((designation) => {
    if (!loadingRef.current[designation]) {
      queueLoad(designation)
    }
  }, [queueLoad])
  
  // Reset all states
  const reset = useCallback(() => {
    setLoadingStates({})
    setLoadingQueue([])
    activeLoadsRef.current.clear()
    loadingRef.current = {}
  }, [])
  
  // Calculate aggregate stats
  const isAnyLoading = Object.values(loadingStates).some(state => state.isLoading)
  const totalSegmentsLoaded = Object.values(loadingStates).reduce(
    (sum, state) => sum + (state.segmentsLoaded || 0),
    0
  )
  const activeLoads = activeLoadsRef.current.size
  const queuedLoads = loadingQueue.length
  
  return {
    loadingStates,
    isAnyLoading,
    totalSegmentsLoaded,
    activeLoads,
    queuedLoads,
    triggerLoadForObject,
    reset
  }
}
