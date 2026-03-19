import api from './api.js'

export const verifyVoter = (formData) =>
  api.post('/api/v1/verification/verify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const enrollBiometrics = (formData) =>
  api.post('/api/v1/verification/enroll', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
