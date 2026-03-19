import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [badge, setBadge] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(badge, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      {/* Decorative grid */}
      <div className={styles.grid} aria-hidden="true" />

      <div className={styles.card}>
        <div className={styles.logoRow}>
          <span className={styles.logoHex}>⬡</span>
          <div>
            <div className={styles.logoTitle}>SSVVS</div>
            <div className={styles.logoSub}>Secure Smart Voting Verification System</div>
          </div>
        </div>

        <div className={styles.divider} />

        <h2 className={styles.heading}>Officer Authentication</h2>
        <p className={styles.hint}>Access restricted to authorised polling personnel</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Badge Number</label>
            <input
              className={styles.input}
              type="text"
              placeholder="e.g. ADMIN-001"
              value={badge}
              onChange={(e) => setBadge(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Password</label>
            <input
              className={styles.input}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <button
            className={styles.submitBtn}
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <span className={styles.spinner} />
            ) : (
              <>
                <span>Authenticate</span>
                <span className={styles.arrow}>→</span>
              </>
            )}
          </button>
        </form>

        <div className={styles.footer}>
          <span className={styles.footerDot} />
          <span>System secured · All access attempts are logged</span>
        </div>
      </div>
    </div>
  )
}
