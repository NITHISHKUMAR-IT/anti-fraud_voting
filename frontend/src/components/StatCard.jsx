import styles from './StatCard.module.css'

export default function StatCard({ label, value, sub, colour = 'default', icon }) {
  return (
    <div className={`${styles.card} ${styles[colour]}`}>
      <div className={styles.top}>
        <span className={styles.label}>{label}</span>
        {icon && <span className={styles.icon}>{icon}</span>}
      </div>
      <div className={styles.value}>{value ?? '—'}</div>
      {sub && <div className={styles.sub}>{sub}</div>}
    </div>
  )
}
