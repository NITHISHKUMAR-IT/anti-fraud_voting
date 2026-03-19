import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { listAlerts, resolveAlert } from '../services/alerts.js'
import PageHeader from '../components/PageHeader.jsx'
import Badge from '../components/Badge.jsx'
import DataTable from '../components/DataTable.jsx'
import { formatDate } from '../utils/format.js'
import styles from './AlertsPage.module.css'

const SEV_COLOUR = { CRITICAL: 'red', HIGH: 'red', MEDIUM: 'yellow', LOW: 'blue' }
const TYPE_LABEL = {
  DUPLICATE_VOTE: 'Duplicate Vote',
  FACE_MISMATCH: 'Face Mismatch',
  FINGERPRINT_MISMATCH: 'FP Mismatch',
  INK_DETECTED_ON_ARRIVAL: 'Prior Ink',
  MULTIPLE_FAILED_ATTEMPTS: 'Multiple Fails',
  UNKNOWN_VOTER: 'Unknown Voter',
  SYSTEM_ERROR: 'System Error',
}

export default function AlertsPage() {
  const { officer } = useAuth()
  const [alerts, setAlerts]       = useState([])
  const [loading, setLoading]     = useState(true)
  const [unresolvedOnly, setUnres] = useState(false)
  const [resolving, setResolving] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await listAlerts({ booth_id: officer?.boothId, unresolved_only: unresolvedOnly, limit: 50 })
      setAlerts(res.data)
    } catch (_) {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [unresolvedOnly])

  const handleResolve = async (id) => {
    setResolving(id)
    try {
      await resolveAlert(id, officer.badge)
      await load()
    } catch (_) {}
    finally { setResolving(null) }
  }

  const cols = [
    { key: 'created_at',  label: 'Time',      width: 160, render: (v) => <span className="mono" style={{fontSize:11, color:'var(--text-muted)'}}>{formatDate(v)}</span> },
    { key: 'severity',    label: 'Severity',   width: 90,  render: (v) => <Badge label={v} colour={SEV_COLOUR[v] || 'blue'} /> },
    { key: 'alert_type',  label: 'Type',       width: 160, render: (v) => <span className="mono" style={{fontSize:11}}>{TYPE_LABEL[v] || v}</span> },
    { key: 'voter_ref',   label: 'Voter ID',   width: 140, render: (v) => <span className="mono" style={{color:'var(--text-mono)', fontSize:12}}>{v || '—'}</span> },
    { key: 'message',     label: 'Details',                render: (v) => <span style={{fontSize:12, color:'var(--text-secondary)'}}>{v}</span> },
    { key: 'is_resolved', label: 'Status',     width: 90,  render: (v) => <Badge label={v ? 'Resolved' : 'Open'} colour={v ? 'green' : 'red'} /> },
    {
      key: 'id', label: 'Action', width: 100,
      render: (v, row) => !row.is_resolved ? (
        <button
          className={styles.resolveBtn}
          disabled={resolving === v}
          onClick={() => handleResolve(v)}
        >
          {resolving === v ? '...' : 'Resolve'}
        </button>
      ) : <span style={{color:'var(--text-muted)', fontSize:11}}>—</span>
    },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title="Alert Management"
        subtitle="Suspicious activity and fraud flags"
        action={
          <label className={styles.toggle}>
            <input type="checkbox" checked={unresolvedOnly} onChange={e => setUnres(e.target.checked)} />
            <span>Unresolved only</span>
          </label>
        }
      />
      {loading ? (
        <div className="skeleton" style={{height: 300, borderRadius: 12}} />
      ) : (
        <DataTable columns={cols} rows={alerts} emptyMessage="No alerts found." />
      )}
    </div>
  )
}
