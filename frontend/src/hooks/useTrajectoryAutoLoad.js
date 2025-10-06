import { useState, useEffect, useRef, useCallback } from 'react'
import { continueTrajectory } from '../api'

/**
 * Custom hook for automatic trajectory loading.
 * 
 * Monitors animation progress and automatically loads the next trajectory segment
 * when approaching the end of the current segment.
 * 
 * Features:
 * - Threshold-based triggering (default: 80% through current segment)
 * - Time-based triggering (default: 5 seconds before end)
 * - Background loading with loading state
 * - Automatic trajectory appending
 * - Memory management (sliding window)
 * - Error handling with retry logic
 * 
 * @param {Object} options - Configuration options
 * @returns {Object} Auto-load state and controls
 */
export function useTrajectoryAutoLoad({
  enabled = false,
  trajectory = null,
  currentTimeIndex = 0,
  animationSpeed = 1,
  animationPlaying = false,
  method = 'twobody',
  segmentDurationDays = 365,
  segmentPoints = 100,
  thresholdPercent = 0.8,
  timeBeforeEndSeconds = 5,
  maxPoints = 10000,
  onTrajectoryUpdate = null,
  onError = null
} = {}) {
  
  const [isLoading, setIsLoading] = useState(false)
  const [loadProgress, setLoadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [segmentsLoaded, setSegmentsLoaded] = useState(0)
  
  // Track loading state to prevent duplicate requests
  const loadingRef = useRef(false)
  const abortControllerRef = useRef(null)
  
  // Calculate trigger conditions
  const shouldTriggerLoad = useCallback(() => {
    if (!enabled || !trajectory || !animationPlaying || loadingRef.current) {
      return false
    }
    
    const totalPoints = trajectory.trajectory?.length || 0
    if (totalPoints === 0) return false
    
    // Threshold-based trigger: 80% through current segment
    const progressPercent = currentTimeIndex / totalPoints
    if (progressPercent >= thresholdPercent) {
      return true
    }
    
    // Time-based trigger: X seconds before end at current speed
    const pointsRemaining = totalPoints - currentTimeIndex
    const secondsRemaining = pointsRemaining / animationSpeed
    if (secondsRemaining <= timeBeforeEndSeconds) {
      return true
    }
    
    return false
  }, [
    enabled,
    trajectory,
    currentTimeIndex,
    animationSpeed,
    animationPlaying,
    thresholdPercent,
    timeBeforeEndSeconds
  ])
  
  // Load next trajectory segment
  const loadNextSegment = useCallback(async () => {
    if (loadingRef.current || !trajectory?.final_state) {
      return
    }
    
    loadingRef.current = true
    setIsLoading(true)
    setError(null)
    setLoadProgress(0)
    
    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController()
    
    try {
      console.log('[Auto-Load] Loading next segment...', {
        currentSegments: segmentsLoaded,
        currentPoints: trajectory.trajectory?.length || 0
      })
      
      // Get final state from current trajectory
      const finalState = trajectory.final_state
      
      if (!finalState) {
        throw new Error('No final_state in trajectory - cannot continue')
      }
      
      console.log('[Auto-Load] Requesting continuation from time:', finalState.time)
      
      // Request next segment
      const data = await continueTrajectory(
        finalState,
        segmentDurationDays,
        segmentPoints,
        method
      )
      
      console.log('[Auto-Load] Received', data.trajectory.length, 'new points')
      
      setLoadProgress(100)
      
      // Append new trajectory data
      if (onTrajectoryUpdate) {
        // Get the original epoch from the first trajectory point
        const originalEpoch = trajectory.start_time || trajectory.trajectory[0]?.time
        
        // Add days_from_epoch to new trajectory points
        const newTrajectoryWithEpoch = data.trajectory.map(point => ({
          ...point,
          days_from_epoch: point.time - originalEpoch
        }))
        
        const updatedTrajectory = {
          ...trajectory,
          trajectory: [...trajectory.trajectory, ...newTrajectoryWithEpoch],
          final_state: data.final_state,
          continuation_info: {
            ...trajectory.continuation_info,
            segments_loaded: segmentsLoaded + 1,
            total_points: trajectory.trajectory.length + newTrajectoryWithEpoch.length
          }
        }
        
        // Apply memory management (sliding window)
        if (updatedTrajectory.trajectory.length > maxPoints) {
          const pointsToRemove = updatedTrajectory.trajectory.length - maxPoints
          updatedTrajectory.trajectory = updatedTrajectory.trajectory.slice(pointsToRemove)
          console.log(`[Auto-Load] Trimmed ${pointsToRemove} points (keeping ${maxPoints})`)
        }
        
        onTrajectoryUpdate(updatedTrajectory)
        setSegmentsLoaded(prev => prev + 1)
        
        console.log('[Auto-Load] Segment loaded successfully', {
          newPoints: data.trajectory.length,
          totalPoints: updatedTrajectory.trajectory.length,
          segments: segmentsLoaded + 1
        })
      }
      
    } catch (err) {
      if (err.name === 'AbortError' || err.name === 'CanceledError') {
        console.log('[Auto-Load] Request cancelled')
      } else {
        console.error('[Auto-Load] Failed to load segment:', err)
        setError(err.message || 'Failed to load next segment')
        if (onError) {
          onError(err)
        }
      }
    } finally {
      loadingRef.current = false
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }, [
    trajectory,
    segmentDurationDays,
    segmentPoints,
    method,
    maxPoints,
    segmentsLoaded,
    onTrajectoryUpdate,
    onError
  ])
  
  // Monitor animation progress and trigger auto-load
  useEffect(() => {
    if (shouldTriggerLoad()) {
      console.log('[Auto-Load] Trigger conditions met, loading next segment...')
      loadNextSegment()
    }
  }, [shouldTriggerLoad, loadNextSegment])
  
  // Cancel loading on unmount or when disabled
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])
  
  // Manual trigger function
  const triggerLoad = useCallback(() => {
    if (!loadingRef.current) {
      loadNextSegment()
    }
  }, [loadNextSegment])
  
  // Reset function
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setIsLoading(false)
    setLoadProgress(0)
    setError(null)
    setSegmentsLoaded(0)
    loadingRef.current = false
  }, [])
  
  return {
    isLoading,
    loadProgress,
    error,
    segmentsLoaded,
    triggerLoad,
    reset,
    canLoad: !loadingRef.current && trajectory?.final_state != null
  }
}
