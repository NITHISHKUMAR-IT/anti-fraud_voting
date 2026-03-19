import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { listLogs } from '../services/logs.js'
import PageHeader from '../components/PageHeader.jsx'
import Badge from '../components/Badge.jsx'
import DataTable from '../components/DataTable.jsx'
import { formatDate, resultColour } from '../utils/format.js'
import styles from './LogsPage.module.css'

export default function LogsPage() {
  const { officer } = useAuth()
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const params = { booth_id: officer?.boothId, limit: 100 }
        if (search.trim()) params.voter_ref = search.trim()
        const res = await listLogs(params)
        setLogs(res.data)
      } catch (_) {}
      finally { setLoading(false) }
    }
    load()
  }, [search])

  const cols = [
    { key: 'timestamp',    label: 'Timestamp',   width: 160, render: (v) => <span className="mono" style={{fontSize:11, color:'var(--text-muted)'}}>{formatDate(v)}</span> },
    { key: 'result',       label: 'Result',       width: 90,  render: (v) => <Badge label={v} colour={resultColour(v)} /> },
    { key: 'action',       label: 'Action',       width: 180, render: (v) => <span className="mono" style={{fontSize:11}}>{v?.replace(/_/g,' ')}</span> },
    { key: 'voter_ref',    label: 'Voter ID',     width: 140, render: (v) => <span className="mono" style={{color:'var(--text-mono)', fontSize:12}}>{v || '—'}</span> },
    { key: 'officer_badge',label: 'Officer',      width: 110, render: (v) => <span className="mono" style={{fontSize:11, color:'var(--text-secondary)'}}>{v || '—'}</span> },
    { key: 'detail',       label: 'Detail',                   render: (v) => <span style={{fontSize:11, color:'var(--text-muted)'}}>{v || '—'}</span> },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title="Audit Logs"
        subtitle="Immutable record of all verification events"
        action={
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search by Voter ID..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        }
      />
      {loading ? (
        <div className="skeleton" style={{height: 300, borderRadius: 12}} />
      ) : (
        <DataTable columns={cols} rows={logs} emptyMessage="No logs found." />
      )}
    </div>
  )
}
