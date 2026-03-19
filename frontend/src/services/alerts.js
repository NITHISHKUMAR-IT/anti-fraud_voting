import api from './api.js'

export const listAlerts = (params = {}) =>
  api.get('/api/v1/alerts/', { params })

export const resolveAlert = (alertId, officerBadge) =>
  api.patch(`/api/v1/alerts/${alertId}/resolve`, { officer_badge: officerBadge })

export const getAlertSummary = (boothId) =>
  api.get('/api/v1/alerts/summary', { params: boothId ? { booth_id: boothId } : {} })
