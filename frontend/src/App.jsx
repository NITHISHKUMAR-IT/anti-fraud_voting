import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import Layout from './components/Layout.jsx'
import LoginPage from './pages/LoginPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import VerifyPage from './pages/VerifyPage.jsx'
import AlertsPage from './pages/AlertsPage.jsx'
import LogsPage from './pages/LogsPage.jsx'
import EnrollPage from './pages/EnrollPage.jsx'
import VotersPage from './pages/VotersPage.jsx'

function ProtectedRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="verify"    element={<VerifyPage />} />
            <Route path="enroll"    element={<EnrollPage />} />
            <Route path="voters"    element={<VotersPage />} />
            <Route path="alerts"    element={<AlertsPage />} />
            <Route path="logs"      element={<LogsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
