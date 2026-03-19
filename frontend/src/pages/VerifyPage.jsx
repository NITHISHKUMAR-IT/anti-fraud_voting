import { useState, useRef, useCallback } from 'react'
import Webcam from 'react-webcam'
import { useAuth } from '../hooks/useAuth.jsx'
import { verifyVoter } from '../services/verification.js'
import PageHeader from '../components/PageHeader.jsx'
import Badge from '../components/Badge.jsx'
import styles from './VerifyPage.module.css'

const STEPS = ['ID Lookup', 'Face Capture', 'Fingerprint', 'Ink Check', 'Decision']

function dataURLtoBlob(dataURL) {
  const [meta, data] = dataURL.split(',')
  const mime = meta.match(/:(.*?);/)[1]
  const bytes = atob(data)
  const arr = new Uint8Array(bytes.length)
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i)
  return new Blob([arr], { type: mime })
}

export default function VerifyPage() {
  const { officer } = useAuth()
  const [step, setStep]         = useState(0)
  const [voterId, setVoterId]   = useState('')
  const [faceImg, setFaceImg]   = useState(null)
  const [fpFile, setFpFile]     = useState(null)
  const [inkFile, setInkFile]   = useState(null)
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const webcamRef               = useRef(null)

  const capturePhoto = useCallback(() => {
    const shot = webcamRef.current?.getScreenshot()
    if (shot) setFaceImg(shot)
  }, [])

  const handleSubmit = async () => {
    if (!faceImg || !fpFile || !inkFile) {
      setError('All three inputs (face, fingerprint, finger image) are required.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const fd = new FormData()
      fd.append('voter_id', voterId.trim())
      fd.append('face_image', dataURLtoBlob(faceImg), 'face.jpg')
      fd.append('fingerprint_scan', fpFile, 'fp.bin')
      fd.append('finger_image', inkFile, 'finger.jpg')
      const res = await verifyVoter(fd)
      setResult(res.data)
      setStep(4)
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStep(0); setVoterId(''); setFaceImg(null)
    setFpFile(null); setInkFile(null); setResult(null); setError('')
  }

  return (
    <div className="fade-up">
      <PageHeader title="Voter Verification" subtitle="Multi-layer biometric identity verification" />

      {/* Step progress */}
      <div className={styles.stepper}>
        {STEPS.map((s, i) => (
          <div key={s} className={`${styles.stepItem} ${i === step ? styles.stepActive : ''} ${i < step ? styles.stepDone : ''}`}>
            <div className={styles.stepCircle}>{i < step ? '✓' : i + 1}</div>
            <span>{s}</span>
            {i < STEPS.length - 1 && <div className={`${styles.stepLine} ${i < step ? styles.stepLineDone : ''}`} />}
          </div>
        ))}
      </div>

      <div className={styles.body}>
        {/* Step 0: Voter ID */}
        {step === 0 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Enter Voter ID</div>
            <p className={styles.panelHint}>Scan or manually enter the voter's electoral photo ID number</p>
            <div className={styles.idInput}>
              <span className={styles.idPrefix}>ID</span>
              <input
                className={styles.idField}
                type="text"
                placeholder="e.g. TN/12/345/678901"
                value={voterId}
                onChange={(e) => setVoterId(e.target.value)}
                autoFocus
              />
            </div>
            {error && <div className={styles.errBox}>{error}</div>}
            <button
              className={styles.primaryBtn}
              onClick={() => { if (voterId.trim()) { setError(''); setStep(1) } else setError('Voter ID is required.') }}
            >
              Continue →
            </button>
          </div>
        )}

        {/* Step 1: Face */}
        {step === 1 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Capture Facial Image</div>
            <p className={styles.panelHint}>Ensure the voter's face is clearly visible and centred</p>
            <div className={styles.webcamWrap}>
              {!faceImg ? (
                <>
                  <Webcam
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className={styles.webcam}
                    mirrored={false}
                    videoConstraints={{ width: 480, height: 360, facingMode: 'user' }}
                  />
                  <div className={styles.scanOverlay}>
                    <div className={styles.scanBeam} />
                    <div className={styles.scanCorner + ' ' + styles.tl} />
                    <div className={styles.scanCorner + ' ' + styles.tr} />
                    <div className={styles.scanCorner + ' ' + styles.bl} />
                    <div className={styles.scanCorner + ' ' + styles.br} />
                  </div>
                </>
              ) : (
                <img src={faceImg} className={styles.webcam} alt="Captured face" />
              )}
            </div>
            <div className={styles.btnRow}>
              {!faceImg ? (
                <button className={styles.primaryBtn} onClick={capturePhoto}>
                  ◉ Capture
                </button>
              ) : (
                <>
                  <button className={styles.secondaryBtn} onClick={() => setFaceImg(null)}>Retake</button>
                  <button className={styles.primaryBtn} onClick={() => setStep(2)}>Continue →</button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Fingerprint */}
        {step === 2 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Fingerprint Scan</div>
            <p className={styles.panelHint}>Place voter's right index finger on the scanner. Upload the raw scan file.</p>
            <div className={styles.fpArea}>
              <div className={styles.fpIcon}>◈</div>
              <div className={styles.fpLabel}>
                {fpFile ? `✓ ${fpFile.name}` : 'No scan uploaded'}
              </div>
              <label className={styles.uploadBtn}>
                Upload Scan File
                <input type="file" accept=".bin,.raw,.bmp,.png,.jpg" hidden onChange={(e) => setFpFile(e.target.files[0])} />
              </label>
            </div>
            <div className={styles.btnRow}>
              <button className={styles.secondaryBtn} onClick={() => setStep(1)}>← Back</button>
              <button className={styles.primaryBtn} disabled={!fpFile} onClick={() => setStep(3)}>Continue →</button>
            </div>
          </div>
        )}

        {/* Step 3: Ink detection */}
        {step === 3 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Finger Ink Inspection</div>
            <p className={styles.panelHint}>Capture or upload a close-up photo of the voter's left index finger to detect prior voting ink</p>
            <div className={styles.fpArea}>
              <div className={styles.fpIcon} style={{color: inkFile ? 'var(--green)' : 'var(--text-muted)'}}>
                {inkFile ? '✓' : '◬'}
              </div>
              <div className={styles.fpLabel}>
                {inkFile ? `✓ ${inkFile.name}` : 'No image uploaded'}
              </div>
              <label className={styles.uploadBtn}>
                Upload Finger Image
                <input type="file" accept="image/*" hidden onChange={(e) => setInkFile(e.target.files[0])} />
              </label>
            </div>
            {error && <div className={styles.errBox}>{error}</div>}
            <div className={styles.btnRow}>
              <button className={styles.secondaryBtn} onClick={() => setStep(2)}>← Back</button>
              <button className={styles.primaryBtn} disabled={loading || !inkFile} onClick={handleSubmit}>
                {loading ? <span className={styles.spinner} /> : 'Run Verification →'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Decision */}
        {step === 4 && result && (
          <div className={styles.resultPanel}>
            <div className={`${styles.verdict} ${result.vote_allowed ? styles.verdictAllow : styles.verdictBlock}`}>
              <div className={styles.verdictIcon}>{result.vote_allowed ? '✓' : '✕'}</div>
              <div className={styles.verdictText}>{result.vote_allowed ? 'VOTE ALLOWED' : 'VOTE BLOCKED'}</div>
            </div>

            <div className={styles.voterMeta}>
              <span className="mono" style={{color:'var(--text-mono)'}}>{result.voter_id}</span>
              {result.full_name && <span style={{color:'var(--text-primary)', fontWeight:600}}>{result.full_name}</span>}
            </div>

            <p className={styles.reason}>{result.reason}</p>

            {/* Check breakdown */}
            <div className={styles.checks}>
              {[
                { label: 'Face Recognition',  ok: result.face?.matched,        detail: `Confidence: ${((result.face?.confidence || 0)*100).toFixed(1)}%` },
                { label: 'Fingerprint Match', ok: result.fingerprint?.matched,  detail: `Score: ${result.fingerprint?.score}` },
                { label: 'No Prior Ink',      ok: !result.ink?.ink_present,     detail: `Ink ratio: ${((result.ink?.ink_ratio||0)*100).toFixed(3)}%` },
              ].map((chk) => (
                <div key={chk.label} className={`${styles.checkRow} ${chk.ok ? styles.checkOk : styles.checkFail}`}>
                  <span className={styles.checkIcon}>{chk.ok ? '✓' : '✕'}</span>
                  <div>
                    <div className={styles.checkLabel}>{chk.label}</div>
                    <div className={styles.checkDetail + ' mono'}>{chk.detail}</div>
                  </div>
                </div>
              ))}
            </div>

            {result.alert_raised && (
              <div className={styles.alertNote}>
                ◬ Alert raised · ID: <span className="mono">{result.alert_id}</span>
              </div>
            )}

            <div className={styles.sessionId}>
              Session: <span className="mono">{result.session_id}</span>
            </div>

            <button className={styles.primaryBtn} style={{marginTop:16}} onClick={reset}>
              ↺ New Verification
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
