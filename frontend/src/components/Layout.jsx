import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import styles from './Layout.module.css'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard',   icon: '▦' },
  { to: '/verify',    label: 'Verify Voter', icon: '◈' },
  { to: '/enroll',    label: 'Enroll',       icon: '◉' },
  { to: '/voters',    label: 'Voters',       icon: '◎' },
  { to: '/alerts',    label: 'Alerts',       icon: '◬' },
  { to: '/logs',      label: 'Audit Logs',   icon: '≡' },
]

export default function Layout() {
  const { officer, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className={styles.shell}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.brandIcon}>⬡</span>
          <div>
            <div className={styles.brandTitle}>SSVVS</div>
            <div className={styles.brandSub}>Voting Verification</div>
          </div>
        </div>

        <div className={styles.boothTag}>
          <span className={styles.dot} />
          <span className="mono">{officer?.boothId || 'BOOTH-??'}</span>
        </div>

        <nav className={styles.nav}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.navItemActive : ''}`
              }
            >
              <span className={styles.navIcon}>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.officerCard}>
            <div className={styles.officerAvatar}>
              {officer?.name?.[0] || 'O'}
            </div>
            <div className={styles.officerInfo}>
              <div className={styles.officerName}>{officer?.name}</div>
              <div className={styles.officerBadge + ' mono'}>{officer?.badge}</div>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            ⏻ Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className={styles.main}>
        <div className={styles.content}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}
