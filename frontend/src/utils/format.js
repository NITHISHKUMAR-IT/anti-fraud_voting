import { format, formatDistanceToNow } from 'date-fns'

export const formatDate = (iso) => {
  if (!iso) return '—'
  return format(new Date(iso), 'dd MMM yyyy, HH:mm')
}

export const timeAgo = (iso) => {
  if (!iso) return '—'
  return formatDistanceToNow(new Date(iso), { addSuffix: true })
}

export const severityColour = (sev) => {
  const map = { CRITICAL: 'red', HIGH: 'red', MEDIUM: 'yellow', LOW: 'blue' }
  return map[sev] || 'blue'
}

export const resultColour = (result) => {
  const map = { SUCCESS: 'green', FAILURE: 'red', WARNING: 'yellow' }
  return map[result] || 'blue'
}
