import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { getBoothStats } from '../services/voters.js'
import { getAlertSummary } from '../services/alerts.js'
import { listLogs } from '../services/logs.js'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import Badge from '../components/Badge.jsx'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { formatDate, resultColour, timeAgo } from '../utils/format.js'
import styles from './DashboardPage.module.css'

const COLOUR_MAP = { SUCCESS: '#22d383', FAILURE: '#ff4d5e', WARNING: '#ffc947' }

export default function DashboardPage() {
  const { officer } = useAuth()
  const [stats, setStats]       = useState(null)
  const [alertSum, setAlertSum] = useState({})
  const [recentLogs, setLogs]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [now, setNow]           = useState(new Date())

  useEffect(() => {
    const tick = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(tick)
  }, [])

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, alertRes, logsRes] = await Promise.all([
          getBoothStats(officer?.boothId),
          getAlertSummary(officer?.boothId),
          listLogs({ booth_id: officer?.boothId, limit: 8 }),
        ])
        setStats(statsRes.data)
        setAlertSum(alertRes.data)
        setLogs(logsRes.data)
      } catch (_) {}
      finally { setLoading(false) }
    }
    if (officer?.boothId) load()
  }, [officer])

  const chartData = recentLogs.reduce((acc, log) => {
    const key = log.action.replace(/_/g, ' ')
    const existing = acc.find(d => d.action === key)
    if (existing) existing.count++
    else acc.push({ action: key, count: 1 })
    return acc
  }, [])

  const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <div className="fade-up">
      <PageHeader
        title="Operations Dashboard"
        subtitle={`Booth ${officer?.boothId} · Monitoring active`}
        action={
          <div className={styles.clock}>
            <div className={styles.clockTime + ' mono'}>{timeStr}</div>
            <div className={styles.clockDate}>{dateStr}</div>
          </div>
        }
      />

      {loading ? (
        <div className={styles.loadingGrid}>
          {[1,2,3,4].map(i => <div key={i} className="skeleton" style={{height:100}} />)}
        </div>
      ) : (
        <>
          <div className={styles.statsGrid}>
            <StatCard label="Registered Voters" value={stats?.total_registered ?? '—'} icon="◎" colour="blue" sub="Total in booth registry" />
            <StatCard label="Votes Cast" value={stats?.total_voted ?? '—'} icon="✓" colour="green" sub="Successfully verified & voted" />
            <StatCard label="Pending" value={stats?.pending ?? '—'} icon="◷" colour="amber" sub="Yet to arrive at booth" />
            <StatCard label="Turnout" value={stats ? `${stats.turnout_percent}%` : '—'} icon="▲" colour={stats?.turnout_percent > 50 ? 'green' : 'default'} sub="Current voter turnout" />
          </div>

          <div className={styles.alertBanner}>
            {['CRITICAL','HIGH','MEDIUM','LOW'].map(sev => (
              alertSum[sev] ? (
                <div key={sev} className={`${styles.alertPill} ${styles['sev_'+sev.toLowerCase()]}`}>
                  <span className={styles.alertCount}>{alertSum[sev]}</span>
                  <span>{sev}</span>
                </div>
              ) : null
            ))}
            {Object.keys(alertSum).length === 0 && (
              <div className={styles.alertClear}>
                <span className={styles.alertDot} /> No active alerts
              </div>
            )}
          </div>

          <div className={styles.bottomGrid}>
            <div className={styles.chartPanel}>
              <div className={styles.panelHeader}>Recent Activity Breakdown</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{top:10, right:0, bottom:40, left:0}}>
                  <XAxis dataKey="action" tick={{fontSize:9, fill:'#4a5a72', fontFamily:'IBM Plex Mono'}} angle={-35} textAnchor="end" interval={0} />
                  <YAxis tick={{fontSize:10, fill:'#4a5a72'}} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{background:'#0d1424', border:'1px solid #1e2d45', borderRadius:6, fontSize:12}}
                    labelStyle={{color:'#e8edf5', fontFamily:'Syne'}}
                    itemStyle={{color:'#f5a623'}}
                  />
                  <Bar dataKey="count" radius={[3,3,0,0]}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={COLOUR_MAP[entry.action.includes('ALLOW') ? 'SUCCESS' : entry.action.includes('BLOCK') ? 'FAILURE' : 'WARNING'] || '#4da6ff'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className={styles.logsPanel}>
              <div className={styles.panelHeader}>Live Audit Feed</div>
              <div className={styles.logsList}>
                {recentLogs.length === 0 && (
                  <div className={styles.logsEmpty}>No recent activity.</div>
                )}
                {recentLogs.map(log => (
                  <div key={log.id} className={styles.logRow}>
                    <div className={styles.logLeft}>
                      <Badge label={log.result} colour={resultColour(log.result)} />
                      <span className={styles.logAction + ' mono'}>{log.action.replace(/_/g,' ')}</span>
                    </div>
                    <div className={styles.logRight}>
                      {log.voter_ref && <span className={styles.logVoter + ' mono'}>{log.voter_ref}</span>}
                      <span className={styles.logTime}>{timeAgo(log.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
