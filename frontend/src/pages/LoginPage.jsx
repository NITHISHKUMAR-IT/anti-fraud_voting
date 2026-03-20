import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [phoneNumber, setPhoneNumber] = useState('')
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState('phone') // 'phone' or 'otp'
  const [otpMessage, setOtpMessage] = useState('')

  const handleRequestOTP = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(phoneNumber, 'request-otp')
      setStep('otp')
      setOtpMessage('OTP sent to your phone number')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to request OTP')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(phoneNumber, otp)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid OTP. Try again.')
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

        {step === 'phone' ? (
          <form onSubmit={handleRequestOTP} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>Phone Number</label>
              <input
                className={styles.input}
                type="tel"
                placeholder="e.g. +91 9876543210"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                autoFocus
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
                  <span>Request OTP</span>
                  <span className={styles.arrow}>→</span>
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOTP} className={styles.form}>
            <div className={styles.otpInfo}>
              <p>{otpMessage}</p>
              <p className={styles.phoneDisplay}>{phoneNumber}</p>
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Enter OTP</label>
              <input
                className={styles.input}
                type="text"
                placeholder="000000"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                autoFocus
                maxLength="6"
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
                  <span>Verify OTP</span>
                  <span className={styles.arrow}>→</span>
                </>
              )}
            </button>

            <button
              className={styles.backBtn}
              type="button"
              onClick={() => {
                setStep('phone')
                setError('')
                setOtp('')
              }}
            >
              ← Back
            </button>
          </form>
        )}

        <div className={styles.footer}>
          <span className={styles.footerDot} />
          <span>System secured · All access attempts are logged</span>
        </div>
      </div>
    </div>
  )
}
