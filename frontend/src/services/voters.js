import api from './api.js'

export const getVoterStatus = (voterId) =>
  api.get(`/api/v1/voters/${voterId}`)

export const listVoters = (params = {}) =>
  api.get('/api/v1/voters/', { params })

export const registerVoter = (payload) =>
  api.post('/api/v1/voters/', payload)

export const getBoothStats = (boothId) =>
  api.get(`/api/v1/voters/stats/${boothId}`)
