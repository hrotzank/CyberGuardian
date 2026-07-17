import api from './api'

/**
 * CyberGuardian Analysis Service
 * POST /api/analyze – runs multi-agent phishing scan
 */
export const analyzeContent = async (content) => {
  const response = await api.post('/analyze', { content })
  return response.data
}

/**
 * Health check endpoint
 * GET /api/health – checks backend status
 */
export const checkHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

/**
 * Future integrations – ready to connect
 * PhishTank, OpenPhish, VirusTotal
 */
export const integrations = {
  // checkPhishTank: (url) => api.post('/integrations/phishtank', { url }),
  // checkVirusTotal: (url) => api.post('/integrations/virustotal', { url }),
  // checkOpenPhish: (url) => api.post('/integrations/openphish', { url }),
}
