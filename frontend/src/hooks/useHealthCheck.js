import { useState, useEffect, useCallback } from 'react'
import { checkHealth } from '../services/analysisService'

/**
 * Polls the backend health endpoint.
 * @param {number} intervalMs – polling interval in ms (default 30s)
 */
export function useHealthCheck(intervalMs = 30000) {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastChecked, setLastChecked] = useState(null)

  const fetch = useCallback(async () => {
    try {
      const data = await checkHealth()
      setHealth(data)
      setError(null)
    } catch (err) {
      setError(err)
      setHealth(null)
    } finally {
      setLoading(false)
      setLastChecked(new Date())
    }
  }, [])

  useEffect(() => {
    fetch()
    const id = setInterval(fetch, intervalMs)
    return () => clearInterval(id)
  }, [fetch, intervalMs])

  const isOnline = !error && health?.status === 'ok'

  return { health, loading, error, isOnline, lastChecked, refetch: fetch }
}
