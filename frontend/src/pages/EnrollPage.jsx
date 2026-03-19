import { useState, useRef, useCallback } from 'react'
import Webcam from 'react-webcam'
import { useAuth } from '../hooks/useAuth.jsx'
import { enrollBiometrics } from '../services/verification.js'
import { registerVoter } from '../services/voters.js'
import PageHeader from '../components/PageHeader.jsx'
import styles from './EnrollPage.module.css'

function dataURLtoBlob(dataURL) {
  const [meta, data] = dataURL.split(',')
  const mime = meta.match(/:(.*?);/)[1]
  const bytes = atob(data)
  const arr = new Uint8Array(bytes.length)
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i)
  return new Blob([arr], { type: mime })
}

export default function EnrollPage() {
  const { officer } = useAuth()
  const webcamRef = useRef(null)

  const [step, setStep]     = useState(0) // 0=details, 1=biometrics, 2=done
  const [form, setForm]     = useState({ voter_id:'', full_name:'', date_of_birth:'', constituency:'', gender:'MALE', phone:'' })
  const [faceImg, setFace]  = useState(null)
  const [fpFile, setFp]     = useState(null)
  const [loading, setLoad]  = useState(false)
  const [error, setError]   = useState('')
  const [done, setDone]     = useState(null)

  const capture = useCallback(() => {
    const s = webcamRef.current?.getScreenshot()
    if (s) setFace(s)
  }, [])

  const setField = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleRegister = async () => {
    const required = ['voter_id','full_name','date_of_birth','constituency','gender']
    for (const k of required) {
      if (!form[k]) { setError(`${k.replace('_',' ')} is required.`); return }
    }
    setError('')
    setStep(1)
  }

  const handleEnroll = async () => {
    if (!faceImg || !fpFile) { setError('Face photo and fingerprint scan are required.'); return }
    setLoad(true); setError('')
    try {
      await registerVoter({ ...form, booth_id: officer.boothId })
      const fd = new FormData()
      fd.append('voter_id', form.voter_id)
      fd.append('face_image', dataURLtoBlob(faceImg), 'face.jpg')
      fd.append('fingerprint_scan', fpFile, 'fp.bin')
      const res = await enrollBiometrics(fd)
      setDone(res.data)
      setStep(2)
    } catch (err) {
      setError(err.response?.data?.detail || 'Enrollment failed.')
    } finally {
      setLoad(false)
    }
  }

  const reset = () => {
    setStep(0); setForm({ voter_id:'', full_name:'', date_of_birth:'', constituency:'', gender:'MALE', phone:'' })
    setFace(null); setFp(null); setDone(null); setError('')
  }

  return (
    <div className="fade-up">
      <PageHeader title="Voter Enrollment" subtitle="Register new voter and capture biometric data" />

      <div className={styles.body}>
        {step === 0 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Voter Details</div>
            <div className={styles.grid2}>
              {[
                { key:'voter_id',      label:'Voter ID',       placeholder:'TN/12/345/000001', type:'text' },
                { key:'full_name',     label:'Full Name',      placeholder:'As on electoral roll', type:'text' },
                { key:'date_of_birth', label:'Date of Birth',  placeholder:'',  type:'date' },
                { key:'constituency',  label:'Constituency',   placeholder:'e.g. Chennai Central', type:'text' },
                { key:'phone',         label:'Phone (opt.)',   placeholder:'+91 XXXXX XXXXX', type:'tel' },
              ].map(f => (
                <div key={f.key} className={styles.field}>
                  <label className={styles.label}>{f.label}</label>
                  <input
                    className={styles.input}
                    type={f.type}
                    placeholder={f.placeholder}
                    value={form[f.key]}
                    onChange={e => setField(f.key, e.target.value)}
                  />
                </div>
              ))}
              <div className={styles.field}>
                <label className={styles.label}>Gender</label>
                <select className={styles.input} value={form.gender} onChange={e => setField('gender', e.target.value)}>
                  <option value="MALE">Male</option>
                  <option value="FEMALE">Female</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
            </div>
            {error && <div className={styles.errBox}>{error}</div>}
            <button className={styles.primaryBtn} onClick={handleRegister}>Continue to Biometrics →</button>
          </div>
        )}

        {step === 1 && (
          <div className={styles.panel}>
            <div className={styles.panelTitle}>Capture Biometrics</div>
            <p className={styles.hint}>Enrolling for: <strong className="mono">{form.voter_id}</strong> — {form.full_name}</p>

            <div className={styles.biometricGrid}>
              <div>
                <div className={styles.sectionLabel}>Face Photo</div>
                <div className={styles.webcamWrap}>
                  {!faceImg ? (
                    <Webcam ref={webcamRef} screenshotFormat="image/jpeg" className={styles.webcam} mirrored={false} />
                  ) : (
                    <img src={faceImg} className={styles.webcam} alt="face" />
                  )}
                </div>
                <div className={styles.btnRow}>
                  {!faceImg
                    ? <button className={styles.primaryBtn} onClick={capture}>◉ Capture</button>
                    : <button className={styles.secondaryBtn} onClick={() => setFace(null)}>Retake</button>
                  }
                </div>
              </div>

              <div>
                <div className={styles.sectionLabel}>Fingerprint Scan</div>
                <div className={styles.fpBox}>
                  <div className={styles.fpIcon}>{fpFile ? '✓' : '◈'}</div>
                  <div className={styles.fpName}>{fpFile ? fpFile.name : 'No file selected'}</div>
                  <label className={styles.uploadBtn}>
                    Upload Scan
                    <input type="file" hidden onChange={e => setFp(e.target.files[0])} />
                  </label>
                </div>
              </div>
            </div>

            {error && <div className={styles.errBox}>{error}</div>}
            <div className={styles.btnRow}>
              <button className={styles.secondaryBtn} onClick={() => setStep(0)}>← Back</button>
              <button className={styles.primaryBtn} disabled={loading || !faceImg || !fpFile} onClick={handleEnroll}>
                {loading ? <span className={styles.spinner}/> : 'Complete Enrollment →'}
              </button>
            </div>
          </div>
        )}

        {step === 2 && done && (
          <div className={styles.panel}>
            <div className={styles.successBanner}>
              <div className={styles.successIcon}>✓</div>
              <div>
                <div className={styles.successTitle}>Enrollment Successful</div>
                <div className={styles.successSub}>Voter registered and biometrics stored securely</div>
              </div>
            </div>
            <div className={styles.summaryRow}>
              <span className={styles.summaryLabel}>Voter ID</span>
              <span className="mono" style={{color:'var(--text-mono)'}}>{done.voter_id}</span>
            </div>
            <div className={styles.summaryRow}>
              <span className={styles.summaryLabel}>Booth</span>
              <span className="mono">{officer.boothId}</span>
            </div>
            <button className={styles.primaryBtn} style={{marginTop:20}} onClick={reset}>
              ↺ Enroll Another Voter
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
