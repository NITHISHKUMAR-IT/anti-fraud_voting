import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { listVoters } from '../services/voters.js'
import PageHeader from '../components/PageHeader.jsx'
import Badge from '../components/Badge.jsx'
import DataTable from '../components/DataTable.jsx'
import { formatDate } from '../utils/format.js'
import styles from './VotersPage.module.css'

export default function VotersPage() {
  const { officer } = useAuth()
  const [voters, setVoters]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const res = await listVoters({ booth_id: officer?.boothId, limit: 100 })
        setVoters(res.data)
      } catch (_) {}
      finally { setLoading(false) }
    }
    load()
  }, [])

  const cols = [
    { key: 'voter_id',    label: 'Voter ID',  width: 160, render: (v) => <span className="mono" style={{color:'var(--text-mono)', fontSize:12}}>{v}</span> },
    { key: 'full_name',   label: 'Name',      width: 180, render: (v) => <span style={{fontWeight:500}}>{v}</span> },
    { key: 'gender',      label: 'Gender',    width: 80,  render: (v) => <span style={{color:'var(--text-muted)', fontSize:12}}>{v}</span> },
    { key: 'constituency',label: 'Constituency' },
    { key: 'has_voted',   label: 'Status',    width: 100, render: (v) => <Badge label={v ? 'Voted' : 'Pending'} colour={v ? 'green' : 'grey'} /> },
    { key: 'voted_at',    label: 'Voted At',  width: 160, render: (v) => <span className="mono" style={{fontSize:11, color:'var(--text-muted)'}}>{formatDate(v)}</span> },
  ]

  return (
    <div className="fade-up">
      <PageHeader
        title="Voter Registry"
        subtitle={`Registered voters — Booth ${officer?.boothId}`}
        action={
          <div className={styles.counter}>
            <span className="mono" style={{color:'var(--accent)', fontSize:18, fontWeight:700}}>{voters.length}</span>
            <span style={{color:'var(--text-muted)', fontSize:11}}>registered</span>
          </div>
        }
      />
      {loading ? (
        <div className="skeleton" style={{height:300, borderRadius:12}} />
      ) : (
        <DataTable columns={cols} rows={voters} emptyMessage="No voters registered for this booth." />
      )}
    </div>
  )
}
