import api from './api.js'

export const listLogs = (params = {}) =>
  api.get('/api/v1/logs/', { params })
