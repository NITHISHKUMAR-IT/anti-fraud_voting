import styles from './Badge.module.css'

export default function Badge({ label, colour = 'blue' }) {
  return <span className={`${styles.badge} ${styles[colour]}`}>{label}</span>
}
