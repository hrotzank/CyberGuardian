/**
 * Returns TailwindCSS badge class and color based on risk level string.
 */
export function getRiskMeta(level = 'LOW') {
  const map = {
    LOW:      { badge: 'cg-badge-low',      color: '#00D26A', label: 'Riesgo Bajo',      icon: '🟢' },
    MEDIUM:   { badge: 'cg-badge-medium',   color: '#FFC857', label: 'Riesgo Medio',     icon: '🟡' },
    HIGH:     { badge: 'cg-badge-high',     color: '#FF4D4D', label: 'Riesgo Alto',      icon: '🔴' },
    CRITICAL: { badge: 'cg-badge-critical', color: '#FF4D4D', label: 'Riesgo Crítico',   icon: '🚨' },
  }
  return map[level?.toUpperCase()] ?? map.LOW
}

/**
 * Format ISO date to readable locale string
 */
export function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

/**
 * Truncate a string to maxLen characters
 */
export function truncate(str, maxLen = 60) {
  if (!str) return ''
  return str.length > maxLen ? `${str.slice(0, maxLen)}…` : str
}

/**
 * Clamp a number between min and max
 */
export function clamp(value, min = 0, max = 100) {
  return Math.min(Math.max(value, min), max)
}

/**
 * Map risk score to stroke-dashoffset for circular gauge
 * @param {number} score 0–100
 * @param {number} radius
 */
export function scoreToOffset(score, radius = 52) {
  const circumference = 2 * Math.PI * radius
  return circumference - (score / 100) * circumference
}
