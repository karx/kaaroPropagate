import axios from 'axios'

// API base URL - update this to match your backend
const API_BASE_URL = 'https://8000--0199ad84-7027-76e5-80a1-b3d96a8105a5.us-east-1-01.gitpod.dev'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const fetchComets = async ({ limit = 100, offset = 0, orbitType = null } = {}) => {
  const params = { limit, offset }
  if (orbitType) params.orbit_type = orbitType
  
  const response = await api.get('/comets', { params })
  return response.data
}

export const fetchComet = async (designation) => {
  const response = await api.get(`/comets/${designation}`)
  return response.data
}

export const fetchTrajectory = async (designation, days = 365, points = 100, method = 'twobody') => {
  const response = await api.get(`/comets/${designation}/trajectory`, {
    params: { days, points, method }
  })
  return response.data
}

export const fetchPosition = async (designation, time = null, daysFromEpoch = null) => {
  const params = {}
  if (time !== null) params.time = time
  if (daysFromEpoch !== null) params.days_from_epoch = daysFromEpoch
  
  const response = await api.get(`/comets/${designation}/position`, { params })
  return response.data
}

export const fetchStatistics = async () => {
  const response = await api.get('/statistics')
  return response.data
}
