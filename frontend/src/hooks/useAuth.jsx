import { createContext, useContext, useState, useCallback } from 'react'
import api from '../services/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('ssvvs_token'))
  const [officer, setOfficer] = useState(() => {
    const raw = localStorage.getItem('ssvvs_officer')
    return raw ? JSON.parse(raw) : null
  })

  const login = useCallback(async (badgeNumber, password) => {
    const res = await api.post('/api/v1/voters/login', {
      badge_number: badgeNumber,
      password,
    })
    const { access_token, officer_name, booth_id } = res.data
    const officerData = { name: officer_name, boothId: booth_id, badge: badgeNumber }
    localStorage.setItem('ssvvs_token', access_token)
    localStorage.setItem('ssvvs_officer', JSON.stringify(officerData))
    setToken(access_token)
    setOfficer(officerData)
    return officerData
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('ssvvs_token')
    localStorage.removeItem('ssvvs_officer')
    setToken(null)
    setOfficer(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, officer, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
